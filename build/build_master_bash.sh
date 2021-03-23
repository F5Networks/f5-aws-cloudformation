#!/bin/bash
python master_bash_generator.py -n 1 && mv deploy_via_bash.sh ../supported/standalone/1nic/deploy_via_bash.sh
python master_bash_generator.py -n 2 && mv deploy_via_bash.sh ../supported/standalone/2nic/deploy_via_bash.sh
python master_bash_generator.py -n 3 && mv deploy_via_bash.sh ../supported/standalone/3nic/deploy_via_bash.sh

# For HA, if more than 2 bigips needed, run with -b flag followed by the number of bigips
python master_bash_generator.py -n 2 -H same-az && mv deploy_via_bash.sh ../supported/cluster/2nic/same-az-ha/deploy_via_bash.sh;
python master_bash_generator.py -n 2 -H across-az && mv deploy_via_bash.sh ../supported/cluster/2nic/across-az-ha/deploy_via_bash.sh