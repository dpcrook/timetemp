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

LOGGING = True
LOGGING = False
COUNT = 0

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS = 300

# How long to wait (in seconds) to display F or C.
ALTERNATE_TEMP_SCALE_SECONDS = 5

# Approximately how often measurements are made (in seconds)
MEASUREMENT_INTERVAL = 2 * ALTERNATE_TEMP_SCALE_SECONDS

# How seldom to upload the sensor data, if LOGGING is on
COUNT_INTERVAL = FREQUENCY_SECONDS / MEASUREMENT_INTERVAL

# Create sensor instance with default I2C bus
bmp = BMP085.BMP085(mode=BMP085.BMP085_HIGHRES, address=0x77)

# Initialize a LED display
segment = SevenSegment(address=0x70)
#segment = SevenSegment(address=0x71)
print(segment)

# Read in Phant config
if LOGGING:
    json_keys_file2 = 'data.crookster.org.json'
    p2 = Phant(jsonPath=json_keys_file2)

    print(
        'Logging sensor measurements taken every {2} seconds to "{0}" every {1} seconds.'
    ).format(p2.title, FREQUENCY_SECONDS, MEASUREMENT_INTERVAL)
    print(p2)

print('Press Ctrl-C to quit.')

with open('weather_logging_config.json') as config_file:
    config = json.loads(config_file.read())

pprint(config)


def convert_json_string_to_hexadecimal_value(s):
    value = 0
    try:
        value = int(s, 16)
    except:
        pass
    return value


bmp_address = convert_json_string_to_hexadecimal_value(
    config["i2c_addresses"]["bmp085"])
led_display_address = convert_json_string_to_hexadecimal_value(
    config["i2c_addresses"]["i2c_led"])
print(bmp_address)
print(led_display_address)

raise SystemExit

while True:

    error_tables = {}

    try:

        # Attempt to get sensor readings.
        temp = bmp.read_temperature()
        pressure = bmp.read_pressure()
        altitude = bmp.read_altitude()

        temp_in_F = (temp * 9.0 / 5.0) + 32.0

        print("BMP Sensor")
        print("  Temp(°C): %.1f C" % temp)
        print("  Temp(°F): %.1f F" % temp_in_F)
        print("Pressure:    %.2f hPa" % (pressure / 100.0))
        print("Altitude:    %.2f m" % altitude)
        print("Press CTRL+C to exit")
        print("")

        for display_tmp_in_F in [False, True]:

            if display_tmp_in_F:

                if round(temp_in_F * 10.0) < 1000.0:
                    segment.set_digit(0, int(round(temp_in_F) / 10))  # Tens
                    segment.set_digit(1, int(round(temp_in_F) % 10))  # Ones
                    segment.set_digit(2, int(
                        int(round(temp_in_F * 10.0)) % 10))  # Tenth
                    segment.set_digit(3, 'F')
                    segment.set_colon(True)
                else:
                    segment.set_digit(0,
                                      int(round(temp_in_F) / 100))  # Hundreds
                    segment.set_digit(1, int(
                        round(temp_in_F - 100.0) / 10))  # Tens
                    segment.set_digit(2, int(round(temp_in_F) % 10))  # Ones
                    segment.set_digit(3, 'F')
                    segment.set_colon(False)

            else:
                # write degrees
                segment.set_digit(0, int(round(temp) / 10))  # Tens
                segment.set_digit(1, int(round(temp) % 10))  # Ones
                segment.set_digit(2,
                                  int(int(round(temp * 10.0)) % 10))  # Tenth
                segment.set_digit(3, 'C')
                segment.set_colon(True)

            segment.write_display()

            time.sleep(ALTERNATE_TEMP_SCALE_SECONDS)

        if LOGGING:

            ambient_temp_C = temp
            ambient_temp_F = temp_in_F
            ambient_pressure = pressure / 100.0

            fields = (ambient_pressure, ambient_temp_C, ambient_temp_F,
                      altitude)
            print(fields)

            if (COUNT % COUNT_INTERVAL) == 0:
                p2.log(altitude, ambient_pressure, ambient_temp_C,
                       ambient_temp_F)
                print('Wrote a row to {0}'.format(p2.title))
                print((p2.remaining_bytes, p2.cap))
            else:
                print('at {0} seconds out of {1}'.format(
                    (COUNT * MEASUREMENT_INTERVAL) % FREQUENCY_SECONDS,
                    FREQUENCY_SECONDS))

        COUNT = COUNT + 1

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
