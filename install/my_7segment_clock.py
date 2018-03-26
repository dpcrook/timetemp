#!/usr/bin/python

import time
import datetime

from Adafruit_LED_Backpack import SevenSegment

import signal
import sys

# To run:
#     sudo python ./my_7segment_clock.py
# ===========================================================================
# Clock Example
# ===========================================================================
segment = SevenSegment.SevenSegment(address=0x70)
#segment = SevenSegment.SevenSegment(address=0x71)

# Initialize the display. Must be called once before using the display.
segment.begin()

#print "Press CTRL+Z to exit"
print "Press CTRL+C to exit"

io_error_count = 0

# Continually update the time on a 4 char, 7-segment display
while (True):

    try:
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second

        segment.clear()

        # Set hours
        if hour >= 10 or hour == 0:  # Tens
            segment.set_digit(0, int(hour / 10))
        else:
            segment.set_digit(0, ' ')

        segment.set_digit(1, hour % 10)  # Ones

        # Set minutes
        segment.set_digit(2, int(minute / 10))  # Tens
        segment.set_digit(3, minute % 10)  # Ones

        # Toggle colon
        segment.set_colon(second % 2)  # Toggle colon at 1Hz

        # Write the display buffer to the hardware.  This must be called to
        # update the actual display LEDs.
        segment.write_display()

        # Wait a quarter second (less than 1 second to prevent colon blinking getting$
        time.sleep(0.25)

    except KeyboardInterrupt:
        segment.clear()
        segment.write_display()
        sys.exit(0)

    # IOError: [Errno 121] Remote I/O error
    # - started happening frequently on stretch
    except IOError:
        io_error_count += 1
        print "Caught ", io_error_count, "IOErrors"
        time.sleep(2)
