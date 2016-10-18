#/usr/bin/python env

from optparse import OptionParser
import json
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
    print "     -s  stack  <network, security_groups, infra, full or existing>"
    print "     -a  <number of AvailabilityZones>"
    print "     -b  <number of Big-IPs>"
    print "     -n  <number fo nics>. <1, 2, or 3>"
    print "     -l  license  <byol, hourly or bigiq>"
    print "     -c  components <waf, autoscale, etc.>"
    print "     -H  ha-type <standalone, same-az, across-az>"
    print "USAGE: "
    print " ex. " + sys.argv[0] + " -s network -n 1"
    print " ex. " + sys.argv[0] + " -s network -n 2 -a 2"
    print " ex. " + sys.argv[0] + " -s security_groups -n 2"
    print " ex. " + sys.argv[0] + " -s infra -n 2"
    print " ex. " + sys.argv[0] + " -s full -n 1 -l byol"
    print " ex. " + sys.argv[0] + " -s existing -n 2 -l bigiq"
    print " ex. " + sys.argv[0] + " -s existing -n 2 -l bigiq -c waf -H across-az"

def main():

    # RFE: Use Metadata / AWS::CloudFormation::Interface/  "ParameterGroups"
    # to clean up Presentation Layer

    PARAMETERS = {}
    MAPPINGS = {}
    RESOURCES = {}
    OUTPUTS = {}

    parser = OptionParser()
    parser.add_option("-s", "--stack", action="store", type="string", dest="stack", help="Stack: network, security_groups, infra, full or existing" )
    parser.add_option("-a", "--num-azs", action="store", type="int", dest="num_azs", default=1, help="Number of Availability Zones" )
    parser.add_option("-b", "--num-bigips", action="store", type="int", dest="num_bigips", default=1, help="Number of Bigips" )
    parser.add_option("-n", "--nics", action="store", type="int", dest="num_nics", default=1, help="Number of nics: 1,2 or 3")
    parser.add_option("-l", "--license", action="store", type="string", dest="license_type", default="hourly", help="Type of License: hourly, byol or bigiq" )
    parser.add_option("-c", "--components", action="store", type="string", dest="components", help="Comma seperated list of components: ex. waf" )
    parser.add_option("-H", "--ha-type", action="store", type="string", dest="ha_type", default="standalone", help="Ha Type: standalone, same-az, across-az" )

    (options, args) = parser.parse_args()


    num_nics = options.num_nics
    license_type = options.license_type
    stack = options.stack
    num_bigips = options.num_bigips
    ha_type = options.ha_type
    num_azs = options.num_azs

    # 1st BIG-IP will always be cluster seed
    CLUSTER_SEED = 1

    # May need to include AWS Creds for various deployments: cluster, auto-scale, etc.
    aws_creds = False 

    if ha_type == "same-az":
        num_azs = 1
        num_bigips = 2
        aws_creds = True

    # num AZs for Across AZ fixed for now. Limited to HA-Pairs
    if ha_type == "across-az":
        num_azs = 2
        num_bigips = 2
        aws_creds = True

    # Not Implemented. Fixed for now
    num_bigips_per_az = 1

    # Note, waf is only component right now
    components = {}
    if options.components:
        for component in options.components.split(','):
            components[component] = True

    network = False
    security_groups = False
    webserver = False
    bigip = False

    if stack == "network":
        network = True
        security_groups = False
        webserver = False
        bigip = False

    if stack == "security_groups":
        network = False
        security_groups = True
        webserver = False
        bigip = False

    if stack == "infra":
        network = True
        security_groups = True
        webserver = True
        bigip = False

    if stack == "full":
        network = True
        security_groups = True
        webserver = True
        bigip = True

    if stack == "existing":
        network = False
        security_groups = False
        webserver = False
        bigip = True


    # Begin Template
    t = Template()

    t.add_version("2010-09-09")

    description = ""
    if stack == "network":
        description = "AWS CloudFormation Template for creating network components for a " + str(num_azs) + " Availability Zone VPC"
    elif stack == "security_groups":
        description = "AWS CloudFormation Template for creating security groups for a " + str(num_nics) + "nic BIG-IP"
    elif stack == "infra":
        description = "AWS CloudFormation Template for creating a " + str(num_azs) + " Availability Zone VPC, subnets, security groups and a webserver (Bitnami LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
    elif stack == "full":
        if ha_type == "standalone":
            description = "AWS CloudFormation Template for creating a full stack with a " + str(num_nics) + "nic BIG-IP, a " + str(num_azs) + " Availability Zone VPC, subnets, security groups and a webeserver (Bitnami LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
        if ha_type == "same-az":
            description = "AWS CloudFormation Template for creating a full stack with a Same-AZ cluster of " + str(num_nics) + "nic BIG-IPs, a " + str(num_azs) + " Availability Zone VPC, subnets, security groups and a webeserver (Bitnami LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
        if ha_type == "across-az":
            description = "AWS CloudFormation Template for creating a full stack with a Across-AZs cluster of " + str(num_nics) + "nic BIG-IPs, a " + str(num_azs) + " Availability Zone VPC, subnets, security groups and a webeserver (Bitnami LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
    elif stack == "existing":
        if ha_type == "standalone":
            description = "AWS CloudFormation Template for creating a " + str(num_nics) + "nic Big-IP in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
        if ha_type == "same-az":
            description = "AWS CloudFormation Template for creating a Same-AZ cluster of " + str(num_nics) + "nic Big-IPs in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
        if ha_type == "across-az":
            description = "AWS CloudFormation Template for creating a Across-AZs cluster of " + str(num_nics) + "nic Big-IPs in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."

    t.add_description(description)

    ### BEGIN PARAMETERS

    if stack != "network": 
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

    if stack != "network" and stack != "security_groups":
        KeyName = t.add_parameter(Parameter(
            "KeyName",
            Type="AWS::EC2::KeyPair::KeyName",
            Description="Name of an existing EC2 KeyPair to enable SSH access to the instance",
        ))


    if network == True:

        for INDEX in range(num_azs):
            AvailabilityZone = "AvailabilityZone" + str(INDEX + 1)
            PARAMETERS[AvailabilityZone] = t.add_parameter(Parameter(
                AvailabilityZone,
            Type="AWS::EC2::AvailabilityZone::Name",
            Description="Name of an Availability Zone in this Region",
        ))

    if webserver == True:
        WebserverInstanceType = t.add_parameter(Parameter(
            "WebserverInstanceType",
            Default="t1.micro",
            ConstraintDescription="must be a valid EC2 instance type",
            Type="String",
            Description="Webserver EC2 instance type",
            AllowedValues=["t1.micro", "m3.medium", "m3.xlarge", "m2.xlarge", "m3.2xlarge", "c3.large", "c3.xlarge"],
        ))


    if bigip == True or security_groups == True:
        if num_nics == 1:
            BigipManagementGuiPort = t.add_parameter(Parameter(
                "BigipManagementGuiPort",
                Default="443",
                ConstraintDescription="Must be a valid, unusued port on BIG-IP.",
                Type="Number",
                Description="Port to use for the managment GUI",
            ))

    if bigip == True:


        if 'waf' in components:
            # Default to 2xlarge
            BigipInstanceType = t.add_parameter(Parameter(
                "BigipInstanceType",
                Default="m3.2xlarge",
                ConstraintDescription="must be a valid Big-IP EC2 instance type",
                Type="String",
                Description="F5 BIG-IP Virtual Instance Type",
                AllowedValues=[
                                "t2.medium",
                                "t2.large",
                                "m3.xlarge",
                                "m3.2xlarge",
                                "m4.large",
                                "m4.xlarge",
                                "m4.2xlarge",
                                "m4.4xlarge",
                                "m4.10xlarge",
                                "c3.2xlarge",
                                "c3.4xlarge",
                                "c3.8xlarge",
                                "c4.xlarge",
                                "c4.2xlarge",
                                "c4.4xlarge",       
                              ],
            ))

        else:

            BigipInstanceType = t.add_parameter(Parameter(
                "BigipInstanceType",
                Default="m3.xlarge",
                ConstraintDescription="must be a valid Big-IP EC2 instance type",
                Type="String",
                Description="F5 BIG-IP Virtual Instance Type",
                AllowedValues=[
                                "t2.medium",
                                "t2.large",
                                "m3.xlarge",
                                "m3.2xlarge",
                                "m4.large",
                                "m4.xlarge",
                                "m4.2xlarge",
                                "m4.4xlarge",
                                "m4.10xlarge",
                                "c3.2xlarge",
                                "c3.4xlarge",
                                "c3.8xlarge",
                                "c4.xlarge",
                                "c4.2xlarge",
                                "c4.4xlarge",       
                              ],
            ))

        if license_type == "hourly" and 'waf' not in components:
            BigipPerformanceType = t.add_parameter(Parameter(
                "BigipPerformanceType",
                Default="Best1000Mbps",
                ConstraintDescription="Must be a valid F5 Big-IP performance type",
                Type="String",
                Description="F5 Bigip Performance Type",
                AllowedValues=[
                                "Good25Mbps",
                                "Good200Mbps",
                                "Good1000Mbps",    
                                "Better25Mbps",
                                "Better200Mbps",
                                "Better1000Mbps",                          
                                "Best25Mbps",
                                "Best200Mbps",
                                "Best1000Mbps",
                              ],
            ))
        if license_type == "hourly" and 'waf' in components:
            BigipPerformanceType = t.add_parameter(Parameter(
                "BigipPerformanceType",
                Default="Best1000Mbps",
                ConstraintDescription="Must be a valid F5 Big-IP performance type",
                Type="String",
                Description="F5 Bigip Performance Type",
                AllowedValues=[                     
                                "Best25Mbps",
                                "Best200Mbps",
                                "Best1000Mbps",
                              ],
            ))
        if license_type != "hourly":
            BigipPerformanceType = t.add_parameter(Parameter(
                "BigipPerformanceType",
                Default="Best",
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

        if aws_creds == True:

            IamAccessKey = t.add_parameter(Parameter(
                "IamAccessKey",
                Description="IAM Access Key",
                Type="String",
                MinLength="16",
                MaxLength="32",
                AllowedPattern="[\\w]*",
                NoEcho=True,
                ConstraintDescription="can contain only ASCII characters.",
            ))

            IamSecretKey = t.add_parameter(Parameter(
                "IamSecretKey",
                Description="IAM Secret Key for Big-IP",
                Type="String",
                MinLength="1",
                MaxLength="255",
                AllowedPattern="[\\x20-\\x7E]*",
                NoEcho=True,
                ConstraintDescription="can contain only ASCII characters.",
            ))

        if license_type == "byol":

            for BIGIP_INDEX in range(num_bigips): 
                BigipLicenseKey = "Bigip" + str(BIGIP_INDEX + 1) + "LicenseKey"
                PARAMETERS[BigipLicenseKey] = t.add_parameter(Parameter(
                    BigipLicenseKey,
                    Type="String",
                    Description="Please enter your F5 BYOL regkey here:",
                    MinLength="1",
                    AllowedPattern="([\\x41-\\x5A][\\x41-\\x5A|\\x30-\\x39]{4})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{7})",
                    MaxLength="255",
                    ConstraintDescription="Please verify your F5 BYOL regkey.",
                ))

        if license_type == "bigiq":
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

    if stack == "existing" or stack == "security_groups":
            Vpc = t.add_parameter(Parameter(
                "Vpc",
                ConstraintDescription="Must be an existing VPC within working region.",
                Type="AWS::EC2::VPC::Id",
            ))

    if stack == "existing":

        for INDEX in range(num_azs):
            ExternalSubnet = "Az" + str(INDEX + 1) + "ExternalSubnet"
            PARAMETERS[ExternalSubnet] = t.add_parameter(Parameter(
                ExternalSubnet,
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

        if num_nics > 1:
            for INDEX in range(num_azs):
                ManagementSubnet = "Az" + str(INDEX + 1) + "ManagementSubnet"
                PARAMETERS[ManagementSubnet] = t.add_parameter(Parameter(
                    ManagementSubnet,
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
        if num_nics > 2:
            for INDEX in range(num_azs):
                InternalSubnet = "Az" + str(INDEX + 1) + "InternalSubnet"
                PARAMETERS[InternalSubnet] = t.add_parameter(Parameter(
                    InternalSubnet,
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

        WebserverPrivateIp = t.add_parameter(Parameter(
            "WebserverPrivateIp",
            ConstraintDescription="Web Server IP used for Big-IP pool Member",
            Type="String",
            Description="Web Server IP used for Big-IP pool member",
        ))


    # BEGIN REGION MAPPINGS FOR AMI IDS
    if bigip == True: 

        if license_type == "hourly":
            with open("cached-hourly-region-map.json") as json_file:
                RegionMap = json.load(json_file)

        if license_type != "hourly":
            with open("cached-byol-region-map.json") as json_file:
                RegionMap = json.load(json_file)

        t.add_mapping("BigipRegionMap", RegionMap )

    # WEB SERVER MAPPING
    if webserver == True:

        with open("cached-webserver-region-map.json") as json_file:
            RegionMap = json.load(json_file)

        t.add_mapping("WebserverRegionMap", RegionMap )


    ### BEGIN RESOURCES
    if network == True:
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

        octet = 1
        for INDEX in range(num_azs):
            ExternalSubnet = "Az" + str(INDEX + 1) + "ExternalSubnet"
            RESOURCES[ExternalSubnet] = t.add_resource(Subnet(
                ExternalSubnet,
                Tags=Tags(
                    Name="Az" + str(INDEX + 1) +  " External Subnet",
                    Application=Ref("AWS::StackId"),
                ),
                VpcId=Ref(Vpc),
                CidrBlock="10.0." + str(octet) + ".0/24",
                AvailabilityZone=Ref("AvailabilityZone" + str(INDEX + 1) ),
            ))
            octet += 10

        ExternalRouteTable = t.add_resource(RouteTable(
            "ExternalRouteTable",
            VpcId=Ref(Vpc),
            Tags=Tags(
                Name="External Route Table",
                Application=Ref("AWS::StackName"),
                Network="External",
            ),
        ))

        ExternalDefaultRoute = t.add_resource(Route(
            "ExternalDefaultRoute",
            DependsOn="AttachGateway",
            GatewayId=Ref(Igw),
            DestinationCidrBlock="0.0.0.0/0",
            RouteTableId=Ref(ExternalRouteTable),
        ))

        for INDEX in range(num_azs):
            ExternalSubnetRouteTableAssociation = "Az" + str(INDEX + 1) + "ExternalSubnetRouteTableAssociation"
            RESOURCES[ExternalSubnetRouteTableAssociation] = t.add_resource(SubnetRouteTableAssociation(
                ExternalSubnetRouteTableAssociation,
                SubnetId=Ref("Az" + str(INDEX + 1) + "ExternalSubnet"),
                RouteTableId=Ref(ExternalRouteTable),
            ))
           

        if num_nics > 1:
            octet = 0

            for INDEX in range(num_azs):
                ManagementSubnet = "Az" + str(INDEX + 1) + "ManagementSubnet"
                RESOURCES[ManagementSubnet] = t.add_resource(Subnet(
                    ManagementSubnet,
                    Tags=Tags(
                        Name="Az" + str(INDEX + 1) +  " Management Subnet",
                        Application=Ref("AWS::StackId"),
                    ),
                    VpcId=Ref(Vpc),
                    CidrBlock="10.0." + str(octet) + ".0/24",
                    AvailabilityZone=Ref("AvailabilityZone" + str(INDEX + 1) ),
                ))
                octet += 10

            ManagementRouteTable = t.add_resource(RouteTable(
                "ManagementRouteTable",
                VpcId=Ref(Vpc),
                Tags=Tags(
                    Name="Management Route Table",
                    Application=Ref("AWS::StackName"),
                    Network="Mgmt",
                ),
            ))

            # Depends On
            #https://forums.aws.amazon.com/thread.jspa?threadID=100750
            ManagementDefaultRoute = t.add_resource(Route(
                "ManagementDefaultRoute",
                DependsOn="AttachGateway",
                GatewayId=Ref(Igw),
                DestinationCidrBlock="0.0.0.0/0",
                RouteTableId=Ref(ManagementRouteTable),
            ))
    
            for INDEX in range(num_azs):
                ManagementSubnetRouteTableAssociation = "Az" + str(INDEX + 1) + "ManagementSubnetRouteTableAssociation"
                RESOURCES[ManagementSubnetRouteTableAssociation] = t.add_resource(SubnetRouteTableAssociation(
                    ManagementSubnetRouteTableAssociation,
                    SubnetId=Ref("Az" + str(INDEX + 1) + "ManagementSubnet"),
                    RouteTableId=Ref(ManagementRouteTable),
                ))


        if num_nics > 2:
            octet = 2
            for INDEX in range(num_azs):
                InternalSubnet = "Az" + str(INDEX + 1) + "InternalSubnet"
                RESOURCES[InternalSubnet] = t.add_resource(Subnet(
                    InternalSubnet,
                    Tags=Tags(
                        Name="Az" + str(INDEX + 1) +  " Internal Subnet",
                        Application=Ref("AWS::StackId"),
                    ),
                    VpcId=Ref(Vpc),
                    CidrBlock="10.0." + str(octet) + ".0/24",
                    AvailabilityZone=Ref("AvailabilityZone" + str(INDEX + 1) ),
                ))
                octet += 10


            InternalRouteTable = t.add_resource(RouteTable(
                "InternalRouteTable",
                VpcId=Ref(Vpc),
                Tags=Tags(
                    Name="Internal Route Table",
                    Application=Ref("AWS::StackName"),
                    Network="Internal",
                ),
            ))

            InternalDefaultRoute = t.add_resource(Route(
                "InternalDefaultRoute",
                DependsOn="AttachGateway",
                GatewayId=Ref(Igw),
                DestinationCidrBlock="0.0.0.0/0",
                RouteTableId=Ref(InternalRouteTable),
            ))

            for INDEX in range(num_azs):
                InternalSubnetRouteTableAssociation = "Az" + str(INDEX + 1) + "InternalSubnetRouteTableAssociation"
                RESOURCES[InternalSubnetRouteTableAssociation] = t.add_resource(SubnetRouteTableAssociation(
                    InternalSubnetRouteTableAssociation,
                    SubnetId=Ref("Az" + str(INDEX + 1) + "InternalSubnet"),
                    RouteTableId=Ref(InternalRouteTable),
                ))

        octet = 3
        for INDEX in range(num_azs):
            ApplicationSubnet = "Az" + str(INDEX + 1) + "ApplicationSubnet"
            RESOURCES[ApplicationSubnet] = t.add_resource(Subnet(
                ApplicationSubnet,
                Tags=Tags(
                    Name="Az" + str(INDEX + 1) +  " Application Subnet",
                    Application=Ref("AWS::StackId"),
                ),
                VpcId=Ref(Vpc),
                CidrBlock="10.0." + str(octet) + ".0/24",
                AvailabilityZone=Ref("AvailabilityZone" + str(INDEX + 1) ),
            ))
            octet += 10

        ApplicationRouteTable = t.add_resource(RouteTable(
            "ApplicationRouteTable",
            VpcId=Ref(Vpc),
            Tags=Tags(
                Name="Application Route Table",
                Application=Ref("AWS::StackName"),
                Network="Application",
            ),
        ))

        ApplicationDefaultRoute = t.add_resource(Route(
            "ApplicationDefaultRoute",
            DependsOn="AttachGateway",
            GatewayId=Ref(Igw),
            DestinationCidrBlock="0.0.0.0/0",
            RouteTableId=Ref(ApplicationRouteTable),
        ))


        for INDEX in range(num_azs):
            ApplicationSubnetRouteTableAssociation = "Az" + str(INDEX + 1) + "ApplicationSubnetRouteTableAssociation"
            RESOURCES[ApplicationSubnetRouteTableAssociation] = t.add_resource(SubnetRouteTableAssociation(
                ApplicationSubnetRouteTableAssociation,
                SubnetId=Ref("Az" + str(INDEX + 1) + "ApplicationSubnet"),
                RouteTableId=Ref(ApplicationRouteTable),
            ))

    # See SOL13946 for more details
    # Clustering uses UDP 1026 UDP (failover) and TCP 4353 (SYNC) 
    # WAF uses 6123-6128 for SYNC
    # As just examples, not going to break down example Security Groups for Cluster & WAF. 
    # However, could further tighten if Standalone or no WAF.  

    if security_groups == True:

        # 1 Nic has consolidated rules
        if num_nics == 1:

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
                    # Required Device Service Clustering (DSC) & GTM DNS
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="4353",
                                ToPort="4353",
                                CidrIp="0.0.0.0/0",
                    ),
                    # Required for DSC Initial Sync
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="22",
                                ToPort="22",
                                CidrIp="10.0.0.0/16",
                    ), 
                    # Required for DSC Network Heartbeat
                    SecurityGroupRule(
                                IpProtocol="udp",
                                FromPort="1026",
                                ToPort="1026",
                                CidrIp="10.0.0.0/16",
                    ), 
                    # ASM SYNC
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="6123",
                                ToPort="6128",
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


        if num_nics > 1:

            BigipExternalSecurityGroup = t.add_resource(SecurityGroup(
                "BigipExternalSecurityGroup",
                SecurityGroupIngress=[
                    # Example port for Virtual Server
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="80",
                                ToPort="80",
                                CidrIp="0.0.0.0/0",
                    ),
                    # Example port for Virtual Server
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="443",
                                ToPort="443",
                                CidrIp="0.0.0.0/0",
                    ),
                    # Required Device Service Clustering (DSC) & GTM DNS
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="4353",
                                ToPort="4353",
                                CidrIp="0.0.0.0/0",
                    ),
                    # Required for DSC Network Heartbeat
                    SecurityGroupRule(
                                IpProtocol="udp",
                                FromPort="1026",
                                ToPort="1026",
                                CidrIp="10.0.0.0/16",
                    ), 
                    # ASM SYNC
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="6123",
                                ToPort="6128",
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
                    # Required for DSC Initial Sync
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="22",
                                ToPort="22",
                                CidrIp="10.0.0.0/16",
                    ),
                    # Required for DSC Initial Sync
                    SecurityGroupRule(
                                IpProtocol="tcp",
                                FromPort="443",
                                ToPort="443",
                                CidrIp="10.0.0.0/16",
                    ),  
                ],
                VpcId=Ref(Vpc),
                GroupDescription="Big-IP Management UI rules",
                Tags=Tags(
                    Name="Bigip Management Security Group",
                    Application=Ref("AWS::StackName"),
                ),
            ))

        # If a 3 nic with additional Internal interface.
        if num_nics > 2:

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

        if webserver == True:

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

    if webserver == True:

        Webserver = t.add_resource(Instance(
            "Webserver",
            UserData=Base64(Join("\n", [
                                         "#cloud-config",
                                         "runcmd:",
                                         " - sudo docker run --name demo -p 80:80 -d f5devcentral/f5-demo-app:latest"
                ])),
            Tags=Tags(
                Name="Webserver",
                Application=Ref("AWS::StackName"),
            ),
            ImageId=FindInMap("WebserverRegionMap", Ref("AWS::Region"), "AMI"),
            KeyName=Ref(KeyName),
            InstanceType=Ref(WebserverInstanceType),
            NetworkInterfaces=[
            NetworkInterfaceProperty(
                SubnetId=Ref("Az1ApplicationSubnet"),
                DeviceIndex="0",
                GroupSet=[Ref(WebserverSecurityGroup)],
                Description=Join("", [Ref("AWS::StackName"), " Webserver Network Interface"]),
                AssociatePublicIpAddress="true",
            ),
            ],
        ))


    if bigip == True:

        for BIGIP_INDEX in range(num_bigips): 

            BigipLicenseKey = "Bigip" + str(BIGIP_INDEX + 1) + "LicenseKey"
            ExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalInterface" 
            ExternalSelfEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalSelfEipAddress"
            ExternalSelfEipAssociation = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalSelfEipAssociation"
            ExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalInterface" 
            BigipInstance = "Bigip" + str(BIGIP_INDEX + 1) + "Instance"

            if num_azs > 1:
                ExternalSubnet = "Az" + str(BIGIP_INDEX + 1) + "ExternalSubnet"
                ManagementSubnet = "Az" + str(BIGIP_INDEX + 1) + "ManagementSubnet"
                InternalSubnet = "Az" + str(BIGIP_INDEX + 1) + "InternalSubnet"              
            else:
                ExternalSubnet = "Az1ExternalSubnet"
                ManagementSubnet = "Az1ManagementSubnet"
                InternalSubnet = "Az1InternalSubnet"


            RESOURCES[ExternalInterface] = t.add_resource(NetworkInterface(
                ExternalInterface,
                SubnetId=Ref(ExternalSubnet),
                GroupSet=[Ref(BigipExternalSecurityGroup)],
                Description="Public External Interface for the Bigip",
                SecondaryPrivateIpAddressCount="1",
            ))

            if stack == "full":
                # External Interface is true on 1nic,2nic,3nic,etc.
                RESOURCES[ExternalSelfEipAddress] = t.add_resource(EIP(    
                    ExternalSelfEipAddress,
                    DependsOn="AttachGateway",
                    Domain="vpc",
                ))

                RESOURCES[ExternalSelfEipAssociation] = t.add_resource(EIPAssociation(
                    ExternalSelfEipAssociation,
                    DependsOn="AttachGateway",
                    NetworkInterfaceId=Ref(ExternalInterface),
                    AllocationId=GetAtt(ExternalSelfEipAddress, "AllocationId"),
                    PrivateIpAddress=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
                ))
            else:
                RESOURCES[ExternalSelfEipAddress] = t.add_resource(EIP(    
                    ExternalSelfEipAddress,
                    Domain="vpc",
                ))

                RESOURCES[ExternalSelfEipAssociation] = t.add_resource(EIPAssociation(
                    ExternalSelfEipAssociation,
                    NetworkInterfaceId=Ref(ExternalInterface),
                    AllocationId=GetAtt(ExternalSelfEipAddress, "AllocationId"),
                    PrivateIpAddress=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
                ))
         
            if num_nics > 1:

                VipEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "VipEipAddress"
                VipEipAssociation = "Bigip" + str(BIGIP_INDEX + 1) + "VipEipAssociation"
                ManagementInterface = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementInterface"
                ManagementEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementEipAddress"
                ManagementEipAssociation = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementEipAssociation"

                if ha_type == "standalone" or (BIGIP_INDEX + 1) == CLUSTER_SEED:

                    if stack == "full":
                        RESOURCES[VipEipAddress] = t.add_resource(EIP(
                            VipEipAddress,
                            DependsOn="AttachGateway",
                            Domain="vpc",
                        ))
                        RESOURCES[VipEipAssociation] = t.add_resource(EIPAssociation(
                            VipEipAssociation,
                            DependsOn="AttachGateway",
                            NetworkInterfaceId=Ref(ExternalInterface),
                            AllocationId=GetAtt(VipEipAddress, "AllocationId"),
                            PrivateIpAddress=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                        ))
                    else:
                        RESOURCES[VipEipAddress] = t.add_resource(EIP(
                            VipEipAddress,
                            Domain="vpc",
                        ))
                        RESOURCES[VipEipAssociation] = t.add_resource(EIPAssociation(
                            VipEipAssociation,
                            NetworkInterfaceId=Ref(ExternalInterface),
                            AllocationId=GetAtt(VipEipAddress, "AllocationId"),
                            PrivateIpAddress=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                        ))

                RESOURCES[ManagementInterface] = t.add_resource(NetworkInterface(
                    ManagementInterface,
                    SubnetId=Ref(ManagementSubnet),
                    GroupSet=[Ref(BigipManagementSecurityGroup)],
                    Description="Management Interface for the Bigip",
                ))

                if stack == "full":
                    RESOURCES[ManagementEipAddress] = t.add_resource(EIP(
                        ManagementEipAddress,
                        DependsOn="AttachGateway",
                        Domain="vpc",
                    ))
                    RESOURCES[ManagementEipAssociation] = t.add_resource(EIPAssociation(
                        ManagementEipAssociation,
                        DependsOn="AttachGateway",
                        NetworkInterfaceId=Ref(ManagementInterface),
                        AllocationId=GetAtt(ManagementEipAddress, "AllocationId"),
                    ))
                else:
                    RESOURCES[ManagementEipAddress] = t.add_resource(EIP(
                        ManagementEipAddress,
                        Domain="vpc",
                    ))
                    RESOURCES[ManagementEipAssociation] = t.add_resource(EIPAssociation(
                        ManagementEipAssociation,
                        NetworkInterfaceId=Ref(ManagementInterface),
                        AllocationId=GetAtt(ManagementEipAddress, "AllocationId"),
                    ))

                if num_nics > 2:

                    InternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "InternalInterface"

                    RESOURCES[InternalInterface] = t.add_resource(NetworkInterface(
                        InternalInterface,
                        SubnetId=Ref(InternalSubnet),
                        GroupSet=[Ref(BigipInternalSecurityGroup)],
                        Description="Internal Interface for the Bigip",
                    ))


            # Build firstrun config
            firstrun_config = []

            firstrun_config += [
                                    "#!/bin/bash\n", 
                                    "HOSTNAME=`curl http://169.254.169.254/latest/meta-data/hostname`\n", 
                                    "TZ='UTC'\n",
                                    "BIGIP_ADMIN_USERNAME='", Ref(BigipAdminUsername), "'\n", 
                                    "BIGIP_ADMIN_PASSWORD='", Ref(BigipAdminPassword), "'\n",
                                ]

            if license_type == "byol":
                firstrun_config += [ "REGKEY=", Ref(BigipLicenseKey), "\n" ]
            elif license_type == "bigiq":
                firstrun_config += [ 
                                    "BIGIQ_ADDRESS='", Ref(BigiqAddress), "'\n",
                                    "BIGIQ_USERNAME='", Ref(BigiqUsername), "'\n",
                                    "BIGIQ_PASSWORD='", Ref(BigiqPassword), "'\n",
                                    "BIGIQ_LICENSE_POOL_UUID='", Ref(BigiqLicensePoolUUID), "'\n"
                                   ]

                if num_nics == 1:
                    firstrun_config += [ "BIGIP_DEVICE_ADDRESS='", Ref(ExternalSelfEipAddress),"'\n" ] 
                if num_nics > 1:
                    firstrun_config += [ "BIGIP_DEVICE_ADDRESS='", Ref(ManagementEipAddress),"'\n" ] 


            if num_nics == 1:
                firstrun_config += [ 
                                    "MANAGEMENT_GUI_PORT='", Ref(BigipManagementGuiPort), "'\n",  
                                    "GATEWAY_MAC=`ifconfig eth0 | egrep HWaddr | awk '{print tolower($5)}'`\n",
                                   ]

            if num_nics > 1:
                firstrun_config += [ 
                                    "GATEWAY_MAC=`ifconfig eth1 | egrep HWaddr | awk '{print tolower($5)}'`\n",
                                   ]

            firstrun_config += [
                                    "GATEWAY_CIDR_BLOCK=`curl http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC}/subnet-ipv4-cidr-block`\n",
                                    "GATEWAY_NET=${GATEWAY_CIDR_BLOCK%/*}\n",
                                    "GATEWAY_PREFIX=${GATEWAY_CIDR_BLOCK#*/}\n",
                                    "GATEWAY=`echo ${GATEWAY_NET} | awk -F. '{ print $1\".\"$2\".\"$3\".\"$4+1 }'`\n",
                                    "VPC_CIDR_BLOCK=`curl http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC}/vpc-ipv4-cidr-block`\n",
                                    "VPC_NET=${VPC_CIDR_BLOCK%/*}\n",
                                    "VPC_PREFIX=${VPC_CIDR_BLOCK#*/}\n",
                                    "NAME_SERVER=`echo ${VPC_NET} | awk -F. '{ print $1\".\"$2\".\"$3\".\"$4+2 }'`\n", 
                                ]


            if num_nics > 1:
                firstrun_config += [ 
                                    "MGMTIP='", GetAtt(ManagementInterface, "PrimaryPrivateIpAddress"), "'\n", 
                                    "EXTIP='", GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"), "'\n", 
                                    "EXTPRIVIP='", Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")), "'\n", 
                                    "EXTMASK='24'\n",
                                    ]
            if num_nics > 2:
                firstrun_config += [ 
                                    "INTIP='",GetAtt(InternalInterface, "PrimaryPrivateIpAddress"),"'\n",
                                    "INTMASK='24'\n", 
                                   ]


            if stack == "full":
                firstrun_config +=  [              
                                    "POOLMEM='", GetAtt('Webserver','PrivateIp'), "'\n", 
                                    "POOLMEMPORT=80\n", 
                                    ]
            elif stack == "existing":
                firstrun_config +=  [
                                    "POOLMEM='", Ref(WebserverPrivateIp), "'\n", 
                                    "POOLMEMPORT=80\n", 
                                    ]         


            firstrun_config +=  [
                                    "APPNAME='demo-app-1'\n", 
                                    "VIRTUALSERVERPORT=80\n",
                                    "CRT='default.crt'\n", 
                                    "KEY='default.key'\n",
                                ]
            if ha_type != "standalone" and (BIGIP_INDEX + 1) == CLUSTER_SEED:
                firstrun_config +=  [
                                    "PEER_HOSTNAME='", GetAtt("Bigip" + str(BIGIP_INDEX + 2) + "Instance", "PrivateDnsName"), "'\n",
                                    "PEER_MGMTIP='", GetAtt("Bigip" + str(BIGIP_INDEX + 2) + "ManagementInterface", "PrimaryPrivateIpAddress"), "'\n",
                                    ]
                
                if num_nics > 1:
                    firstrun_config +=  [
                                        "PEER_EXTPRIVIP='", Select("0", GetAtt("Bigip" + str(BIGIP_INDEX + 2) + "ExternalInterface", "SecondaryPrivateIpAddresses")), "'\n", 
                                        "VIPEIP='",Ref(VipEipAddress),"'\n",
                                        ]

            if aws_creds == True:
                firstrun_config +=  [
                                      "IAM_ACCESS_KEY='", Ref(IamAccessKey), "'\n",
                                      "IAM_SECRET_KEY='", Ref(IamSecretKey), "'\n",
                                    ]
            # build firstrun.sh vars

            license_byol =  [ 
                                "echo 'start install byol license'\n",
                                "networkUp 120 \n",
                                "LicenseBigIP ${REGKEY}\n",
                                # "nohup tcpdump -U -ni 0.0:nnn -s0 -c 10000 udp port 53 or host 104.219.104.132 -w /var/tmp/license-attempt.pcap &\n",
                                # "sleep 10\n",
                                # "LICENSE_RETURN=$( tmsh install /sys license registration-key \"${REGKEY}\")\n",
                                # "echo \"LICENSE_RETURN=${LICENSE_RETURN}\"\n",
                                # "pid=$(ps -e | pgrep tcpdump)\n",
                                # "echo killing pid=${pid}\n",
                                # "kill ${pid}\n", 
                            ]

            # License file downloaded remotely from https://cdn.f5.com/product/iapp/utils/license-from-bigiq.sh
            license_from_bigiq =  [
                                "echo 'start install biqiq license'\n",
                                ". /tmp/license_from_bigiq.sh\n",
                                ]

            provision_asm = [
                                "echo 'provisioning asm'\n",
                                "tmsh modify /sys provision asm level nominal\n",
                                "checkretstatus='stop'\n",
                                "while [[ $checkretstatus != \"run\" ]]; do\n",
                                "     checkStatus\n",
                                "     if [[ $checkretstatus == \"restart\" ]]; then\n",
                                "         echo restarting\n",
                                "         tmsh modify /sys provision asm level none\n",
                                "         checkStatusnoret\n",
                                "         checkretstatus='stop'\n",
                                "         tmsh modify /sys provision asm level nominal\n",
                                "     fi\n",
                                "done\n",
                                "echo 'done provisioning asm'\n",
                            ]


            # TMSH CMD
            # tmsh create /sys application service HA_Across_AZs template f5.aws_advanced_ha.v1.2.0rc1 tables add { eip_mappings__mappings { column-names { eip az1_vip az2_vip } rows { { row { 52.27.196.185 /Common/10.0.1.100 /Common/10.0.11.100 } } } } } variables add { eip_mappings__inbound { value yes } }

            aws_advanced_ha_iapp_rest_payload = '{ \
    "name": "HA_Across_AZs", \
    "partition": "Common", \
    "inheritedDevicegroup": "true", \
    "inheritedTrafficGroup": "true", \
    "strictUpdates": "enabled", \
    "template": "/Common/f5.aws_advanced_ha.v1.2.0.tmpl", \
    "templateModified": "no", \
    "tables": [ \
        { \
            "name": "eip_mappings__mappings", \
            "columnNames": [ \
                "eip", \
                "az1_vip", \
                "az2_vip" \
            ], \
            "rows": [ \
                { \
                    "row": [ \
                        "${VIPEIP}", \
                        "/Common/${EXTPRIVIP}", \
                        "/Common/${PEER_EXTPRIVIP}" \
                    ] \
                }, \
            ] \
        }, \
        { \
            "name": "subnet_routes__cidr_blocks" \
        } \
    ], \
    "variables": [ \
        { \
            "encrypted": "no", \
            "name": "eip_mappings__inbound", \
            "value": "yes" \
        }, \
        { \
            "encrypted": "no", \
            "name": "options__advanced_mode", \
            "value": "yes" \
        }, \
        { \
            "encrypted": "no", \
            "name": "options__display_help", \
            "value": "hide" \
        }, \
        { \
            "encrypted": "no", \
            "name": "options__log_debug", \
            "value": "no" \
        }, \
        { \
            "encrypted": "no", \
            "name": "subnet_routes__route_management", \
            "value": "no" \
        } \
    ] \
}'

            # begin building firstrun.sh and cloud lib calls
            firstrun_sh =       [
                                    "#!/bin/bash\n",
                                ] 
            onboard_BIG_IP =    [
                                ]
            firstrun_BIG_IP =   [
                                    "f5-rest-node /shared/f5-cloud-libs/scripts/runScript.js",
                                    "--wait-for ONBOARD_DONE",
                                    "--file /tmp/firstrun.sh",
                                    "-o /var/log/firstrun_1.log",
                                    "--background",
                                ]                 
            if num_nics == 1:
                if ha_type != "standalone":
                    firstrun_sh += [
                                        "/usr/bin/setdb provision.1nicautoconfig disable\n",
                                   ]
            firstrun_sh +=  [ 
                                ". /tmp/firstrun.config\n",
                                ". /tmp/firstrun.utils\n",
                                "FILE=/tmp/firstrun.log\n",
                                "if [ ! -e $FILE ]\n",
                                " then\n",
                                "     touch $FILE\n",
                                "     nohup $0 0<&- &>/dev/null &\n",
                                "     exit\n",
                                "fi\n",
                                "exec 1<&-\n",
                                "exec 2<&-\n",
                                "exec 1<>$FILE\n",
                                "exec 2>&1\n",
                                "date\n",
                            ]


            # Global Settings
            firstrun_sh += [
                                "echo 'starting tmsh config'\n",
                            ]
            onboard_BIG_IP += [
                               "NAME_SERVER=`/shared/f5-cloud-libs/scripts/aws/getNameServer.sh eth1`;",
                               "f5-rest-node /shared/f5-cloud-libs/scripts/onboard.js",
                               "-o  /var/log/onboard.log",
                               "--background",
                               "--no-reboot",
                               "--host localhost",
                               "--user admin",
                               "--password '", { "Ref": "BigipAdminPassword" }, "'",
                               "--set-password admin:'", { "Ref": "BigipAdminPassword" }, "'",
                               "--hostname `curl http://169.254.169.254/latest/meta-data/hostname`",
                               "--ntp 0.us.pool.ntp.org",
                               "--ntp 1.us.pool.ntp.org",
                               "--tz UTC",
                               "--dns ${NAME_SERVER}",
                               "--module ltm:nominal",
                               ]               

            if aws_creds:
                firstrun_sh += [
                                "tmsh modify sys global-settings aws-access-key ${IAM_ACCESS_KEY}\n",
                                "tmsh modify sys global-settings aws-secret-key ${IAM_SECRET_KEY}\n",
                                ]   


            if num_nics == 1:

                firstrun_sh +=  [
                                "tmsh modify sys httpd ssl-port ${MANAGEMENT_GUI_PORT}\n",
                                ] 

                # Sync and Failover ( UDP 1026 and TCP 4353 already included in self-allow defaults )
                if 'waf' not in components:
                    firstrun_sh +=  [ 
                                    "tmsh modify net self-allow defaults add { tcp:${MANAGEMENT_GUI_PORT} }\n",

                                    ]

                if 'waf' in components:
                    firstrun_sh +=  [ 
                                    "tmsh modify net self-allow defaults add { tcp:${MANAGEMENT_GUI_PORT} tcp:6123 tcp:6124 tcp:6125 tcp:6126 tcp:6127 tcp:6128 }\n",
                                    ]

                firstrun_sh +=  [
                                    "if [[ \"${MANAGEMENT_GUI_PORT}\" != \"443\" ]]; then tmsh modify net self-allow defaults delete { tcp:443 }; fi \n",
                                ] 


            # Network Settings
            if num_nics > 1:

                firstrun_sh +=  [ 
                                "tmsh create net vlan external interfaces add { 1.1 } \n",
                                ]

                if ha_type == "standalone":

                    if 'waf' not in components:
                        firstrun_sh +=  [ 
                                        "tmsh create net self ${EXTIP}/${EXTMASK} vlan external allow-service add { tcp:4353 }\n",
                                        ]

                    if 'waf' in components:                    
                        firstrun_sh +=  [ 
                                        "tmsh create net self ${EXTIP}/${EXTMASK} vlan external allow-service add { tcp:6123 tcp:6124 tcp:6125 tcp:6126 tcp:6127 tcp:6128 }\n",
                                        ]


                if ha_type != "standalone":

                    if 'waf' not in components:
                        firstrun_sh +=  [ 
                                        "tmsh create net self ${EXTIP}/${EXTMASK} vlan external allow-service add { tcp:4353 udp:1026 }\n",
                                        ]

                    if 'waf' in components:
                        firstrun_sh +=  [ 
                                        "tmsh create net self ${EXTIP}/${EXTMASK} vlan external allow-service add { tcp:4353 udp:1026 tcp:6123 tcp:6124 tcp:6125 tcp:6126 tcp:6127 tcp:6128 }\n",
                                        ]


                                
            if num_nics > 2:
                firstrun_sh +=  [ 
                                "tmsh create net vlan internal interfaces add { 1.2 } \n",
                                "tmsh create net self ${INTIP}/${INTMASK} vlan internal allow-service default\n",
                                ]

            # Set Gateway

            if ha_type == "across-az":
                firstrun_sh +=  [                  
                                    "tmsh create sys folder /LOCAL_ONLY device-group none traffic-group traffic-group-local-only\n",
                                    "tmsh create net route /LOCAL_ONLY/default network default gw ${GATEWAY}\n",
                                ]
            else:
                if num_nics > 1:
                    firstrun_sh +=  [
                                        "tmsh create net route default gw ${GATEWAY}\n",
                                    ]

            # Disable DHCP if clustering. 
            if ha_type != "standalone":

                firstrun_sh += [ 
                                    "tmsh modify sys db dhclient.mgmt { value disable }\n",
                                ] 


                if num_nics == 1:
                    firstrun_sh += [
                                    "MGMT_ADDR=$(tmsh list sys management-ip | awk '/management-ip/ {print $3}')\n",
                                    "MGMT_IP=${MGMT_ADDR%/*}\n",
                                    "tmsh modify cm device ${HOSTNAME} configsync-ip ${MGMT_IP} }\n", 
                                   ]
                else:
                    # For simplicity, putting all clustering endpoints on external subnet
                    firstrun_sh += [
                                    "tmsh modify cm device ${HOSTNAME} configsync-ip ${EXTIP} unicast-address { { effective-ip ${EXTIP} effective-port 1026 ip ${EXTIP} } }\n", 
                                   ]

            firstrun_sh +=  [ "tmsh save /sys config\n", ]

            # License Device
            if license_type == "byol":
                firstrun_sh += license_byol
            elif license_type == "bigiq":
                firstrun_sh += license_from_bigiq

            # Wait until licensing finishes
            firstrun_sh += [
                              "checkStatusnoret\n",
                              "sleep 20 \n",
                              "tmsh save /sys config\n",
                           ]

            # Provision Modules
            if 'waf' in components:
                firstrun_sh += provision_asm


            # Cluster Devices if Cluster Seed
            if ha_type != "standalone" and (BIGIP_INDEX + 1) == CLUSTER_SEED:
                firstrun_sh +=  [
                                "echo 'sleeping additional 120 secs to wait for peer to boot'\n",
                                "sleep 120\n",
                                "tmsh modify cm trust-domain Root ca-devices add { ${PEER_MGMTIP} } name ${PEER_HOSTNAME} username admin password \"'${BIGIP_ADMIN_PASSWORD}'\"\n",    
                                "tmsh create cm device-group my_sync_failover_group type sync-failover devices add { ${HOSTNAME} ${PEER_HOSTNAME} } auto-sync enabled\n",
                                "tmsh run cm config-sync to-group my_sync_failover_group\n", 
                                ]


            if ha_type == "standalone" or (BIGIP_INDEX + 1) == CLUSTER_SEED:

                #Add Pool
                firstrun_sh +=  [
                                    "tmsh create ltm pool ${APPNAME}-pool members add { ${POOLMEM}:${POOLMEMPORT} } monitor http\n",
                                ]

                # Add virtual service with simple URI-Routing ltm policy
                if 'waf' not in components:

                    firstrun_sh +=  [
                      "tmsh create ltm policy uri-routing-policy controls add { forwarding } requires add { http } strategy first-match legacy\n",
                      "tmsh modify ltm policy uri-routing-policy rules add { service1.example.com { conditions add { 0 { http-uri host values { service1.example.com } } } actions add { 0 { forward select pool ${APPNAME}-pool } } ordinal 1 } }\n",
                      "tmsh modify ltm policy uri-routing-policy rules add { service2.example.com { conditions add { 0 { http-uri host values { service2.example.com } } } actions add { 0 { forward select pool ${APPNAME}-pool } } ordinal 2 } }\n",
                      "tmsh modify ltm policy uri-routing-policy rules add { apiv2 { conditions add { 0 { http-uri path starts-with values { /apiv2 } } } actions add { 0 { forward select pool ${APPNAME}-pool } } ordinal 3 } }\n",
                    ]

                    if ha_type != "across-az":

                        if num_nics == 1:
                            firstrun_sh +=  [

                                            "tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination 0.0.0.0:${VIRTUALSERVERPORT} mask any ip-protocol tcp pool /Common/${APPNAME}-pool policies replace-all-with { uri-routing-policy { } } profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\n",
                                            ]

                        if num_nics > 1:
                            firstrun_sh +=  [
                                            "tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp pool /Common/${APPNAME}-pool policies replace-all-with { uri-routing-policy { } } profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\n",
                                            ]
                    if ha_type == "across-az":                      
                        firstrun_sh +=  [
                                            "tmsh create ltm virtual /Common/AZ1-${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp pool /Common/${APPNAME}-pool policies replace-all-with { uri-routing-policy { } } profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\n",
                                            "tmsh create ltm virtual /Common/AZ2-${APPNAME}-${VIRTUALSERVERPORT} { destination ${PEER_EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp pool /Common/${APPNAME}-pool policies replace-all-with { uri-routing-policy { } } profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\n",
                                            "tmsh modify ltm virtual-address ${EXTPRIVIP} traffic-group none\n",
                                            "tmsh modify ltm virtual-address ${PEER_EXTPRIVIP} traffic-group none\n",
                                        ]

                if 'waf' in components:
                    # 12.1.0 requires "first match legacy"
                    firstrun_sh += [
                                      "curl -o /home/admin/asm-policy-linux-high.xml http://cdn.f5.com/product/templates/utils/asm-policy-linux-high.xml \n",
                                      "tmsh load asm policy file /home/admin/asm-policy-linux-high.xml\n",
                                      "# modify asm policy names below (ex. /Common/linux-high) to match name in xml\n",
                                      "tmsh modify asm policy /Common/linux-high active\n",
                                      "tmsh create ltm policy app-ltm-policy strategy first-match legacy\n",
                                      "tmsh modify ltm policy app-ltm-policy controls add { asm }\n",
                                      "tmsh modify ltm policy app-ltm-policy rules add { associate-asm-policy { actions replace-all-with { 0 { asm request enable policy /Common/linux-high } } } }\n",
                                    ]

                    if ha_type != "across-az":

                        if num_nics == 1:
                            firstrun_sh +=  [
                                              "tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination 0.0.0.0:${VIRTUALSERVERPORT} mask any ip-protocol tcp policies replace-all-with { app-ltm-policy { } } pool /Common/${APPNAME}-pool profiles replace-all-with { http { } tcp { } websecurity { } } security-log-profiles replace-all-with { \"Log illegal requests\" } source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled}\n",
                                            ]

                        if num_nics > 1:
                            firstrun_sh +=  [
                                              "tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp policies replace-all-with { app-ltm-policy { } } pool /Common/${APPNAME}-pool profiles replace-all-with { http { } tcp { } websecurity { } } security-log-profiles replace-all-with { \"Log illegal requests\" } source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled}\n",
                                            ]
                    if ha_type == "across-az":                      
                        firstrun_sh +=  [
                                            "tmsh create ltm virtual /Common/AZ1-${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp policies replace-all-with { app-ltm-policy { } } pool /Common/${APPNAME}-pool profiles replace-all-with { http { } tcp { } websecurity { } } security-log-profiles replace-all-with { \"Log illegal requests\" } source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled}\n",
                                            "tmsh create ltm virtual /Common/AZ2-${APPNAME}-${VIRTUALSERVERPORT} { destination ${PEER_EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp policies replace-all-with { app-ltm-policy { } } pool /Common/${APPNAME}-pool profiles replace-all-with { http { } tcp { } websecurity { } } security-log-profiles replace-all-with { \"Log illegal requests\" } source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled}\n",
                                            "tmsh modify ltm virtual-address ${EXTPRIVIP} traffic-group none\n",
                                            "tmsh modify ltm virtual-address ${PEER_EXTPRIVIP} traffic-group none\n",
                                        ]

                if ha_type == "across-az":
                    firstrun_sh += [
                                            "curl -sSk -o /tmp/f5.aws_advanced_ha.v1.2.0rc1.tmpl --max-time 15 https://cdn.f5.com/product/templates/f5.aws_advanced_ha.v1.2.0rc1.tmpl\n",
                                            "tmsh load sys application template /tmp/f5.aws_advanced_ha.v1.2.0rc1.tmpl\n",
                                            "tmsh create /sys application service HA_Across_AZs template f5.aws_advanced_ha.v1.2.0rc1 tables add { eip_mappings__mappings { column-names { eip az1_vip az2_vip } rows { { row { ${VIPEIP} /Common/${EXTPRIVIP} /Common/${PEER_EXTPRIVIP} } } } } } variables add { eip_mappings__inbound { value yes } }\n",
                                            "tmsh modify sys application service HA_Across_AZs.app/HA_Across_AZs execute-action definition\n",
                                            "tmsh run cm config-sync to-group my_sync_failover_group\n",
                                            "sleep 15\n",
                                            "curl -sSk -u admin:\"${BIGIP_ADMIN_PASSWORD}\" -H 'Content-Type: application/json' -X PATCH -d '{\"execute-action\":\"definition\"}' https://${PEER_MGMTIP}/mgmt/tm/sys/application/service/~Common~HA_Across_AZs.app~HA_Across_AZs\n",
                                    ]

            # If ASM, Need to use overwite Config (SOL16509 / BZID: 487538 )
            if ha_type != "standalone" and (BIGIP_INDEX + 1) == CLUSTER_SEED:
                if 'waf' in components:

                    firstrun_sh += [
                                            "tmsh modify cm device-group datasync-global-dg devices modify { ${HOSTNAME} { set-sync-leader } }\n", 
                                            "tmsh run cm config-sync to-group datasync-global-dg\n",
                                    ]

            if license_type == "byol":                
                firstrun_sh += [
                                    "tmsh save /sys config\n",
                                    "date\n",
                                    "# for security purposes, remove firstrun.config\n",
                                    "# rm /tmp/firstrun.config\n"
                               ]
            else:
                firstrun_sh += [
                                    "tmsh save /sys config\n",
                                    "date\n",
                                    "# remove_license_from_bigiq.sh uses firstrun.config but for security purposes, typically want to remove firstrun.config\n",
                                    "# rm /tmp/firstrun.config\n"
                               ]             


            if license_type == "bigiq":

                metadata = Metadata(
                        Init({
                            'config': InitConfig(
                                files=InitFiles(
                                    {
                                        '/tmp/firstrun.config': InitFile(
                                            content=Join('', firstrun_config ),
                                            mode='000755',
                                            owner='root',
                                            group='root'
                                        ),
                                        '/tmp/firstrun.utils': InitFile(
                                            source='http://cdn.f5.com/product/templates/utils/firstrun.utils',
                                            mode='000755',
                                            owner='root',
                                            group='root'
                                        ),
                                        '/tmp/license_from_bigiq.sh': InitFile(
                                            source='http://cdn.f5.com/product/templates/utils/license_from_bigiq_v5.0.sh',
                                            mode='000755',
                                            owner='root',
                                            group='root'
                                        ),
                                        '/tmp/remove_license_from_bigiq.sh': InitFile(
                                            source='http://cdn.f5.com/product/templates/utils/remove_license_from_bigiq_v5.0.sh',
                                            mode='000755',
                                            owner='root',
                                            group='root'
                                        ),
                                        '/shared/f5-cloud-libs/scripts/aws/firstrun.sh': InitFile(
                                            content=Join('', firstrun_sh ),
                                            mode='000755',
                                            owner='root',
                                            group='root'
                                        )
                                    } 
                                ),
                                commands={
                                            "002-onboard-BIG-IP": {
                                                "command": { "Fn::Join" : [ " ", onboard_BIG_IP
                                                                          ]
                                                }
                                            }

                                }
                            ) 
                        })
                    )
            else:
                metadata = Metadata(
                        Init({
                            'config': InitConfig(
                                files=InitFiles(
                                    {
                                        '/tmp/firstrun.config': InitFile(
                                            content=Join('', firstrun_config ),
                                            mode='000755',
                                            owner='root',
                                            group='root'
                                        ),
                                        '/tmp/firstrun.utils': InitFile(
                                            source='http://cdn.f5.com/product/templates/utils/firstrun.utils',
                                            mode='000755',
                                            owner='root',
                                            group='root'
                                        ),
                                        '/tmp/firstrun.sh': InitFile(
                                            content=Join('', firstrun_sh ),
                                            mode='000755',
                                            owner='root',
                                            group='root'
                                        )
                                    } 
                                ),
                                sources= {
                                            "/shared": "https://f5-cloud-libs.s3.amazonaws.com/f5-cloud-libs.tar.gz"
                                },
                                commands={
                                            "001-onboard-BIG-IP": {
                                                "command": { 
                                                    "Fn::Join" : [ " ", onboard_BIG_IP
                                                                 ]
                                                }
                                            },
                                            "firstrun-BIG-IP": {
                                                "command": { 
                                                    "Fn::Join" : [ " ", firstrun_BIG_IP
                                                                 ]
                                                }
                                            },
                                }
                            ) 
                        })
                    )

            NetworkInterfaces = []

            if num_nics == 1:
                NetworkInterfaces = [
                    NetworkInterfaceProperty(
                        DeviceIndex="0",
                        NetworkInterfaceId=Ref(ExternalInterface),
                        Description="Public or External Interface",
                    ),
                ]

            if num_nics == 2:  
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

            if num_nics == 3:  
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
                    NetworkInterfaceProperty(
                        DeviceIndex="2",
                        NetworkInterfaceId=Ref(InternalInterface),
                        Description="Private or Internal Interface",
                    ), 
                ]

            if ha_type != "standalone" and (BIGIP_INDEX + 1) == CLUSTER_SEED:
                RESOURCES[BigipInstance] = t.add_resource(Instance(
                    BigipInstance,
                    DependsOn="Bigip" + str(BIGIP_INDEX + 2) + "Instance",
                    Metadata=metadata,
                    UserData=Base64(Join("", ["#!/bin/bash\n", "/opt/aws/apitools/cfn-init-1.4-0.amzn1/bin/cfn-init -v -s ", Ref("AWS::StackId"), " -r ", BigipInstance , " --region ", Ref("AWS::Region"), "\n"])),
                    Tags=Tags(
                        Name=Join("", ["Big-IP: ", Ref("AWS::StackName")] ),
                        Application=Ref("AWS::StackName"),
                    ),
                    ImageId=FindInMap("BigipRegionMap", Ref("AWS::Region"), Ref(BigipPerformanceType)),
                    KeyName=Ref(KeyName),
                    InstanceType=Ref(BigipInstanceType),
                    NetworkInterfaces=NetworkInterfaces
                ))
            else:
                RESOURCES[BigipInstance] = t.add_resource(Instance(
                    BigipInstance,
                    Metadata=metadata,
                    UserData=Base64(Join("", ["#!/bin/bash\n", "/opt/aws/apitools/cfn-init-1.4-0.amzn1/bin/cfn-init -v -s ", Ref("AWS::StackId"), " -r ", BigipInstance , " --region ", Ref("AWS::Region"), "\n"])),
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

    if network == True:
        Vpc = t.add_output(Output(
            "Vpc",
            Description="VPC ID",
            Value=Ref(Vpc),
        ))

        DnsServers = t.add_output(Output(
            "DnsServers",
            Description="DNS server for VPC",
            Value="10.0.0.2",
        ))

        for INDEX in range(num_azs):
            ApplicationSubnet = "Az" + str(INDEX + 1) + "ApplicationSubnet"
            OUTPUTS[ApplicationSubnet] = t.add_output(Output(
                ApplicationSubnet,
                Description="Az" + str(INDEX + 1) +  "Application Subnet Id",
                Value=Ref(ApplicationSubnet),
            ))

        for INDEX in range(num_azs):
            ExternalSubnet = "Az" + str(INDEX + 1) + "ExternalSubnet"
            OUTPUTS[ExternalSubnet] = t.add_output(Output(
                ExternalSubnet,
                Description="Az" + str(INDEX + 1) +  "External Subnet Id",
                Value=Ref(ExternalSubnet),
            ))

        if num_nics > 1:
            for INDEX in range(num_azs):
                ManagementSubnet = "Az" + str(INDEX + 1) + "ManagementSubnet"
                OUTPUTS[ManagementSubnet] = t.add_output(Output(
                    ManagementSubnet,
                    Description="Az" + str(INDEX + 1) +  "Management Subnet Id",
                    Value=Ref(ManagementSubnet),
                ))

        if num_nics > 2:
            for INDEX in range(num_azs):
                InternalSubnet = "Az" + str(INDEX + 1) + "InternalSubnet"
                OUTPUTS[InternalSubnet] = t.add_output(Output(
                    InternalSubnet,
                    Description="Az" + str(INDEX + 1) +  "Internal Subnet Id",
                    Value=Ref(InternalSubnet),
                ))

    if security_groups == True:

        BigipExternalSecurityGroup = t.add_output(Output(
            "BigipExternalSecurityGroup",
            Description="Public or External Security Group",
            Value=Ref(BigipExternalSecurityGroup),
        ))

        if num_nics > 1:
            BigipManagementSecurityGroup = t.add_output(Output(
                "BigipManagementSecurityGroup",
                Description="Management Security Group",
                Value=Ref(BigipManagementSecurityGroup),
            ))

        if num_nics > 2:
            BigipInternalSecurityGroup = t.add_output(Output(
                "BigipInternalSecurityGroup",
                Description="Private or Internal Security Group",
                Value=Ref(BigipInternalSecurityGroup),
            ))


    if bigip == True:

        for BIGIP_INDEX in range(num_bigips): 

            ExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalInterface"
            ExternalInterfacePrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalInterfacePrivateIp"
            ExternalSelfEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalSelfEipAddress"
            ExternalSelfEipAssociation = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalSelfEipAssociation"
            ExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalInterface"
            BigipInstance = "Bigip" + str(BIGIP_INDEX + 1) + "Instance"
            BigipInstanceId = "Bigip" + str(BIGIP_INDEX + 1) + "InstanceId"
            BigipUrl = "Bigip" + str(BIGIP_INDEX + 1) + "Url"
            AvailabilityZone = "AvailabilityZone" + str(BIGIP_INDEX + 1)

            OUTPUTS[BigipInstanceId] = t.add_output(Output(
                BigipInstanceId,
                Description="Instance Id of Big-IP in Amazon",
                Value=Ref(BigipInstance),
            ))

            OUTPUTS[AvailabilityZone] = t.add_output(Output(
                AvailabilityZone,
                Description="Availability Zone",
                Value=GetAtt(BigipInstance, "AvailabilityZone"),
            ))

            OUTPUTS[ExternalInterface] = t.add_output(Output(
                ExternalInterface,
                Description="External interface Id on Big-IP",
                Value=Ref(ExternalInterface),
            ))

            OUTPUTS[ExternalInterfacePrivateIp] = t.add_output(Output(
                ExternalInterfacePrivateIp,
                Description="Internally routable Ip of public interface on BIG-IP",
                Value=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
            ))

            OUTPUTS[ExternalSelfEipAddress] = t.add_output(Output(
                ExternalSelfEipAddress,
                Description="IP Address of External interface attached to BIG-IP",
                Value=Ref(ExternalSelfEipAddress),
            ))

            if num_nics == 1:

                VipEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "VipEipAddress"

                OUTPUTS[BigipUrl] = t.add_output(Output(
                    BigipUrl,
                    Description="Big-IP Management GUI",
                    Value=Join("", [ "https://", GetAtt(BigipInstance, "PublicIp"), ":", Ref(BigipManagementGuiPort) ]),
                ))

                OUTPUTS[VipEipAddress] = t.add_output(Output(
                    VipEipAddress,
                    Description="EIP address for VIP",
                    Value=Join("", ["http://", GetAtt(BigipInstance, "PublicIp") , ":80"]),
                ))


            if num_nics > 1:


                ManagementInterface = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementInterface"
                ManagementInterfacePrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementInterfacePrivateIp"
                ManagementEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementEipAddress"
                VipPrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "VipPrivateIp"
                VipEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "VipEipAddress"

                OUTPUTS[BigipUrl] = t.add_output(Output(
                    BigipUrl,
                    Description="Big-IP Management GUI",
                    Value=Join("", ["https://", GetAtt(BigipInstance, "PublicIp")]),
                ))

                OUTPUTS[ManagementInterface] = t.add_output(Output(
                    ManagementInterface,
                    Description="Management interface Id on BIG-IP",
                    Value=Ref(ManagementInterface),
                ))

                OUTPUTS[ManagementInterfacePrivateIp] = t.add_output(Output(
                    ManagementInterfacePrivateIp,
                    Description="Internally routable Ip of management interface on BIG-IP",
                    Value=GetAtt(ManagementInterface, "PrimaryPrivateIpAddress"),
                ))

                OUTPUTS[ManagementEipAddress] = t.add_output(Output(
                    ManagementEipAddress,
                    Description="Ip address of management port on BIG-IP",
                    Value=Ref(ManagementEipAddress),
                ))

                if ha_type == "standalone":
                    OUTPUTS[VipPrivateIp] = t.add_output(Output(
                        VipPrivateIp,
                        Description="VIP on External Interface Secondary IP 1",
                        Value=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                    ))

                    OUTPUTS[VipEipAddress] = t.add_output(Output(
                        VipEipAddress,
                        Description="EIP address for VIP",
                        Value=Join("", ["http://", Ref(VipEipAddress), ":80"]),
                    ))
                else:
                    # if clustered, needs to be cluster seed
                    if (BIGIP_INDEX + 1) == CLUSTER_SEED:
                        OUTPUTS[VipPrivateIp] = t.add_output(Output(
                            VipPrivateIp,
                            Description="VIP on External Interface Secondary IP 1",
                            Value=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                        ))

                        OUTPUTS[VipEipAddress] = t.add_output(Output(
                            VipEipAddress,
                            Description="EIP address for VIP",
                            Value=Join("", ["http://", Ref(VipEipAddress), ":80"]),
                        ))

            if num_nics > 2:

                InternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "InternalInterface"
                InternalInterfacePrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "InternalInterfacePrivateIp"

                OUTPUTS[InternalInterface] = t.add_output(Output(
                    InternalInterface,
                    Description="Internal interface ID on BIG-IP",
                    Value=Ref(InternalInterface),
                ))

                OUTPUTS[InternalInterfacePrivateIp] = t.add_output(Output(
                    InternalInterfacePrivateIp,
                    Description="Internally routable IP of internal interface on BIG-IP",
                    Value=GetAtt(InternalInterface, "PrimaryPrivateIpAddress"),
                ))

    if webserver == True:
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


    if stack == "full":
        print(t.to_json(indent=1))
    else:
        print(t.to_json(indent=2))  

if __name__ == "__main__":
    main()
