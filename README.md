# stats agent / server implementation

Simple scripts to send metrics from a linux host to kafka. Then consume them from a server implementation and store into postgres.

Terraform code to set up the environment (HCL2 / terraform 0.12). Either create a bucket for the remote state and run with no locks on the first go or remove the locks and remote state and use a local state.

## stats_agent.py

stats_agent requires an environment variable KAFKA_SERVER

## stats_server.py

stats_server requires environment variables POSTGRES_URI and KAFKA_SERVER

## Known issues

* no tests
* not enough error handling
* still using the main users and not the users with lower privileges

