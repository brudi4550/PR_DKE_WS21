trap "kill 0" EXIT
source venv/bin/activate
cd Fahrplansystem
flask run -p 5001 >/dev/null 2>&1 & 
echo "Fahrplansystem running on 127.0.0.1:5001"
wait
