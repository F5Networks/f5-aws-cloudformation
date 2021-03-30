#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 5

# Grab stack info based on stack type

# Grab stack info based on stack type
stack=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME> | jq .Stacks[0].Outputs)
eipOutputName="Bigip1subnet1Az1SelfEipAddress"

# verify EIP was created
if [[ "<PUBLIC IP>" == "Yes" ]]; then
    if echo $stack | grep $eipOutputName; then
        echo "SUCCESS"
    else
    echo "FAILED"
    echo "Events:$events"
    fi
else
    echo "Not provisioning Public IP; continuing."
    echo "SUCCESS"
fi
