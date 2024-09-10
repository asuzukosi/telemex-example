from kafka import KafkaProducer, KafkaConsumer
from typing import List

# Kafka Configuration (replace with your actual broker address)
bootstrap_servers = 'ec2-51-21-150-184.eu-north-1.compute.amazonaws.com:9092' 
topic_name = 'telemex'

# Consumer
consumer  = KafkaConsumer(topic_name, 
                          bootstrap_servers=bootstrap_servers,
                          auto_offset_reset='earliest')

# Consume messages
for message in consumer:
    print(f"Received message: {message.value.decode('utf-8')}")