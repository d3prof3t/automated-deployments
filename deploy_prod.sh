#!/bin/bash

ansible-playbook ./prod/deploy.yml --private-key=./ssh_keys/128.199.168.57_prod_key -K -u deployer -i ./prod/hosts
