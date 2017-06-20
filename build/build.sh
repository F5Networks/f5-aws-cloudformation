#/bin/bash

# To populate cache files, run
# python image_finder.py

# Network Only (experimental)
python master_template.py -s network -a 1 -n 1 > ../experimental/reference/1nic/network-only/f5-network-only-1AZ-for-1nic-bigip.template
python master_template.py -s network -a 1 -n 2 > ../experimental/reference/2nic/network-only/f5-network-only-1AZ-for-2nic-bigip.template
python master_template.py -s network -a 1 -n 3 > ../experimental/reference/3nic/network-only/f5-network-only-1AZ-for-3nic-bigip.template
python master_template.py -s network -a 2 -n 1 > ../experimental/reference/1nic/network-only/f5-network-only-2AZ-for-1nic-bigip.template
python master_template.py -s network -a 2 -n 2 > ../experimental/reference/2nic/network-only/f5-network-only-2AZ-for-2nic-bigip.template
python master_template.py -s network -a 2 -n 3 > ../experimental/reference/3nic/network-only/f5-network-only-2AZ-for-3nic-bigip.template

# Security Groups Only (experimental)
python master_template.py -s security_groups -n 1 > ../experimental/reference/1nic/security-group-creation/f5-security-groups-for-1nic-bigip.template
python master_template.py -s security_groups -n 2 > ../experimental/reference/2nic/security-group-creation/f5-security-groups-for-2nic-bigip.template
python master_template.py -s security_groups -n 3 > ../experimental/reference/3nic/security-group-creation/f5-security-groups-for-3nic-bigip.template

# Infra - Everything But BIG-IPs (experimental)
python master_template.py -s infra -a 1 -n 1 > ../experimental/reference/1nic/infrastructure-only/f5-infra-only-1AZ-for-1nic-bigip.template
python master_template.py -s infra -a 1 -n 2 > ../experimental/reference/2nic/infrastructure-only/f5-infra-only-1AZ-for-2nic-bigip.template
python master_template.py -s infra -a 1 -n 3 > ../experimental/reference/3nic/infrastructure-only/f5-infra-only-1AZ-for-3nic-bigip.template
python master_template.py -s infra -a 2 -n 1 > ../experimental/reference/1nic/infrastructure-only/f5-infra-only-2AZ-for-1nic-bigip.template
python master_template.py -s infra -a 2 -n 2 > ../experimental/reference/2nic/infrastructure-only/f5-infra-only-2AZ-for-2nic-bigip.template
python master_template.py -s infra -a 2 -n 3 > ../experimental/reference/3nic/infrastructure-only/f5-infra-only-2AZ-for-3nic-bigip.template

# BIGIP Stacks (Standalone)
## Supported
python master_template.py -s existing -n 1 -l hourly > ../supported/standalone/1nic/f5-existing-stack-hourly-1nic-bigip.template
python master_template.py -s existing -n 2 -l hourly > ../supported/standalone/2nic/f5-existing-stack-hourly-2nic-bigip.template
python master_template.py -s existing -n 3 -l hourly > ../supported/standalone/3nic/f5-existing-stack-hourly-3nic-bigip.template
python master_template.py -s existing -n 1 -l byol > ../supported/standalone/1nic/f5-existing-stack-byol-1nic-bigip.template
python master_template.py -s existing -n 2 -l byol > ../supported/standalone/2nic/f5-existing-stack-byol-2nic-bigip.template
python master_template.py -s existing -n 3 -l byol > ../supported/standalone/3nic/f5-existing-stack-byol-3nic-bigip.template
python master_template.py -s existing -n 1 -l bigiq > ../supported/standalone/1nic/f5-existing-stack-bigiq-1nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq > ../supported/standalone/2nic/f5-existing-stack-bigiq-2nic-bigip.template
## Experimental
python master_template.py -s existing -n 3 -l bigiq > ../experimental/reference/3nic/bigiq/f5-existing-stack-bigiq-license-pool-3nic-bigip.template
python master_template.py -s existing -n 1 -l hourly -c waf > ../experimental/reference/1nic/waf/f5-existing-stack-hourly-1nic-bigip-w-waf.template
python master_template.py -s existing -n 1 -l byol -c waf > ../experimental/reference/1nic/waf/f5-existing-stack-byol-1nic-bigip-w-waf.template
python master_template.py -s existing -n 1 -l bigiq -c waf > ../experimental/reference/1nic/bigiq/f5-existing-stack-bigiq-license-pool-1nic-bigip-w-waf.template

## Experimental - learning/POC
python master_template.py -s full -n 1 -l hourly > ../experimental/learning-stacks/standalone/1nic/f5-full-stack-hourly-1nic-bigip.template
python master_template.py -s full -n 2 -l hourly > ../experimental/learning-stacks/standalone/2nic/f5-full-stack-hourly-2nic-bigip.template
python master_template.py -s full -n 3 -l hourly > ../experimental/learning-stacks/standalone/3nic/f5-full-stack-hourly-3nic-bigip.template
python master_template.py -s full -n 1 -l byol > ../experimental/learning-stacks/standalone/1nic/f5-full-stack-byol-1nic-bigip.template
python master_template.py -s full -n 2 -l byol > ../experimental/learning-stacks/standalone/2nic/f5-full-stack-byol-2nic-bigip.template
python master_template.py -s full -n 3 -l byol > ../experimental/learning-stacks/standalone/3nic/f5-full-stack-byol-3nic-bigip.template
python master_template.py -s full -n 1 -l bigiq > ../experimental/learning-stacks/reference/1nic/bigiq/f5-full-stack-bigiq-license-pool-1nic-bigip.template
python master_template.py -s full -n 2 -l bigiq > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-bigiq-license-pool-2nic-bigip.template
python master_template.py -s full -n 3 -l bigiq > ../experimental/learning-stacks/reference/3nic/bigiq/f5-full-stack-bigiq-license-pool-3nic-bigip.template
python master_template.py -s full -n 1 -l hourly -c waf > ../experimental/learning-stacks/reference/1nic/waf/f5-full-stack-hourly-1nic-bigip-w-waf.template
python master_template.py -s full -n 1 -l byol -c waf > ../experimental/learning-stacks/reference/1nic/waf/f5-full-stack-byol-1nic-bigip-w-waf.template
python master_template.py -s full -n 1 -l bigiq -c waf > ../experimental/learning-stacks/reference/1nic/bigiq/f5-full-stack-bigiq-license-pool-1nic-bigip-w-waf.template

# Clusters
## Supported
python master_template.py -s existing -n 2 -l hourly -H same-az > ../supported/cluster/2nic/same-az-ha/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H same-az > ../supported/cluster/2nic/same-az-ha/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq -H same-az > ../supported/cluster/2nic/same-az-ha/f5-existing-stack-same-az-cluster-bigiq-2nic-bigip.template 
python master_template.py -s existing -n 2 -l hourly -H across-az > ../supported/cluster/2nic/across-az-ha/f5-existing-stack-across-az-cluster-hourly-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H across-az > ../supported/cluster/2nic/across-az-ha/f5-existing-stack-across-az-cluster-byol-2nic-bigip.template

## Experimental
python master_template.py -s existing -n 2 -l hourly -c waf -H same-az > ../experimental/reference/2nic/waf/f5-existing-stack-same-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l byol -c waf -H same-az > ../experimental/reference/2nic/waf/f5-existing-stack-same-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l bigiq -c waf -H same-az > ../experimental/reference/2nic/bigiq/f5-existing-stack-same-az-cluster-bigiq-license-pool-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l hourly -c waf -H across-az > ../experimental/reference/2nic/waf/f5-existing-stack-across-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l byol -c waf -H across-az > ../experimental/reference/2nic/waf/f5-existing-stack-across-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l bigiq -H across-az > ../experimental/reference/2nic/bigiq/f5-existing-stack-across-az-cluster-bigiq-license-pool-2nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq -c waf -H across-az > ../experimental/reference/2nic/bigiq/f5-existing-stack-across-az-cluster-bigiq-license-pool-2nic-bigip-w-waf.template

## Experimental - learning/POC
python master_template.py -s full -n 2 -l hourly -H same-az > ../experimental/learning-stacks/cluster/2nic/f5-full-stack-same-az-cluster-hourly-2nic-bigip.template
python master_template.py -s full -n 2 -l hourly -c waf -H same-az > ../experimental/learning-stacks/reference/2nic/waf/f5-full-stack-same-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l byol -H same-az > ../experimental/learning-stacks/cluster/2nic/f5-full-stack-same-az-cluster-byol-2nic-bigip.template
python master_template.py -s full -n 2 -l byol -c waf -H same-az > ../experimental/learning-stacks/reference/2nic/waf/f5-full-stack-same-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l bigiq -H same-az > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-same-az-cluster-bigiq-license-pool-2nic-bigip.template
python master_template.py -s full -n 2 -l bigiq -c waf -H same-az > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-same-az-cluster-bigiq-license-pool-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l hourly -H across-az > ../experimental/learning-stacks/cluster/2nic/f5-full-stack-across-az-cluster-hourly-2nic-bigip.template
python master_template.py -s full -n 2 -l hourly -c waf -H across-az > ../experimental/learning-stacks/reference/2nic/waf/f5-full-stack-across-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l byol -H across-az > ../experimental/learning-stacks/cluster/2nic/f5-full-stack-across-az-cluster-byol-2nic-bigip.template
python master_template.py -s full -n 2 -l byol -c waf -H across-az > ../experimental/learning-stacks/reference/2nic/waf/f5-full-stack-across-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l bigiq -H across-az > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-across-az-cluster-bigiq-license-pool-2nic-bigip.template
python master_template.py -s full -n 2 -l bigiq -c waf -H across-az > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-across-az-cluster-bigiq-license-pool-2nic-bigip-w-waf.template