#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#  - read indoor-located pressure/temperature sensor
#    - log sensor data to a phant server
#    - log external temperature data

import sys
import time
import datetime
import json
from pprint import pprint
import ssl

import Adafruit_BMP.BMP085 as BMP085
from Adafruit_LED_Backpack.SevenSegment import SevenSegment
from phant import Phant

# https://github.com/ZeevG/python-forecast.io
import forecastio

# Logging sensor readings to Phant
LOGGING = True
#LOGGING = False
LOGGING_COUNT = 0

# Use Dark Sky API for local weather - https://darksky.net/dev/docs
DARK_SKY_WEATHER_API = True
#DARK_SKY_WEATHER_API = False

# How long to wait (in seconds) between logging measurements.
FREQUENCY_SECONDS = 300L

# How long to wait (in seconds) to display F or C.
ALTERNATE_TEMP_SCALE_SECONDS = 5L

# Approximately how often measurements are made (in seconds)
MEASUREMENT_INTERVAL = 2 * ALTERNATE_TEMP_SCALE_SECONDS

# How seldom to upload the sensor log data, if LOGGING is on
COUNT_INTERVAL = FREQUENCY_SECONDS / MEASUREMENT_INTERVAL

# Additional characters for 7 segment display
RAW_DIGIT_VALUES = {
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
        'Logging sensor measurements taken every {2} seconds to "{0}" every {1} seconds.'
    ).format(p2.title, FREQUENCY_SECONDS, MEASUREMENT_INTERVAL)
    #print(p2)

# Initialize 'currently'
if DARK_SKY_WEATHER_API:
    forecast = forecastio.load_forecast(secret_key, lat, lng)
    print(forecast.http_headers['X-Forecast-API-Calls'], ' API calls')
    currently = forecast.currently()
    print(currently.summary)
    print(currently.time)
    print(currently.temperature)


def display_temperature_in_fahrenheit(led_display, temperature, outdoorQ):
    segment = led_display
    if round(temperature * 10.0) < 1000.0:
        segment.set_digit(0, int(round(temperature) / 10))  # Tens
        segment.set_digit(1, int(round(temperature) % 10))  # Ones
        if outdoorQ:
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['outdoor_degrees'])
            segment.set_digit(3, 'F')
        else:
            segment.set_digit_raw(2, RAW_DIGIT_VALUES['°'])
            segment.set_digit(3, 'F')

        segment.set_colon(False)
    else:
        segment.set_digit(0, int(round(temperature) / 100))  # Hundreds
        segment.set_digit(1, int(round(temperature - 100.0) / 10))  # Tens
        segment.set_digit(2, int(round(temperature) % 10))  # Ones
        segment.set_digit(3, 'F')
        segment.set_colon(False)


print('Press Ctrl-C to quit.')

while True:

    error_tables = {}

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
        print("")

        for display_indoor_temp_in_F in [False, True]:

            if display_indoor_temp_in_F:
                display_temperature_in_fahrenheit(segment, temp_in_F, False)
            else:
                if DARK_SKY_WEATHER_API:
                    outside_temperature = currently.temperature
                    display_temperature_in_fahrenheit(
                        segment, outside_temperature, True)
                else:
                    display_temperature_in_fahrenheit(segment, temp_in_F,
                                                      False)

            segment.write_display()

            time.sleep(ALTERNATE_TEMP_SCALE_SECONDS)

        if LOGGING:

            ambient_temp_C = temp
            ambient_temp_F = temp_in_F
            ambient_pressure = pressure / 100.0

            fields = (ambient_pressure, ambient_temp_C, ambient_temp_F,
                      altitude)
            print(fields)

            if (LOGGING_COUNT % COUNT_INTERVAL) == 0:
                p2.log(altitude, ambient_pressure, ambient_temp_C,
                       ambient_temp_F)
                print('Wrote a row to {0}'.format(p2.title))
                print((p2.remaining_bytes, p2.cap))

                # Use same interval as logging to request darksky API
                if DARK_SKY_WEATHER_API:
                    forecast = forecastio.load_forecast(secret_key, lat, lng)
                    currently = forecast.currently()
                    print("DarkSky API:")
                    print(forecast.http_headers['X-Forecast-API-Calls'])
                    print(currently.time)
                    print(currently.temperature)

            else:
                print('at {0} seconds out of {1}'.format(
                    (LOGGING_COUNT * MEASUREMENT_INTERVAL) % FREQUENCY_SECONDS,
                    FREQUENCY_SECONDS))

        LOGGING_COUNT = LOGGING_COUNT + 1

    except KeyboardInterrupt:
        segment.clear()
        segment.write_display()
        if 'KI' not in error_tables:
            error_tables['KI'] = 1
        else:
            error_tables['KI'] += 1
        print(error_tables)
        sys.exit(0)

    except ssl.SSLError:
        # we had a network issue, try again later
        if 'ssl.SSLError' not in error_tables:
            error_tables['ssl.SSLError'] = 1
        else:
            error_tables['ssl.SSLError'] += 1
        segment.clear()
        segment.write_display()
        print(error_tables)

#    except:
#        print "unhandled exception, skipping"
#        if 'Unhandled' not in error_tables:
#            error_tables['Unhandled'] = 1
#        else:
#            error_tables['Unhandled'] += 1
#        print error_tables

    finally:
        segment.clear()
        segment.write_display()
        print(error_tables)
