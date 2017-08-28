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
python master_template.py -s existing -n 3 -l bigiq > ../supported/standalone/3nic/f5-existing-stack-bigiq-3nic-bigip.template

## Experimental
python master_template.py -s existing -n 1 -l hourly -c waf > ../experimental/reference/1nic/waf/f5-existing-stack-hourly-1nic-bigip-w-waf.template
python master_template.py -s existing -n 1 -l byol -c waf > ../experimental/reference/1nic/waf/f5-existing-stack-byol-1nic-bigip-w-waf.template
python master_template.py -s existing -n 1 -l bigiq -c waf > ../experimental/reference/1nic/bigiq/f5-existing-stack-bigiq-1nic-bigip-w-waf.template

## Experimental - learning/POC
python master_template.py -s full -n 1 -l hourly > ../experimental/learning-stacks/standalone/1nic/f5-full-stack-hourly-1nic-bigip.template
python master_template.py -s full -n 2 -l hourly > ../experimental/learning-stacks/standalone/2nic/f5-full-stack-hourly-2nic-bigip.template
python master_template.py -s full -n 3 -l hourly > ../experimental/learning-stacks/standalone/3nic/f5-full-stack-hourly-3nic-bigip.template
python master_template.py -s full -n 1 -l byol > ../experimental/learning-stacks/standalone/1nic/f5-full-stack-byol-1nic-bigip.template
python master_template.py -s full -n 2 -l byol > ../experimental/learning-stacks/standalone/2nic/f5-full-stack-byol-2nic-bigip.template
python master_template.py -s full -n 3 -l byol > ../experimental/learning-stacks/standalone/3nic/f5-full-stack-byol-3nic-bigip.template
python master_template.py -s full -n 1 -l bigiq > ../experimental/learning-stacks/reference/1nic/bigiq/f5-full-stack-bigiq-1nic-bigip.template
python master_template.py -s full -n 2 -l bigiq > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-bigiq-2nic-bigip.template
python master_template.py -s full -n 3 -l bigiq > ../experimental/learning-stacks/reference/3nic/bigiq/f5-full-stack-bigiq-3nic-bigip.template
python master_template.py -s full -n 1 -l hourly -c waf > ../experimental/learning-stacks/reference/1nic/waf/f5-full-stack-hourly-1nic-bigip-w-waf.template
python master_template.py -s full -n 1 -l byol -c waf > ../experimental/learning-stacks/reference/1nic/waf/f5-full-stack-byol-1nic-bigip-w-waf.template
python master_template.py -s full -n 1 -l bigiq -c waf > ../experimental/learning-stacks/reference/1nic/bigiq/f5-full-stack-bigiq-1nic-bigip-w-waf.template

# Clusters
## Supported
python master_template.py -s existing -n 2 -l hourly -H same-az > ../supported/cluster/2nic/same-az-ha/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H same-az > ../supported/cluster/2nic/same-az-ha/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq -H same-az > ../supported/cluster/2nic/same-az-ha/f5-existing-stack-same-az-cluster-bigiq-2nic-bigip.template 
python master_template.py -s existing -n 2 -l hourly -H across-az > ../supported/cluster/2nic/across-az-ha/f5-existing-stack-across-az-cluster-hourly-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H across-az > ../supported/cluster/2nic/across-az-ha/f5-existing-stack-across-az-cluster-byol-2nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq -H across-az > ../supported/cluster/2nic/across-az-ha/f5-existing-stack-across-az-cluster-bigiq-2nic-bigip.template

## Marketplace
python master_template.py -s existing -n 2 -l hourly -H across-az -M Good25Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Good25Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Good200Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Good200Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Good1000Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Good1000Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Good5000Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Good5000Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Better25Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Better25Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Better200Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Better200Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Better1000Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Better1000Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Better5000Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Better5000Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Best25Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Best25Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Best200Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Best200Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Best1000Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Best1000Mbps-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -M Best5000Mbps > ../supported/cluster/2nic/across-az-ha/marketplace/f5-existing-stack-across-az-cluster-Best5000Mbps-2nic-bigip.template

## Experimental
python master_template.py -s existing -n 2 -l hourly -c waf -H same-az > ../experimental/reference/2nic/waf/f5-existing-stack-same-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l byol -c waf -H same-az > ../experimental/reference/2nic/waf/f5-existing-stack-same-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l bigiq -c waf -H same-az > ../experimental/reference/2nic/bigiq/f5-existing-stack-same-az-cluster-bigiq-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l hourly -c waf -H across-az > ../experimental/reference/2nic/waf/f5-existing-stack-across-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l byol -c waf -H across-az > ../experimental/reference/2nic/waf/f5-existing-stack-across-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l bigiq -c waf -H across-az > ../experimental/reference/2nic/bigiq/f5-existing-stack-across-az-cluster-bigiq-2nic-bigip-w-waf.template

## Experimental - learning/POC
python master_template.py -s full -n 2 -l hourly -H same-az > ../experimental/learning-stacks/cluster/2nic/f5-full-stack-same-az-cluster-hourly-2nic-bigip.template
python master_template.py -s full -n 2 -l hourly -c waf -H same-az > ../experimental/learning-stacks/reference/2nic/waf/f5-full-stack-same-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l byol -H same-az > ../experimental/learning-stacks/cluster/2nic/f5-full-stack-same-az-cluster-byol-2nic-bigip.template
python master_template.py -s full -n 2 -l byol -c waf -H same-az > ../experimental/learning-stacks/reference/2nic/waf/f5-full-stack-same-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l bigiq -H same-az > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-same-az-cluster-bigiq-2nic-bigip.template
python master_template.py -s full -n 2 -l bigiq -c waf -H same-az > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-same-az-cluster-bigiq-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l hourly -H across-az > ../experimental/learning-stacks/cluster/2nic/f5-full-stack-across-az-cluster-hourly-2nic-bigip.template
python master_template.py -s full -n 2 -l hourly -c waf -H across-az > ../experimental/learning-stacks/reference/2nic/waf/f5-full-stack-across-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l byol -H across-az > ../experimental/learning-stacks/cluster/2nic/f5-full-stack-across-az-cluster-byol-2nic-bigip.template
python master_template.py -s full -n 2 -l byol -c waf -H across-az > ../experimental/learning-stacks/reference/2nic/waf/f5-full-stack-across-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s full -n 2 -l bigiq -H across-az > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-across-az-cluster-bigiq-2nic-bigip.template
python master_template.py -s full -n 2 -l bigiq -c waf -H across-az > ../experimental/learning-stacks/reference/2nic/bigiq/f5-full-stack-across-az-cluster-bigiq-2nic-bigip-w-waf.template

## Build sh512 checksum file for supported templates
python checksum-sha512.py