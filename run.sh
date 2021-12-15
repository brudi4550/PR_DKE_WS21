#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"
trap "exit" INT TERM
trap "kill 0" EXIT
if [ ! -d "venv" ]; then
	echo "Virtual environment  not found, run install.sh first"
    exit 1
fi
source venv/bin/activate

QUIET=false
check_connection () {
    CONNECTION_SUCCESSFUL=false
    response="$(curl --write-out '%{http_code}\n' --silent -o /dev/null http://127.0.0.1:$1 -L)"
    if [ "$response" -eq 200 ]; then
            CONNECTION_SUCCESSFUL=true
    fi
}

run_server () {
    echo "Trying to run $1 on port $2"
    if [ -d "$1" ]; then
	    echo "  $1 directory found"
        cd "$1"
    else
        echo -e "\033[0;31m  $1 directory not found, not starting server\033[0m"
        return
    fi
    if [[ $(lsof -i -P -n | grep "$2" | grep -i "Python") ]]; then
        echo -e "\033[0;31m  Flask application $1 on port $2 is already running\033[0m"
        cd ..
        return
    fi
    if [ -f ".flaskenv" ]; then
	    echo "  .flaskenv file for $1 system found"
        if [ "$QUIET" = false ]; then
            flask run -p $2 > /dev/null &    
        else
            flask run -p $2 &> /dev/null &
            end="$((SECONDS+5))"
            while [ $SECONDS -lt $end ]; do
                check_connection $2
                if [ "$CONNECTION_SUCCESSFUL" = true ]; then
                    break
                fi
                sleep 0.1
            done
            if [ "$CONNECTION_SUCCESSFUL" = true ]; then
                echo -e "\033[0;36m  Running $1 on http://127.0.0.1:$2/ \033[0m"
            else
                echo -e "\033[0;31m  Something went wrong, not starting server\033[0m"
            fi
        fi
        cd ..
    else
        echo -e "\033[0;31m  .flaskenv file not found, not starting server\033[0m"
        cd ..
        return
    fi
}

run_all () {
    RUN_FA=true
    RUN_FL=true
    RUN_ST=true
    RUN_TI=true
}

check_arguments () {
    for argument in "$@";
    do
        if [ "$argument" = "fa" ]; then
            RUN_FA=true
        fi
        if [ "$argument" = "fl" ]; then
            RUN_FL=true
        fi
        if [ "$argument" = "st" ]; then
            RUN_ST=true
        fi
        if [ "$argument" = "ti" ]; then
            RUN_TI=true
        fi
        if [ "$argument" = "q" ]; then
            QUIET=true
            if [ "$#" -eq 1 ]; then
                run_all
            fi
        fi
    done
}

if [ $# -eq 0 ]; then
        run_all
else
    check_arguments "$@"
fi

if [ "$RUN_FA" = true ]; then
    run_server "Fahrplansystem" 5000
fi
if [ "$RUN_FL" = true ]; then
    run_server "Flottensystem" 5001
fi
if [ "$RUN_ST" = true ]; then
    run_server "Streckensystem" 5002
fi
if [ "$RUN_TI" = true ]; then
    run_server "Ticketsystem" 5003
fi
wait
