#!/usr/bin/python

# Google Spreadsheet BMP Sensor Data-logging Example

# Depends on the 'gspread' package being installed.  If you have pip installed
# execute:
#   sudo pip install gspread

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys
import time
import datetime
import json
import ssl

import Adafruit_BMP.BMP085 as BMP085
from Adafruit_LED_Backpack.SevenSegment import SevenSegment

from phant import Phant

LOGGING = True
COUNT = 0

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 300

# How long to wait (in seconds) to display F or C.
ALTERNATE_TEMP_SCALE_SECONDS      = 5

# Approximately how often measurements are made (in seconds)
MEASUREMENT_INTERVAL =  2 * ALTERNATE_TEMP_SCALE_SECONDS

# How seldom to upload the sensor data, if LOGGING is on
COUNT_INTERVAL =  FREQUENCY_SECONDS / MEASUREMENT_INTERVAL


# Create sensor instance with default I2C bus (On Raspberry Pi either 0 or
# 1 based on the revision, on Beaglebone Black default to 1).
bmp = BMP085.BMP085(mode=BMP085.BMP085_HIGHRES, address=0x77)

# Initialize a LED display
#segment = SevenSegment(address=0x70)
segment = SevenSegment(address=0x71)
print segment

# Read in Phant config
json_keys_file2 = 'data.crookster.org.json'
p2=Phant(jsonPath=json_keys_file2)


print 'Logging sensor measurements taken every {2} seconds to "{0}" every {1} seconds.'.format(p2.title, FREQUENCY_SECONDS, MEASUREMENT_INTERVAL)
print p2
print 'Press Ctrl-C to quit.'

while True:

    error_tables = {}

    try:

	# Attempt to get sensor readings.
	temp = bmp.read_temperature()
	pressure = bmp.read_pressure()
	altitude = bmp.read_altitude()

        temp_in_F = (temp * 9.0 / 5.0) + 32.0

        print "Temperature: %.2f C" % temp
        print "Temperature: %.2f F" % temp_in_F
        print "Pressure:    %.2f hPa" % (pressure / 100.0)
        print "Altitude:    %.2f m" % altitude
        print "Press CTRL+C to exit"
        print ""

        for display_tmp_in_F in [False, True]:

            if display_tmp_in_F:

                if round(temp_in_F * 10.0) < 1000.0:
                    segment.set_digit(0, int(round(temp_in_F) / 10))     # Tens
                    segment.set_digit(1, int(round(temp_in_F) % 10))          # Ones
                    segment.set_digit(2, int(int(round(temp_in_F * 10.0)) % 10))   # Tenth
                    segment.set_digit(3, 'F')
                    segment.set_colon(True)
                else:
                    segment.set_digit(0, int(round(temp_in_F) / 100))     # Hundreds
                    segment.set_digit(1, int(round(temp_in_F - 100.0) / 10))      # Tens
                    segment.set_digit(2, int(round(temp_in_F) % 10))      # Ones
                    segment.set_digit(3, 'F')
                    segment.set_colon(False)

            else:
                # write degrees
                segment.set_digit(0, int(round(temp) / 10))     # Tens
                segment.set_digit(1, int(round(temp) % 10))          # Ones
                segment.set_digit(2, int(int(round(temp * 10.0)) % 10))   # Tenth
                segment.set_digit(3, 'C')
                segment.set_colon(True)

            segment.write_display()

            time.sleep(ALTERNATE_TEMP_SCALE_SECONDS)

        if LOGGING:

            ambient_temp_C = temp
            ambient_temp_F = temp_in_F
            ambient_pressure = pressure / 100.0

            fields = (ambient_pressure, ambient_temp_C, ambient_temp_F, altitude)
            print fields

            if (COUNT % COUNT_INTERVAL) == 0:
                p2.log(altitude, ambient_pressure, ambient_temp_C, ambient_temp_F)
	        print 'Wrote a row to {0}'.format(p2.title)
                print(p2.remaining_bytes, p2.cap)
            else:
	        print 'at {0} seconds out of {1}'.format((COUNT * MEASUREMENT_INTERVAL) % FREQUENCY_SECONDS, FREQUENCY_SECONDS )


        COUNT = COUNT + 1

    except KeyboardInterrupt:
        segment.clear()
        segment.write_display()
        if 'KI' not in error_tables:
            error_tables['KI'] = 1
        else:
            error_tables['KI'] += 1
        print error_tables
        sys.exit(0)

    except ssl.SSLError:
        # we had a network issue, try again later
        if 'ssl.SSLError' not in error_tables:
            error_tables['ssl.SSLError'] = 1
        else:
            error_tables['ssl.SSLError'] += 1
        segment.clear()
        segment.write_display()
        print error_tables

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
        print error_tables
