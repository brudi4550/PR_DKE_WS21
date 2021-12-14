#!/bin/bash
trap "exit" INT TERM
trap "kill 0" EXIT
if [ ! -d "venv" ]; then
	echo "venv directory not found, run install.sh first"
    exit 1
fi
source venv/bin/activate

run_server () {
    if [ -d "$1" ]; then
	    echo "$1 directory found"
        cd "$1"
    else
        echo "$1 directory not found, not starting server"
        return
    fi
    if [[ $(lsof -i -P -n | grep "$2" | grep -i "Python") ]]; then
        echo "Flask application $1 on port $2 is already running"
        cd ..
        return
    fi
    if [ -f ".flaskenv" ]; then
	    echo ".flaskenv file for $1 system found"
        flask run -p $2 &> /dev/null &
        echo "Running $1 on localhost:$2"
        cd ..
    else
        echo ".flaskenv file not found, not starting server"
        cd ..
        return
    fi
}

run_server "Fahrplansystem" 5000
run_server "Flottensystem" 5001
run_server "Streckensystem" 5002
wait
