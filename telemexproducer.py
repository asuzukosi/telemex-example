from time import time, sleep
import logging
import subprocess
import json
import argparse
from kafka import KafkaProducer
from concurrent.futures import ThreadPoolExecutor, as_completed

bootstrap_servers = 'ec2-51-21-150-184.eu-north-1.compute.amazonaws.com:9092' 
topic_name = 'telemex'

producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

def convert_coordinates(lat_str, lon_str):
    def parse_coordinate(coord_str):
        # Remove the direction (N/S/E/W) and split into degrees and minutes
        direction = coord_str[-1]
        parts = coord_str[:-1].split('.')
        degrees = float(parts[0][:-2])
        minutes = float(parts[0][-2:] + '.' + parts[1])
        
        # Convert to decimal degrees
        decimal_degrees = degrees + (minutes / 60)
        
        # Adjust sign based on direction
        if direction in ['S', 'W']:
            decimal_degrees = -decimal_degrees
        
        return round(decimal_degrees, 5)

    lat = parse_coordinate(lat_str)
    lon = parse_coordinate(lon_str)
    return lat, lon

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
        logging.error(f"error converting string to json: {e}")
        return data
    

def run_terminal_command(command):
    """
    Runs a terminal command and returns its output and error.
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    logging.debug("running command: {}".format(command))
    stdout, stderr = process.communicate()
    return stdout, stderr

def print_returner(data):
    print(data)

def kafka_returner(data):
    message = str(json.dumps(data))
    producer.send(topic_name, message.encode('utf-8'))
    producer.flush()
    logging.debug("message sent to kafka for data {}".format(data))

class Telemex:
    def __init__(self, queries, returner):
        self.queries = queries
        self.returner = returner
    
    def execute_command(self, query):
        # TODO: add error handling
        command = f"autopi obd.query {query}"
        output, error = run_terminal_command(command)
        if error:
            logging.error(f"error while executing command {command} : {error}")
            raise Exception(error)
        return output
    
    def handle_query(self, query):
        try:
            result = self.execute_command(query)
        except Exception as e:
            logging.error(f"failed to execute query {query} due to exception {e}")
            return
        result = string_to_json(result)
        self.returner(result)
        
        
    def get_location(self):
        command = "autopi gnss.connection gnss_location"
        try:
            result = self.execute_command(command)
        except Exception as e:
            logging.error(f"failed to execute command {command} due to exception {e}")
        result = string_to_json(result)
        result = self.process_location(result)
        self.returner(result)
        
    def process_location(location_json):
        data = dict()
        data["type"] = location_json["type"]
        data["stamp"] = location_json["stamp"]
        data["unit"] = "lat,lon"
        lat, lon = convert_coordinates(location_json["lat"], location_json["lon"])
        data["value"] = str(lat) + "," + str(lon)
        return data
        

    def get_data(self):
        with ThreadPoolExecutor() as executor:
            _ = [executor.submit(self.handle_query, query) for query in self.queries]
            _ = executor.submit(self.get_location) # location is an independent request separate from obd queries

    def run(self, limit=None, delay=5):
        increment = True if limit is not None else False
        limit = limit if limit is not None else 1
        pos = 0
        while pos < limit:
            self.get_data()
            sleep(delay) 
            if increment:
                pos += 1
                
def get_queries(filepath):
    queries = set()
    with open(filepath, 'r') as f:
        for line in f.readlines():
            if line and line != '' and line !='\n' :
                queries.add(line.strip())
    return list(queries)

if __name__ == "__main__":
    logging.basicConfig(
                        level=logging.DEBUG, 
                        format="%(asctime)s - %(levelname)s - %(message)s", 
                        datefmt="%Y-%m-%d : %H:%M:%S")
    
    parser = argparse.ArgumentParser(description='Telemex Local Logger Script to send data to Kafka pipeline')
    # Add arguments
    parser.add_argument("-l", "--limit", type=int, required=True, help="Number of times to execute function")
    parser.add_argument("-p", "--q_path", type=str, nargs="*", default=None, help="Path to retreive queries from")
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
    
    if q_path and len(q_path) > 0 :
        queries = set()
        for path in q_path :
            p_queries = get_queries(path)
            queries.update(p_queries)
        queries = list(queries)
    else:
        queries = ['SPEED', 'RPM']
    print("the queris are : {0}".format(queries))
    telemex = Telemex(queries=queries, returner=kafka_returner)
    telemex.run(limit=limit, delay=delay)
