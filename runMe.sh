#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );
sudo raspi-config nonint do_i2c 0;  # the program needs i2c, so enable it

cd $SCRIPT_DIR;
source virtualEnv/bin/activate;
python3 mydht22.py;
