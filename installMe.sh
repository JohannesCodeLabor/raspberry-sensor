#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );
sudo raspi-config nonint do_i2c 0;  # the program needs i2c, so enable it

echo "j" | sudo apt update;
echo "j" | sudo apt upgrade;
sudo apt install python3-dev python3-pip;
sudo apt-get install python3-smbus i2c-tools -y;

cd $SCRIPT_DIR;
python3 -m venv virtualEnv;  # create virtual environment to install libraries into
source virtualEnv/bin/activate;
python3 -m pip install adafruit-circuitpython-dht adafruit-circuitpython-ADXL34x