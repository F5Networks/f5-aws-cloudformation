#/bin/bash

# Tell troposphere to output
# python object True/False as JSON boolean
export TROPO_REAL_BOOL=true

# To populate cache files, run
# python image_finder.py

# BIGIP Stacks (Standalone)
## Supported - existing stacks
python master_template.py -s existing -n 1 -l hourly -T f5-existing-stack-payg-1nic-bigip.template > ../supported/standalone/1nic/existing-stack/payg/f5-existing-stack-payg-1nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -T f5-existing-stack-payg-2nic-bigip.template > ../supported/standalone/2nic/existing-stack/payg/f5-existing-stack-payg-2nic-bigip.template
python master_template.py -s existing -n 3 -l hourly -T f5-existing-stack-payg-3nic-bigip.template > ../supported/standalone/3nic/existing-stack/payg/f5-existing-stack-payg-3nic-bigip.template
python master_template.py -s existing -n 1 -l byol -T f5-existing-stack-byol-1nic-bigip.template > ../supported/standalone/1nic/existing-stack/byol/f5-existing-stack-byol-1nic-bigip.template
python master_template.py -s existing -n 2 -l byol -T f5-existing-stack-byol-2nic-bigip.template > ../supported/standalone/2nic/existing-stack/byol/f5-existing-stack-byol-2nic-bigip.template
python master_template.py -s existing -n 3 -l byol -T f5-existing-stack-byol-3nic-bigip.template > ../supported/standalone/3nic/existing-stack/byol/f5-existing-stack-byol-3nic-bigip.template
python master_template.py -s existing -n 1 -l bigiq -T f5-existing-stack-bigiq-1nic-bigip.template > ../supported/standalone/1nic/existing-stack/bigiq/f5-existing-stack-bigiq-1nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq -T f5-existing-stack-bigiq-2nic-bigip.template > ../supported/standalone/2nic/existing-stack/bigiq/f5-existing-stack-bigiq-2nic-bigip.template
python master_template.py -s existing -n 3 -l bigiq -T f5-existing-stack-bigiq-3nic-bigip.template > ../supported/standalone/3nic/existing-stack/bigiq/f5-existing-stack-bigiq-3nic-bigip.template

## Supported n-nic
python master_template.py -s existing -n 8 -l hourly -T f5-existing-stack-payg-n-nic-bigip.template > ../supported/standalone/n-nic/existing-stack/payg/f5-existing-stack-payg-n-nic-bigip.template
python master_template.py -s existing -n 8 -l byol -T f5-existing-stack-byol-n-nic-bigip.template > ../supported/standalone/n-nic/existing-stack/byol/f5-existing-stack-byol-n-nic-bigip.template
python master_template.py -s existing -n 8 -l bigiq -T f5-existing-stack-bigiq-n-nic-bigip.template > ../supported/standalone/n-nic/existing-stack/bigiq/f5-existing-stack-bigiq-n-nic-bigip.template

# Clusters
## Supported -existing stacks
### 2nic
python master_template.py -s existing -n 2 -l hourly -H same-az -T f5-existing-stack-same-az-cluster-payg-2nic-bigip.template > ../supported/failover/same-net/via-api/2nic/existing-stack/payg/f5-existing-stack-same-az-cluster-payg-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H same-az -T f5-existing-stack-same-az-cluster-byol-2nic-bigip.template > ../supported/failover/same-net/via-api/2nic/existing-stack/byol/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq -H same-az -T f5-existing-stack-same-az-cluster-bigiq-2nic-bigip.template > ../supported/failover/same-net/via-api/2nic/existing-stack/bigiq/f5-existing-stack-same-az-cluster-bigiq-2nic-bigip.template
python master_template.py -s existing -n 2 -l hourly -H across-az -T f5-existing-stack-across-az-cluster-payg-2nic-bigip.template > ../supported/failover/across-net/via-api/2nic/existing-stack/payg/f5-existing-stack-across-az-cluster-payg-2nic-bigip.template
python master_template.py -s existing -n 2 -l byol -H across-az -T f5-existing-stack-across-az-cluster-byol-2nic-bigip.template > ../supported/failover/across-net/via-api/2nic/existing-stack/byol/f5-existing-stack-across-az-cluster-byol-2nic-bigip.template
python master_template.py -s existing -n 2 -l bigiq -H across-az -T f5-existing-stack-across-az-cluster-bigiq-2nic-bigip.template > ../supported/failover/across-net/via-api/2nic/existing-stack/bigiq/f5-existing-stack-across-az-cluster-bigiq-2nic-bigip.template
### 3nic
python master_template.py -s existing -n 3 -l hourly -H same-az -T f5-existing-stack-same-az-cluster-payg-3nic-bigip.template > ../supported/failover/same-net/via-api/3nic/existing-stack/payg/f5-existing-stack-same-az-cluster-payg-3nic-bigip.template
python master_template.py -s existing -n 3 -l byol -H same-az -T f5-existing-stack-same-az-cluster-byol-3nic-bigip.template > ../supported/failover/same-net/via-api/3nic/existing-stack/byol/f5-existing-stack-same-az-cluster-byol-3nic-bigip.template
python master_template.py -s existing -n 3 -l bigiq -H same-az -T f5-existing-stack-same-az-cluster-bigiq-3nic-bigip.template > ../supported/failover/same-net/via-api/3nic/existing-stack/bigiq/f5-existing-stack-same-az-cluster-bigiq-3nic-bigip.template
python master_template.py -s existing -n 3 -l hourly -H across-az -T f5-existing-stack-across-az-cluster-payg-3nic-bigip.template > ../supported/failover/across-net/via-api/3nic/existing-stack/payg/f5-existing-stack-across-az-cluster-payg-3nic-bigip.template
python master_template.py -s existing -n 3 -l byol -H across-az -T f5-existing-stack-across-az-cluster-byol-3nic-bigip.template > ../supported/failover/across-net/via-api/3nic/existing-stack/byol/f5-existing-stack-across-az-cluster-byol-3nic-bigip.template
python master_template.py -s existing -n 3 -l bigiq -H across-az -T f5-existing-stack-across-az-cluster-bigiq-3nic-bigip.template > ../supported/failover/across-net/via-api/3nic/existing-stack/bigiq/f5-existing-stack-across-az-cluster-bigiq-3nic-bigip.template

## Supported - autoscale
# via-lb
python master_template.py -s existing -n 1 -l hourly -H autoscale -T f5-payg-autoscale-bigip-ltm.template > ../supported/autoscale/ltm/via-lb/1nic/existing-stack/payg/f5-payg-autoscale-bigip-ltm.template
python master_template.py -s existing -n 1 -l bigiq -H autoscale -T f5-bigiq-autoscale-bigip-ltm.template > ../supported/autoscale/ltm/via-lb/1nic/existing-stack/bigiq/f5-bigiq-autoscale-bigip-ltm.template
python master_template.py -s existing -n 1 -l hourly -H autoscale -c waf -T f5-payg-autoscale-bigip-waf.template > ../supported/autoscale/waf/via-lb/1nic/existing-stack/payg/f5-payg-autoscale-bigip-waf.template
python master_template.py -s existing -n 1 -l bigiq -H autoscale -c waf -T f5-bigiq-autoscale-bigip-waf.template > ../supported/autoscale/waf/via-lb/1nic/existing-stack/bigiq/f5-bigiq-autoscale-bigip-waf.template

# via-dns
python master_template.py -s existing -n 1 -l hourly -H autoscale -c dns -T f5-payg-autoscale-bigip-ltm-dns.template > ../supported/autoscale/ltm/via-dns/1nic/existing-stack/payg/f5-payg-autoscale-bigip-ltm-dns.template
python master_template.py -s existing -n 1 -l bigiq -H autoscale -c dns -T f5-bigiq-autoscale-bigip-ltm-dns.template > ../supported/autoscale/ltm/via-dns/1nic/existing-stack/bigiq/f5-bigiq-autoscale-bigip-ltm-dns.template
python master_template.py -s existing -n 1 -l hourly -H autoscale -c waf,dns -T f5-payg-autoscale-bigip-waf-dns.template > ../supported/autoscale/waf/via-dns/1nic/existing-stack/payg/f5-payg-autoscale-bigip-waf-dns.template
python master_template.py -s existing -n 1 -l bigiq -H autoscale -c waf,dns -T f5-bigiq-autoscale-bigip-waf-dns.template > ../supported/autoscale/waf/via-dns/1nic/existing-stack/bigiq/f5-bigiq-autoscale-bigip-waf-dns.template


### Experimental deprecated as of ESECLDTPLT-3106
# Network Only (experimental)
# python master_template.py -s network -a 1 -n 1 -T f5-network-only-1AZ-for-1nic-bigip.template > ../experimental/reference/1nic/network-only/f5-network-only-1AZ-for-1nic-bigip.template
# python master_template.py -s network -a 1 -n 2 -T f5-network-only-1AZ-for-2nic-bigip.template > ../experimental/reference/2nic/network-only/f5-network-only-1AZ-for-2nic-bigip.template
# python master_template.py -s network -a 1 -n 3 -T f5-network-only-1AZ-for-3nic-bigip.template > ../experimental/reference/3nic/network-only/f5-network-only-1AZ-for-3nic-bigip.template
# python master_template.py -s network -a 2 -n 1 -T f5-network-only-2AZ-for-1nic-bigip.template > ../experimental/reference/1nic/network-only/f5-network-only-2AZ-for-1nic-bigip.template
# python master_template.py -s network -a 2 -n 2 -T f5-network-only-2AZ-for-2nic-bigip.template > ../experimental/reference/2nic/network-only/f5-network-only-2AZ-for-2nic-bigip.template
# python master_template.py -s network -a 2 -n 3 -T f5-network-only-2AZ-for-3nic-bigip.template > ../experimental/reference/3nic/network-only/f5-network-only-2AZ-for-3nic-bigip.template

# Security Groups Only (experimental)
# python master_template.py -s security_groups -n 1 -T f5-security-groups-for-1nic-bigip.template > ../experimental/reference/1nic/security-group-creation/f5-security-groups-for-1nic-bigip.template
# python master_template.py -s security_groups -n 2 -T f5-security-groups-for-2nic-bigip.template > ../experimental/reference/2nic/security-group-creation/f5-security-groups-for-2nic-bigip.template
# python master_template.py -s security_groups -n 3 -T f5-security-groups-for-3nic-bigip.template > ../experimental/reference/3nic/security-group-creation/f5-security-groups-for-3nic-bigip.template

# Infra - Everything But BIG-IPs (experimental)
# python master_template.py -s infra -a 1 -n 1 -T f5-infra-only-1AZ-for-1nic-bigip.template > ../experimental/reference/1nic/infrastructure-only/f5-infra-only-1AZ-for-1nic-bigip.template
# python master_template.py -s infra -a 1 -n 2 -T f5-infra-only-1AZ-for-2nic-bigip.template > ../experimental/reference/2nic/infrastructure-only/f5-infra-only-1AZ-for-2nic-bigip.template
# python master_template.py -s infra -a 1 -n 3 -T f5-infra-only-1AZ-for-3nic-bigip.template > ../experimental/reference/3nic/infrastructure-only/f5-infra-only-1AZ-for-3nic-bigip.template
# python master_template.py -s infra -a 2 -n 1 -T f5-infra-only-2AZ-for-1nic-bigip.template > ../experimental/reference/1nic/infrastructure-only/f5-infra-only-2AZ-for-1nic-bigip.template
# python master_template.py -s infra -a 2 -n 2 -T f5-infra-only-2AZ-for-2nic-bigip.template > ../experimental/reference/2nic/infrastructure-only/f5-infra-only-2AZ-for-2nic-bigip.template
# python master_template.py -s infra -a 2 -n 3 -T f5-infra-only-2AZ-for-3nic-bigip.template > ../experimental/reference/3nic/infrastructure-only/f5-infra-only-2AZ-for-3nic-bigip.template

## Experimental
# python master_template.py -s existing -n 1 -l hourly -c waf -T f5-existing-stack-payg-1nic-bigip-w-waf.template > ../experimental/standalone/1nic/existing-stack/payg/f5-existing-stack-payg-1nic-bigip-w-waf.template
# python master_template.py -s existing -n 1 -l byol -c waf -T f5-existing-stack-byol-1nic-bigip-w-waf.template > ../experimental/standalone/1nic/existing-stack/byol/f5-existing-stack-byol-1nic-bigip-w-waf.template
# python master_template.py -s existing -n 1 -l bigiq -c waf -T f5-existing-stack-bigiq-1nic-bigip-w-waf.template > ../experimental/standalone/1nic/existing-stack/bigiq/f5-existing-stack-bigiq-1nic-bigip-w-waf.template

## Experimental - learning/POC
# python master_template.py -s full -n 1 -l hourly -T f5-full-stack-payg-1nic-bigip.template > ../experimental/standalone/1nic/learning-stack/payg/f5-full-stack-payg-1nic-bigip.template
# python master_template.py -s full -n 2 -l hourly -T f5-full-stack-payg-2nic-bigip.template > ../experimental/standalone/2nic/learning-stack/payg/f5-full-stack-payg-2nic-bigip.template
# python master_template.py -s full -n 3 -l hourly -T f5-full-stack-payg-3nic-bigip.template > ../experimental/standalone/3nic/learning-stack/payg/f5-full-stack-payg-3nic-bigip.template
# python master_template.py -s full -n 1 -l byol -T f5-full-stack-byol-1nic-bigip.template > ../experimental/standalone/1nic/learning-stack/byol/f5-full-stack-byol-1nic-bigip.template
# python master_template.py -s full -n 2 -l byol -T f5-full-stack-byol-2nic-bigip.template > ../experimental/standalone/2nic/learning-stack/byol/f5-full-stack-byol-2nic-bigip.template
# python master_template.py -s full -n 3 -l byol -T f5-full-stack-byol-3nic-bigip.template > ../experimental/standalone/3nic/learning-stack/byol/f5-full-stack-byol-3nic-bigip.template
# python master_template.py -s full -n 1 -l bigiq -T f5-full-stack-bigiq-1nic-bigip.template > ../experimental/standalone/1nic/learning-stack/bigiq/f5-full-stack-bigiq-1nic-bigip.template
# python master_template.py -s full -n 2 -l bigiq -T f5-full-stack-bigiq-2nic-bigip.template > ../experimental/standalone/2nic/learning-stack/bigiq/f5-full-stack-bigiq-2nic-bigip.template
# python master_template.py -s full -n 3 -l bigiq -T f5-full-stack-bigiq-3nic-bigip.template > ../experimental/standalone/3nic/learning-stack/bigiq/f5-full-stack-bigiq-3nic-bigip.template
# python master_template.py -s full -n 1 -l hourly -c waf -T f5-full-stack-payg-1nic-bigip-w-waf.template > ../experimental/standalone/1nic/learning-stack/payg/f5-full-stack-payg-1nic-bigip-w-waf.template
# python master_template.py -s full -n 1 -l byol -c waf -T f5-full-stack-byol-1nic-bigip-w-waf.template > ../experimental/standalone/1nic/learning-stack/byol/f5-full-stack-byol-1nic-bigip-w-waf.template
# python master_template.py -s full -n 1 -l bigiq -c waf -T f5-full-stack-bigiq-1nic-bigip-w-waf.template > ../experimental/standalone/1nic/learning-stack/bigiq/f5-full-stack-bigiq-1nic-bigip-w-waf.template

## Experimental (no longer generated)
#python master_template.py -s existing -n 2 -l hourly -c waf -H same-az -T f5-existing-stack-same-az-cluster-payg-2nic-bigip-w-waf.template > ../experimental/failover/same-net/via-api/2nic/existing-stack/payg/f5-existing-stack-same-az-cluster-payg-2nic-bigip-w-waf.template
#python master_template.py -s existing -n 2 -l byol -c waf -H same-az -T f5-existing-stack-same-az-cluster-byol-2nic-bigip-w-waf.template > ../experimental/failover/same-net/via-api/2nic/existing-stack/byol/f5-existing-stack-same-az-cluster-byol-2nic-bigip-w-waf.template
#python master_template.py -s existing -n 2 -l bigiq -c waf -H same-az -T f5-existing-stack-same-az-cluster-bigiq-2nic-bigip-w-waf.template > ../experimental/failover/same-net/via-api/2nic/existing-stack/bigiq/f5-existing-stack-same-az-cluster-bigiq-2nic-bigip-w-waf.template
#python master_template.py -s existing -n 2 -l hourly -c waf -H across-az -T f5-existing-stack-across-az-cluster-payg-2nic-bigip-w-waf.template > ../experimental/failover/across-net/via-api/2nic/existing-stack/payg/f5-existing-stack-across-az-cluster-payg-2nic-bigip-w-waf.template
#python master_template.py -s existing -n 2 -l byol -c waf -H across-az -T f5-existing-stack-across-az-cluster-byol-2nic-bigip-w-waf.template > ../experimental/failover/across-net/via-api/2nic/existing-stack/byol/f5-existing-stack-across-az-cluster-byol-2nic-bigip-w-waf.template
#python master_template.py -s existing -n 2 -l bigiq -c waf -H across-az -T f5-existing-stack-across-az-cluster-bigiq-2nic-bigip-w-waf.template > ../experimental/failover/across-net/via-api/2nic/existing-stack/bigiq/f5-existing-stack-across-az-cluster-bigiq-2nic-bigip-w-waf.template

## Experimental - learning/POC (no longer generated)
#python master_template.py -s full -n 2 -l hourly -H same-az -T f5-full-stack-same-az-cluster-payg-2nic-bigip.template > ../experimental/failover/same-net/via-api/2nic/learning-stack/payg/f5-full-stack-same-az-cluster-payg-2nic-bigip.template
#python master_template.py -s full -n 2 -l hourly -c waf -H same-az -T f5-full-stack-same-az-cluster-payg-2nic-bigip-w-waf.template > ../experimental/failover/same-net/via-api/2nic/learning-stack/payg/f5-full-stack-same-az-cluster-payg-2nic-bigip-w-waf.template
#python master_template.py -s full -n 2 -l byol -H same-az -T f5-full-stack-same-az-cluster-byol-2nic-bigip.template > ../experimental/failover/same-net/via-api/2nic/learning-stack/byol/f5-full-stack-same-az-cluster-byol-2nic-bigip.template
#python master_template.py -s full -n 2 -l byol -c waf -H same-az -T f5-full-stack-same-az-cluster-byol-2nic-bigip-w-waf.template > ../experimental/failover/same-net/via-api/2nic/learning-stack/byol/f5-full-stack-same-az-cluster-byol-2nic-bigip-w-waf.template
#python master_template.py -s full -n 2 -l bigiq -H same-az -T f5-full-stack-same-az-cluster-bigiq-2nic-bigip.template > ../experimental/failover/same-net/via-api/2nic/learning-stack/bigiq/f5-full-stack-same-az-cluster-bigiq-2nic-bigip.template
#python master_template.py -s full -n 2 -l bigiq -c waf -H same-az -T f5-full-stack-same-az-cluster-bigiq-2nic-bigip-w-waf.template > ../experimental/failover/same-net/via-api/2nic/learning-stack/bigiq/f5-full-stack-same-az-cluster-bigiq-2nic-bigip-w-waf.template
#python master_template.py -s full -n 2 -l hourly -H across-az -T f5-full-stack-across-az-cluster-payg-2nic-bigip.template > ../experimental/failover/across-net/via-api/2nic/learning-stack/payg/f5-full-stack-across-az-cluster-payg-2nic-bigip.template
#python master_template.py -s full -n 2 -l hourly -c waf -H across-az -T f5-full-stack-across-az-cluster-payg-2nic-bigip-w-waf.template > ../experimental/failover/across-net/via-api/2nic/learning-stack/payg/f5-full-stack-across-az-cluster-payg-2nic-bigip-w-waf.template
#python master_template.py -s full -n 2 -l byol -H across-az -T f5-full-stack-across-az-cluster-byol-2nic-bigip.template > ../experimental/failover/across-net/via-api/2nic/learning-stack/byol/f5-full-stack-across-az-cluster-byol-2nic-bigip.template
#python master_template.py -s full -n 2 -l byol -c waf -H across-az -T f5-full-stack-across-az-cluster-byol-2nic-bigip-w-waf.template > ../experimental/failover/across-net/via-api/2nic/learning-stack/byol/f5-full-stack-across-az-cluster-byol-2nic-bigip-w-waf.template
#python master_template.py -s full -n 2 -l bigiq -H across-az -T f5-full-stack-across-az-cluster-bigiq-2nic-bigip.template > ../experimental/failover/across-net/via-api/2nic/learning-stack/bigiq/f5-full-stack-across-az-cluster-bigiq-2nic-bigip.template
#python master_template.py -s full -n 2 -l bigiq -c waf -H across-az -T f5-full-stack-across-az-cluster-bigiq-2nic-bigip-w-waf.template > ../experimental/failover/across-net/via-api/2nic/learning-stack/bigiq/f5-full-stack-across-az-cluster-bigiq-2nic-bigip-w-waf.template

## Experimental - autoscale
# via-nlb
# python master_template.py -s existing -n 1 -l hourly -H autoscale -c nlb -T f5-payg-autoscale-bigip-ltm-nlb.template > ../experimental/autoscale/ltm/via-nlb/1nic/existing-stack/payg/f5-payg-autoscale-bigip-ltm-nlb.template
# python master_template.py -s existing -n 1 -l bigiq -H autoscale -c nlb -T f5-bigiq-autoscale-bigip-ltm-nlb.template > ../experimental/autoscale/ltm/via-nlb/1nic/existing-stack/bigiq/f5-bigiq-autoscale-bigip-ltm-nlb.template

# python master_template.py -s existing -n 1 -l hourly -H autoscale -c waf,nlb -T f5-payg-autoscale-bigip-waf-nlb.template > ../experimental/autoscale/waf/via-nlb/1nic/existing-stack/payg/f5-payg-autoscale-bigip-waf-nlb.template
# python master_template.py -s existing -n 1 -l bigiq -H autoscale -c waf,nlb -T f5-bigiq-autoscale-bigip-waf-nlb.template > ../experimental/autoscale/waf/via-nlb/1nic/existing-stack/bigiq/f5-bigiq-autoscale-bigip-waf-nlb.template

# via-lb (bigiqpayg)
# python master_template_autoscale_bigiqpayg.py -s existing -n 1 -l hourly,bigiq -H autoscale -T f5-bigiq-payg-autoscale-bigip-ltm.template > ../experimental/autoscale/ltm/via-lb/1nic/existing-stack/bigiq-payg/f5-bigiq-payg-autoscale-bigip-ltm.template
# python master_template_autoscale_bigiqpayg.py -s existing -n 1 -l hourly,bigiq -H autoscale -c waf -T f5-bigiq-payg-autoscale-bigip-waf.template > ../experimental/autoscale/waf/via-lb/1nic/existing-stack/bigiq-payg/f5-bigiq-payg-autoscale-bigip-waf.template