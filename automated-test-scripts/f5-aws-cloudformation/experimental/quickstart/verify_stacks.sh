#!/usr/bin/env bash
#  expectValue = "Stack Created Successfully"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 40

# Locate nested stacks
stacks=($(aws cloudformation list-stacks --region us-east-2 |jq -r '.StackSummaries[]| select(.StackName|contains("greg7-test"))| .StackName'))
# Determine Stack Status
for i in "${stacks[@]}"; do 
   echo $i
   result=$(aws cloudformation describe-stacks --region us-east-2 --stack-name $i|jq -r '.Stacks[].StackStatus')
   results="${results} $result"
   echo "Stack:$i | Status: $result"
done

# Determine Stacks total Status
for i in $results; do
    if [[ "$i" != "CREATE_COMPLETE" ]]; then
        echo "Stack not complete: $result"
        exit 1
    fi
done
echo "Stack Created Successfully"
echo "Results: $results"