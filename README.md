Testing out ideas for telemex

sudo nano /etc/systemd/system/telemex.service

/usr/bin/python3  /home/pi/telemex-example/telemex-local.py

python telemex-local.py --limit 10  --q_path "queries.txt" --delay 5