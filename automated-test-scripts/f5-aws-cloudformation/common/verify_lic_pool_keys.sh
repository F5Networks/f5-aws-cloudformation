#!/usr/bin/env bash
#  expectValue = "License pool keys set"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10

IP=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1Url")|.OutputValue|split(":")[1]|.[2:]')

response=$(curl -sku admin:<AUTOFILL PASSWORD> https://${IP}/mgmt/cm/device/licensing/pool/initial-activation/<AUTOFILL CLPV2 LICENSE KEY> | jq -r '.name');
response2=$(curl -sku admin:<AUTOFILL PASSWORD> https://${IP}/mgmt/cm/device/licensing/pool/initial-activation/<AUTOFILL CLPV2 LICENSE KEY> | jq -r '.status');
echo "Response: $response"
echo "Response2: $response2"

if [[ $response2 == "READY" ]] ; then
    echo "License pool keys set"
fi
if [[ "<LICENSE POOL KEYS>" == "Do Not Create" ]] ; then
    echo "License pool keys set"
fi