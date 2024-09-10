from time import time, sleep
import logging
import subprocess

# from kafka import KafkaProducer

log = logging.getLogger(__name__)

bootstrap_servers = 'ec2-51-21-150-51.eu-north-1.compute.amazonaws.com:9092' 
topic_name = 'telemex'

# producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

def string_to_json(input_string:str):
    """
    Converts the provided string into a JSON object.
    """

    try:
        data = {}
        for line in input_string.splitlines():
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
        print(f"Error converting string to JSON: {e}")
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
    pass

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
                

telemex = Telemex(queries=['SPEED', 'RPM'], returner=print_returner)

telemex.run(10)