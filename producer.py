from kafka import KafkaProducer, KafkaConsumer
import time

# Kafka Configuration (replace with your actual broker address)
bootstrap_servers = 'ec2-51-21-150-51.eu-north-1.compute.amazonaws.com:9092' 
topic_name = 'kosi'

# Producer
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

for i in range(100):
    # Send a message (encode it as bytes if needed)
    message = 'Hello, Kafka! ' + str(i) 
    producer.send(topic_name, message.encode('utf-8'))
    producer.flush()  # Ensure all messages are sent
    print(f"message {i} sent")
    time.sleep(2)