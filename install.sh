#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"
if ! command -v python3 | grep -q 'python3'; then
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
		cd "$1"
	else
		echo -e "\033[0;31m	$1 directory could not be found, no dependencies will be installed\033[0m"
		return
	fi
	if [ -f "requirements.txt" ]; then
		pip3 install -r requirements.txt --force-reinstall &> /dev/null
		retval=$?
		if [ "$retval" -eq 0 ]; then
    		echo -e "\033[0;36m	All requirements for $1 successfully installed\033[0m"
		else
			echo -e "\033[0;31m	Something went wrong\033[0m"
			echo "	install exit code: $retval"
		fi
		cd ..
	else
 		echo -e "\033[0;31m	Requirements file for $1 not found, no dependencies will be installed\033[0m"
		cd ..
		return
	fi
}

install_dependencies "Fahrplansystem"
install_dependencies "Flottensystem"
install_dependencies "Streckensystem"
install_dependencies "Ticketsystem"
