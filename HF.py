import argparse
import os
import signal
import time
from datetime import datetime
from typing import List

from utilities.logger import log

"""
The aim of this program is to check for a new post of one or more threads, and to check the inbox for new PM's.
If new post or PM's are found then the program will create a push notification using PushBullet to all devices on your
PushBullet account. Can be run as a CronJob, Windows Task Scheduler, or equivalent. 
"""

go = True


def signal_handler(_, _1):
    print()
    log('Stopping...')
    global go
    go = False


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configure the settings")
    parser.add_argument('-r', '--requestsPerHour', action='store', type=int,
                        help="Sets the requests per hour maximum", default=120)
    parser.add_argument('-k', '--hackforumsKey', action='store', type=str,
                        help="Pass your Hackforums API key", default=None)
    parser.add_argument('-p', '--pushbulletKey', action='store', type=str,
                        help="Pass your Pushbullet API key", default=None)
    args = parser.parse_args()
    hf_key = os.getenv("HF_API_KEY")
    pb_key = os.getenv("PB_API_KEY")
    requests_per_hour = args.requestsPerHour

    from endpoints.base import BaseEndpoint
    from endpoints.private_message import PrivateMessageEndpoint
    from endpoints.thread import ThreadEndpoint

    endpoint_list = [ThreadEndpoint(), PrivateMessageEndpoint()]  # type: List[BaseEndpoint]
    request_delay_coefficient = (60 / (requests_per_hour / len(endpoint_list))) / len(endpoint_list)
    wait_time = len(endpoint_list) * request_delay_coefficient
    log(f"Delay time is {wait_time} minutes")
    log(f"Current rates are {requests_per_hour} requests per hour")
    BaseEndpoint.add_api(args.hackforumsKey, args.pushbulletKey)
    log("Running")
    last_run = datetime.now()
    while go:
        if (datetime.now() - last_run).total_seconds() / 60 >= wait_time:
            if BaseEndpoint.sleep_until:
                if datetime.now() < BaseEndpoint.sleep_until:
                    continue
            log("Updating forum data.")
            for e in endpoint_list:
                e.update()
            last_run = datetime.now()
        time.sleep(0.1)
