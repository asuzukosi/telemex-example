Testing out ideas for telemex

# /etc/systemd/system/telemexproducer.service
[Unit]
Description=Telemex Kafka Data Producer Pipeline System
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/bin/python3  /home/pi/telemex-example/telemexproducer.py --limit -1  --q_path "/home/pi/telemex-example/queries/queries.txt" --delay 5
Restart=on-failure

# /etc/systemd/system/telemexconsumer.service
[Unit]
Description=Telemex Kafka Data Consumer Pipeline System
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/home/ubuntu/telemex-example/venv/bin/python3  /home/ubuntu/telemex-example/telemexconsumer.py
Restart=on-failure





location query structure

_stamp: '2024-09-12T15:12:21.579937'
_type: gnss_location
alt: 116.5
cog: 223.5
date_utc: '2024-09-12'
fix: 3D
hdop: 0.8
lat: 5229.1358N
lon: 00152.8854W
nsat_glonass: 4
nsat_gps: 9
sog_km: 0.0
sog_kn: 0.0
time_utc: '15:12:21'