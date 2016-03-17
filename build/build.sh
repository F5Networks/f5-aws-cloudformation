#/bin/bash

BUILD_DIR="../unsupported"

python master-template.py -n 1 -l byol -s create > ${BUILD_DIR}/full-stack-vpc-w-byol-1nic-bigip.template
python master-template.py -n 2 -l byol -s create > ${BUILD_DIR}/full-stack-vpc-w-byol-2nic-bigip.template
python master-template.py -n 3 -l byol -s create > ${BUILD_DIR}/full-stack-vpc-w-byol-3nic-bigip.template

python master-template.py -n 1 -l byol -s existing > ${BUILD_DIR}/existing-stack-byol-1nic-bigip.template
python master-template.py -n 2 -l byol -s existing > ${BUILD_DIR}/existing-stack-byol-2nic-bigip.template
python master-template.py -n 3 -l byol -s existing > ${BUILD_DIR}/existing-stack-byol-3nic-bigip.template

python master-template.py -n 1 -l bigiq -s create > ${BUILD_DIR}/full-stack-bigiq-license-pool-1nic-bigip.template
python master-template.py -n 2 -l bigiq -s create > ${BUILD_DIR}/full-stack-bigiq-license-pool-2nic-bigip.template
python master-template.py -n 3 -l bigiq -s create > ${BUILD_DIR}/full-stack-bigiq-license-pool-3nic-bigip.template

python master-template.py -n 1 -l bigiq -s existing > ${BUILD_DIR}/existing-stack-bigiq-license-pool-1nic-bigip.template
python master-template.py -n 2 -l bigiq -s existing > ${BUILD_DIR}/existing-stack-bigiq-license-pool-2nic-bigip.template
python master-template.py -n 3 -l bigiq -s existing > ${BUILD_DIR}/existing-stack-bigiq-license-pool-3nic-bigip.template