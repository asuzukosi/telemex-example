from time import time, sleep
import logging
import subprocess
import json
import argparse
from kafka import KafkaProducer

log = logging.getLogger(__name__)

bootstrap_servers = 'ec2-51-21-150-184.eu-north-1.compute.amazonaws.com:9092' 
topic_name = 'telemex'

producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

def string_to_json(input_string:str):
    """
    Converts the provided string into a JSON object.
    """

    try:
        data = {}
        for line in input_string.strip().splitlines():
            key, value = line.split(': ', 1)
            key = key.lstrip('_')
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            data[key] = value
        return data
    except Exception as e:
        print(f"error converting string to json: {e}")
        return data
    

def run_terminal_command(command):
    """
    Runs a terminal command and returns its output and error.
    """

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    return stdout, stderr

def print_returner(data):
    print(data)

def kafka_returner(data):
    message = str(json.dumps(data))
    producer.send(topic_name, message.encode('utf-8'))
    producer.flush()
    print("message sent to kafka")

class Telemex:
    def __init__(self, queries, returner):
        self.queries = queries
        self.returner = returner
    
    def execute_command(self, query):
        command = f"autopi obd.query {query}"
        output, error = run_terminal_command(command)
        if error:
            print(f"error while executing command {command} : {error}")
        return output
    
    def get_data(self):
        for query in self.queries:
            result = self.execute_command(query)
            result = string_to_json(result)
            self.returner(result)
    
    def run(self, limit=None, delay=5):
        if limit is None:
            while True:
                self.get_data()
                sleep(delay)  
        else:
            for i in range(limit):
                self.get_data()
                sleep(delay)
                
def get_queries(filepath):
    queries = []
    with open(filepath, 'r') as f:
        for line in f.readlines():
            if line and line != '' and line !='\n' :
                queries.append(line.strip())
    return queries

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Telemex Local Logger Script to send data to Kafka pipeline')
    # Add arguments
    parser.add_argument("-l", "--limit", type=int, required=True, help="Number of times to execute function")
    parser.add_argument("-p", "--q_path", type=str, default=None, help="Path to retreive queries from")
    parser.add_argument("-d", "--delay", type=int, default=5, help="delay between calls in the run loop to request the queries")

    # Parse arguments
    args = parser.parse_args()

    # Access parsed arguments
    limit = args.limit
    q_path = args.q_path
    delay = args.delay
    
    if limit < 0 :
        # the function to run till infinity
        limit = None
    
    if q_path:
        queries = get_queries(q_path)
    else:
        queries = ['SPEED', 'RPM']

    telemex = Telemex(queries=queries, returner=kafka_returner)
    telemex.run(limit=limit, delay=delay)
