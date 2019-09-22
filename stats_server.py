#!/usr/bin/env python3
# pylint: disable=C0301,C0111

"""
A tool for reading stats data from kafka and storing them in postgres.

Usage:
  ./stats_server.py
"""

import json
import logging
import os
import sys
import time

import psycopg2
import kafka.errors
from kafka import KafkaConsumer


__author__ = "Markus Koskinen"
__license__ = "GPLv2"

_LOG_FORMAT = "%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s"
_DEBUG = False

_CONNECT_RETRY_SECONDS = 15
_REQUIRED_ENV_VARS = ['KAFKA_SERVER', 'POSTGRES_URI']

if _DEBUG:
    logging.basicConfig(level=logging.DEBUG, format=_LOG_FORMAT)
else:
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)


def syntax(execname):
    print("Syntax: %s" % execname)
    sys.exit(1)


def init_kafka_consumer():
    """ Return a kafka consumer. Wait for a connection to be available. """
    logging.info("Initializing kafka consumer ...")
    consumer = None

    while consumer is None:
        try:
            consumer = KafkaConsumer(
                "stats_topic",
                client_id="stats-client-1",
                group_id="stats-group",
                auto_offset_reset="earliest",
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                bootstrap_servers=os.environ['KAFKA_SERVER'],
                enable_auto_commit=True,
                security_protocol="SSL",
                ssl_cafile="ca.pem",
                ssl_certfile="service.cert",
                ssl_keyfile="service.key",
            )
        except kafka.errors.NoBrokersAvailable as kafka_error:
            logging.error("No brokers available, retrying in %d seconds. Kafka error: %s", _CONNECT_RETRY_SECONDS, kafka_error)
            time.sleep(_CONNECT_RETRY_SECONDS)

    return consumer


def test_postgres_connection():
    """ Initialize a postgres connection. """
    logging.info("Testing Postgres connection ...")

    db_conn = None
    while db_conn is None:
        try:
            db_conn = psycopg2.connect(os.environ['POSTGRES_URI'])
            cursor = db_conn.cursor()
            cursor.execute("SELECT version();")
            pg_version = cursor.fetchone()
            logging.info("Connected to %s.", pg_version)
        except psycopg2.Error as pg_error:
            logging.error("Cannot connect to Postgres: '%s'. Retrying in %d seconds.", pg_error, _CONNECT_RETRY_SECONDS)
            time.sleep(_CONNECT_RETRY_SECONDS)
        finally:
            if db_conn:
                db_conn.close()


def stats_gathering_loop():
    """ A loop that consumes messages from kafka and puts them into postgres. """
    test_postgres_connection()
    consumer = init_kafka_consumer()

    with psycopg2.connect(os.environ['POSTGRES_URI']) as pg_conn:
        for message in consumer:
            logging.info("Received message: %s", message.value)
            # We would make a data validity/correctness check here before storing to the db

            with pg_conn.cursor() as cursor:
                # Consider inserting batches of data vs one insert/message
                sql = """INSERT INTO stats_events VALUES (DEFAULT, %s, DEFAULT)"""
                cursor.execute(sql, (json.dumps(message.value),))


def main():
    """ Handle command line arguments and syntax, then start the loop. """
    logging.info("Statistics gathering server starting.")

    stats_gathering_loop()
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (1, 2):
        syntax(sys.argv[0])

    for env_var in _REQUIRED_ENV_VARS:
        if not env_var in os.environ:
            logging.error("You are missing required environment variable '%s'. Exiting.", env_var)
            sys.exit(1)

    sys.exit(main())
