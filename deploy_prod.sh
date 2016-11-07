#!/bin/bash

ansible-playbook ./prod/deploy.yml --private-key=./ssh_keys/139.59.44.245_prod_key -K -u deployer -i ./prod/hosts
