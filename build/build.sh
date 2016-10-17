#/bin/bash

BUILD_DIR_1NIC="../experimental/1NIC_Deployments"
BUILD_DIR_2NIC="../experimental/2NIC_Deployments"
BUILD_DIR_3NIC="../experimental/3NIC_Deployments"
HOURLY_DIR="/hourly"
BYOL_DIR="/byol"
POOL_DIR="/pool"

# To populate cache files, run
# python image_finder.py

# Network Only
python master_template.py -s network -a 1 -n 1 > ${BUILD_DIR_1NIC}/network-only-1AZ-for-1nic-bigip.template
python master_template.py -s network -a 1 -n 2 > ${BUILD_DIR_2NIC}/network-only-1AZ-for-2nic-bigip.template
python master_template.py -s network -a 1 -n 3 > ${BUILD_DIR_3NIC}/network-only-1AZ-for-3nic-bigip.template

python master_template.py -s network -a 2 -n 1 > ${BUILD_DIR_1NIC}/network-only-2AZ-for-1nic-bigip.template
python master_template.py -s network -a 2 -n 2 > ${BUILD_DIR_2NIC}/network-only-2AZ-for-2nic-bigip.template
python master_template.py -s network -a 2 -n 3 > ${BUILD_DIR_3NIC}/network-only-2AZ-for-3nic-bigip.template

# Security Groups Only
python master_template.py -s security_groups -n 1 > ${BUILD_DIR_1NIC}/security-groups-for-1nic-bigip.template
python master_template.py -s security_groups -n 2 > ${BUILD_DIR_2NIC}/security-groups-for-2nic-bigip.template
python master_template.py -s security_groups -n 3 > ${BUILD_DIR_3NIC}/security-groups-for-3nic-bigip.template


# Infra (Everything But BIG-IPs)
python master_template.py -s infra -a 1 -n 1 > ${BUILD_DIR_1NIC}/infra-only-1AZ-for-1nic-bigip.template
python master_template.py -s infra -a 1 -n 2 > ${BUILD_DIR_2NIC}/infra-only-1AZ-for-2nic-bigip.template
python master_template.py -s infra -a 1 -n 3 > ${BUILD_DIR_3NIC}/infra-only-1AZ-for-3nic-bigip.template

python master_template.py -s infra -a 2 -n 1 > ${BUILD_DIR_1NIC}/infra-only-2AZ-for-1nic-bigip.template
python master_template.py -s infra -a 2 -n 2 > ${BUILD_DIR_2NIC}/infra-only-2AZ-for-2nic-bigip.template
python master_template.py -s infra -a 2 -n 3 > ${BUILD_DIR_3NIC}/infra-only-2AZ-for-3nic-bigip.template



# BIGIP Stacks
python master_template.py -s full -n 1 -l hourly > ${BUILD_DIR_1NIC}${HOURLY_DIR}/full-stack-hourly-1nic-bigip.template
python master_template.py -s full -n 2 -l hourly > ${BUILD_DIR_2NIC}${HOURLY_DIR}/full-stack-hourly-2nic-bigip.template
python master_template.py -s full -n 3 -l hourly > ${BUILD_DIR_3NIC}${HOURLY_DIR}/full-stack-hourly-3nic-bigip.template

python master_template.py -s existing -n 1 -l hourly > ${BUILD_DIR_1NIC}${HOURLY_DIR}/existing-stack-hourly-1nic-bigip.template
python master_template.py -s existing -n 2 -l hourly > ${BUILD_DIR_2NIC}${HOURLY_DIR}/existing-stack-hourly-2nic-bigip.template
python master_template.py -s existing -n 3 -l hourly > ${BUILD_DIR_3NIC}${HOURLY_DIR}/existing-stack-hourly-3nic-bigip.template

python master_template.py -s full -n 1 -l byol > ${BUILD_DIR_1NIC}${BYOL_DIR}/full-stack-byol-1nic-bigip.template
python master_template.py -s full -n 2 -l byol > ${BUILD_DIR_2NIC}${BYOL_DIR}/full-stack-byol-2nic-bigip.template
python master_template.py -s full -n 3 -l byol > ${BUILD_DIR_3NIC}${BYOL_DIR}/full-stack-byol-3nic-bigip.template

python master_template.py -s existing -n 1 -l byol > ${BUILD_DIR_1NIC}${BYOL_DIR}/existing-stack-byol-1nic-bigip.template
python master_template.py -s existing -n 2 -l byol > ${BUILD_DIR_2NIC}${BYOL_DIR}/existing-stack-byol-2nic-bigip.template
python master_template.py -s existing -n 3 -l byol > ${BUILD_DIR_3NIC}${BYOL_DIR}/existing-stack-byol-3nic-bigip.template

python master_template.py -s full -n 1 -l bigiq > ${BUILD_DIR_1NIC}${POOL_DIR}/full-stack-bigiq-license-pool-1nic-bigip.template
python master_template.py -s full -n 2 -l bigiq > ${BUILD_DIR_2NIC}${POOL_DIR}/full-stack-bigiq-license-pool-2nic-bigip.template
python master_template.py -s full -n 3 -l bigiq > ${BUILD_DIR_3NIC}${POOL_DIR}/full-stack-bigiq-license-pool-3nic-bigip.template

python master_template.py -s existing -n 1 -l bigiq > ${BUILD_DIR_1NIC}${POOL_DIR}/existing-stack-bigiq-license-pool-1nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq > ${BUILD_DIR_2NIC}${POOL_DIR}/existing-stack-bigiq-license-pool-2nic-bigip.template
python master_template.py -s existing -n 3 -l bigiq > ${BUILD_DIR_3NIC}${POOL_DIR}/existing-stack-bigiq-license-pool-3nic-bigip.template


# Components 

## WAF
python master_template.py -s full -n 1 -l hourly -c waf > ${BUILD_DIR_1NIC}${HOURLY_DIR}/full-stack-hourly-1nic-bigip-w-waf.template
python master_template.py -s existing -n 1 -l hourly -c waf > ${BUILD_DIR_1NIC}${HOURLY_DIR}/existing-stack-hourly-1nic-bigip-w-waf.template
python master_template.py -s full -n 1 -l byol -c waf > ${BUILD_DIR_1NIC}${BYOL_DIR}/full-stack-byol-1nic-bigip-w-waf.template
python master_template.py -s existing -n 1 -l byol -c waf > ${BUILD_DIR_1NIC}${BYOL_DIR}/existing-stack-byol-1nic-bigip-w-waf.template
python master_template.py -s full -n 1 -l bigiq -c waf > ${BUILD_DIR_1NIC}${POOL_DIR}/full-stack-bigiq-license-pool-1nic-bigip-w-waf.template
python master_template.py -s existing -n 1 -l bigiq -c waf > ${BUILD_DIR_1NIC}${POOL_DIR}/existing-stack-bigiq-license-pool-1nic-bigip-w-waf.template


## Clusters 

### SAME AZ

#### HOURLY
python master_template.py -s full -n 2 -l hourly -H same-az > ${BUILD_DIR_2NIC}${HOURLY_DIR}/full-stack-same-az-cluster-hourly-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H same-az > ${BUILD_DIR_2NIC}${HOURLY_DIR}/existing-stack-same-az-cluster-hourly-2nic-bigip.template
#### WITH WAF 
python master_template.py -s full -n 2 -l hourly -c waf -H same-az > ${BUILD_DIR_2NIC}${HOURLY_DIR}/full-stack-same-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l hourly -c waf -H same-az > ${BUILD_DIR_2NIC}${HOURLY_DIR}/existing-stack-same-az-cluster-hourly-2nic-bigip-w-waf.template

#### BYOL
python master_template.py -s full -n 2 -l byol -H same-az > ${BUILD_DIR_2NIC}${BYOL_DIR}/full-stack-same-az-cluster-byol-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H same-az > ${BUILD_DIR_2NIC}${BYOL_DIR}/existing-stack-same-az-cluster-byol-2nic-bigip.template
#### WITH WAF 
python master_template.py -s full -n 2 -l byol -c waf -H same-az > ${BUILD_DIR_2NIC}${BYOL_DIR}/full-stack-same-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l byol -c waf -H same-az > ${BUILD_DIR_2NIC}${BYOL_DIR}/existing-stack-same-az-cluster-byol-2nic-bigip-w-waf.template

#### BIQ-IQ
python master_template.py -s full -n 2 -l bigiq -H same-az > ${BUILD_DIR_2NIC}${POOL_DIR}/full-stack-same-az-cluster-bigiq-license-pool-2nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq -H same-az > ${BUILD_DIR_2NIC}${POOL_DIR}/existing-stack-same-az-cluster-bigiq-license-pool-2nic-bigip.template
#### WITH WAF
python master_template.py -s full -n 2 -l bigiq -c waf -H same-az > ${BUILD_DIR_2NIC}${POOL_DIR}/full-stack-same-az-cluster-bigiq-license-pool-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l bigiq -c waf -H same-az > ${BUILD_DIR_2NIC}${POOL_DIR}/existing-stack-same-az-cluster-bigiq-license-pool-2nic-bigip-w-waf.template



### ACROSS AZ

#### HOURLY
python master_template.py -s full -n 2 -l hourly -H across-az > ${BUILD_DIR_2NIC}${HOURLY_DIR}/full-stack-across-az-cluster-hourly-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az > ${BUILD_DIR_2NIC}${HOURLY_DIR}/existing-stack-across-az-cluster-hourly-2nic-bigip.template
#### WITH WAF 
python master_template.py -s full -n 2 -l hourly -c waf -H across-az > ${BUILD_DIR_2NIC}${HOURLY_DIR}/full-stack-across-az-cluster-hourly-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l hourly -c waf -H across-az > ${BUILD_DIR_2NIC}${HOURLY_DIR}/existing-stack-across-az-cluster-hourly-2nic-bigip-w-waf.template

#### BYOL
python master_template.py -s full -n 2 -l byol -H across-az > ${BUILD_DIR_2NIC}${BYOL_DIR}/full-stack-across-az-cluster-byol-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H across-az > ${BUILD_DIR_2NIC}${BYOL_DIR}/existing-stack-across-az-cluster-byol-2nic-bigip.template
#### WITH WAF 
python master_template.py -s full -n 2 -l byol -c waf -H across-az > ${BUILD_DIR_2NIC}${BYOL_DIR}/full-stack-across-az-cluster-byol-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l byol -c waf -H across-az > ${BUILD_DIR_2NIC}${BYOL_DIR}/existing-stack-across-az-cluster-byol-2nic-bigip-w-waf.template

#### BIQ-IQ
python master_template.py -s full -n 2 -l bigiq -H across-az > ${BUILD_DIR_2NIC}${POOL_DIR}/full-stack-across-az-cluster-bigiq-license-pool-2nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq -H across-az > ${BUILD_DIR_2NIC}${POOL_DIR}/existing-stack-across-az-cluster-bigiq-license-pool-2nic-bigip.template
#### WITH WAF
python master_template.py -s full -n 2 -l bigiq -c waf -H across-az > ${BUILD_DIR_2NIC}${POOL_DIR}/full-stack-across-az-cluster-bigiq-license-pool-2nic-bigip-w-waf.template
python master_template.py -s existing -n 2 -l bigiq -c waf -H across-az > ${BUILD_DIR_2NIC}${POOL_DIR}/existing-stack-across-az-cluster-bigiq-license-pool-2nic-bigip-w-waf.template
