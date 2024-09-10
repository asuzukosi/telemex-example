import logging
from kafka import KafkaProducer

log = logging.getLogger(__name__)

bootstrap_servers = 'ec2-51-21-150-51.eu-north-1.compute.amazonaws.com:9092' 
topic_name = 'telemex'

producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

def run(result):
    """
    custom returner for sending data directly to kafka pipeline
    """
    message = str(result)
    producer.send(topic_name, message.encode('utf-8'))
    producer.flush()
    print("message sent to kafka")
