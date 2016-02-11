#!/bin/bash

ansible-playbook ./prod/deploy.yml --private-key=./ssh_keys/128.199.253.141_prod_key -K -u deployer -i ./prod/hosts
