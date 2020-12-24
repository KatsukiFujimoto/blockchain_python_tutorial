#!/bin/bash

set -e

pip install --upgrade pip setuptools
pip install -r requirements.txt
python opt/blockchain_server.py -p $PORT
