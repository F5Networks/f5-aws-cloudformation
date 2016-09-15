#!/bin/bash

### BEGIN BIGIQ LICENSE ###
declare -i i
i=0
while ([ -z "${MACHINE_STATE}" ] || [ "${MACHINE_STATE}" == "null" ]);
do
     logger -p local0.info "license_from_bigiq_debug: Attempting to register the BIGIP: ${BIGIP_DEVICE_ADDRESS} with BIGIQ: ${BIGIQ_ADDRESS}"
     curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} -o /tmp/add-managed-device-output.json --max-time 15  -H "Content-Type: application/json" -X POST -d '{"deviceAddress": "'${BIGIP_DEVICE_ADDRESS}'", "username":"'${BIGIP_ADMIN_USERNAME}'", "password":"'${BIGIP_ADMIN_PASSWORD}'", "automaticallyUpdateFramework":"true", "rootUsername":"root", "rootPassword":"'${BIGIP_ROOT_PASSWORD}'"}' https://${BIGIQ_ADDRESS}/mgmt/cm/cloud/managed-devices
     MACHINE_ID=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .machineId`
     MACHINE_SELFLINK=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .selfLink`
     MACHINE_STATE=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .state`
     MACHINE_CODE=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .code`
     MACHINE_MESSAGE=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .message`
     if [ $i == 10 ]; then
         logger -p local0.err "license_from_bigiq_debug: EXITING - Could not register the device. CODE: ${MACHINE_CODE}, MESSAGE: ${MACHINE_MESSAGE}"
         exit 1
    fi
    i=$i+1
    sleep 10
done
i=0
while [ "${MACHINE_STATE}" != "ACTIVE" ];
do 
     MACHINE_STATE=$( curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} --max-time 15 -H "Content-Type: application/json" -X GET https://${BIGIQ_ADDRESS}/mgmt/cm/cloud/managed-devices/${MACHINE_ID} | /usr/bin/jq -r .state )
     if [ $i == 30 ] && [ "${MACHINE_STATE}" != "ACTIVE" ]; then
       logger -p local0.err "license_from_bigiq_debug: ABORT! Taking too long to register this BIGIP with BIGIQ."
       exit 1
     fi
     i=$i+1
     logger -p local0.info "license_from_bigiq_debug: Machine State: ${MACHINE_STATE}..."
     sleep 30
done
# Install License From Pool
i=0
while ( [ -z "${LICENSE_STATE}" ] || [ "${LICENSE_STATE}" == "null" ] );
do
     logger -p local0.info "license_from_bigiq_debug: Attempting to get license BIG-IP: ${MACHINE_ID} from license pool: ${BIGIQ_LICENSE_POOL_UUID}"
     curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} -o /tmp/install-license-output.json --max-time 15  -H "Content-Type: application/json" -X POST -d '{"deviceReference":{"link": "'${MACHINE_SELFLINK}'"}}' https://${BIGIQ_ADDRESS}/mgmt/cm/shared/licensing/pools/${BIGIQ_LICENSE_POOL_UUID}/members
     LICENSE_UUID=`cat /tmp/install-license-output.json | /usr/bin/jq -r .uuid`
     LICENSE_STATE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .state`
     LICENSE_CODE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .code`
     LICENSE_MESSAGE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .message`
     if [ $i == 5 ]; then
       logger -p local0.err "license_from_bigiq_debug: EXITING, could not license the device. CODE: ${LICENSE_CODE}, MESSAGE: ${LICENSE_MESSAGE}"
       exit 1
     fi
     i=$i+1
     sleep 10
done
i=0
while [ "${LICENSE_STATE}" != "LICENSED" ];
do
     LICENSE_STATE=$( curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} --max-time 15 -H "Content-Type: application/json" -X GET https://${BIGIQ_ADDRESS}/mgmt/cm/shared/licensing/pools/${BIGIQ_LICENSE_POOL_UUID}/members/${LICENSE_UUID} | /usr/bin/jq -r .state )
     if [ "${LICENSE_STATE}" == "INSTALL" ] ; then
       sleep 5
       continue
     fi
     if [ $i == 5 ] && [ "${LICENSE_STATE}" != "LICENSED" ]; then
       logger -p local0.info "license_from_bigiq_debug: BIGIP node not moving to 'LICENSED' state"
       exit 1
     fi
     i=$i+1
     logger -p local0.info "license_from_bigiq_debug: License Status: ${LICENSE_STATE}..."
     sleep 10
done
### END BIGIQ LICENSE ###
