# timetemp

Raspberry Pi powered time and temperature display with cloud logging.

**UPDATED** (05-Nov-2016): Added pointer to [Porting indoor weather (BMP085) logging project to SFE Phant](http://github.crookster.org/Moving-Indoor-Weather-Logging-To-Phant/) blog entry.

<img src="https://github.com/idcrook/timetemp/raw/master/images/Updated_Final.jpg" alt="Project picture" width="489" height="489" />

This project uses a Raspberry Pi, and some additional electronics (plus an Internet connection) to display time along with temperature. It uses a sensor that can measure temperature and air pressure.

<img src="https://github.com/idcrook/timetemp/raw/master/images/BreadboardWiring_fritzing.png" alt="Breadboard wiring" width="434" height="277" /> <img src="https://github.com/idcrook/timetemp/raw/master/images/Schematic_fritzing.png" alt="Schematic wiring" width="330" height="215" />

 - [Fritzing source file](https://github.com/idcrook/timetemp/raw/master/src/timetemp_sketch.fzz) ([Fritzing app](http://fritzing.org/home/))




## my scripts

I used Adafruit python libraries on this Pi way back in 2013 when I created this project. I updated in October, 2016 to use more recent library versions.

 - "Clock", displays current time (the Raspberry Pi uses NTP to stay synced)
   - [my_7segment_clock.py](https://github.com/idcrook/Adafruit_Python_LED_Backpack/blob/master/examples/my_7segment_clock.py)
 - "Temp", reads from BMP085 sensor, and displays to LED 7-segment display. Logs to a [stream at Sparkfun](https://data.sparkfun.com/streams/o8gab0Q996fNz2lW6gdr)
   - [logging_sparkfun.py](https://github.com/idcrook/Adafruit_Python_BMP/blob/master/examples/logging_sparkfun.py)
   - using phant requires a stream to be created. Uses a `.json` file generated during stream creation process to hold configuration settings

## Source Libraries

My local forked repositories

 - [Adafruit_Python_LED_Backpack](https://github.com/idcrook/Adafruit_Python_LED_Backpack)
 - [Adafruit_Python_BMP](https://github.com/idcrook/Adafruit_Python_BMP)
 - [python-phant](https://github.com/matze/python-phant)

Upstream

 - https://github.com/adafruit/Adafruit_Python_LED_Backpack
 - https://github.com/adafruit/Adafruit_Python_BMP
 - https://github.com/matze/python-phant

## Hardware References

 - 2 of [Adafruit 1.2" 4-Digit 7-Segment Display w/I2C Backpack](https://www.adafruit.com/product/1268), with custom designed 3D printed case
 - [BMP085 sensor breakout board](https://www.adafruit.com/product/391) (Discontinued)
 - Raspberry Pi Model B (1st gen.) plus PSU and Ethernet networking, running Raspbian
 - [I2C Level converter](https://www.adafruit.com/product/757)
 - Solderless Breadboard, wires, and [Pi Cobbler Breakout + Cable for Raspberry Pi](https://www.adafruit.com/products/914)

<img src="https://github.com/idcrook/timetemp/raw/master/images/AdafruitBoards.jpg" alt="Boards and cables from Adafruit" width="489" height="342" />

<img src="https://github.com/idcrook/timetemp/raw/master/images/7SegLEDpanels.JPG" alt="Back of Adafruit 1.2&quot; LED displays within custom case" width="489" height="652" />
