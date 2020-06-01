#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  - read indoor-located pressure/temperature sensor
#    - log sensor data to a phant server
#    - log external weather data (read from Web API)

import sys
import time

# import datetime
import json
from pprint import pprint
import signal
import ssl
import requests  # so can handle exceptions

import Adafruit_BMP.BMP085 as BMP085
from Adafruit_LED_Backpack.SevenSegment import SevenSegment

# from phant3 import VERSION
from phant3.Phant import Phant

import nest  # https://github.com/jkoelker/python-nest/
from pyowm.owm import OWM  # https://github.com/csparpa/pyowm
from pyowm.commons import exceptions as OwmExceptions

import forecastio  # https://github.com/ZeevG/python-forecast.io

# Logging sensor readings to Phant
LOGGING = True
# LOGGING = False
LOGGING_COUNT = 0

# Use Dark Sky API for local weather - https://darksky.net/dev/docs
# DARK_SKY_WEATHER_API = True
DARK_SKY_WEATHER_API = False

# Use Open Weather Map API for local weather - https://openweathermap.org/api https://openweathermap.org/api/one-call-api
OWM_API = True
# OWM_API = False

# Use Nest API for another indoor temperature source
NEST_API = True
# NEST_API = False

# How long to wait (in seconds) between logging measurements.
FREQUENCY_SECONDS = 300

# How long to wait (in seconds) to display F or C.
ALTERNATE_TEMP_SCALE_SECONDS = 5

# Approximately how often measurements are made (in seconds)
MEASUREMENT_INTERVAL = 3 * ALTERNATE_TEMP_SCALE_SECONDS

# How seldom to upload the sensor log data, if LOGGING is on
COUNT_INTERVAL = FREQUENCY_SECONDS / MEASUREMENT_INTERVAL

# Additional characters for 7 segment display
RAW_DIGIT_VALUES = {
    'tickmark': 0x02,
    'outdoor_degrees': 0x6B,
    '°': 0x63,
}

# Read in config file
with open('weather_logging_config.json') as config_file:
    config = json.loads(config_file.read())
# pprint(config)
pprint(config["i2c_addresses"])


def convert_json_string_to_hexadecimal_value(s):
    value = 0
    try:
        value = int(s, 16)
    except:
        pass
    return value


bmp_address = convert_json_string_to_hexadecimal_value(
    config["i2c_addresses"]["bmp085"]
)
led_display_address = convert_json_string_to_hexadecimal_value(
    config["i2c_addresses"]["i2c_led"]
)
# print(bmp_address)
# print(led_display_address)
darksky_secret_key = config["darksky"]["secret-key"]
darksky_lat = config["darksky"]["lat"]
darksky_lng = config["darksky"]["lng"]
# print(darksky_lat, darksky_lng)
owm_secret_key = config["owm"]["secret-key"]
owm_lat = config["owm"]["lat"]
owm_lon = config["owm"]["lon"]

nest_client_id = config['timetemp_nest']['client_id']
nest_client_secret = config['timetemp_nest']['client_secret']
nest_access_token_cache_file = 'nest.json'

# Create sensor instance with default I2C bus
bmp = BMP085.BMP085(mode=BMP085.BMP085_HIGHRES, address=bmp_address)

# Initialize a LED display
segment = SevenSegment(address=led_display_address)
segment.begin()
print(segment)

if LOGGING:
    # Read in Phant config file
    json_keys_file2 = 'phant-config.json'
    p2 = Phant(jsonPath=json_keys_file2)

    print(
        'Logging sensor measurements taken every {2} seconds \
        to "{0}" every {1} seconds.'.format(
            p2.title, FREQUENCY_SECONDS, MEASUREMENT_INTERVAL
        )
    )
    # print(p2)

# Initialize 'currently' and 'outside_temperature'
if DARK_SKY_WEATHER_API:
    outside_temperature = 42
    forecast = forecastio.load_forecast(darksky_secret_key, darksky_lat, darksky_lng)
    if 'X-Forecast-API-Calls' in forecast.http_headers:
        print(forecast.http_headers['X-Forecast-API-Calls'], ' API calls')
    currently = forecast.currently()
    print(currently.summary)
    print(currently.time)
    print(currently.temperature)

if OWM_API:
    outside_temperature = 42
    owm = OWM(owm_secret_key)
    mgr = owm.weather_manager()
    try:
        one_call = mgr.one_call(owm_lat, owm_lon)
        currently = one_call.current
        print(currently.status)
        print(currently.detailed_status)
        print(currently.reference_time())
        print(currently.temperature(unit='fahrenheit'))
    except requests.exceptions.ConnectionError as errec:
        print("OWM API: Error Connecting:", errec)
        print('-W- Is network down?')
    except OwmExceptions.APIRequestError as errapi:
        print("OWM API Error:", errapi)
    finally:
        # disable API if a network error encountered
        if not currently:
            OWM_API = False

# Initialize 'NAPI' and 'nest_temperature'
global NAPI
NAPI = None
if NEST_API:
    nest_temperature = 35.0
    NAPI = nest.Nest(
        client_id=nest_client_id,
        client_secret=nest_client_secret,
        access_token_cache_file=nest_access_token_cache_file,
    )
    try:
        if NAPI.authorization_required:
            print('Authorization required.  Run "python ./nest_access.py"')
            raise SystemExit

        for structure in NAPI.structures:
            print('Structure %s' % structure.name)
            print('    Away: %s' % structure.away)
            print('    Devices:')

            for device in structure.thermostats:
                print('        Device: %s' % device.name)
                print('            Temp: %0.1f' % device.temperature)
                nest_temperature = device.temperature
    except requests.exceptions.ConnectionError as errec:
        print("Nest API: Error Connecting:", errec)
        print('-W- Is network down?')
        # log_error(error_type='OWM API: ConnectionError')
    finally:
        # disable API if a network error encountered
        if nest_temperature == 35.0:
            NEST_API = False

def display_temperature_in_fahrenheit(led_display, temperature, where):
    segment = led_display
    if round(temperature * 10.0) >= 1000.0:  # 100 degrees or above (###F)
        segment.set_digit(0, int(round(temperature) / 100))  # Hundreds
        segment.set_digit(1, int(round(temperature - 100.0) / 10))  # Tens
        segment.set_digit(2, int(round(temperature) % 10))  # Ones
        segment.set_digit(3, 'F')
        segment.set_colon(False)
    elif round(temperature * 10.0) > 95.0:  # 10 to 99 degrees (##°F)
        segment.set_digit(0, int(round(temperature) / 10))  # Tens
        segment.set_digit(1, int(round(temperature) % 10))  # Ones
        if where == 'outdoor':
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['outdoor_degrees'])
            segment.set_digit(3, 'F')
        elif where == 'nest':
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['°'])
            segment.set_digit(3, 'F')
        else:
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['tickmark'])
            segment.set_digit(3, 'F')

        segment.set_colon(False)
    elif round(temperature * 10.0) > -5.0:  # -0 to 9 degrees    (_#°F)
        rounded = int(round(temperature))
        if rounded == 10:
            segment.set_digit(0, 1)
        else:
            segment.set_digit(0, ' ')  # Tens
        segment.set_digit(1, int(round(temperature) % 10))  # Ones
        if where == 'outdoor':
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['outdoor_degrees'])
            segment.set_digit(3, 'F')
        elif where == 'nest':
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['°'])
            segment.set_digit(3, 'F')
        else:
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['tickmark'])
            segment.set_digit(3, 'F')

        segment.set_colon(False)
    elif round(temperature * 10.0) > -94.9:  # -9 to 0 degrees (-#°F)
        segment.set_digit(0, '-')
        segment.set_digit(1, int(round(abs(temperature)) % 10))  # Ones
        if where == 'outdoor':
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['outdoor_degrees'])
            segment.set_digit(3, 'F')
        elif where == 'nest':
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['°'])
            segment.set_digit(3, 'F')
        else:
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['tickmark'])
            segment.set_digit(3, 'F')

        segment.set_colon(False)

    elif round(temperature * 10.0) >= -995.0:  # -99 to -10 degrees (-##F)
        segment.set_digit(0, '-')  # Tens
        segment.set_digit(1, int(round(abs(temperature)) / 10))  # Tens
        segment.set_digit(2, int(round(abs(temperature)) % 10))  # Ones
        segment.set_digit(3, 'F')

        segment.set_colon(False)

    else:  # error (do not expect to reach here)
        segment.set_digit(1, 'E')
        segment.set_digit(2, 'E')
        segment.set_digit(3, 'E')
        segment.set_digit(4, 'E')

        segment.set_colon(False)


# systemd: time_display.service: State 'stop-sigterm' timed out. Killing.
print('Press Ctrl-C to quit.')
ERROR_TABLES = {}


def log_error(error_type='UnknownError'):
    global ERROR_TABLES

    if error_type not in ERROR_TABLES:
        ERROR_TABLES[error_type] = 1
    else:
        ERROR_TABLES[error_type] = ERROR_TABLES[error_type] + 1


def print_error_tables():
    global ERROR_TABLES

    print(ERROR_TABLES, end='')
    sys.stdout.flush()


def handler_stop_signals(signum, frame):
    segment.clear()
    segment.write_display()
    print_error_tables()
    ## time.sleep(4)
    # Raises SystemExit(0):
    sys.exit(0)


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

while True:
    try:
        # Attempt to get sensor readings.
        temp = bmp.read_temperature()
        pressure = bmp.read_pressure()
        altitude = bmp.read_altitude()

        temp_in_F = (temp * 9.0 / 5.0) + 32.0

        print("\nBMP Sensor", end=" ")
        print("  Temp(°C): %.1f°C" % temp, end=" ")
        print("  Temp(°F): %.1f°F" % temp_in_F, end=" ")
        print("  Pressure: %.1f hPa" % (pressure / 100.0), end=" ")
        print("  Altitude: %.1f m" % altitude)
        print("  Nest Temp(°F): %.1f°F" % nest_temperature, end=" ")
        print("  outside Temp(°F): %.1f°F" % outside_temperature)
        print("Press CTRL+C to exit")
        # print("")

        for temp_where in ['outdoor', 'sensor', 'nest']:

            if temp_where == 'sensor':
                display_temperature_in_fahrenheit(segment, temp_in_F, temp_where)
            elif temp_where == 'outdoor':
                if DARK_SKY_WEATHER_API:
                    outside_temperature = 42
                    try:
                        outside_temperature = currently.temperature
                    except forecastio.utils.PropertyUnavailable as e:
                        print("DarkSky API: Error:", e)
                        log_error(error_type='DarkSky API: PropertyUnavailable')

                    display_temperature_in_fahrenheit(
                        segment, outside_temperature, temp_where
                    )
                else:
                    display_temperature_in_fahrenheit(segment, temp_in_F, 'sensor')
                if OWM_API:
                    outside_temperature = 42
                    try:
                        outside_temperature = currently.temperature(unit='fahrenheit')[
                            'temp'
                        ]
                    except:
                        print("OWM: Unexpected error:", sys.exc_info()[0])
                        raise

                    display_temperature_in_fahrenheit(
                        segment, outside_temperature, temp_where
                    )
                else:
                    display_temperature_in_fahrenheit(segment, temp_in_F, 'sensor')
            elif temp_where == 'nest':
                if NEST_API:
                    indoor_temperature = nest_temperature
                    display_temperature_in_fahrenheit(
                        segment, indoor_temperature, temp_where
                    )
                else:
                    display_temperature_in_fahrenheit(segment, temp_in_F, 'sensor')
            segment.write_display()
            print_error_tables()
            time.sleep(ALTERNATE_TEMP_SCALE_SECONDS)

        if LOGGING:

            ambient_temp_C = temp
            ambient_temp_F = temp_in_F

            ambient_pressure = pressure / 100.0

            if False:
                fields = (ambient_pressure, ambient_temp_C, ambient_temp_F, altitude)
                print(fields)

            if (LOGGING_COUNT % COUNT_INTERVAL) == 0:

                # Use same interval as logging to request darksky API
                if DARK_SKY_WEATHER_API:
                    try:
                        forecast = forecastio.load_forecast(
                            darksky_secret_key, darksky_lat, darksky_lng
                        )
                        currently = forecast.currently()
                    except requests.exceptions.HTTPError as e:
                        # Need an 404, 503, 500, 403 etc.
                        status_code = e.response.status_code
                        print("HTTPError:", status_code, e)
                        log_error(error_type='Dark Sky API: HTTPError')
                    except requests.exceptions.ConnectionError as errec:
                        print("Dark Sky API: Error Connecting:", errec)
                        print('-W- Is network down?')
                        log_error(error_type='Dark Sky API: ConnectionError')
                    print("DarkSky API:")
                    if 'X-Forecast-API-Call' in forecast.http_headers:
                        print(forecast.http_headers['X-Forecast-API-Calls'])
                    try:
                        print(currently.time)
                        print(currently.temperature)
                    except forecastio.utils.PropertyUnavailable as e:
                        print("DarkSky API: Error:", e)
                        log_error(error_type='DarkSky API: PropertyUnavailable')

                # Use same interval as logging to request OMW API
                if OWM_API:
                    try:
                        one_call = mgr.one_call(owm_lat, owm_lon)
                        currently = one_call.current
                    except requests.exceptions.HTTPError as e:
                        # Need an 404, 503, 500, 403 etc.
                        status_code = e.response.status_code
                        print("HTTPError:", status_code, e)
                        log_error(error_type='OWM API: HTTPError')
                    except requests.exceptions.ConnectionError as errec:
                        print("OWM API: Error Connecting:", errec)
                        print('-W- Is network down?')
                        log_error(error_type='OWM API: ConnectionError')
                    except OwmExceptions.APIRequestError as errapi:
                        print("OWM API Error:", errapi)
                        log_error(error_type='OWM API: APIRequestError')
                    print("OWM API:", end="  ")
                    try:
                        print(currently.ref_time)
                        print(currently.temperature(unit='fahrenheit'))
                    except:
                        print("OWM: Error:")
                        print("Unexpected error:", sys.exc_info()[0])
                        log_error(error_type='OWM API: Exception')
                        raise

                # Use same interval as logging to request Nest API
                if NEST_API:
                    try:
                        if NAPI.authorization_required:
                            print(
                                'Authorization required.  Run \
                                "python ./nest_access.py"'
                            )
                            raise SystemExit

                        for structure in NAPI.structures:
                            for device in structure.thermostats:
                                nest_temperature = device.temperature
                                print('Nest temperature: {0}'.format(nest_temperature))
                    except requests.exceptions.ConnectionError as errec:
                        print("NEST API: Error Connecting:", errec)
                        print('-W- Is network down?')
                        log_error(error_type='NEST API: ConnectionError')
                    except IndexError as e:
                        print("NEST API: IndexError:", e)
                        log_error(error_type='NEST API: IndexError')
                    except nest.nest.APIError as errnapi:
                        print("NEST API: APIError:", errnapi)
                        log_error(error_type='NEST API: APIError')

                # the following are only available in the OWM API
                cloudiness = currently.clouds  # percent
                cond = currently.status
                cond_desc = currently.detailed_status
                dew_point = currently.dewpoint
                dt = currently.ref_time
                in_humid = 0
                in_pres = ambient_pressure
                in_tc = ambient_temp_C
                in_tf = ambient_temp_F
                out_feels_like = currently.temperature(unit='fahrenheit')['feels_like']
                out_humid = currently.humidity
                out_pres = currently.pressure['press']
                out_temp = currently.temperature(unit='fahrenheit')['temp']
                uvi = currently.uvi
                weather_code = currently.weather_code
                weather_icon_name = currently.weather_icon_name
                wind = currently.wind(unit='miles_hour')
                wind_deg = wind['deg']
                wind_speed = wind['speed']

                try:
                    if False:
                        p2.log(
                            altitude, ambient_pressure, ambient_temp_C, ambient_temp_F
                        )
                    else:
                        # cloudiness cond cond_desc dew_point dt in_humid
                        # in_pres in_tc in_tf out_feels_like out_humid out_pres
                        # out_temp uvi weather_code weather_icon_name wind_deg
                        # wind_speed
                        p2.log(
                            cloudiness,
                            cond,
                            cond_desc,
                            dew_point,
                            dt,
                            in_humid,
                            in_pres,
                            in_tc,
                            in_tf,
                            out_feels_like,
                            out_humid,
                            out_pres,
                            out_temp,
                            uvi,
                            weather_code,
                            weather_icon_name,
                            wind_deg,
                            wind_speed,
                        )

                    print('Wrote a row to {0}'.format(p2.title))
                    print((p2.remaining_bytes, p2.cap))
                except ValueError as errv:
                    print('-E- Error logging to {}'.format(p2.title))
                    print('-W- Is phant server down?')
                    print('ValueError: {}'.format(str(errv)))
                    log_error(error_type='ValueError')
                except requests.exceptions.ConnectionError as errec:
                    print("Error Connecting:", errec)
                    print('-W- Is network down?')
                    log_error(error_type='ConnectionError')
                except requests.exceptions.Timeout as errt:
                    print("Timeout Error:", errt)
                    log_error(error_type='Timeout')

                except requests.exceptions.RequestException as err:
                    print("Network request Error:", err)
                    log_error(error_type='RequestError')

            else:
                print(
                    'at {0} seconds out of {1}'.format(
                        (LOGGING_COUNT * MEASUREMENT_INTERVAL) % FREQUENCY_SECONDS,
                        FREQUENCY_SECONDS,
                    )
                )

        LOGGING_COUNT = LOGGING_COUNT + 1

    except KeyboardInterrupt:
        segment.clear()
        segment.write_display()
        log_error(error_type='KeyboardInterrupt')
        print_error_tables()
        sys.exit(0)

    except ssl.SSLError:
        # we had a network issue, try again later
        log_error(error_type='ssl.SSLError')
        segment.clear()
        segment.write_display()
        print_error_tables()

    # except:
    #     print("unhandled exception, skipping")
    #     log_error(error_type='Unhandled'))
    #     print_error_tables()

    finally:
        segment.clear()
        segment.write_display()
        print_error_tables()
