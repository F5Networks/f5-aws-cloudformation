#!/bin/bash

python master_bash_generator.py -n 1 && mv deploy_via_bash.sh ../supported/standalone/1nic/deploy_via_bash.sh
python master_bash_generator.py -n 2 && mv deploy_via_bash.sh ../supported/standalone/2nic/deploy_via_bash.sh
python master_bash_generator.py -n 2 -H same-az && mv deploy_via_bash.sh ../supported/cluster/2nic/same-az/deploy_via_bash.sh
python master_bash_generator.py -n 2 -H accross-az && mv deploy_via_bash.sh ../supported/cluster/2nic/accross-az/deplpy_via_bash.sh 

