#!/bin/bash

### BEGIN BIGIQ LICENSE ON BIG-IQ 5.0 as "Unmanaged" Device ###
# Ex. Obtaining License Pool UUID
# curl -sk -u admin:admin -H "Content-Type: application/json" https://${BIGIQ_ADDRESS}/mgmt/cm/shared/licensing/pools/?\$select=uuid,name
# {"items":[{"uuid":"aa588908-48c3-4b74-b505-053942b17566","name":"aws_license_pool"}],"generation":20,"kind":"cm:shared:licensing:pools:licensepoolworkercollectionstate","lastUpdateMicros":1473891034730907,"selfLink":"https://localhost/mgmt/cm/shared/licensing/pools"}

# Install License From Pool
declare -i i
i=0
while ( [ -z "${LICENSE_STATE}" ] || [ "${LICENSE_STATE}" == "null" ] );
do
     logger -p local0.info "license_from_bigiq_debug: Attempting to get license BIG-IP: ${MACHINE_ID} from license pool: ${BIGIQ_LICENSE_POOL_UUID}"

     curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} -o /tmp/install-license-output.json --max-time 15  -H "Content-Type: application/json" -X POST -d '{"deviceAddress":"'${BIGIP_DEVICE_ADDRESS}'", "username":"'${BIGIP_ADMIN_USERNAME}'", "password":"'${BIGIP_ADMIN_PASSWORD}'"}' https://${BIGIQ_ADDRESS}/mgmt/cm/shared/licensing/pools/${BIGIQ_LICENSE_POOL_UUID}/members
     LICENSE_UUID=`cat /tmp/install-license-output.json | /usr/bin/jq -r .uuid`
     LICENSE_STATE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .state`
     LICENSE_CODE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .code`
     LICENSE_MESSAGE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .message`
     if [ $i == 30 ]; then
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
     if [ $i == 30 ] && [ "${LICENSE_STATE}" != "LICENSED" ]; then
       logger -p local0.info "license_from_bigiq_debug: BIGIP node not moving to 'LICENSED' state"
       exit 1
     fi
     i=$i+1
     logger -p local0.info "license_from_bigiq_debug: License Status: ${LICENSE_STATE}..."
     sleep 10
done
### END BIGIQ LICENSE ###
