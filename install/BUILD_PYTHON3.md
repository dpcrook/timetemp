Install these scripts
=====================

See the systemd configs in `../bin/` for details on the `systemd` installations' use of GNU `screen` and attaching to the running sessions

To monitor them running, access their `screen` terminals:

```
screen -D -R -S timesvc
screen -D -R -S tempsvc
```

Build the required modules
--------------------------

```
# so we can build Python extensions
sudo apt update
sudo apt install -y git build-essential python3-setuptools python3-dev python3-pip python3-venv python3-wheel

mkdir -p ~/projects/
cd ~/projects/
git clone https://github.com/idcrook/timetemp.git
cd timetemp

# populate submodules
git submodule update --init --recursive

# get these too
sudo apt install python3-smbus python3-pil

cd install/

# make and enter python3 virtual env
python3 -m venv env
source env/bin/activate

cd Adafruit_Python_BMP/
python setup.py install
cd ..

cd Adafruit_Python_LED_Backpack/
python setup.py install
cd ..

cd python3-phant/
python setup.py install
cd ..

# Optional
pip install --upgrade pip

# API for Dark Sky
#     https://github.com/ZeevG/python-forecast.io for Dark Sky API
pip install python-forecastio

# API for Open Weather Map
#     https://github.com/csparpa/pyowm
pip install pyowm
# 2020-05-17: to access OneCall API
pip install geojson # silent pre-req
pip install git+https://github.com/csparpa/pyowm.git@develop


# API for Nest
#     https://github.com/jkoelker/python-nest/ for Nest thermostat
pip install python-nest
```

Test run
--------

Ensure the I2C bus is enabled

```
sudo raspi-config
# 5 Interfacing Options -> P5 I2C -> Enable
```

Requires the components to be hooked up to I2C bus. I2C addresses are specified in the scripts or in config files.

```bash
# time
python ./my_7segment_clock.py

# requires json files with valid keys in them
#  - nest.json (cached)
#  - phant-config.json
#  - weather_logging_config.json
python ./weather_logging_phant3.py || date
```

How these were added to git repo
--------------------------------

```
git submodule add -b master https://github.com/adafruit/Adafruit_Python_BMP.git
git add Adafruit_Python_BMP

git submodule add -b master https://github.com/adafruit/Adafruit_Python_LED_Backpack.git
git add Adafruit_Python_LED_Backpack

git submodule add -b master https://github.com/idcrook/python3-phant.git
git add python3-phant
```
