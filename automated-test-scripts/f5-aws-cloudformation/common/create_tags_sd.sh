#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = false
#  replayTimeout = 0

#Get instance ID of the Dewpoint server 
INSTANCE_ID=$(aws cloudformation list-stack-resources --stack-name <STACK NAME>-vpc --region <REGION> |jq -r '.StackResourceSummaries[]| select(.LogicalResourceId=="Webserver")| .PhysicalResourceId')

# Create a tag in Dewpoint Webserver and verify created successfully 
TAGS_KEY="Dptest"
TAGS_VALUE=<DEWPOINT JOB ID>
aws ec2 create-tags --region <REGION> --resources $INSTANCE_ID --tags Key=$TAGS_KEY,Value=$TAGS_VALUE

#Get reponse to check if the tag successfully created
RESPONSE=$(aws ec2 describe-tags --region <REGION> --filters "Name=resource-id,Values=$INSTANCE_ID" | jq .Tags[].Key | grep $TAGS_KEY)
echo "RESPONSE: $RESPONSE"
if [ -z "$RESPONSE" ]; then
    echo "FAILED" 
else
    echo "SUCCESS" #Response contain tags key
fi
        
