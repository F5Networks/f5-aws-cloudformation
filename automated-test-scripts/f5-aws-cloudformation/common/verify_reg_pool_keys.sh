#!/usr/bin/env bash
#  expectValue = "Reg pool keys set"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10

IP=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1Url")|.OutputValue|split(":")[1]|.[2:]')

response=$(curl -sku admin:<AUTOFILL PASSWORD> https://${IP}/mgmt/cm/device/licensing/pool/regkey/licenses | jq .items[].name);
echo "Response: $response"

if echo $response | grep 'PoolName2'; then
    echo "Reg pool keys set"
fi

if [[ "<REGISTRATION POOL KEYS>" == "Do Not Create" ]] ; then
    echo "Reg pool keys set"
fi