#!/bin/bash

ansible-playbook ./prod/deploy.yml --private-key=./ssh_keys/128.199.208.174_prod_key -K -u deployer -i ./prod/hosts
