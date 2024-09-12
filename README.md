Testing out ideas for telemex

sudo nano /etc/systemd/system/telemex.service

/usr/bin/python3  /home/pi/telemex-example/telemex-local.py

/home/ubuntu/telemex-example

/home/ubuntu/telemex-example/venv/bin/python3

python telemex-local.py --limit 10  --q_path "queries.txt" --delay 5

[Unit]
Description=Telemex Kafka Pipeline System
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/bin/python3  /home/pi/telemex-example/telemex-local.py --limit -1  --q_path "/home/pi/telemex-example/queries.txt" --delay 5
Restart=on-failure