from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Kafka Configuration (replace with your actual broker address)
bootstrap_servers = 'ec2-51-21-150-184.eu-north-1.compute.amazonaws.com:9092' 
topic_name = 'telemex'

# InfluxDB configuration
influxdb_url = 'http://51.21.150.184:8086'
influxdb_token= 'Ko56AxiFuG1yr5J15PvXRXAOdRd6FS10-elWV7orRGFw8a9xhgc3yrIVBaqchlZQODuTqs4JGvjE5AbaSIYCoQ=='
influxdb_org = 'telemex'
influxdb_bucket = 'telemextest1'

# Create Kafka consumer
consumer = KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers)

# Create InfluxDB client
client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Process messages from Kafka and write to InfluxDB
for message in consumer:
    data:str = message.value.decode('utf-8')
    data = data.replace("\"'", '"').replace("'\"", '"').replace("'", '"')
    data = json.loads(data)
    if "unit" not in data:
        data["unit"] = "unk"
    logging.info("extracted data {}".format(data))
    try:
        # Create InfluxDB Point
        point = Point(data['type']) \
            .tag("unit", data['unit']) \
            .field("value", data['value']) \
            .time(data['stamp'])

        # Write Point to InfluxDB
        write_api.write(bucket="telemextest-" + str(data["device"]).replace(" ", "").lower(), org=influxdb_org, record=point)
        logging.info(f"Wrote data point to InfluxDB: {point}")
    except Exception as e:
        logging.info(f"failed to save data {data} with exception {e}")

# Close the InfluxDB client when done
client.close()