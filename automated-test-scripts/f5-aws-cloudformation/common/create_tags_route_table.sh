#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = false
#  replayTimeout = 0

#Get Route Table ID for test run 
ROUTE_TABLE_ID=$(aws ec2 describe-route-tables --region <REGION> | jq -r '.RouteTables[] | select (.Tags[].Value=="External Route Table<STACK NAME>-vpc")|.RouteTableId')

# Create a tag in route table and verify created successfull
TAGS_KEY="f5_cloud_failover_label"
TAGS_VALUE=<STACK NAME>
aws ec2 create-tags --region <REGION> --resources $ROUTE_TABLE_ID --tags Key=$TAGS_KEY,Value=$TAGS_VALUE

# Create route for failover testing
ene_id=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME> | jq -r '.Stacks[].Outputs[] | select(.OutputKey=="Bigip1subnet1Az1Interface") | .OutputValue')
echo "Interface ID: $ene_id"
create_route=$(aws ec2 create-route --route-table-id  $ROUTE_TABLE_ID --destination-cidr-block 192.0.2.0/24 --network-interface-id $ene_id --region <REGION>)
#Get reponse to check if the tag successfully created
RESPONSE=$(aws ec2 describe-tags --region <REGION> --filters "Name=resource-id,Values=$ROUTE_TABLE_ID" | jq .Tags[].Key | grep $TAGS_KEY)
echo "RESPONSE: $RESPONSE"
if [ -n "$RESPONSE" ] && echo $create_route | grep "true"; then
    echo "SUCCESS" #Response contain tags key and test route created 
else
    echo "FAILED"
fi