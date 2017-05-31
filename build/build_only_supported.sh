#!/bin/bash

# --- BIG-IP Supported Stacks ---
# Standalone

python master_template.py -s existing -n 1 -l hourly > ../supported/standalone/1nic/f5-existing-stack-hourly-1nic-bigip.template
python master_template.py -s existing -n 2 -l hourly > ../supported/standalone/2nic/f5-existing-stack-hourly-2nic-bigip.template

python master_template.py -s existing -n 1 -l byol > ../supported/standalone/1nic/f5-existing-stack-byol-1nic-bigip.template
python master_template.py -s existing -n 2 -l byol > ../supported/standalone/2nic/f5-existing-stack-byol-2nic-bigip.template

# Cluster/HA
# SAME-AZ
python master_template.py -s existing -n 2 -l hourly -H same-az > ../supported/cluster/2nic/same-az-ha/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H same-az > ../supported/cluster/2nic/same-az-ha/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template
# ACROSS-AZ
python master_template.py -s existing -n 2 -l hourly -H across-az > ../supported/cluster/2nic/across-az-ha/f5-existing-stack-across-az-cluster-hourly-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H across-az > ../supported/cluster/2nic/across-az-ha/f5-existing-stack-across-az-cluster-byol-2nic-bigip.template

# --- End BIG-IP Supported Stacks ---
