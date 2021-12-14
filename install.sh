#!/bin/bash
if command -v python3 | grep -q 'python3'; then
	echo "Python 3 is installed"
else
	echo "Python 3 needs to be installed for this script to work"
	exit 1
fi
if [ -d "venv" ]; then
	echo "venv directory already exists, deleting and creating new one"
	rm -rf ./venv
fi
python3 -m venv venv
source venv/bin/activate

install_dependencies () {
	echo "Trying to install dependecies for $1"
	if [ -d "$1" ]; then
		echo "$1 directory found"
		cd "$1"
	else
		echo "$1 directory could not be found, no dependencies will be installed"
		return
	fi
	if [ -f "requirements.txt" ]; then
 		echo "Requirements file for $1 found"
 		pip3 install -r requirements.txt &> /dev/null
		echo "All requirements for $1 successfully installed"
		cd ..
	else
 		echo "Requirements file for $1 not found, no dependencies will be installed"
		cd ..
		return
	fi
}

install_dependencies "Fahrplansystem"
install_dependencies "Flottensystem"
install_dependencies "Streckensystem"
