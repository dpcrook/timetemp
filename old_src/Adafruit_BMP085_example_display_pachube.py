#!/usr/bin/python

from Adafruit_BMP085 import BMP085
import time

import os
import ssl

import sys
lib_path1 = os.path.join(os.path.pardir, 'Adafruit_LEDBackpack')
if os.path.isdir(lib_path1):
    sys.path.insert(0, lib_path1)

lib_path2 = os.path.join(os.path.expanduser('~pi'), 'python-eeml')
if os.path.isdir(lib_path2):
    sys.path.insert(0, lib_path2)

from Adafruit_7Segment import SevenSegment

import eeml
import eeml.datastream
import eeml.unit

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the BMP085 and use STANDARD mode (default value)
# bmp = BMP085(0x77, debug=True)
###bmp = BMP085(0x77)
bmp = BMP085(0x77, 2)

# To specify a different operating mode, uncomment one of the following:
# bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
# bmp = BMP085(0x77, 1)  # STANDARD Mode
# bmp = BMP085(0x77, 2)  # HIRES Mode
# bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode

# COSM variables. The API_KEY and FEED are specific to your COSM account and must be changed 
API_KEY = 'USE_YOUR_API_KEY'
FEED = 987654
 
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)


# Initialize a LED display
segment = SevenSegment(address=0x71)

#OUTPUT_IN_F = True
OUTPUT_IN_F = False

LOGGER = True
COUNT = 0

# Continually update the temp on a 4 char, 7-segment display
while(True):
    
    error_tables = {}

    try: 

        temp = bmp.readTemperature()
        pressure = bmp.readPressure()
        altitude = bmp.readAltitude()

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
                    # write degrees
                    segment.writeDigit(0, int(round(temp_in_F) / 10))     # Tens
                    segment.writeDigit(1, int(round(temp_in_F) % 10))          # Ones
                    segment.writeDigit(3, int(int(round(temp_in_F * 10.0)) % 10))   # Tenth
                    segment.writeDigit(4, 15)        # F
                    
                    segment.setColon(1)              # 
                else:
                    # write degrees
                    segment.writeDigit(0, int(round(temp_in_F) / 100))     # Hundreds
                    segment.writeDigit(1, int(round(temp_in_F - 100.0) / 10))      # Tens
                    segment.writeDigit(3, int(round(temp_in_F) % 10))      # Ones
                    segment.writeDigit(4, 15)        # F

                    segment.setColon(0)               

            else:
                # write degrees
                segment.writeDigit(0, int(round(temp) / 10))     # Tens
                segment.writeDigit(1, int(round(temp) % 10))          # Ones
                segment.writeDigit(3, int(int(round(temp * 10.0)) % 10))   # Tenth
                segment.writeDigit(4, 12)        # c

                segment.setColon(1)              # 

            time.sleep(5)


        # Wait fifteen (5 + 5 + 5 more) seconds between readings
        time.sleep(5)

        # every 20 * 15 seconds (300 seconds or 5 minutes) to upload the data to pachube
        if LOGGER:
            if (COUNT % 20) == 0:

                ambient_temp_C = temp
                ambient_temp_F = temp_in_F
                ambient_pressure = pressure / 100.0


                loc = eeml.Location(name = 'Great Room',
                                    lat = 40.45657,
                                    lon = -105.0294,
                                    ele = 1514.86,
                                    exposure = 'indoor',
                                    domain = 'physical',
                                    disposition = 'fixed'
                                    )
                                       

                # open up your cosm feed
                ####pac = eeml.Pachube(API_URL, API_KEY)
                pac = eeml.datastream.Cosm(API_URL, API_KEY)

                #send celsius data
                pac.update([eeml.Data(0, ambient_temp_C, unit=eeml.unit.Celsius(), 
                                      tags=['temperature'], id_name='ambient_temp_C')])

                #send fahrenheit data
                pac.update([eeml.Data(1, ambient_temp_F, unit=eeml.unit.Fahrenheit(), 
                                      tags=['temperature'], id_name='ambient_temp_F')])

                #send pressure data
                pac.update([eeml.Data(2, ambient_pressure, unit=eeml.unit.hPa(), 
                                      tags=['atmospheric_pressure'], id_name='ambient_pressure')])

                # send altitude data
                u = eeml.unit.Unit('meter', 'basicSI', 'm')
                pac.update([eeml.Data(3, altitude, unit = u, 
                                      tags=['altitude'], id_name='computed_altitude')])

                # send data to cosm
                print(pac.geteeml())
                print 'Count:', COUNT
                print
                pac.put()

        
        COUNT = COUNT + 1

    except KeyboardInterrupt:
        segment.disp.clear()
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
        print error_tables

    except:
        print "unhandled exception, skipping"
        if 'Unhandled' not in error_tables:
            error_tables['Unhandled'] = 1
        else:
            error_tables['Unhandled'] += 1

    finally:
        print error_tables
