#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#  - read indoor-located pressure/temperature sensor
#    - log sensor data to a phant server
#    - log external temperature data
from __future__ import print_function

import sys
import time
# import datetime
import json
from pprint import pprint
import ssl
import requests  # so can handle exceptions

import Adafruit_BMP.BMP085 as BMP085
from Adafruit_LED_Backpack.SevenSegment import SevenSegment
from phant import Phant
# https://github.com/jkoelker/python-nest/
import nest
# https://github.com/ZeevG/python-forecast.io
import forecastio

# Logging sensor readings to Phant
LOGGING = True
#LOGGING = False
LOGGING_COUNT = 0

# Use Dark Sky API for local weather - https://darksky.net/dev/docs
DARK_SKY_WEATHER_API = True
#DARK_SKY_WEATHER_API = False

# Use Nest API for another indoor temperature source
NEST_API = True
#NEST_API = False

# How long to wait (in seconds) between logging measurements.
FREQUENCY_SECONDS = 300L

# How long to wait (in seconds) to display F or C.
ALTERNATE_TEMP_SCALE_SECONDS = 5L

# Approximately how often measurements are made (in seconds)
MEASUREMENT_INTERVAL = 3 * ALTERNATE_TEMP_SCALE_SECONDS

# How seldom to upload the sensor log data, if LOGGING is on
COUNT_INTERVAL = FREQUENCY_SECONDS / MEASUREMENT_INTERVAL

# Additional characters for 7 segment display
RAW_DIGIT_VALUES = {
    'tickmark': 0x02,
    'outdoor_degrees': 0x6b,
    '°': 0x63,
}

# Read in config file
with open('weather_logging_config.json') as config_file:
    config = json.loads(config_file.read())
#pprint(config)


def convert_json_string_to_hexadecimal_value(s):
    value = 0
    # TODO: Add error and exception handling
    try:
        value = int(s, 16)
    except:
        pass
    return value


bmp_address = convert_json_string_to_hexadecimal_value(
    config["i2c_addresses"]["bmp085"])
led_display_address = convert_json_string_to_hexadecimal_value(
    config["i2c_addresses"]["i2c_led"])
#print(bmp_address)
#print(led_display_address)
secret_key = config["darksky"]["secret-key"]
lat = config["darksky"]["lat"]
lng = config["darksky"]["lng"]
#print(lat, lng)
nest_client_id = config['timetemp_nest']['client_id']
nest_client_secret = config['timetemp_nest']['client_secret']
nest_access_token_cache_file = 'nest.json'

# Create sensor instance with default I2C bus
bmp = BMP085.BMP085(mode=BMP085.BMP085_HIGHRES, address=bmp_address)

# Initialize a LED display
segment = SevenSegment(address=led_display_address)
print(segment)

# Read in Phant config
if LOGGING:
    json_keys_file2 = 'data.crookster.org.json'
    p2 = Phant(jsonPath=json_keys_file2)

    print(
        'Logging sensor measurements taken every {2} seconds to "{0}" every {1} seconds.'.
        format(p2.title, FREQUENCY_SECONDS, MEASUREMENT_INTERVAL))
    #print(p2)

# Initialize 'currently'
if DARK_SKY_WEATHER_API:
    forecast = forecastio.load_forecast(secret_key, lat, lng)
    if 'X-Forecast-API-Calls' in forecast.http_headers:
        print(forecast.http_headers['X-Forecast-API-Calls'], ' API calls')
    currently = forecast.currently()
    print(currently.summary)
    print(currently.time)
    print(currently.temperature)

# Initialize 'napi' and 'nest_temperature'
if NEST_API:
    napi = nest.Nest(
        client_id=nest_client_id,
        client_secret=nest_client_secret,
        access_token_cache_file=nest_access_token_cache_file)

    if napi.authorization_required:
        print('Authorization required.  Run "python ./nest_access.py"')
        raise SystemExit

    for structure in napi.structures:
        print('Structure %s' % structure.name)
        print('    Away: %s' % structure.away)
        print('    Devices:')

        for device in structure.thermostats:
            print('        Device: %s' % device.name)
            print('            Temp: %0.1f' % device.temperature)
            nest_temperature = device.temperature


def display_temperature_in_fahrenheit(led_display, temperature, where):
    segment = led_display
    if round(temperature * 10.0) < 1000.0:
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
    else:
        segment.set_digit(0, int(round(temperature) / 100))  # Hundreds
        segment.set_digit(1, int(round(temperature - 100.0) / 10))  # Tens
        segment.set_digit(2, int(round(temperature) % 10))  # Ones
        segment.set_digit(3, 'F')
        segment.set_colon(False)


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


while True:
    try:
        # Attempt to get sensor readings.
        temp = bmp.read_temperature()
        pressure = bmp.read_pressure()
        altitude = bmp.read_altitude()

        temp_in_F = (temp * 9.0 / 5.0) + 32.0

        print("BMP Sensor")
        print("  Temp(°C): %.1f°C" % temp)
        print("  Temp(°F): %.1f°F" % temp_in_F)
        print("  Pressure: %.1f hPa" % (pressure / 100.0))
        print("  Altitude: %.1f m" % altitude)
        print("Press CTRL+C to exit")
        #print("")

        for temp_where in ['outdoor', 'sensor', 'nest']:

            if temp_where == 'sensor':
                display_temperature_in_fahrenheit(segment, temp_in_F,
                                                  temp_where)
            elif temp_where == 'outdoor':
                if DARK_SKY_WEATHER_API:
                    outside_temperature = currently.temperature
                    display_temperature_in_fahrenheit(
                        segment, outside_temperature, temp_where)
                else:
                    display_temperature_in_fahrenheit(segment, temp_in_F,
                                                      'sensor')
            elif temp_where == 'nest':
                if NEST_API:
                    indoor_temperature = nest_temperature
                    display_temperature_in_fahrenheit(
                        segment, indoor_temperature, temp_where)
                else:
                    display_temperature_in_fahrenheit(segment, temp_in_F,
                                                      'sensor')
            segment.write_display()
            print_error_tables()
            time.sleep(ALTERNATE_TEMP_SCALE_SECONDS)

        if LOGGING:

            ambient_temp_C = temp
            ambient_temp_F = temp_in_F
            ambient_pressure = pressure / 100.0

            fields = (ambient_pressure, ambient_temp_C, ambient_temp_F,
                      altitude)
            print(fields)

            if (LOGGING_COUNT % COUNT_INTERVAL) == 0:
                try:
                    p2.log(altitude, ambient_pressure, ambient_temp_C,
                           ambient_temp_F)
                    print('Wrote a row to {0}'.format(p2.title))
                    print((p2.remaining_bytes, p2.cap))
                except ValueError as errv:
                    print('-E- Error logging to {}'.format(p2.title))
                    print('-W- Is phant server down?')
                    print('ValueError: {}'.format(str(errv)))
                    log_error(error_type='ValueError')
                # raise ConnectionError(e, request=request)
#requests.exceptions.ConnectionError: HTTPSConnectionPool(host='data.crookster.org', port=443): Max retries exceeded with url: /input/zb40GXNBOoCZwyvyGX6vS4NBago.json?tf=67.46&private_key=5qmAlvwLb3UXZM5M0DL5HdamVxn&alt=1470.383813622594&pres=848.65&tc=19.7 (Caused by NewConnectionError('<requests.packages.urllib3.connection.VerifiedHTTPSConnection object at 0xb63b7310>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution',))
                except requests.exceptions.ConnectionError as errec:
                    print("Error Connecting:", errec)
                    print('-W- Is network down?')
                    log_error(error_type='ConnectionError')
                except ConnectionError as errc:
                    print("Error Connecting:", errc)
                    print('-W- Is network down?')
                    log_error(error_type='ConnectionError')
                except requests.exceptions.Timeout as errt:
                    print("Timeout Error:", errt)
                    log_error(error_type='Timeout')

                except requests.exceptions.RequestException as err:
                    print("Network request Error:", err)
                    log_error(error_type='RequestError')

                # Use same interval as logging to request darksky API
                if DARK_SKY_WEATHER_API:
                    forecast = forecastio.load_forecast(secret_key, lat, lng)
                    currently = forecast.currently()
                    print("DarkSky API:")
                    if 'X-Forecast-API-Call' in forecast.http_headers:
                        print(forecast.http_headers['X-Forecast-API-Calls'])
                    print(currently.time)
                    print(currently.temperature)

                # Use same interval as logging to request Nest API
                if NEST_API:
                    try:
                        napi = nest.Nest(
                            client_id=nest_client_id,
                            client_secret=nest_client_secret,
                            access_token_cache_file=nest_access_token_cache_file
                        )

                        if napi.authorization_required:
                            print(
                                'Authorization required.  Run "python ./nest_access.py"'
                            )
                            raise SystemExit

                        for structure in napi.structures:
                            for device in structure.thermostats:
                                nest_temperature = device.temperature
                                print('Nest temperature: {0}'.format(
                                    nest_temperature))
                    except requests.exceptions.ConnectionError as errec:
                        print("NEST API: Error Connecting:", errec)
                        print('-W- Is network down?')
                        log_error(error_type='NEST API: ConnectionError')

            else:
                print('at {0} seconds out of {1}'.format(
                    (LOGGING_COUNT * MEASUREMENT_INTERVAL) % FREQUENCY_SECONDS,
                    FREQUENCY_SECONDS))

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
