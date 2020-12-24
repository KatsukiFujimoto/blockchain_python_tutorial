#!/bin/bash

set -e

pip install --upgrade pip setuptools
pip install -r requirements.txt
python opt/wallet_server.py -p 8080 -g http://172.16.238.1:5001
