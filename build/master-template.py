#/usr/bin/python env

from optparse import OptionParser
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
# from troposphere.ec2 import EIPAssociation
# from troposphere.ec2 import EIP
# from troposphere.ec2 import PortRange
# from troposphere.ec2 import Instance
from troposphere.ec2 import *


def usage():
    print "OPTIONS:"
    print "     -n  <number fo nics>. <1, 2, or 3>"
    print "     -l  license  <byol, util or bigiq>"
    print "     -s  stack  <full or existing>"
    print "USAGE: "
    print " ex. " + sys.argv[0] + " -n 1 -l byol -s create"
    print " ex. " + sys.argv[0] + " -n 2 -l bigiq -s existing"

def main():


    parser = OptionParser()
    parser.add_option("-n", "--nics", action="store", type="int", dest="num_nics", help="Number of nics: 1,2 or 3")
    parser.add_option("-l", "--license", action="store", type="string", dest="license_type", help="Type of License: byol, util or bigiq" )
    parser.add_option("-s", "--stack", action="store", type="string", dest="stack", help="Stack: create or existing" )
    (options, args) = parser.parse_args()



    t = Template()

    t.add_version("2010-09-09")


    if options.stack == "create":
        if options.num_nics == 1:
            t.add_description("""AWS CloudFormation Template for creating an a full stack with VPC, 4 subnets, 2nic BIG-IP and Bitnami webeserver LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template.""")
        elif options.num_nics == 2:
            t.add_description("""AWS CloudFormation Template for creating an a full stack with VPC, 4 subnets, 2nic BIG-IP and Bitnami webeserver LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template.""")
        elif options.num_nics == 3:
            t.add_description("""AWS CloudFormation Template for creating an a full stack with VPC, 4 subnets, 3nic BIG-IP and Bitnami webeserver LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template.""")
    elif options.stack == "existing":
        if options.num_nics == 1:
            t.add_description("""AWS CloudFormation Template for creating an 1nic Big-IP in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template.""")
        elif options.num_nics == 2:
            t.add_description("""AWS CloudFormation Template for creating an 2nic Big-IP in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template.""")
        elif options.num_nics == 3:
            t.add_description("""AWS CloudFormation Template for creating an 3nic Big-IP in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template.""")

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

    BigipInstanceType = t.add_parameter(Parameter(
        "BigipInstanceType",
        Default="m3.xlarge",
        ConstraintDescription="must be a valid Big-IP EC2 instance type",
        Type="String",
        Description="F5 BIG-IP Virtual Instance Type",
        AllowedValues=["m3.xlarge", "m3.2xlarge", "c1.medium", "c1.xlarge", "cc1.4xlarge", "cc2.8xlarge", "cg1.4xlarge"],
    ))

    BigipPerformanceType = t.add_parameter(Parameter(
        "BigipPerformanceType",
        Default="Good",
        ConstraintDescription="Must be a valid F5 Big-IP performance type",
        Type="String",
        Description="F5 Bigip Performance Type",
        AllowedValues=["Good", "Better", "Best"],
    ))

    BigipAdminUsername = t.add_parameter(Parameter(
        "BigipAdminUsername",
        Type="String",
        Description="Please enter your BIG-IP Admin Username",
        Default="admin",
        MinLength="1",
        MaxLength="255",
        ConstraintDescription="Please verify your BIG-IP Admin Username",
    ))

    BigipAdminPassword = t.add_parameter(Parameter(
        "BigipAdminPassword",
        Type="String",
        Description="Please enter your BIG-IP Admin Password",
        MinLength="1",
        NoEcho=True,
        MaxLength="255",
        ConstraintDescription="Please verify your BIG-IP Admin Password",
    ))

    if options.stack == "create":
        AvailabilityZone1 = t.add_parameter(Parameter(
            "AvailabilityZone1",
            Type="AWS::EC2::AvailabilityZone::Name",
            Description="Name of an Availability Zone in this Region",
        ))

        AvailabilityZone2 = t.add_parameter(Parameter(
            "AvailabilityZone2",
            Type="AWS::EC2::AvailabilityZone::Name",
            Description="Name of an Availability Zone in this Region",
        ))

    if options.stack == "existing":
        Vpc = t.add_parameter(Parameter(
            "Vpc",
            ConstraintDescription="Must be an existing VPC within working region.",
            Type="AWS::EC2::VPC::Id",
        ))

        Az1ExternalSubnet = t.add_parameter(Parameter(
            "Az1ExternalSubnet",
            ConstraintDescription="Must be subnet ID within existing VPC",
            Type="AWS::EC2::Subnet::Id",
            Description="Public or External subnet ID",
        ))
        BigipExternalSecurityGroup = t.add_parameter(Parameter(
            "BigipExternalSecurityGroup",
            ConstraintDescription="Must be security group ID within existing VPC",
            Type="AWS::EC2::SecurityGroup::Id",
            Description="Public or External Security Group ID",
        ))

        if options.num_nics > 1:
            Az1ManagementSubnet = t.add_parameter(Parameter(
                "Az1ManagementSubnet",
                ConstraintDescription="Must be subnet ID within existing VPC",
                Type="AWS::EC2::Subnet::Id",
                Description="Management Subnet ID",
            ))
            BigipManagementSecurityGroup = t.add_parameter(Parameter(
                "BigipManagementSecurityGroup",
                ConstraintDescription="Must be security group ID within existing VPC",
                Type="AWS::EC2::SecurityGroup::Id",
                Description="Bigip Management Security Group",
            ))
        if options.num_nics > 2:
            Az1InternalSubnet = t.add_parameter(Parameter(
                "Az1InternalSubnet",
                ConstraintDescription="Must be subnet ID within existing VPC",
                Type="AWS::EC2::Subnet::Id",
                Description="Private or Internal subnet ID",
            ))
            BigipInternalSecurityGroup = t.add_parameter(Parameter(
                "BigipInternalSecurityGroup",
                ConstraintDescription="Must be security group ID within existing VPC",
                Type="AWS::EC2::SecurityGroup::Id",
                Description="Private or Internal Security Group ID",
            ))

    if options.stack == "create":
        WebserverInstanceType = t.add_parameter(Parameter(
            "WebserverInstanceType",
            Default="t1.micro",
            ConstraintDescription="must be a valid EC2 instance type",
            Type="String",
            Description="Webserver EC2 instance type",
            AllowedValues=["t1.micro", "m3.medium", "m3.xlarge", "m2.xlarge", "m3.2xlarge", "c3.large", "c3.xlarge"],
        ))

    if options.stack == "existing":
        WebserverPrivateIp = t.add_parameter(Parameter(
            "WebserverPrivateIp",
            ConstraintDescription="Web Server IP used for Big-IP pool Member",
            Type="String",
            Description="Web Server IP used for Big-IP pool member",
        ))


    if options.num_nics == 1:
        BigipManagementGuiPort = t.add_parameter(Parameter(
            "BigipManagementGuiPort",
            Default="443",
            ConstraintDescription="Must be a valid, unusued port on BIG-IP.",
            Type="Number",
            Description="Port to use for the managment GUI",
        ))

    if options.license_type == "byol":
        BigipLicenseKey = t.add_parameter(Parameter(
            "BigipLicenseKey",
            Type="String",
            Description="Please enter your F5 BYOL regkey here:",
            MinLength="1",
            AllowedPattern="([\\x41-\\x5A][\\x41-\\x5A|\\x30-\\x39]{4})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{7})",
            MaxLength="255",
            ConstraintDescription="Please verify your F5 BYOL regkey.",
        ))

    if options.license_type == "bigiq":
        BigiqAddress = t.add_parameter(Parameter(
            "BigiqAddress",
            MinLength="1",
            ConstraintDescription="Please verify your BIG-IQ Hostname or IP",
            Type="String",
            Description="Please enter your BIG-IQ Hostname or IP",
            MaxLength="255",
        ))

        BigiqUsername = t.add_parameter(Parameter(
            "BigiqUsername",
            MinLength="1",
            ConstraintDescription="Please verify your BIG-IQ Username.",
            Type="String",
            Description="Please enter your BIG-IQ Username",
            MaxLength="255",
        ))

        BigiqPassword = t.add_parameter(Parameter(
            "BigiqPassword",
            Type="String",
            Description="Please enter your BIG-IQ Password",
            MinLength="1",
            NoEcho=True,
            MaxLength="255",
            ConstraintDescription="Please verify your BIG-IQ Password",
        ))

        BigiqLicensePoolUUID = t.add_parameter(Parameter(
            "BigiqLicensePoolUUID",
            MinLength="1",
            ConstraintDescription="Please verify your BIG-IQ License Pool UUID",
            Type="String",
            Description="Please enter your BIG-IQ License Pool UUID",
            MaxLength="255",
        ))



    ### BEGIN MAPPINGS
    if options.license_type != "util":
        t.add_mapping("BigipRegionMap",
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

    if options.stack == "create":
        t.add_mapping("AWSRegionArch2AMI",
        {u'ap-northeast-1': {u'AMI': u'ami-489b8049'},
         u'ap-southeast-1': {u'AMI': u'ami-0ad2f858'},
         u'eu-west-1': {u'AMI': u'ami-7dfc720a'},
         u'sa-east-1': {u'AMI': u'ami-6def5070'},
         u'us-east-1': {u'AMI': u'ami-00266568'},
         u'us-west-1': {u'AMI': u'ami-fc8b93b9'},
         u'us-west-2': {u'AMI': u'ami-71520941'}}
        )


    ### BEGIN RESOURCES
    if options.stack == "create":
        Vpc = t.add_resource(VPC(
            "Vpc",
            EnableDnsSupport="true",
            CidrBlock="10.0.0.0/16",
            EnableDnsHostnames="true",
            Tags=Tags(
                Name=Ref("AWS::StackId"),
                Application=Ref("AWS::StackId"),
            ),
        ))

        Az1ManagementSubnet = t.add_resource(Subnet(
            "Az1ManagementSubnet",
            Tags=Tags(
                Name="Az1 Management Subnet",
                Application=Ref("AWS::StackId"),
            ),
            VpcId=Ref(Vpc),
            CidrBlock="10.0.0.0/24",
            AvailabilityZone=Ref(AvailabilityZone1),
        ))

        Az2ManagementSubnet = t.add_resource(Subnet(
            "Az2ManagementSubnet",
            Tags=Tags(
                Name="Az2 Management Subnet",
                Application=Ref("AWS::StackId"),
            ),
            VpcId=Ref(Vpc),
            CidrBlock="10.0.10.0/24",
            AvailabilityZone=Ref(AvailabilityZone2),
        ))

        Az1ExternalSubnet = t.add_resource(Subnet(
            "Az1ExternalSubnet",
            Tags=Tags(
                Name="Az1 External Subnet",
                Application=Ref("AWS::StackId"),
            ),
            VpcId=Ref(Vpc),
            CidrBlock="10.0.1.0/24",
            AvailabilityZone=Ref(AvailabilityZone1),
        ))

        Az2ExternalSubnet = t.add_resource(Subnet(
            "Az2ExternalSubnet",
            Tags=Tags(
                Name="Az2 External Subnet",
                Application=Ref("AWS::StackId"),
            ),
            VpcId=Ref(Vpc),
            CidrBlock="10.0.11.0/24",
            AvailabilityZone=Ref(AvailabilityZone2),
        ))

        Az1InternalSubnet = t.add_resource(Subnet(
            "Az1InternalSubnet",
            Tags=Tags(
                Name="Az1 Internal Subnet",
                Application=Ref("AWS::StackId"),
            ),
            VpcId=Ref(Vpc),
            CidrBlock="10.0.2.0/24",
            AvailabilityZone=Ref(AvailabilityZone1),
        ))

        Az2InternalSubnet = t.add_resource(Subnet(
            "Az2InternalSubnet",
            Tags=Tags(
                Name="Az2 Internal Subnet",
                Application=Ref("AWS::StackId"),
            ),
            VpcId=Ref(Vpc),
            CidrBlock="10.0.12.0/24",
            AvailabilityZone=Ref(AvailabilityZone2),
        ))

        Az1ApplicationSubnet = t.add_resource(Subnet(
            "Az1ApplicationSubnet",
            Tags=Tags(
                Name="Az1 Application Subnet",
                Application=Ref("AWS::StackId"),
            ),
            VpcId=Ref(Vpc),
            CidrBlock="10.0.3.0/24",
            AvailabilityZone=Ref(AvailabilityZone1),
        ))

        Az2ApplicationSubnet = t.add_resource(Subnet(
            "Az2ApplicationSubnet",
            Tags=Tags(
                Name="Az2 Application Subnet",
                Application=Ref("AWS::StackId"),
            ),
            VpcId=Ref(Vpc),
            CidrBlock="10.0.13.0/24",
            AvailabilityZone=Ref(AvailabilityZone2),
        ))

        Igw = t.add_resource(InternetGateway(
            "InternetGateway",
            Tags=Tags(
                Application=Ref("AWS::StackId"),
            ),
        ))

        AttachGateway = t.add_resource(VPCGatewayAttachment(
            "AttachGateway",
            VpcId=Ref(Vpc),
            InternetGatewayId=Ref(Igw),
        ))

        ManagementRouteTable = t.add_resource(RouteTable(
            "ManagementRouteTable",
            VpcId=Ref(Vpc),
            Tags=Tags(
                Name="Management Route Table",
                Application=Ref("AWS::StackName"),
                Network="Mgmt",
            ),
        ))

        ExternalRouteTable = t.add_resource(RouteTable(
            "ExternalRouteTable",
            VpcId=Ref(Vpc),
            Tags=Tags(
                Name="External Route Table",
                Application=Ref("AWS::StackName"),
                Network="External",
            ),
        ))

        InternalRouteTable = t.add_resource(RouteTable(
            "InternalRouteTable",
            VpcId=Ref(Vpc),
            Tags=Tags(
                Name="Internal Route Table",
                Application=Ref("AWS::StackName"),
                Network="Internal",
            ),
        ))

        ApplicationRouteTable = t.add_resource(RouteTable(
            "ApplicationRouteTable",
            VpcId=Ref(Vpc),
            Tags=Tags(
                Name="Application Route Table",
                Application=Ref("AWS::StackName"),
                Network="Application",
            ),
        ))

        ManagementDefaultRoute = t.add_resource(Route(
            "ManagementDefaultRoute",
            GatewayId=Ref(Igw),
            DestinationCidrBlock="0.0.0.0/0",
            RouteTableId=Ref(ManagementRouteTable),
        ))

        ExternalDefaultRoute = t.add_resource(Route(
            "ExternalDefaultRoute",
            GatewayId=Ref(Igw),
            DestinationCidrBlock="0.0.0.0/0",
            RouteTableId=Ref(ExternalRouteTable),
        ))

        InternalDefaultRoute = t.add_resource(Route(
            "InternalDefaultRoute",
            GatewayId=Ref(Igw),
            DestinationCidrBlock="0.0.0.0/0",
            RouteTableId=Ref(InternalRouteTable),
        ))

        ApplicationDefaultRoute = t.add_resource(Route(
            "ApplicationDefaultRoute",
            GatewayId=Ref(Igw),
            DestinationCidrBlock="0.0.0.0/0",
            RouteTableId=Ref(ApplicationRouteTable),
        ))


        Az1ManagementSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
            "Az1ManagementSubnetRouteTableAssociation",
            SubnetId=Ref(Az1ManagementSubnet),
            RouteTableId=Ref(ManagementRouteTable),
        ))

        Az2ManagementSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
            "Az2ManagementSubnetRouteTableAssociation",
            SubnetId=Ref(Az2ManagementSubnet),
            RouteTableId=Ref(ManagementRouteTable),
        ))

        Az1ExternalSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
            "Az1ExternalSubnetRouteTableAssociation",
            SubnetId=Ref(Az1ExternalSubnet),
            RouteTableId=Ref(ExternalRouteTable),
        ))

        Az2ExternalSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
            "Az2ExternalSubnetRouteTableAssociation",
            SubnetId=Ref(Az2ExternalSubnet),
            RouteTableId=Ref(ExternalRouteTable),
        ))

        Az1InternalSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
            "Az1InternalSubnetRouteTableAssociation",
            SubnetId=Ref(Az1InternalSubnet),
            RouteTableId=Ref(InternalRouteTable),
        ))

        Az2InternalSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
            "Az2InternalSubnetRouteTableAssociation",
            SubnetId=Ref(Az2InternalSubnet),
            RouteTableId=Ref(InternalRouteTable),
        ))

        Az1ApplicationSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
            "Az1ApplicationSubnetRouteTableAssociation",
            SubnetId=Ref(Az1ApplicationSubnet),
            RouteTableId=Ref(ApplicationRouteTable),
        ))

        Az2ApplicationSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
            "Az2ApplicationSubnetRouteTableAssociation",
            SubnetId=Ref(Az2ApplicationSubnet),
            RouteTableId=Ref(ApplicationRouteTable),
        ))

        # 1 Nic has consolidated rules
        if options.num_nics == 1:

            BigipExternalSecurityGroup = t.add_resource(SecurityGroup(
                "BigipExternalSecurityGroup",
                SecurityGroupIngress=[
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="22",
                                ToPort="22",
                                CidrIp=Ref(SSHLocation),
                    ),
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort=Ref(BigipManagementGuiPort),
                                ToPort=Ref(BigipManagementGuiPort),
                                CidrIp=Ref(SSHLocation),
                    ),
                    SecurityGroupRule(
                                IpProtocol="icmp",
                                FromPort="-1",
                                ToPort="-1",
                                CidrIp=Ref(SSHLocation),
                    ),         
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="80",
                                ToPort="80",
                                CidrIp="0.0.0.0/0",
                    ),
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="443",
                                ToPort="443",
                                CidrIp="0.0.0.0/0",
                    ),
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="4353",
                                ToPort="4353",
                                CidrIp="0.0.0.0/0",
                    ),
                    SecurityGroupRule(
                                IpProtocol="udp",
                                FromPort="1026",
                                ToPort="1026",
                                CidrIp="10.0.0.0/16",
                    ), 
                ],
                VpcId=Ref(Vpc),
                GroupDescription="Public or External interface rules",
                Tags=Tags(
                    Name=Join("", ["Bigip Security Group: ", Ref("AWS::StackName")] ),
                    Application=Ref("AWS::StackName"),
                ),
            ))

        if options.num_nics > 1:

            BigipManagementSecurityGroup = t.add_resource(SecurityGroup(
                "BigipManagementSecurityGroup",
                SecurityGroupIngress=[
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="22",
                                ToPort="22",
                                CidrIp=Ref(SSHLocation),
                    ),
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="443",
                                ToPort="443",
                                CidrIp=Ref(SSHLocation),
                    ),
                    SecurityGroupRule(
                                IpProtocol="icmp",
                                FromPort="-1",
                                ToPort="-1",
                                CidrIp=Ref(SSHLocation),
                    ),
                ],
                VpcId=Ref(Vpc),
                GroupDescription="Big-IP Management UI rules",
                Tags=Tags(
                    Name="Bigip Management Security Group",
                    Application=Ref("AWS::StackName"),
                ),
            ))

            BigipExternalSecurityGroup = t.add_resource(SecurityGroup(
                "BigipExternalSecurityGroup",
                SecurityGroupIngress=[
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="80",
                                ToPort="80",
                                CidrIp="0.0.0.0/0",
                    ),
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="443",
                                ToPort="443",
                                CidrIp="0.0.0.0/0",
                    ),
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="4353",
                                ToPort="4353",
                                CidrIp="0.0.0.0/0",
                    ),
                    SecurityGroupRule(
                                IpProtocol="udp",
                                FromPort="1026",
                                ToPort="1026",
                                CidrIp="10.0.0.0/16",
                    ),
                ],
                VpcId=Ref(Vpc),
                GroupDescription="Public or External interface rules",
                Tags=Tags(
                    Name="Bigip External Security Group",
                    Application=Ref("AWS::StackName"),
                ),
            ))

        # If a 3 nic with additional Internal interface.
        if options.num_nics > 2:

            BigipInternalSecurityGroup = t.add_resource(SecurityGroup(
                "BigipInternalSecurityGroup",
                SecurityGroupIngress=[
                    SecurityGroupRule(
                                IpProtocol="-1",
                                FromPort="-1",
                                ToPort="-1",
                                CidrIp="10.0.0.0/16",
                    ),
                ],
                VpcId=Ref(Vpc),
                GroupDescription="Allow All from Intra-VPC only",
                Tags=Tags(
                    Name="Bigip Internal Security Group",
                    Application=Ref("AWS::StackName"),
                ),
            ))


        WebserverSecurityGroup = t.add_resource(SecurityGroup(
            "WebserverSecurityGroup",
            SecurityGroupIngress=[
                SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort="22",
                            ToPort="22",
                            CidrIp="0.0.0.0/0",
                ),
                SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort="80",
                            ToPort="80",
                            CidrIp="0.0.0.0/0",
                ),
                SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort="443",
                            ToPort="443",
                            CidrIp="0.0.0.0/0",
                ),
                SecurityGroupRule(
                            IpProtocol="icmp",
                            FromPort="-1",
                            ToPort="-1",
                            CidrIp="0.0.0.0/0",
                ),
            ],
            VpcId=Ref(Vpc),
            GroupDescription="Enable Access to Webserver",
            Tags=Tags(
                Name="Webserver Security Group",
                Application=Ref("AWS::StackName"),
            ),
        ))

    # External Interface is true on 1nic,2nic,3nic,etc.    
    ExternalInterface = t.add_resource(NetworkInterface(
        "ExternalInterface",
        SubnetId=Ref(Az1ExternalSubnet),
        GroupSet=[Ref(BigipExternalSecurityGroup)],
        Description="Public External Interface for the Bigip",
        SecondaryPrivateIpAddressCount="1",
    ))

    # Need to figure out optimal "Depends On" for EIP config.
    # Won't build with it and won't teardown cleanly without it. 
    # Deletes always fail with:
    # "AWS::EC2::VPCGatewayAttachment  AttachGateway   Network vpc-a2be80c6 has some mapped public address(es). Please unmap those public address(es) before detaching the gateway.
    # Workaround is to manually detach/destroy Internet Gateway and retry deleting stack

    ExternalSelfEipAddress = t.add_resource(EIP(
        "ExternalSelfEipAddress",
        #DependsOn="AttachGateway",
        Domain="vpc",
    ))

    ExternalSelfEipAssociation = t.add_resource(EIPAssociation(
        "ExternalSelfEipAssociation",
        NetworkInterfaceId=Ref(ExternalInterface),
        AllocationId=GetAtt(ExternalSelfEipAddress, "AllocationId"),
        PrivateIpAddress=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
    ))
 
    if options.num_nics > 1:

        VipEipAddress = t.add_resource(EIP(
            "VipEipAddress",
            #DependsOn="AttachGateway",
            Domain="vpc",
        ))

        VipEipAssociation = t.add_resource(EIPAssociation(
            "VipEipAssociation",
            NetworkInterfaceId=Ref(ExternalInterface),
            AllocationId=GetAtt(VipEipAddress, "AllocationId"),
            PrivateIpAddress=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
        ))


        ManagementInterface = t.add_resource(NetworkInterface(
            "ManagementInterface",
            SubnetId=Ref(Az1ManagementSubnet),
            GroupSet=[Ref(BigipManagementSecurityGroup)],
            Description="Management Interface for the Bigip",
        ))

        ManagementEipAddress = t.add_resource(EIP(
            "ManagementEipAddress",
            #DependsOn="AttachGateway",
            Domain="vpc",
        ))

        ManagementEipAssociation = t.add_resource(EIPAssociation(
            "ManagementEipAssociation",
            NetworkInterfaceId=Ref(ManagementInterface),
            AllocationId=GetAtt(ManagementEipAddress, "AllocationId"),
        ))

        if options.num_nics > 2:
            InternalInterface = t.add_resource(NetworkInterface(
                "InternalInterface",
                SubnetId=Ref(Az1InternalSubnet),
                GroupSet=[Ref(BigipInternalSecurityGroup)],
                Description="Internal Interface for the Bigip",
            ))

    if options.stack == "create":

        Webserver = t.add_resource(Instance(
            "Webserver",
            UserData=Base64(Join("", ["#!/bin/bash -x\n", "echo \"Hello World\"\n"])),
            Tags=Tags(
                Name="Webserver",
                Application=Ref("AWS::StackName"),
            ),
            ImageId=FindInMap("AWSRegionArch2AMI", Ref("AWS::Region"), "AMI"),
            KeyName=Ref(KeyName),
            InstanceType=Ref(WebserverInstanceType),
            NetworkInterfaces=[
            NetworkInterfaceProperty(
                SubnetId=Ref(Az1ApplicationSubnet),
                DeviceIndex="0",
                GroupSet=[Ref(WebserverSecurityGroup)],
                Description=Join("", [Ref("AWS::StackName"), " Webserver Network Interface"]),
                AssociatePublicIpAddress="true",
            ),
            ],
        ))

    # Build firstrun config
    firstrun_config = []

    firstrun_config += [
                            "#!/bin/bash\n", 
                            "HOSTNAME=`curl http://169.254.169.254/latest/meta-data/hostname`\n", 
                            "TZ='America/Los_Angeles'\n", 
                            "BIGIP_ADMIN_USERNAME='", Ref(BigipAdminUsername), "'\n", 
                            "BIGIP_ADMIN_PASSWORD='", Ref(BigipAdminPassword), "'\n", 
                            "APPNAME='demo-app-1'\n", 
                            "VIRTUALSERVERPORT=80\n",
                            "CRT='default.crt'\n", 
                            "KEY='default.key'\n",
                        ]

    if options.stack == "create":
        firstrun_config +=  [              
                            "POOLMEM='", GetAtt('Webserver','PrivateIp'), "'\n", 
                            "POOLMEMPORT=80\n", 
                            ]
    elif options.stack == "existing":
        firstrun_config +=  [ 
                            "POOLMEM='", Ref(WebserverPrivateIp), "'\n", 
                            "POOLMEMPORT=80\n", 
                            ]         


    if options.num_nics == 1:
        firstrun_config += [ "MANAGEMENT_GUI_PORT='", Ref(BigipManagementGuiPort), "'\n", ] 
    if options.num_nics > 1:
        firstrun_config += [ 
                            "MGMTIP='", GetAtt("ManagementInterface", "PrimaryPrivateIpAddress"), "'\n", 
                            "EXTIP='", GetAtt("ExternalInterface", "PrimaryPrivateIpAddress"), "'\n", 
                            "EXTPRIVIP='", Select("0", GetAtt("ExternalInterface", "SecondaryPrivateIpAddresses")), "'\n", 
                            "EXTMASK='24'\n" 
                            ]
    if options.num_nics > 2:
        firstrun_config += [ 
                            "INTIP='",GetAtt("InternalInterface", "PrimaryPrivateIpAddress"),"'\n",
                            "INTMASK='24'\n", 
                           ]


    if options.license_type == "byol":
        firstrun_config += [ "REGKEY='", Ref(BigipLicenseKey), "'\n" ]
    elif options.license_type == "bigiq":
        firstrun_config += [ 
                            "BIGIQ_ADDRESS='", Ref(BigiqAddress), "'\n",
                            "BIGIQ_USERNAME='", Ref(BigiqUsername), "'\n",
                            "BIGIQ_PASSWORD='", Ref(BigiqPassword), "'\n",
                            "BIGIQ_LICENSE_POOL_UUID='", Ref(BigiqLicensePoolUUID), "'\n"
                           ]

        if options.num_nics == 1:
            firstrun_config += [ "BIGIP_DEVICE_ADDRESS='", Ref(ExternalSelfEipAddress),"'\n" ] 
        if options.num_nics > 1:
            firstrun_config += [ "BIGIP_DEVICE_ADDRESS='", Ref(ManagementEipAddress),"'\n" ] 


    # build firstrun.sh vars

    checkF5Ready =  [
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
                    ]

    license_byol =  [ 
                        "tmsh install /sys license registration-key ${REGKEY}\n" 
                    ]

    license_from_bigiq =  [                    
                        "### BEGIN BIGIQ LICENSE ###\n",
                        "declare -i i\n",
                        "i=0\n",
                        "while ([ -z \"${MACHINE_STATE}\" ] || [ \"${MACHINE_STATE}\" == \"null\" ]);\n",
                        "do\n",
                        "     logger -p local0.info \"license_from_bigiq_debug: Attempting to register the BIGIP: ${BIGIP_DEVICE_ADDRESS} with BIGIQ: ${BIGIQ_ADDRESS}\"\n",
                        "     curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} -o /tmp/add-managed-device-output.json --max-time 15  -H \"Content-Type: application/json\" -X POST -d '{\"deviceAddress\": \"'${BIGIP_DEVICE_ADDRESS}'\", \"username\":\"'${BIGIP_ADMIN_USERNAME}'\", \"password\":\"'${BIGIP_ADMIN_PASSWORD}'\", \"automaticallyUpdateFramework\":\"true\", \"rootUsername\":\"root\", \"rootPassword\":\"'${BIGIP_ROOT_PASSWORD}'\"}' https://${BIGIQ_ADDRESS}/mgmt/cm/cloud/managed-devices\n",
                        "     MACHINE_ID=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .machineId`\n",
                        "     MACHINE_SELFLINK=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .selfLink`\n",
                        "     MACHINE_STATE=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .state`\n",
                        "     MACHINE_CODE=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .code`\n",
                        "     MACHINE_MESSAGE=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .message`\n",
                        "     if [ $i == 10 ]; then\n",
                        "         logger -p local0.err \"license_from_bigiq_debug: EXITING - Could not register the device. CODE: ${MACHINE_CODE}, MESSAGE: ${MACHINE_MESSAGE}\"\n",
                        "         exit 1\n",
                        "    fi\n",
                        "    i=$i+1\n",
                        "    sleep 10\n",
                        "done\n",
                        "i=0\n",
                        "while [ \"${MACHINE_STATE}\" != \"ACTIVE\" ];\n",
                        "do \n",
                        "     MACHINE_STATE=$( curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} --max-time 15 -H \"Content-Type: application/json\" -X GET https://${BIGIQ_ADDRESS}/mgmt/cm/cloud/managed-devices/${MACHINE_ID} | /usr/bin/jq -r .state )\n",
                        "     if [ $i == 30 ] && [ \"${MACHINE_STATE}\" != \"ACTIVE\" ]; then\n",
                        "       logger -p local0.err \"license_from_bigiq_debug: ABORT! Taking too long to register this BIGIP with BIGIQ.\"\n",
                        "       exit 1\n",
                        "     fi\n",
                        "     i=$i+1\n",
                        "     logger -p local0.info \"license_from_bigiq_debug: Machine State: ${MACHINE_STATE}...\"\n",
                        "     sleep 30\n",
                        "done\n",
                        "# Install License From Pool\n",
                        "i=0\n",
                        "while ( [ -z \"$LICENSE_STATE\" ] || [ \"${LICENSE_STATE}\" == \"null\" ] );\n",
                        "do\n",
                        "     logger -p local0.info \"license_from_bigiq_debug: Attempting to get license BIG-IP: ${MACHINE_ID} from license pool: ${BIGIQ_LICENSE_POOL_UUID}\"\n",
                        "     curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} -o /tmp/install-license-output.json --max-time 15  -H \"Content-Type: application/json\" -X POST -d '{\"deviceReference\":{\"link\": \"'${MACHINE_SELFLINK}'\"}}' https://${BIGIQ_ADDRESS}/mgmt/cm/shared/licensing/pools/${BIGIQ_LICENSE_POOL_UUID}/members\n",
                        "     LICENSE_UUID=`cat /tmp/install-license-output.json | /usr/bin/jq -r .uuid`\n",
                        "     LICENSE_STATE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .state`\n",
                        "     LICENSE_CODE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .code`\n",
                        "     LICENSE_MESSAGE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .message`\n",
                        "     if [ $i == 5 ]; then\n",
                        "       logger -p local0.err \"license_from_bigiq_debug: EXITING, could not license the device. CODE: ${LICENSE_CODE}, MESSAGE: ${LICENSE_MESSAGE}\"\n",
                        "       exit 1\n",
                        "     fi\n",
                        "     i=$i+1\n",
                        "     sleep 10\n",
                        "done\n",
                        "i=0\n",
                        "while [ \"${LICENSE_STATE}\" != \"LICENSED\" ];\n",
                        "do\n",
                        "     LICENSE_STATE=$( curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} --max-time 15 -H \"Content-Type: application/json\" -X GET https://${BIGIQ_ADDRESS}/mgmt/cm/shared/licensing/pools/${BIGIQ_LICENSE_POOL_UUID}/members/${LICENSE_UUID} | /usr/bin/jq -r .state )\n",
                        "     if [ \"${LICENSE_STATE}\" == \"INSTALL\" ] ; then\n",
                        "       sleep 5\n",
                        "       continue\n",
                        "     fi\n",
                        "     if [ $i == 5 ] && [ \"${LICENSE_STATE}\" != \"LICENSED\" ]; then\n",
                        "       logger -p local0.info \"license_from_bigiq_debug: BIGIP node not moving to 'LICENSED' state\"\n",
                        "       exit 1\n",
                        "     fi\n",
                        "     i=$i+1\n",
                        "     logger -p local0.info \"license_from_bigiq_debug: License Status: ${LICENSE_STATE}...\"\n",
                        "     sleep 10\n",
                        "done\n",
                        "### END BIGIQ LICENSE ###\n",
                        ]

    # begin building firstrun.sh
    firstrun_sh = [] 

    firstrun_sh +=  [ 
                        "#!/bin/bash\n",
                        ". /tmp/firstrun.config\n",
                        "FILE=/tmp/firstrun.log\n",
                    ]

    firstrun_sh += checkF5Ready

    firstrun_sh += [
                        "tmsh modify /sys global-settings hostname ${HOSTNAME}\n",
                        "tmsh mv cm device bigip1 ${HOSTNAME}\n",
                        "tmsh modify auth password root <<< $'${BIGIP_ADMIN_PASSWORD}\n${BIGIP_ADMIN_PASSWORD}\n'\n",
                        "tmsh modify auth user admin password \"'${BIGIP_ADMIN_PASSWORD}'\"\n",
                        "tmsh save /sys config\n",
                    ]

    if options.license_type == "byol":
        firstrun_sh += license_byol
    elif options.license_type == "bigiq":
        firstrun_sh += license_from_bigiq

    # Global
    firstrun_sh += [ 
                        "checkStatusnoret\n",
                        "sleep 30\n",
                        "tmsh save /sys config\n",
                        "tmsh modify sys db dhclient.mgmt { value disable }\n",
                        "tmsh modify sys ntp timezone ${TZ}\n",
                        "tmsh modify sys ntp servers add { 0.pool.ntp.org 1.pool.ntp.org }\n",
                        "tmsh modify sys global-settings gui-setup disabled\n",
                        "checkStatusnoret\n",
                    ]

    if options.num_nics == 1:
        firstrun_sh +=  [
                        "tmsh modify sys httpd ssl-port ${MANAGEMENT_GUI_PORT}\n",
                        "tmsh modify net self-allow defaults add { tcp:${MANAGEMENT_GUI_PORT} }\n",
                        ] 

    if options.num_nics > 1:
        firstrun_sh +=  [ 
                        "tmsh create net vlan external interfaces add { 1.1 } \n",
                        "tmsh create net self ${EXTIP}/${EXTMASK} vlan external allow-service add { tcp:4353 udp:1026 }\n",
                        "tmsh create net route default gw 10.0.1.1\n",
                        ]
    if options.num_nics > 2:
        firstrun_sh +=  [ 
                        "tmsh create net vlan internal interfaces add { 1.2 } \n",
                        "tmsh create net self ${INTIP}/${INTMASK} vlan internal allow-service default\n",
                        ]

    firstrun_sh += [
                        "tmsh save /sys config\n",
                        "checkStatusnoret\n",
                   ]

    # Add virtual service
    if options.num_nics == 1:
        firstrun_sh +=  [
                        "tmsh create ltm pool ${APPNAME}-pool members add { ${POOLMEM}:${POOLMEMPORT} } monitor http\n",
                        "tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination 0.0.0.0:${VIRTUALSERVERPORT} ip-protocol tcp mask any pool /Common/${APPNAME}-pool source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\n",
                        ]

    if options.num_nics > 1:
        firstrun_sh +=  [
                        "tmsh create ltm pool ${APPNAME}-pool members add { ${POOLMEM}:${POOLMEMPORT} } monitor http\n",
                        "tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} ip-protocol tcp mask 255.255.255.255 pool /Common/${APPNAME}-pool source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\n",
                        ]
    firstrun_sh += [
                        "tmsh save /sys config\n"
                   ]

    metadata = Metadata(
            Init({
                'config': InitConfig(
                    files=InitFiles(
                        {
                            '/tmp/firstrun.config': InitFile(
                                content=Join('', firstrun_config ),
                                mode='000777',
                                owner='root',
                                group='root'
                            ),
                            '/tmp/firstrun.sh': InitFile(
                                content=Join('', firstrun_sh ),
                                mode='000777',
                                owner='root',
                                group='root'
                            )
                        } 
                    ),
                    commands={
                               "b-configure-Bigip" : {
                                    "command" : "/tmp/firstrun.sh\n"
                                }
                    }
                ) 
            })
        )

    NetworkInterfaces = []

    if options.num_nics == 1:
        NetworkInterfaces = [
            NetworkInterfaceProperty(
                DeviceIndex="0",
                NetworkInterfaceId=Ref(ExternalInterface),
                Description="Public or External Interface",
            ),
        ]

    if options.num_nics == 2:  
        NetworkInterfaces = [
            NetworkInterfaceProperty(
                DeviceIndex="0",
                NetworkInterfaceId=Ref(ManagementInterface),
                Description="Management Interface",
            ),
            NetworkInterfaceProperty(
                DeviceIndex="1",
                NetworkInterfaceId=Ref(ExternalInterface),
                Description="Public or External Interface",
            ),    
        ]

    if options.num_nics == 3:  
        NetworkInterfaces = [
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
        ]


    BigipInstance = t.add_resource(Instance(
        "BigipInstance",
        Metadata=metadata,
        UserData=Base64(Join("", ["#!/bin/bash\n", "/opt/aws/apitools/cfn-init-1.4-0.amzn1/bin/cfn-init -v -s ", Ref("AWS::StackId"), " -r BigipInstance ", " --region ", Ref("AWS::Region"), "\n"])),
        Tags=Tags(
            Name=Join("", ["Big-IP: ", Ref("AWS::StackName")] ),
            Application=Ref("AWS::StackName"),
        ),
        ImageId=FindInMap("BigipRegionMap", Ref("AWS::Region"), Ref(BigipPerformanceType)),
        KeyName=Ref(KeyName),
        InstanceType=Ref(BigipInstanceType),
        NetworkInterfaces=NetworkInterfaces
    ))

    ### BEGIN OUTPUT

    if options.stack == "create":
        Vpc = t.add_output(Output(
            "Vpc",
            Description="VPC ID",
            Value=Ref(Vpc),
        ))

        AvailabilityZone = t.add_output(Output(
            "AvailabilityZone",
            Description="Availability Zone",
            Value=GetAtt(BigipInstance, "AvailabilityZone"),
        ))

        Az1ManagementSubnet = t.add_output(Output(
            "Az1ManagementSubnet",
            Description="Az1 Management Subnet Id",
            Value=Ref(Az1ManagementSubnet),
        ))

        Az2ManagementSubnet = t.add_output(Output(
            "Az2ManagementSubnet",
            Description="Az2 Management Subnet Id",
            Value=Ref(Az2ManagementSubnet),
        ))

        Az1ExternalSubnet = t.add_output(Output(
            "Az1ExternalSubnet",
            Description="Az1 Public or External Subnet Id",
            Value=Ref(Az1ExternalSubnet),
        ))

        Az2ExternalSubnet = t.add_output(Output(
            "Az2ExternalSubnet",
            Description="Az2 Public or External Subnet Id",
            Value=Ref(Az2ExternalSubnet),
        ))

        Az1InternalSubnet = t.add_output(Output(
            "Az1InternalSubnet",
            Description="Az1 Private or Internal Subnet Id",
            Value=Ref(Az1InternalSubnet),
        ))

        Az2InternalSubnet = t.add_output(Output(
            "Az2InternalSubnet",
            Description="Az2 Private or Internal Subnet Id",
            Value=Ref(Az2InternalSubnet),
        ))

        Az1ApplicationSubnet = t.add_output(Output(
            "Az1ApplicationSubnet",
            Description="Az1 Application Subnet Id",
            Value=Ref(Az1ApplicationSubnet),
        ))

        Az2ApplicationSubnet = t.add_output(Output(
            "Az2ApplicationSubnet",
            Description="Az2 Application Subnet Id",
            Value=Ref(Az1ApplicationSubnet),
        ))

    BigipInstanceId = t.add_output(Output(
        "BigipInstanceId",
        Description="Instance Id of Big-IP in Amazon",
        Value=Ref(BigipInstance),
    ))

    BigipExternalSecurityGroup = t.add_output(Output(
        "BigipExternalSecurityGroup",
        Description="Public or External Security Group",
        Value=Ref(BigipExternalSecurityGroup),
    ))

    ExternalInterface = t.add_output(Output(
        "ExternalInterface",
        Description="External interface Id on BIG-Ip",
        Value=Ref(ExternalInterface),
    ))

    ExternalInterfacePrivateIp = t.add_output(Output(
        "ExternalInterfacePrivateIp",
        Description="Internally routable Ip of public interface on BIG-Ip",
        Value=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
    ))

    ExternalSelfEipAddress = t.add_output(Output(
        "ExternalSelfEipAddress",
        Description="IP Address of External interface attached to BIG-IP",
        Value=Ref(ExternalSelfEipAddress),
    ))

    if options.num_nics == 1:

        BigipUrl = t.add_output(Output(
            "BigipUrl",
            Description="Big-IP Management GUI",
            Value=Join("", [ "https://", GetAtt(BigipInstance, "PublicIp"), ":", Ref(BigipManagementGuiPort) ]),
        ))

    if options.num_nics > 1:

        BigipUrl = t.add_output(Output(
            "BigipUrl",
            Description="Big-IP Management GUI",
            Value=Join("", ["https://", GetAtt(BigipInstance, "PublicIp")]),
        ))

        BigipManagementSecurityGroup = t.add_output(Output(
            "BigipManagementSecurityGroup",
            Description="Management Security Group",
            Value=Ref(BigipManagementSecurityGroup),
        ))

        ManagementInterface = t.add_output(Output(
            "ManagementInterface",
            Description="Management interface Id on BIG-Ip",
            Value=Ref(ManagementInterface),
        ))

        ManagementInterfacePrivateIp = t.add_output(Output(
            "ManagementInterfacePrivateIp",
            Description="Internally routable Ip of management interface on BIG-Ip",
            Value=GetAtt(ManagementInterface, "PrimaryPrivateIpAddress"),
        ))

        ManagementEipAddress = t.add_output(Output(
            "ManagementEipAddress",
            Description="Ip address of management port on BIG-Ip",
            Value=Ref(ManagementEipAddress),
        ))

        VipPrivateIp = t.add_output(Output(
            "VipPrivateIp",
            Description="VIP on External Interface Secondary IP 1",
            Value=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
        ))

        VipEipAddress = t.add_output(Output(
            "VipEipAddress",
            Description="EIP address for VIP",
            Value=Join("", ["http://", Ref(VipEipAddress), ":80"]),
        ))

    if options.num_nics > 2:
        BigipInternalSecurityGroup = t.add_output(Output(
            "BigipInternalSecurityGroup",
            Description="Private or Internal Security Group",
            Value=Ref(BigipInternalSecurityGroup),
        ))

        InternalInterface = t.add_output(Output(
            "InternalInterface",
            Description="Internal interface ID on BIG-IP",
            Value=Ref(InternalInterface),
        ))

        InternalInterfacePrivateIp = t.add_output(Output(
            "InternalInterfacePrivateIp",
            Description="Internally routable IP of internal interface on BIG-IP",
            Value=GetAtt(InternalInterface, "PrimaryPrivateIpAddress"),
        ))

    if options.stack == "create":
        WebserverPrivateIp = t.add_output(Output(
            "WebserverPrivateIp",
            Description="Private Ip for Webserver",
            Value=GetAtt(Webserver, "PrivateIp"),
        ))

        WebserverPublicIp = t.add_output(Output(
            "WebserverPublicIp",
            Description="Public Ip for Webserver",
            Value=GetAtt(Webserver, "PublicIp"),
        ))

        WebserverPublicUrl = t.add_output(Output(
            "WebserverPublicUrl",
            Description="Public Url for Webserver",
            Value=Join("", ["http://", GetAtt(Webserver, "PublicIp")]),
        ))

    print(t.to_json())

if __name__ == "__main__":
    main()
