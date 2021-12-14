#!/bin/bash
if command -v python3 | grep -q 'python3'; then
	echo "Python 3 is installed"
else
	echo "Python 3 needs to be installed for this script to work"
	exit 1
fi
if [ -d "venv" ]; then
	echo "Everything already installed, run run.sh to continue"
	exit 1
fi
python3 -m venv venv
source venv/bin/activate
cd Fahrplansystem
pip3 install -r requirements.txt
cd ..
