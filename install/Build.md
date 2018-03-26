# Install these scripts


## Build the required modules

```
git clone https://github.com/idcrook/timetemp.git
cd timetemp

# so we can build Python extensions
sudo apt-get update
sudo apt-get install build-essential python-dev

# get these too
sudo apt-get install python-smbus python-imaging
git submodule update --init --recursive

cd install/

cd Adafruit_Python_BMP/
sudo python setup.py install
cd ..

cd Adafruit_Python_LED_Backpack/
sudo python setup.py install
cd ..

cd python-phant/
sudo python setup.py install
cd ..

```

## Test run

Requires the components to be hooked up to I2C bus

```bash
# time
sudo python ./my_7segment_clock.py

# temp - requires a json file that has keys in it
sudo python ./logging_sparkfun.py || date
```


## How these were added to git repo

```
git submodule add -b master https://github.com/adafruit/Adafruit_Python_BMP.git
git add Adafruit_Python_BMP

git submodule add -b master https://github.com/adafruit/Adafruit_Python_LED_Backpack.git
git add Adafruit_Python_LED_Backpack

git submodule add -b master https://github.com/idcrook/python-phant.git
git add python-phant
```