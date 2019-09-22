#!/usr/bin/env python3
# pylint: disable=C0301,C0111

"""
A tool for sending stats from an EC2 instance to Kafka.

Usage:
  ./stats_agent.py [a name identifying this host]

If no host id is supplied in argv 1, the hostname is used.
"""

import datetime
import json
import logging
import os
import sys
import socket
import time

import psutil
import kafka.errors
from kafka import KafkaProducer


__author__ = "Markus Koskinen"
__license__ = "GPLv2"

_LOG_FORMAT = "%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s"
_DEBUG = False
_INTERVAL_SECONDS = 10
_REQUIRED_ENV_VARS = ['KAFKA_SERVER']
_METRICS_VERSION = 1
_CONNECT_RETRY_SECONDS = 15

if _DEBUG:
    logging.basicConfig(level=logging.DEBUG, format=_LOG_FORMAT)
else:
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)


def syntax(execname):
    print("Syntax: %s [host-id]" % execname)
    sys.exit(1)


def get_stats():
    """ Gather the metrics from the host with psutil and return as dict. """
    cpu_usage_percent = psutil.cpu_percent()
    memory_usage_percent = psutil.virtual_memory()[2]
    swap_usage_percent = psutil.swap_memory()[3]

    return {
        'cpu_usage_percent': cpu_usage_percent,
        'memory_usage_percent': memory_usage_percent,
        'swap_usage_percent': swap_usage_percent,
        'utc_time': str(datetime.datetime.utcnow())
        }


def init_kafka_producer():
    """ Return a kafka producer. Wait for a connection to be available. """
    logging.info("Initializing kafka producer ...")
    producer = None

    while producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=os.environ['KAFKA_SERVER'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                security_protocol="SSL",
                ssl_cafile="ca.pem",
                ssl_certfile="service.cert",
                ssl_keyfile="service.key",
            )
        except kafka.errors.NoBrokersAvailable as kafka_error:
            logging.error("No brokers available, retrying in %d seconds. Kafka error: %s", _CONNECT_RETRY_SECONDS, kafka_error)
            time.sleep(_CONNECT_RETRY_SECONDS)

    return producer


def stats_loop(host_id):
    """ This loop calls functions gathering system metrics and sends them to kafka every _INTERVAL_SECONDS. """
    producer = init_kafka_producer()

    while True:
        # Gather the stats and add some metadata values to the dict
        stats = get_stats()
        stats['host_id'] = host_id
        stats['message_type'] = "metrics_v%d" % _METRICS_VERSION
        logging.debug("Stats dict: %s", stats)

        # Send the data to kafka
        logging.info("Sending metrics data to kafka: %s", stats)
        future = producer.send("stats_topic", key=bytearray(host_id, 'utf-8'), value=stats)

        try:
            record_metadata = future.get(timeout=10)
            logging.debug(record_metadata)
        except KafkaError as kafka_error:
            logging.error("Failed to send data to kafka: %s", kafka_error)

        # We're all done, sleep before a new iteration
        logging.debug("Sleeping for %d seconds", _INTERVAL_SECONDS)
        time.sleep(_INTERVAL_SECONDS)


def main(argv):
    """ Handle command line arguments and syntax, then start the loop. """
    host_id = socket.gethostname()

    if len(argv) == 2:
        host_id = argv[1]

    logging.info("Stats agent starting. Host id: '%s'.", host_id)
    stats_loop(host_id)
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (1, 2):
        syntax(sys.argv[0])

    for env_var in _REQUIRED_ENV_VARS:
        if not env_var in os.environ:
            logging.error("You are missing required environment variable '%s'. Exiting.", env_var)
            sys.exit(1)

    sys.exit(main(sys.argv))
