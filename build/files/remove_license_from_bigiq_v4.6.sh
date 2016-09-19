#!/bin/bash

# Simple example script to remove device and restore license to Big-IQ pool
# To be run before shutdown
# https://aws.amazon.com/blogs/aws/auto-scaling-update-lifecycle-standby-detach/
# https://aws.amazon.com/blogs/compute/scheduling-ssh-jobs-using-aws-lambda/


# Source varables from firstrun.config
# ex. 
# BIGIQ_ADDRESS=52.89.223.113
# BIGIQ_USERNAME="admin"
# BIGIQ_PASSWORD='XXXXXXXXX'
# BIGIQ_LICENSE_POOL_UUID=92ff652f-3569-40ce-80db-6f0fce4b900a
source /tmp/firstrun.config


LICENSE_UUID=`cat /tmp/install-license-output.json | /usr/bin/jq -r .uuid`
LICENSE_STATE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .state`
MACHINE_ID=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .machineId`


echo "Removing License ${LICENSE_UUID} from BIG-IQ License Pool"
LICENSE_CMD_RETURN=$(curl -sk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} --max-time 15 -H "Content-Type: application/json" -X DELETE https://${BIGIQ_ADDRESS}/mgmt/cm/shared/licensing/pools/${BIGIQ_LICENSE_POOL_UUID}/members/${LICENSE_UUID} | /usr/bin/jq -r .state )
if [ "${LICENSE_CMD_RETURN}" == "LICENSED" ]; then
	logger -p local0.info "license_from_bigiq_debug: Remove License Call Successful"
fi

sleep 5

echo "Removing Machine ID ${MACHINE_ID} from BIG-IQ Managed Devices"
MACHINE_CMD_RETURN=$(curl -sk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} --max-time 15 -H "Content-Type: application/json" -X DELETE https://${BIGIQ_ADDRESS}/mgmt/cm/cloud/managed-devices/${MACHINE_ID} | /usr/bin/jq -r .state )
if [ "${MACHINE_CMD_RETURN}" == "ACTIVE" ]; then
	logger -p local0.info "license_from_bigiq_debug: Remove Machine Call Successful"
fi

