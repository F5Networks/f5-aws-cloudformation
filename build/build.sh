#/bin/bash

BUILD_DIR="../unsupported"

# Populate Cache
python image_finder.py

python master_template.py -s network > ${BUILD_DIR}/network-only.template

python master_template.py -s infra -n 1 > ${BUILD_DIR}/infra-only-for-1nic-bigip.template
python master_template.py -s infra -n 2 > ${BUILD_DIR}/infra-only-for-2nic-bigip.template
python master_template.py -s infra -n 3 > ${BUILD_DIR}/infra-only-for-3nic-bigip.template

# Uncomment when v12/v13 hourly is avail
# python master_template.py -s full -n 1 -l hourly > ${BUILD_DIR}/full-stack-vpc-w-hourly-1nic-bigip.template
# python master_template.py -s full -n 2 -l hourly > ${BUILD_DIR}/full-stack-vpc-w-hourly-2nic-bigip.template
# python master_template.py -s full -n 3 -l hourly > ${BUILD_DIR}/full-stack-vpc-w-hourly-3nic-bigip.template

# python master_template.py -s existing -n 1 -l hourly > ${BUILD_DIR}/existing-stack-hourly-1nic-bigip.template
# python master_template.py -s existing -n 2 -l hourly > ${BUILD_DIR}/existing-stack-hourly-2nic-bigip.template
# python master_template.py -s existing -n 3 -l hourly > ${BUILD_DIR}/existing-stack-hourly-3nic-bigip.template

python master_template.py -s full -n 1 -l byol > ${BUILD_DIR}/full-stack-vpc-w-byol-1nic-bigip.template
python master_template.py -s full -n 2 -l byol > ${BUILD_DIR}/full-stack-vpc-w-byol-2nic-bigip.template
python master_template.py -s full -n 3 -l byol > ${BUILD_DIR}/full-stack-vpc-w-byol-3nic-bigip.template

python master_template.py -s existing -n 1 -l byol > ${BUILD_DIR}/existing-stack-byol-1nic-bigip.template
python master_template.py -s existing -n 2 -l byol > ${BUILD_DIR}/existing-stack-byol-2nic-bigip.template
python master_template.py -s existing -n 3 -l byol > ${BUILD_DIR}/existing-stack-byol-3nic-bigip.template

python master_template.py -s full -n 1 -l bigiq > ${BUILD_DIR}/full-stack-bigiq-license-pool-1nic-bigip.template
python master_template.py -s full -n 2 -l bigiq > ${BUILD_DIR}/full-stack-bigiq-license-pool-2nic-bigip.template
python master_template.py -s full -n 3 -l bigiq > ${BUILD_DIR}/full-stack-bigiq-license-pool-3nic-bigip.template

python master_template.py -s existing -n 1 -l bigiq > ${BUILD_DIR}/existing-stack-bigiq-license-pool-1nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq > ${BUILD_DIR}/existing-stack-bigiq-license-pool-2nic-bigip.template
python master_template.py -s existing -n 3 -l bigiq > ${BUILD_DIR}/existing-stack-bigiq-license-pool-3nic-bigip.template


##### Components  #####

# WAF
python master_template.py -s full -n 1 -l byol -c waf > ${BUILD_DIR}/full-stack-vpc-w-byol-1nic-bigip-w-waf.template
python master_template.py -s existing -n 1 -l byol -c waf > ${BUILD_DIR}/existing-stack-byol-1nic-bigip-w-waf.template
python master_template.py -s full -n 1 -l bigiq -c waf > ${BUILD_DIR}/full-stack-bigiq-license-pool-1nic-bigip-w-waf.template
python master_template.py -s existing -n 1 -l bigiq -c waf > ${BUILD_DIR}/existing-stack-bigiq-license-pool-1nic-bigip-w-waf.template
