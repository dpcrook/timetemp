timetemp
========

Raspberry Pi-powered time and temperature in custom, 3D printed display. With cloud logging.


**IMPORTANT**: The Raspberry Pi code has been superceded by the follow-on project:

 -  [idcrook/timetemp3: Monitor and display time/temp with RasPi and log to cloud, 2020 refresh](https://github.com/idcrook/timetemp3)
 
 The [website with live charts](https://idcrook.github.io/timetemp/) is still found in this repo (in `gh-pages` branch).

---


-	This project originally launched in 2013.
-	It includes a sensor that measures indoor temperature and air pressure. It also connects to online APIs to get thermostat readings and outdoor temperatures.
-	It's still in use today.

**UPDATED** **(2020-May-17)**:

-	Switch API for outdoor temperature and conditions

**UPDATED** **(2018-Jun-09)**:

-	Cleanup and ported to Python 3
-	Created an updated library [idcrook/python3-phant](https://github.com/idcrook/python3-phant)
-	See [BUILD_PYTHON3.md](install/BUILD_PYTHON3.md)

More [updates](#updates) described below

<img src="https://github.com/idcrook/timetemp/raw/main/images/display_in_semi_shroud.jpg" alt="Project picture" width="740" />

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->

-	[Wiring Diagrams](#wiring-diagrams)
-	[Hardware References](#hardware-references)
-	[My scripts](#my-scripts)
	-	[Updates](#updates)
-	[Source Code](#source-code)
	-	[Repos on GitHub](#repos-on-github)
	-	[Upstream](#upstream)

<!-- markdown-toc end -->

Wiring Diagrams
---------------

<img src="https://github.com/idcrook/timetemp/raw/main/images/BreadboardWiring_fritzing.png" alt="Breadboard wiring" width="434" height="277" /> <img src="https://github.com/idcrook/timetemp/raw/main/images/Schematic_fritzing.png" alt="Schematic wiring" width="330" height="215" />

-	[Fritzing source file](https://github.com/idcrook/timetemp/raw/main/install/Archive/old_src/timetemp_sketch.fzz) ([Fritzing app](http://fritzing.org/home/)\)

<img src="https://github.com/idcrook/timetemp/raw/main/images/backside_of_display_panel.JPG" alt="Backside of displays" width="740" />

Hardware References
-------------------

-	2 of [Adafruit 1.2" 4-Digit 7-Segment Display w/I2C Backpack](https://www.adafruit.com/product/1268), with custom designed 3D printed case
-	Adafruit [BMP085 sensor breakout board](https://www.adafruit.com/product/391) (Discontinued)
-	Adafruit [I2C Level converter](https://www.adafruit.com/product/757)
-	Raspberry Pi Model 2 B
	-	PSU and Ethernet networking, running Raspbian
-	Seeedstudio [Breakout Kit for Raspberry Pi B w/40pin to 26pin Cable](https://www.seeedstudio.com/Breakout-Kit-for-Raspberry-Pi-B-w%26amp%3B-40pin-to-26pin-Cable-p-2080.html) (Discontinued)
-	Solderless Breadboard, wires, and a shelve
-	~~Raspberry Pi Model B (1st gen.)~~
-	~~[Pi Cobbler Breakout + Cable for Raspberry Pi](https://www.adafruit.com/products/914)~~

My scripts
----------

Way back in 2013, used Adafruit python libraries on this Pi when this project was created, on my first ever Raspberry Pi.

Updated in October 2016 to use more recent library versions and overhauled in 2018 to additionally use Nest API (thermostat temperature), Dark Sky API (local outdoor weather), and swap in some other hardware.

-	**"Time"**, displays current local time (relies on NTP to sync Internet time)
	-	[my_7segment_clock.py](https://github.com/idcrook/timetemp/blob/main/install/my_7segment_clock.py)
-	**"Temp"**, reads BMP085 sensor, displays on LED display. Logs to a stream [at my own phant server](https://data.crookster.org/streams/zb40GXNBOoCZwyvyGX6vS4NBago)
	-	[weather_logging_phant3.py](https://github.com/idcrook/timetemp/blob/main/install/weather_logging_phant3.py)
	-	`.json` files to hold configuration settings (like phant stream and API keys)

<img src="https://github.com/idcrook/timetemp/raw/main/images/AdafruitBoards.jpg" alt="Boards and cables from Adafruit" width="489" height="342" />

### Updates

**(2018-Jun-03)**:

-	Updated to work with latest (version `4.0.1`) python-nest module

**(2018-Apr-19)**:

-	Added Dark Sky and Nest API support for displaying outdoor and other indoor temperatures.

**(2018-Mar-25)**:

-	Added most recent code and explicit dependencies as git submodules. See [Build.md](install/Archive/BUILD.md)

**(2016-Nov-05)**:

-	Added pointer to [Porting indoor weather (BMP085) logging project to SFE Phant](http://github.crookster.org/Moving-Indoor-Weather-Logging-To-Phant/) blog entry.

Source Code
-----------

### Repos on GitHub

-	[idcrook/python3-phant](https://github.com/idcrook/python3-phant)
-	[idcrook/timetemp](https://github.com/idcrook/timetemp) (This project)

### Upstream

-	https://github.com/csparpa/pyowm/tree/develop
-	https://github.com/adafruit/Adafruit_Python_LED_Backpack
-	https://github.com/adafruit/Adafruit_Python_BMP
-	https://github.com/jkoelker/python-nest

-	https://github.com/matze/python-phant (Deprecated)

-	https://github.com/ZeevG/python-forecast.io (Deprecated - switch to OWM)
