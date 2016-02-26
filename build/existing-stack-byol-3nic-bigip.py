#/usr/bin/python env

from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init, Metadata, InitConfig, InitFiles, InitFile
# from troposphere.ec2 import VPC
# from troposphere.ec2 import InternetGateway
# from troposphere.ec2 import VPCGatewayAttachment
# from troposphere.ec2 import Subnet
# from troposphere.ec2 import RouteTable
# from troposphere.ec2 import Route
# from troposphere.ec2 import SubnetRouteTableAssociation
# from troposphere.ec2 import NetworkInterface
# from troposphere.ec2 import NetworkInterfaceProperty
# from troposphere.ec2 import PrivateIpAddressSpecification
# from troposphere.ec2 import EIPAssociation
# from troposphere.ec2 import EIP
# from troposphere.ec2 import PortRange
# from troposphere.ec2 import Instance
from troposphere.ec2 import *


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
AWS CloudFormation Template for creating an 3nic Big-IP in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template.""")

### BEGIN PARAMETERS

KeyName = t.add_parameter(Parameter(
    "KeyName",
    Type="AWS::EC2::KeyPair::KeyName",
    Description="Name of an existing EC2 KeyPair to enable SSH access to the instance",
))

SSHLocation = t.add_parameter(Parameter(
    "SSHLocation",
    ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
    Description=" The IP address range that can be used to SSH to the EC2 instances",
    Default="0.0.0.0/0",
    MinLength="9",
    AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
    MaxLength="18",
    Type="String",
))

VPC = t.add_parameter(Parameter(
    "VPC",
    ConstraintDescription="Must be an existing VPC within working region.",
    Type="AWS::EC2::VPC::Id",
))

ManagementSubnetId = t.add_parameter(Parameter(
    "ManagementSubnetId",
    ConstraintDescription="Must be subnet ID within existing VPC",
    Type="AWS::EC2::Subnet::Id",
    Description="Management Subnet ID",
))

ExternalSubnetId = t.add_parameter(Parameter(
    "ExternalSubnetId",
    ConstraintDescription="Must be subnet ID within existing VPC",
    Type="AWS::EC2::Subnet::Id",
    Description="Public or External subnet ID",
))

InternalSubnetId = t.add_parameter(Parameter(
    "InternalSubnetId",
    ConstraintDescription="Must be subnet ID within existing VPC",
    Type="AWS::EC2::Subnet::Id",
    Description="Private or Internal subnet ID",
))

BigIPManagementSecurityGroupId = t.add_parameter(Parameter(
    "BigIPManagementSecurityGroupId",
    ConstraintDescription="Must be security group ID within existing VPC",
    Type="AWS::EC2::SecurityGroup::Id",
    Description="BigIP Management Security Group",
))

BigIPExternalSecurityGroupId = t.add_parameter(Parameter(
    "BigIPExternalSecurityGroupId",
    ConstraintDescription="Must be security group ID within existing VPC",
    Type="AWS::EC2::SecurityGroup::Id",
    Description="Public or External Security Group ID",
))

BigIPInternalSecurityGroupId = t.add_parameter(Parameter(
    "BigIPInternalSecurityGroupId",
    ConstraintDescription="Must be security group ID within existing VPC",
    Type="AWS::EC2::SecurityGroup::Id",
    Description="Private or Internal Security Group ID",
))

BigIPInstanceType = t.add_parameter(Parameter(
    "BigIPInstanceType",
    Default="m3.xlarge",
    ConstraintDescription="must be a valid Big-IP EC2 instance type",
    Type="String",
    Description="F5 BIG-IP Virtual Instance Type",
    AllowedValues=["m3.xlarge", "m3.2xlarge", "c1.medium", "c1.xlarge", "cc1.4xlarge", "cc2.8xlarge", "cg1.4xlarge"],
))

LicenseKey = t.add_parameter(Parameter(
    "LicenseKey",
    Type="String",
    Description="Please enter your F5 BYOL regkey here:",
    MinLength="1",
    AllowedPattern="([\\x41-\\x5A][\\x41-\\x5A|\\x30-\\x39]{4})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{7})",
    MaxLength="255",
    ConstraintDescription="Please verify your F5 BYOL regkey.",
))

BigIPPerformanceType = t.add_parameter(Parameter(
    "BigIPPerformanceType",
    Default="Good",
    ConstraintDescription="Must be a valid F5 Big-IP performance type",
    Type="String",
    Description="F5 BigIP Performance Type",
    AllowedValues=["Good", "Better", "Best"],
))

# BigIPManagementGuiPort = t.add_parameter(Parameter(
#     "BigIPManagementGuiPort",
#     Default="8443",
#     ConstraintDescription="Must be a valid, unusued port on BIG-IP.",
#     Type="Number",
#     Description="Port to use for the managment GUI",
# ))

BigIPAdminUsername = t.add_parameter(Parameter(
    "BigIPAdminUsername",
    Type="String",
    Description="Please enter your BIG-IP Admin Username",
    Default="admin",
    MinLength="1",
    MaxLength="255",
    ConstraintDescription="Please verify your BIG-IP Admin Username",
))

BigIPAdminPassword = t.add_parameter(Parameter(
    "BigIPAdminPassword",
    Type="String",
    Description="Please enter your BIG-IP Admin Password",
    MinLength="1",
    NoEcho=True,
    MaxLength="255",
    ConstraintDescription="Please verify your BIG-IP Admin Password",
))

# WebserverInstanceType = t.add_parameter(Parameter(
#     "WebserverInstanceType",
#     Default="t1.micro",
#     ConstraintDescription="must be a valid EC2 instance type",
#     Type="String",
#     Description="Webserver EC2 instance type",
#     AllowedValues=["t1.micro", "m3.medium", "m3.xlarge", "m2.xlarge", "m3.2xlarge", "c3.large", "c3.xlarge"],
# ))

Webserver = t.add_parameter(Parameter(
    "Webserver",
    ConstraintDescription="Web Server IP used for Big-IP pool Member",
    Type="String",
    Description="Web Server IP used for Big-IP pool member",
))

### BEGIN MAPPINGS

t.add_mapping("BigIPRegionMap",
{u'ap-northeast-1': {u'Best': u'ami-bcf69bbc',
                     u'Better': u'ami-d6f69bd6',
                     u'Good': u'ami-1ef69b1e'},
 u'ap-southeast-1': {u'Best': u'ami-3c9a896e',
                     u'Better': u'ami-249a8976',
                     u'Good': u'ami-029a8950'},
 u'ap-southeast-2': {u'Best': u'ami-bfd69c85',
                     u'Better': u'ami-45d69c7f',
                     u'Good': u'ami-63d69c59'},
 u'eu-west-1': {u'Best': u'ami-3798a740',
                u'Better': u'ami-2b98a75c',
                u'Good': u'ami-f799a680'},
 u'sa-east-1': {u'Best': u'ami-a3952dcf',
                u'Better': u'ami-f69e269a',
                u'Good': u'ami-36962e5a'},
 u'us-east-1': {u'Best': u'ami-98715bf0',
                u'Better': u'ami-f1421d94',
                u'Good': u'ami-03421d66'},
 u'us-west-1': {u'Best': u'ami-a70bc8e3',
                u'Better': u'ami-af0bc8eb',
                u'Good': u'ami-e90bc8ad'},
 u'us-west-2': {u'Best': u'ami-e2d735d1',
                u'Better': u'ami-ccd735ff',
                u'Good': u'ami-36d73505'}}
)

# t.add_mapping("AWSRegionArch2AMI",
# {u'ap-northeast-1': {u'AMI': u'ami-489b8049'},
#  u'ap-southeast-1': {u'AMI': u'ami-0ad2f858'},
#  u'eu-west-1': {u'AMI': u'ami-7dfc720a'},
#  u'sa-east-1': {u'AMI': u'ami-6def5070'},
#  u'us-east-1': {u'AMI': u'ami-00266568'},
#  u'us-west-1': {u'AMI': u'ami-fc8b93b9'},
#  u'us-west-2': {u'AMI': u'ami-71520941'}}
# )


### BEGIN RESOURCES

# VPC = t.add_resource(VPC(
#     "VPC",
#     EnableDnsSupport="true",
#     CidrBlock="10.0.0.0/16",
#     EnableDnsHostnames="true",
#     Tags=Tags(
#         Name=Ref("AWS::StackId"),
#         Application=Ref("AWS::StackId"),
#     ),
# ))

# AZ1ManagementSubnet = t.add_resource(Subnet(
#     "AZ1ManagementSubnet",
#     Tags=Tags(
#         Name="AZ1 Management Subnet",
#         Application=Ref("AWS::StackId"),
#     ),
#     VpcId=Ref("VPC"),
#     CidrBlock="10.0.0.0/24",
#     AvailabilityZone=Ref(AvailabilityZone1),
# ))

# AZ1ExternalSubnet = t.add_resource(Subnet(
#     "AZ1ExternalSubnet",
#     Tags=Tags(
#         Name="AZ1 External Subnet",
#         Application=Ref("AWS::StackId"),
#     ),
#     VpcId=Ref("VPC"),
#     CidrBlock="10.0.1.0/24",
#     AvailabilityZone=GetAtt("AZ1ManagementSubnet", "AvailabilityZone"),
# ))

# AZ1InternalSubnet = t.add_resource(Subnet(
#     "AZ1InternalSubnet",
#     Tags=Tags(
#         Name="AZ1 Internal Subnet",
#         Application=Ref("AWS::StackId"),
#     ),
#     VpcId=Ref("VPC"),
#     CidrBlock="10.0.2.0/24",
#     AvailabilityZone=GetAtt("AZ1ManagementSubnet", "AvailabilityZone"),
# ))

# AZ1ApplicationSubnet = t.add_resource(Subnet(
#     "AZ1ApplicationSubnet",
#     Tags=Tags(
#         Name="AZ1 Application Subnet",
#         Application=Ref("AWS::StackId"),
#     ),
#     VpcId=Ref("VPC"),
#     CidrBlock="10.0.3.0/24",
#     AvailabilityZone=GetAtt("AZ1ManagementSubnet", "AvailabilityZone"),
# ))

# InternetGateway = t.add_resource(InternetGateway(
#     "InternetGateway",
#     Tags=Tags(
#         Application=Ref("AWS::StackId"),
#     ),
# ))

# AttachGateway = t.add_resource(VPCGatewayAttachment(
#     "AttachGateway",
#     VpcId=Ref(VPC),
#     InternetGatewayId=Ref(InternetGateway),
# ))

# ManagementRouteTable = t.add_resource(RouteTable(
#     "ManagementRouteTable",
#     VpcId=Ref("VPC"),
#     Tags=Tags(
#         Name="Management Route Table",
#         Application=Ref("AWS::StackName"),
#         Network="Mgmt",
#     ),
# ))

# ExternalRouteTable = t.add_resource(RouteTable(
#     "ExternalRouteTable",
#     VpcId=Ref("VPC"),
#     Tags=Tags(
#         Name="External Route Table",
#         Application=Ref("AWS::StackName"),
#         Network="External",
#     ),
# ))

# InternalRouteTable = t.add_resource(RouteTable(
#     "InternalRouteTable",
#     VpcId=Ref("VPC"),
#     Tags=Tags(
#         Name="Internal Route Table",
#         Application=Ref("AWS::StackName"),
#         Network="Internal",
#     ),
# ))

# ApplicationRouteTable = t.add_resource(RouteTable(
#     "ApplicationRouteTable",
#     VpcId=Ref("VPC"),
#     Tags=Tags(
#         Name="Application Route Table",
#         Application=Ref("AWS::StackName"),
#         Network="Application",
#     ),
# ))

# ManagementRoute = t.add_resource(Route(
#     "ManagementRoute",
#     GatewayId=Ref("InternetGateway"),
#     DestinationCidrBlock="0.0.0.0/0",
#     RouteTableId=Ref("ManagementRouteTable"),
# ))

# ExternalRoute = t.add_resource(Route(
#     "ExternalRoute",
#     GatewayId=Ref("InternetGateway"),
#     DestinationCidrBlock="0.0.0.0/0",
#     RouteTableId=Ref(ExternalRouteTable),
# ))

# InternalRoute = t.add_resource(Route(
#     "InternalRoute",
#     GatewayId=Ref("InternetGateway"),
#     DestinationCidrBlock="0.0.0.0/0",
#     RouteTableId=Ref(InternalRouteTable),
# ))

# ApplicationRoute = t.add_resource(Route(
#     "ApplicationRoute",
#     GatewayId=Ref(InternetGateway),
#     DestinationCidrBlock="0.0.0.0/0",
#     RouteTableId=Ref(ApplicationRouteTable),
# ))


# ManagementSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
#     "ManagementSubnetRouteTableAssociation",
#     SubnetId=Ref("AZ1ManagementSubnet"),
#     RouteTableId=Ref(ManagementRouteTable),
# ))

# ExternalSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
#     "ExternalSubnetRouteTableAssociation",
#     SubnetId=Ref(AZ1ExternalSubnet),
#     RouteTableId=Ref(ExternalRouteTable),
# ))

# InternalSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
#     "InternalSubnetRouteTableAssociation",
#     SubnetId=Ref(AZ1InternalSubnet),
#     RouteTableId=Ref(InternalRouteTable),
# ))

# ApplicationSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
#     "ApplicationSubnetRouteTableAssociation",
#     SubnetId=Ref(AZ1ApplicationSubnet),
#     RouteTableId=Ref(ApplicationRouteTable),
# ))


# BigIPExternalSecurityGroup = t.add_resource(SecurityGroup(
#     "BigIPExternalSecurityGroup",
#     SecurityGroupIngress=[{ "ToPort": "22", "IpProtocol": "tcp", "CidrIp": Ref(SSHLocation), "FromPort": "22" }, { "ToPort": Ref(BigIPManagementGuiPort), "IpProtocol": "tcp", "CidrIp": Ref(SSHLocation), "FromPort": Ref(BigIPManagementGuiPort) }, { "ToPort": "80", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "80" }, { "ToPort": "443", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "443" }, { "ToPort": "4353", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "4353" }, { "ToPort": "1026", "IpProtocol": "udp", "CidrIp": "10.0.0.0/16", "FromPort": "1026" }, { "ToPort": "-1", "IpProtocol": "icmp", "CidrIp": "0.0.0.0/0", "FromPort": "-1" }],
#     VpcId=Ref(VPC),
#     GroupDescription="Public or External interface rules",
#     Tags=Tags(
#         Name="BigIP External Security Group",
#         Application=Ref("AWS::StackName"),
#     ),
# ))


# WebserverSecurityGroup = t.add_resource(SecurityGroup(
#     "WebserverSecurityGroup",
#     SecurityGroupIngress=[{ "ToPort": "22", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "22" }, { "ToPort": "80", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "80" }, { "ToPort": "443", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "443" }, { "ToPort": "-1", "IpProtocol": "icmp", "CidrIp": "0.0.0.0/0", "FromPort": "-1" }],
#     VpcId=Ref(VPC),
#     GroupDescription="Enable Access to Webserver",
#     Tags=Tags(
#         Name="Webserver Security Group",
#         Application=Ref("AWS::StackName"),
#     ),
# ))


# NOTE: Need to toggle Subnet Referenced

ManagementInterface = t.add_resource(NetworkInterface(
    "ManagementInterface",
    # SubnetId=Ref(AZ1ManagementSubnet),
    SubnetId=Ref(ManagementSubnetId),
    GroupSet=[Ref(BigIPManagementSecurityGroupId)],
    Description="Management Interface for the BigIP",
))

ExternalInterface = t.add_resource(NetworkInterface(
    "ExternalInterface",
    # SubnetId=Ref(AZ1ExternalSubnet),
    SubnetId=Ref(ExternalSubnetId),
    GroupSet=[Ref(BigIPExternalSecurityGroupId)],
    Description="Public External Interface for the BigIP",
    SecondaryPrivateIpAddressCount="1",
))

InternalInterface = t.add_resource(NetworkInterface(
    "InternalInterface",
    # SubnetId=Ref(AZ1InternalSubnet),
    SubnetId=Ref(InternalSubnetId),
    GroupSet=[Ref(BigIPInternalSecurityGroupId)],
    Description="Management Interface for the BigIP",
))

ManagementEipAddress = t.add_resource(EIP(
    "ManagementEipAddress",
    Domain="vpc",
))

ExternalSelfEipAddress = t.add_resource(EIP(
    "ExternalSelfEipAddress",
    Domain="vpc",
))

VipEipAddress = t.add_resource(EIP(
    "VipEipAddress",
    Domain="vpc",
))


ManagementEipAssociation = t.add_resource(EIPAssociation(
    "ManagementEipAssociation",
    NetworkInterfaceId=Ref(ManagementInterface),
    AllocationId=GetAtt(ManagementEipAddress, "AllocationId"),
))

ExternalSelfEipAssociation = t.add_resource(EIPAssociation(
    "ExternalSelfEipAssociation",
    NetworkInterfaceId=Ref(ExternalInterface),
    AllocationId=GetAtt("ExternalSelfEipAddress", "AllocationId"),
    PrivateIpAddress=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
))

VipEipAssociation = t.add_resource(EIPAssociation(
    "VipEipAssociation",
    NetworkInterfaceId=Ref("ExternalInterface"),
    AllocationId=GetAtt("VipEipAddress", "AllocationId"),
    PrivateIpAddress=Select("0", GetAtt("ExternalInterface", "SecondaryPrivateIpAddresses")),
))


# Note: If existing Webserver input changes

three_nic_metadata = Metadata(
    Init({
        'config': InitConfig(
            files=InitFiles(
                {
                    '/tmp/firstrun.config': InitFile(
                        content=Join('',[
                            "#!/bin/bash\n", 
                            "HOSTNAME=`curl http://169.254.169.254/latest/meta-data/hostname`\n", 
                            "REGKEY='", Ref(LicenseKey), "'\n", 
                            "TZ='America/Los_Angeles'\n", 
                            "MGMTIP='", GetAtt("ManagementInterface", "PrimaryPrivateIpAddress"), "'\n", 
                            "EXTIP='", GetAtt("ExternalInterface", "PrimaryPrivateIpAddress"), "'\n", 
                            "EXTPRIVIP='", Select("0", GetAtt("ExternalInterface", "SecondaryPrivateIpAddresses")), "'\n",
                            "INTIP='",GetAtt("InternalInterface", "PrimaryPrivateIpAddress"),"'\n",
                            "EXTMASK='24'\n",
                            "INTMASK='24'\n", 
                            "BIGIP_ADMIN_USERNAME='", Ref(BigIPAdminUsername), "'\n", 
                            "BIGIP_ADMIN_PASSWORD='", Ref(BigIPAdminPassword), "'\n", 
                            "APPNAME='demo-app-1'\n", "VIRTUALSERVERPORT=80\n", 
                            "POOLMEM='", Ref(Webserver), "'\n", 
                            "POOLMEMPORT=80\n", 
                            "CRT='default.crt'\n", 
                            "KEY='default.key'\n"
                            ]
                        ),
                        mode='000777',
                        owner='root',
                        group='root'
                    ),
                    '/tmp/firstrun.sh': InitFile(
                        content=Join('',[
                            "#!/bin/bash\n",
                            ". /tmp/firstrun.config\n",
                            "FILE=/tmp/firstrun.log\n",
                            "if [ ! -e $FILE ]\n"," then\n",
                            "     touch $FILE\n",
                            "     nohup $0 0<&- &>/dev/null &\n",
                            "     exit\n",
                            "fi\n",
                            "function checkF5Ready {\n",
                            "     sleep 5\n",
                            "     while [[ ! -e '/var/prompt/ps1' ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "done \n",
                            "sleep 5\n",
                            "STATUS=`cat /var/prompt/ps1`\n",
                            "while [[ ${STATUS}x != 'NO LICENSE'x ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "     STATUS=`cat /var/prompt/ps1`\n",
                            "done\n",
                            "echo -n ' '\n",
                            "while [[ ! -e '/var/prompt/cmiSyncStatus' ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "done \n",
                            "STATUS=`cat /var/prompt/cmiSyncStatus`\n",
                            "while [[ ${STATUS}x != 'Standalone'x ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "     STATUS=`cat /var/prompt/cmiSyncStatus`\n",
                            "done\n",
                            "}\n",
                            "function checkStatusnoret {\n",
                            "sleep 10\n",
                            "STATUS=`cat /var/prompt/ps1`\n",
                            "while [[ ${STATUS}x != 'Active'x ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "     STATUS=`cat /var/prompt/ps1`\n",
                            "done\n",
                            "}\n",
                            "exec 1<&-\n",
                            "exec 2<&-\n",
                            "exec 1<>$FILE\n",
                            "exec 2>&1\n",
                            "checkF5Ready\n",
                            "tmsh modify /sys global-settings hostname ${HOSTNAME}\n",
                            "tmsh mv cm device bigip1 ${HOSTNAME}\n",
                            "tmsh modify auth password root <<< $'${BIGIP_ADMIN_PASSWORD}\n${BIGIP_ADMIN_PASSWORD}\n'\n",
                            "tmsh modify auth user admin password \"'${BIGIP_ADMIN_PASSWORD}'\"\n",
                            "tmsh save /sys config\n",
                            "tmsh install /sys license registration-key ${REGKEY} license-server activate.f5.com\n",
                            "tmsh save /sys config\n",
                            "checkF5Ready\n",
                            "checkStatusnoret\n",
                            "sleep 20\n",
                            "tmsh modify sys db dhclient.mgmt { value disable }\n",
                            "tmsh modify sys ntp timezone ${TZ}\n",
                            "tmsh modify sys ntp servers add { 0.pool.ntp.org 1.pool.ntp.org }\n",
                            "tmsh modify sys global-settings gui-setup disabled\n",
                            "tmsh create net vlan external interfaces add { 1.1 } \n",
                            "tmsh create net vlan internal interfaces add { 1.2 } \n",
                            "tmsh create net self ${EXTIP}/${EXTMASK} vlan external allow-service add { tcp:4353 udp:1026 }\n",
                            "tmsh create net self ${INTIP}/${INTMASK} vlan internal allow-service default\n",
                            "tmsh create net route default gw 10.0.1.1\n",
                            "tmsh save /sys config\n",
                            "tmsh create ltm pool ${APPNAME}-pool members add { ${POOLMEM}:${POOLMEMPORT} } monitor gateway_icmp\n",
                            "tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} ip-protocol tcp mask 255.255.255.255 pool /Common/${APPNAME}-pool source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\n",
                            "tmsh save /sys config\n"
                            ]
                        ),
                        mode='000777',
                        owner='root',
                        group='root'
                    )
                } 
            ),
            commands={
                       "b-configure-BigIP" : {
                            "command" : "/tmp/firstrun.sh\n"
                        }
            }
        ) 
    })
)

BigIPInstance = t.add_resource(Instance(
    "BigIPInstance",
    Metadata=three_nic_metadata,
    UserData=Base64(Join("", ["#!/bin/bash\n", "/opt/aws/apitools/cfn-init-1.4-0.amzn1/bin/cfn-init -v -s ", Ref("AWS::StackId"), " -r BigIPInstance ", " --region ", Ref("AWS::Region"), "\n"])),
    Tags=Tags(
        Application=Ref("AWS::StackId"),
    ),
    ImageId=FindInMap("BigIPRegionMap", Ref("AWS::Region"), Ref(BigIPPerformanceType)),
    KeyName=Ref(KeyName),
    InstanceType=Ref(BigIPInstanceType),
    NetworkInterfaces=[
    NetworkInterfaceProperty(
        DeviceIndex="0",
        NetworkInterfaceId=Ref("ManagementInterface"),
        Description="Management Interface",
    ),
    NetworkInterfaceProperty(
        DeviceIndex="1",
        NetworkInterfaceId=Ref("ExternalInterface"),
        Description="Public or External Interface",
    ),
    NetworkInterfaceProperty(
        DeviceIndex="2",
        NetworkInterfaceId=Ref("InternalInterface"),
        Description="Private or Internal Interface",
    ),
    ],
))


# Webserver = t.add_resource(Instance(
#     "Webserver",
#     UserData=Base64(Join("", ["#!/bin/bash -x\n", "echo \"Hello World\"\n"])),
#     Tags=Tags(
#         Name="Webserver",
#         Application=Ref("AWS::StackName"),
#     ),
#     ImageId=FindInMap("AWSRegionArch2AMI", Ref("AWS::Region"), "AMI"),
#     KeyName=Ref(KeyName),
#     InstanceType=Ref(WebserverInstanceType),
#     NetworkInterfaces=[
#     NetworkInterfaceProperty(
#         SubnetId=Ref(AZ1ApplicationSubnet),
#         DeviceIndex="0",
#         GroupSet=[Ref("WebserverSecurityGroup")],
#         Description=Join("", [Ref("AWS::StackName"), " Webserver Network Interface"]),
#         AssociatePublicIpAddress="true",
#     ),
#     ],
# ))

### BEGIN OUTPUT

VpcID = t.add_output(Output(
    "VpcID",
    Description="VPC ID",
    Value=Ref(VPC),
))

AvailabilityZone = t.add_output(Output(
    "AvailabilityZone",
    Description="Availability Zone",
    Value=GetAtt(BigIPInstance, "AvailabilityZone"),
))

# AZ1ManagementSubnetID = t.add_output(Output(
#     "AZ1ManagementSubnetID",
#     Description="AZ1 Management Subnet ID",
#     Value=Ref(AZ1ManagementSubnet),
# ))

# Note: AZ1 part of name needs to be stripped
ExternalSubnetId = t.add_output(Output(
    "Az1ExternalSubnetId",
    Description="Az1 Public or External Subnet Id",
    Value=Ref(ExternalSubnetId),
))

# AZ1InternalSubnetID = t.add_output(Output(
#     "AZ1InternalSubnetID",
#     Description="AZ1 Private or Internal Subnet ID",
#     Value=Ref(AZ1InternalSubnet),
# ))

# AZ1ApplicationSubnetID = t.add_output(Output(
#     "AZ1ApplicationSubnetID",
#     Description="AZ1 Application Subnet ID",
#     Value=Ref(AZ1ApplicationSubnet),
# ))

BigIPInstanceId = t.add_output(Output(
    "BigIPInstanceId",
    Description="Instance ID of Big-IP in Amazon",
    Value=Ref(BigIPInstance),
))

BigIPManagementSecurityGroupId = t.add_output(Output(
    "BigIPManagementSecurityGroupId",
    Description="Big-IP Management Security Group",
    Value=Ref(BigIPManagementSecurityGroupId),
))

BigIPExternalSecurityGroupId = t.add_output(Output(
    "BigIPExternalSecurityGroupId",
    Description="Public or External Security Group",
    Value=Ref(BigIPExternalSecurityGroupId),
))

BigIPInternalSecurityGroupID = t.add_output(Output(
    "BigIPInternalSecurityGroupID",
    Description="Private or Internal Security Group",
    Value=Ref(BigIPInternalSecurityGroupId),
))

ManagementEipAddress = t.add_output(Output(
    "ManagementEipAddress",
    Description="IP address of management port on BIG-IP",
    Value=Ref(ManagementEipAddress),
))

ManagementInterfaceId = t.add_output(Output(
    "ManagementInterfaceId",
    Description="Management interface ID on BIG-IP",
    Value=Ref(ManagementInterface),
))

ManagementInterfacePrivateIp = t.add_output(Output(
    "ManagementInterfacePrivateIp",
    Description="Internally routable IP of management interface on BIG-IP",
    Value=GetAtt(ManagementInterface, "PrimaryPrivateIpAddress"),
))

ExternalInterfaceId = t.add_output(Output(
    "ExternalInterfaceId",
    Description="External interface ID on BIG-IP",
    Value=Ref(ExternalInterface),
))

ExternalInterfacePrivateIp = t.add_output(Output(
    "ExternalInterfacePrivateIp",
    Description="Internally routable IP of public interface on BIG-IP",
    Value=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
))

VipPrivateIp = t.add_output(Output(
    "ViprivateIp",
    Description="VIP on External Interface Secondary IP 1",
    Value=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
))

VipEipAddress = t.add_output(Output(
    "VipEipAddress",
    Description="EIP address for VIP",
    Value=Join("", ["http://", Ref(VipEipAddress), ":80"]),
))


BigIPUrl = t.add_output(Output(
    "BigIPUrl",
    Description="BigIP Management GUI",
    Value=Join("", ["https://", GetAtt(BigIPInstance, "PublicIp")]),
))


InternalInterfaceId = t.add_output(Output(
    "InternalInterfaceId",
    Description="Internal interface ID on BIG-IP",
    Value=Ref(InternalInterface),
))

InternalInterfacePrivateIp = t.add_output(Output(
    "InternalInterfacePrivateIp",
    Description="Internally routable IP of internal interface on BIG-IP",
    Value=GetAtt(InternalInterface, "PrimaryPrivateIpAddress"),
))


# WebserverPrivateIP = t.add_output(Output(
#     "WebserverPrivateIP",
#     Description="Private IP for Webserver",
#     Value=GetAtt(Webserver, "PrivateIp"),
# ))

# WebserverPublicIP = t.add_output(Output(
#     "WebserverPublicIP",
#     Description="Public IP for Webserver",
#     Value=GetAtt(Webserver, "PublicIp"),
# ))

# WebserverPublicURL = t.add_output(Output(
#     "WebserverPublicURL",
#     Description="Public URL for Webserver",
#     Value=Join("", ["http://", GetAtt(Webserver, "PublicIp")]),
# ))


print(t.to_json())

