# stats agent / server implementation

Simple scripts to send metrics from a linux host to kafka. Then consume them from a server implementation and store into postgres.

Terraform code to set up the environment (HCL2 / terraform 0.12). Either create a bucket for the remote state and run with no locks on the first go or remove the locks and remote state and use a local state.

