# name of custom code accelerationlogger
import logging

log = logging.getLogger(__name__)

def accelerationlogger(data):
    with open("/tmp/accelerationlogs.txt", "a") as f:
        f.write("{:)n". format (data))

# name of returner
# accelerationloggerreturner.accelerationlogger

# name of worker
# accelerationloggerworker