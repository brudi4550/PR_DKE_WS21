#!/bin/bash
if command -v python3 | grep -q 'python3'; then
	echo "Python 3 is installed"
else
	echo "Python 3 needs to be installed for this script to work"
	return
fi
if [ -d "venv" ]; then
	echo "Everything already installed, run run.sh to continue"
	return
fi
python3 -m venv venv
source venv/bin/activate
cd Fahrplansystem
pip3 install -r requirements.txt
cd ..
