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

import psycopg2
from kafka import KafkaConsumer


__author__ = "Markus Koskinen"
__license__ = "GPLv2"

_LOG_FORMAT = "%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s"
_DEBUG = False

_INTERVAL_SECONDS = 10
_REQUIRED_ENV_VARS = ['KAFKA_SERVER', 'POSTGRES_URI']

if _DEBUG:
    logging.basicConfig(level=logging.DEBUG, format=_LOG_FORMAT)
else:
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)


def syntax(execname):
    print("Syntax: %s" % execname)
    sys.exit(1)


def init_kafka_consumer():
    logging.info("Creating Kafka consumer...")
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
    return consumer


def test_postgres_connection():
    logging.info("Connecting to Postgres...")

    try:
        db_conn = psycopg2.connect(os.environ['POSTGRES_URI'])
        cursor = db_conn.cursor()
        cursor.execute("SELECT version();")
        pg_version = cursor.fetchone()
        logging.info("Connected to %s.", pg_version)
    except (psycopg2.Error, Exception) as error:
        logging.fatal("Could not connect to Postgres: '%s'. Exiting.", error)
        sys.exit(1)
    finally:
        if db_conn:
            db_conn.close()


def stats_gathering_loop():
    """ A loop that consumes messages from kafka and puts them into postgres. """
    consumer = init_kafka_consumer()
    pg_conn = psycopg2.connect(os.environ['POSTGRES_URI'])

    for message in consumer:
        logging.info("Received message: %s", message.value)
        # We would make a data validity/correctness check here before storing to the db

        with pg_conn.cursor() as cursor:
            # Consider inserting batches of data vs one insert/message
            sql = """INSERT INTO stats_events VALUES (DEFAULT, %s, DEFAULT)"""
            cursor.execute(sql, (json.dumps(message.value),))

        pg_conn.commit()


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
