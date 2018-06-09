# Install these scripts


## Build the required modules

```
# so we can build Python extensions
sudo apt-get update
sudo apt-get install -y git build-essential python3-dev python3-pip
git clone https://github.com/idcrook/timetemp.git
cd timetemp

# get these too
sudo apt-get install python3-smbus python3-pil
git submodule update --init --recursive

cd install/

cd Adafruit_Python_BMP/
sudo python3 setup.py install
cd ..

cd Adafruit_Python_LED_Backpack/
sudo python3 setup.py install
cd ..

cd python3-phant/
sudo python3 setup.py install
cd ..

# Optional
sudo pip3 install --upgrade pip

# API for Dark Sky
#     https://github.com/ZeevG/python-forecast.io for Dark Sky API
sudo pip3 install python-forecastio

# API for Nest
#     https://github.com/jkoelker/python-nest/ for Nest thermostat
sudo pip3 install python-nest
```

## Test run

Ensure the I2C bus is enabled

```
sudo raspi-config
# 5 Interfacing Options -> P5 I2C -> Enable
```

Requires the components to be hooked up to I2C bus. I2C addresses are specified in the scripts or in config files.

```bash
# time
sudo python ./my_7segment_clock.py

# requires json files with valid keys in them
#  - nest.json (cached)
#  - phant-config.json
#  - weather_logging_config.json
sudo python ./weather_logging_phant3.py || date
```


## How these were added to git repo

```
git submodule add -b master https://github.com/adafruit/Adafruit_Python_BMP.git
git add Adafruit_Python_BMP

git submodule add -b master https://github.com/adafruit/Adafruit_Python_LED_Backpack.git
git add Adafruit_Python_LED_Backpack

git submodule add -b master https://github.com/idcrook/python3-phant.git
git add python3-phant
```
