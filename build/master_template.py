# /usr/bin/python env
import sys
import requests
import urllib3
from optparse import OptionParser
import json
from troposphere import Base64, Select, Split, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template, Condition, Equals, And, Or, Not, If
from troposphere.cloudformation import Init, Metadata, InitConfig, InitFiles, InitFile
from troposphere.policies import CreationPolicy, ResourceSignal
from troposphere.s3 import Bucket, PublicRead, BucketOwnerFullControl, BucketPolicy
import troposphere.iam as iam
from awacs.aws import Statement, Principal, Allow, Policy
from awacs.sts import AssumeRole
from troposphere.ec2 import *
import troposphere.ec2 as ec2
import troposphere.autoscaling as autoscaling
import troposphere.sqs as sqs
import troposphere.sns as sns
from troposphere.policies import (
    AutoScalingRollingUpdate, UpdatePolicy
)
from troposphere.cloudwatch import Alarm

def usage():
    print("OPTIONS:")
    print("     -s  stack  <network, security_groups, infra, full or existing>")
    print("     -a  <number of AvailabilityZones>")
    print("     -b  <number of BIG-IPs>")
    print("     -n  <number of NICs>. <1, 2, 3 or 8>")
    print("     -l  license  <BYOL, hourly or BIG-IQ>")
    print("     -c  components <WAF, autoscale, etc.>")
    print("     -H  ha-type <autoscale, standalone, same-az, across-az>")
    print("USAGE: ")
    print(" ex. " + sys.argv[0] + " -s network -n 1")
    print(" ex. " + sys.argv[0] + " -s network -n 2 -a 2")
    print(" ex. " + sys.argv[0] + " -s security_groups -n 2")
    print(" ex. " + sys.argv[0] + " -s infra -n 2")
    print(" ex. " + sys.argv[0] + " -s full -n 1 -l byol")
    print(" ex. " + sys.argv[0] + " -s existing -n 2 -l bigiq")
    print(" ex. " + sys.argv[0] + " -s existing -n 2 -l bigiq -c waf -H across-az")

def add_template_description_autoscale(t_license_type, t_components):
    if t_license_type == "bigiq":
        if 'waf' in t_components:
            t_description = "Deploys an AWS Auto Scaling group of F5 WAF BYOL instances licensed by BIG-IQ. Example scaling policies and CloudWatch alarms are associated with the Auto Scaling group."
        else:
            t_description = "Deploys an AWS Auto Scaling group of F5 LTM BYOL instances licensed by BIG-IQ. Example scaling policies and CloudWatch alarms are associated with the Auto Scaling group."
    elif t_license_type == "hourly":
        if 'waf' in t_components:
            t_description = "Deploys an AWS Auto Scaling group of F5 WAF PAYG instances. Example scaling policies and CloudWatch alarms are associated with the Auto Scaling group."
        else:
            t_description = "Deploys an AWS Auto Scaling group of F5 LTM PAYG instances. Example scaling policies and CloudWatch alarms are associated with the Auto Scaling group."
    return t_description

def add_mappings_autoscale():
    print("STUB for add_mapping_autoscale")

def add_outputs_autoscale():
    print("STUB for add_outputs_autoscale")

def add_security_group_resource(t, restrictedSrcAddress, managementGuiPort, restrictedSrcAddressApp, Vpc):
    return t.add_resource(SecurityGroup(
        "bigipExternalSecurityGroup",
        SecurityGroupIngress=[
            SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=22,
                ToPort=22,
                CidrIp=Ref(restrictedSrcAddress),
            ),
            SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=Ref(managementGuiPort),
                ToPort=Ref(managementGuiPort),
                CidrIp=Ref(restrictedSrcAddress),
            ),
            SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=80,
                ToPort=80,
                CidrIp=Ref(restrictedSrcAddressApp),
            ),
            SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=443,
                ToPort=443,
                CidrIp=Ref(restrictedSrcAddressApp),
            ),
        ],
        VpcId=Ref(Vpc),
        GroupDescription="Public or External interface rules, including BIG-IP management",
        Tags=Tags(
            Name=Join("", ["Bigip Security Group: ", Ref("AWS::StackName")]),
            Application=Ref("application"),
            Environment=Ref("environment"),
            Group=Ref("group"),
            Owner=Ref("owner"),
            Costcenter=Ref("costcenter"),
        ),
    ))

def add_security_group_ingress_resource(t, bigipExternalSecurityGroup, name, ip_protocol, from_port, to_port):
    return t.add_resource(SecurityGroupIngress(
        name,
        GroupId=Ref(bigipExternalSecurityGroup),
        IpProtocol=ip_protocol,
        FromPort=from_port,
        ToPort=to_port,
        SourceSecurityGroupId=Ref(bigipExternalSecurityGroup),
    ))

def build_cloudlibs_sh(cfe_verify, comment_out, package_as3):
    cloudlibs_sh = [
        "\n",
        "#!/bin/bash",
        "echo about to execute",
        "checks=0",
        "while [ $checks -lt 120 ]; do echo checking mcpd",
        "    tmsh -a show sys mcp-state field-fmt | grep -q running",
        "    if [ $? == 0 ]; then",
        "        echo mcpd ready",
        "        break",
        "    fi",
        "    echo mcpd not ready yet",
        "    let checks=checks+1",
        "    sleep 10",
        "done",
        "echo loading verifyHash script",
        str(comment_out) + "if ! tmsh load sys config merge file /config/verifyHash; then",
        str(comment_out) + "    echo cannot validate signature of /config/verifyHash",
        str(comment_out) + "    exit",
        str(comment_out) + "fi",
        str(comment_out) + "echo loaded verifyHash",
        str(comment_out) + "declare -a filesToVerify=(\"/config/cloud/f5-cloud-libs.tar.gz\" \"/config/cloud/f5-cloud-libs-aws.tar.gz\")",
        str(comment_out) + "for fileToVerify in \"${filesToVerify[@]}\"",
        str(comment_out) + "do",
        str(comment_out) + "    echo verifying \"$fileToVerify\"",
        str(comment_out) + "    if ! tmsh run cli script verifyHash \"$fileToVerify\"; then",
        str(comment_out) + "        echo \"$fileToVerify\" is not valid",
        str(comment_out) + "        exit 1",
        str(comment_out) + "    fi",
        str(comment_out) + "    echo verified \"$fileToVerify\"",
        str(comment_out) + "done",
        "mkdir -p /config/cloud/aws/node_modules/@f5devcentral",
        "echo expanding f5-cloud-libs.tar.gz",
        "tar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/aws/node_modules/@f5devcentral",
    ]

    cloudlibs_sh += [
        "echo installing dependencies",
        "tar xvfz /config/cloud/f5-cloud-libs-aws.tar.gz -C /config/cloud/aws/node_modules/@f5devcentral",
        "echo cloud libs install complete",
    ]
    cloudlibs_sh += [
        "touch /config/cloud/cloudLibsReady"
    ]
    return cloudlibs_sh

def build_get_nameserver():
    get_nameserver = [
        "\n",
        "INTERFACE=$1",
        "INTERFACE_MAC=`ifconfig ${INTERFACE} | egrep ether | awk '{print tolower($2)}'`",
        "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`",
        "VPC_CIDR_BLOCK=`/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${INTERFACE_MAC}/vpc-ipv4-cidr-block`",
        "VPC_NET=${VPC_CIDR_BLOCK%/*}",
        "NAME_SERVER=`echo ${VPC_NET} | awk -F. '{ printf \"%d.%d.%d.%d\", $1, $2, $3, $4+2 }'`",
        "echo $NAME_SERVER"
    ]
    return get_nameserver

def build_waitthenrun_sh():
    waitthenrun_sh = [
        "\n",
        "#!/bin/bash",
        "while true; do echo \"waiting for cloud libs install to complete\"",
        "    if [ -f /config/cloud/cloudLibsReady ]; then",
        "        break",
        "    else",
        "        sleep 10",
        "    fi",
        "done",
        "\"$@\""
    ]
    return waitthenrun_sh


def build_rm_password_sh():
    rm_password_sh = [
        "",
        "#!/bin/bash\n",
        "PROGNAME=$(basename $0)\n",
        "function error_exit {\n",
        "echo \"${PROGNAME}: ${1:-\"Unknown Error\"}\" 1>&2\n",
        "exit 1\n",
        "}\n",
        "date\n",
        "echo 'starting rm-srv-user'\n",
        "declare -a tmsh=()\n",
    ]


def build_init_commands(ha_type, loglevel, components, license_type, BIGIP_VERSION, template_name, version, package_as3, runtime_init_url, package_runtime_init):

    download_runtime_command = "/usr/bin/curl -fv --retry 1 --connect-timeout 5 -L " + runtime_init_url + " -o " + "/var/config/rest/downloads/" + package_runtime_init + "\n"
    install_runtime_command = "bash " + "/var/config/rest/downloads/" + package_runtime_init + " -- '--cloud aws'\n"

    unpack_libs = [
        "mkdir -p /var/log/cloud/aws;",
        "nohup /config/installCloudLibs.sh",
        "&>> /var/log/cloud/aws/install.log < /dev/null &"
    ]

    if ha_type == 'autoscale':

        network_config = [
            "nohup /config/waitThenRun.sh",
            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
            "--file /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/aws/1nicSetup.sh",
            "--cwd /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/aws",
            "--log-level " + loglevel,
            "-o /var/log/cloud/aws/1nicSetup.log",
            "--signal NETWORK_CONFIG_DONE",
            "&>> /var/log/cloud/aws/install.log < /dev/null",
            "&"
        ]

        set_masterKey = [
            "nohup /config/waitThenRun.sh",
            " f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
            " --signal MASTER_KEY_CONFIGURED",
            " --wait-for NETWORK_CONFIG_DONE",
            " --file f5-rest-node",
            " --cl-args '/config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/setMasterKey --log-level silly --cloud aws --provider-options s3Bucket:",
            {"Ref": "S3Bucket"},
            ",mgmtPort:",
            {"Ref": "managementGuiPort"},
            "' --log-level silly",
            " -o /var/log/cloud/aws/setMasterKey.log",
            " &>> /var/log/cloud/aws/install.log < /dev/null",
            " &"
        ]

        generate_password = [
            "nohup /config/waitThenRun.sh",
            " f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
            " --signal PASSWORD_CREATED",
            " --wait-for MASTER_KEY_CONFIGURED",
            " --file f5-rest-node",
            " --cl-args '/config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/generatePassword --file /config/cloud/aws/.adminPassword --encrypt --include-special-characters'",
            " --log-level " + loglevel,
            " -o /var/log/cloud/aws/generatePassword.log",
            " &>> /var/log/cloud/aws/install.log < /dev/null",
            " &"
        ]


        admin_user = [
            "nohup /config/waitThenRun.sh",
            " f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
        ]

        admin_user += [
        " --wait-for PASSWORD_CREATED",
        " --signal ADMIN_CREATED",
        " --file /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/createUser.sh",
        " --cl-args '--user ",
        {"Ref": "adminUsername"},
        " --password-file /config/cloud/aws/.adminPassword",
        " --password-encrypted",
        "'",
        " --log-level " + loglevel,
        " -o /var/log/cloud/aws/createUser.log",
        " &>> /var/log/cloud/aws/install.log < /dev/null",
        " &"
        ]

        onboard_BIG_IP_metrics = [
            "DEPLOYMENTID=`echo \"",
            {
                "Ref": "AWS::StackId"
            },
            "\"|sha512sum|cut -d \" \" -f 1`;",
            "CUSTOMERID=`echo \"",
            {
                "Ref": "AWS::AccountId"
            },
            "\"|sha512sum|cut -d \" \" -f 1`;",
            "NAME_SERVER=`/config/cloud/aws/getNameServer.sh eth0`;",
            "nohup /config/waitThenRun.sh",
            "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`;",
            "HOSTNAME=`/usr/bin/curl -sS --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`;",
            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/onboard.js",
            "--log-level " + loglevel,
            "--wait-for ADMIN_CREATED",
            "--signal ONBOARD_DONE",
            "-o /var/log/cloud/aws/onboard.log",
            "--host localhost",
            "--user",
            {"Ref": "adminUsername"},
            "--password-url file:///config/cloud/aws/.adminPassword",
            "--password-encrypted",
            "--hostname ${HOSTNAME}",
            "--ntp ",
            {"Ref": "ntpServer"},
            "--tz ",
            {"Ref": "timezone"},
            "--dns ${NAME_SERVER}",
            "--port 8443",
            "--ssl-port ",
            {"Ref": "managementGuiPort"},
            "--modules ",
            {"Ref": "bigIpModules"},
            # "--metrics \"cloudName:aws,region:${region},bigipVersion:13.1.0.2,customerId:${CUSTOMERID},deploymentId:${DEPLOYMENTID},templateName:f5-payg-autoscale-bigip-ltm.template,templateVersion:3.2.0,licenseType:payg\"",
            # "--metrics \"cloudName:aws,region:${region},bigipVersion:13.1.0.2,customerId:${CUSTOMERID},deploymentId:${DEPLOYMENTID},templateName:",
            # f5-payg-autoscale-bigip-ltm.template,
            # "templateVersion:3.2.0,licenseType:",
            # payg,
            # "\"",
            "--metrics \"cloudName:aws,region:${REGION},bigipVersion:" + BIGIP_VERSION + ",customerId:${CUSTOMERID},deploymentId:${DEPLOYMENTID},templateName:" + template_name + ",templateVersion:" + version + ",licenseType:" + license_type + "\"",
            "-d tm.tcpudptxchecksum:software-only ",
            "--ping",
            "&>> /var/log/cloud/aws/install.log < /dev/null",
            "&"
        ]
        onboard_BIG_IP = [
            "NAME_SERVER=`/config/cloud/aws/getNameServer.sh eth0`;",
            "nohup /config/waitThenRun.sh",
            "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`;",
            "HOSTNAME=`/usr/bin/curl -sS --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`;",
            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/onboard.js",
            "--log-level " + loglevel,
            "--wait-for ADMIN_CREATED",
            "--signal ONBOARD_DONE",
            "-o /var/log/cloud/aws/onboard.log",
            "--host localhost",
            "--port 8443",
            "--user",
            {"Ref": "adminUsername"},
            "--password-url file:///config/cloud/aws/.adminPassword",
            "--password-encrypted",
            "--hostname ${HOSTNAME}",
            "--ntp ",
            {"Ref": "ntpServer"},
            "--tz ",
            {"Ref": "timezone"},
            "--dns ${NAME_SERVER}",
            "--ssl-port ",
            {"Ref": "managementGuiPort"},
            "--modules ",
            {"Ref": "bigIpModules"},
            "-d tm.tcpudptxchecksum:software-only ",
            "--ping",
            "&>> /var/log/cloud/aws/install.log < /dev/null",
            "&"
        ]
        onboard_lists = [onboard_BIG_IP_metrics, onboard_BIG_IP]

        if license_type == "bigiq":
            for list in onboard_lists:
                ping = list.index("--ping")
                list[ping:ping] = [
                    "--license-pool --cloud aws",
                    "--big-iq-host",
                    {
                        "Ref": "bigIqAddress"
                    },
                    "--big-iq-user ",
                    {
                        "Ref": "bigIqUsername"
                    },
                    "--big-iq-password-uri ",
                    {
                        "Ref": "bigIqPasswordS3Arn"
                    },
                    "--license-pool-name ",
                    {
                        "Ref": "bigIqLicensePoolName"
                    },
                    "--tenant ",
                    {
                        "Fn::If": [
                            "noTenant",
                            {
                                "Ref": "AWS::NoValue"
                            },
                            {
                                "Ref": "bigIqLicenseTenant"
                            }
                        ]
                    },
                    "--unit-of-measure ",
                    {
                        "Fn::If": [
                            "noUnitOfMeasure",
                            {
                                "Ref": "AWS::NoValue"
                            },
                            {
                                "Ref": "bigIqLicenseUnitOfMeasure"
                            }
                        ]
                    },
                    "--sku-keyword-1 ",
                    {
                        "Fn::If": [
                            "noSkuKeyword1",
                            {
                                "Ref": "AWS::NoValue"
                            },
                            {
                                "Ref": "bigIqLicenseSkuKeyword1"
                            }
                        ]
                    },
                    "--sku-keyword-2 ",
                    {
                        "Fn::If": [
                            "noSkuKeyword2",
                            {
                                "Ref": "AWS::NoValue"
                            },
                            {
                                "Ref": "bigIqLicenseSkuKeyword2"
                            }
                        ]
                    }
                ]

        custom_command = [
            "nohup /config/waitThenRun.sh",
            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
            "--log-level " + loglevel,
            "--file /config/cloud/aws/custom-config.sh",
            "--cwd /config/cloud/aws",
            "-o /var/log/cloud/aws/custom-config.log",
            "--wait-for ONBOARD_DONE",
            "--signal CUSTOM_CONFIG_DONE",
            "&>> /var/log/cloud/aws/install.log < /dev/null",
            "&"
        ]

        verify_deployment = [
            "nohup /config/waitThenRun.sh",
            " f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
            " --wait-for CUSTOM_CONFIG_DONE",
            " --signal DEPLOYMENT_VERIFIED",
            " --file /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs-aws/scripts/verifyDeploymentCompletion.js",
            " --cl-args '--user ",
            {
                "Ref": "adminUsername"
            },
            " --password-url file:///config/cloud/aws/.adminPassword",
            " --password-encrypted true",
            " --host localhost",
            " --port ",
            {
                "Ref": "managementGuiPort"
            },
            " --solution autoscale",
            " --log-level silly",
            " --instances-count ",
            {
                "Ref": "scalingMinSize"
            },
            "'",
            " --log-level silly",
            " -o /var/log/cloud/aws/verifyDeploymentCompletion.log",
            " &>> /var/log/cloud/aws/install.log < /dev/null",
            " &"
        ]


        commands = {
            '000-disable-1nicautoconfig': {'command': "/usr/bin/setdb provision.1nicautoconfig disable"},
            '001-rest-provision-extramb': {'command': "/usr/bin/setdb provision.extramb 1000"},
            '002-rest-use-extramb': {'command': "/usr/bin/setdb restjavad.useextramb true"},
            '003-rest-post': {'command': "/usr/bin/curl -s -f -u admin: -H \"Content-Type: application/json\" -d '{\"maxMessageBodySize\":134217728}' -X POST http://localhost:8100/mgmt/shared/server/messaging/settings/8100 | jq ."},
            '004-rest-restart': {'command': "bigstart restart restjavad restnoded"},
            '010-install-libs': {'command': {"Fn::Join": [" ", unpack_libs]}},
            '015-network-config': {'command': {"Fn::Join": [" ", network_config]}},
            '017-set-master-key': {'command': {"Fn::Join": ["", set_masterKey]}},
            '020-generate-password': {'command': {"Fn::Join": ["", generate_password]}},
            '030-create-admin-user': {'command': {"Fn::Join": ["", admin_user]}},
            '050-onboard-BIG-IP': {'command': {"Fn::If": ["optin", {"Fn::Join": [" ", onboard_BIG_IP_metrics]}, {"Fn::Join": [" ", onboard_BIG_IP]}]}},
            '060-custom-config': {'command': {"Fn::Join": [" ", custom_command]}},
            '070-verify-deployment': {'command':{"Fn::Join":[" ",verify_deployment]}},
        }

    else:
        generate_password = [
            "nohup /config/waitThenRun.sh",
            " f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
            " --signal PASSWORD_CREATED",
            " --file f5-rest-node",
            " --cl-args '/config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/generatePassword --file /config/cloud/aws/.adminPassword --encrypt --include-special-characters'",
            " --log-level " + loglevel,
            " -o /var/log/cloud/aws/generatePassword.log",
            " &>> /var/log/cloud/aws/install.log < /dev/null",
            " &"
        ]
        admin_user = [
            "nohup /config/waitThenRun.sh",
            " f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
        ]
        admin_user += [
            " --wait-for PASSWORD_CREATED",
            " --signal ADMIN_CREATED",
            " --file /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/createUser.sh",
            " --cl-args '--user ",
            {"Ref": "adminUsername"},
            " --password-file /config/cloud/aws/.adminPassword",
            " --password-encrypted",
            "'",
            " --log-level " + loglevel,
            " -o /var/log/cloud/aws/createUser.log",
            " &>> /var/log/cloud/aws/install.log < /dev/null",
            " &"
        ]
        network_config = [
            "nohup /config/waitThenRun.sh",
            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
            "--file /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/aws/1nicSetup.sh",
            "--cwd /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/aws",
            "--log-level " + loglevel,
            "-o /var/log/cloud/aws/1nicSetup.log",
            "--wait-for ADMIN_CREATED",
            "--signal NETWORK_CONFIG_DONE",
            "&>> /var/log/cloud/aws/install.log < /dev/null",
            "&"
        ]
        onboard_BIG_IP_metrics = [
            "DEPLOYMENTID=`echo \"",
            {
                "Ref": "AWS::StackId"
            },
            "\"|sha512sum|cut -d \" \" -f 1`;",
            "CUSTOMERID=`echo \"",
            {
                "Ref": "AWS::AccountId"
            },
            "\"|sha512sum|cut -d \" \" -f 1`;",
            "NAME_SERVER=`/config/cloud/aws/getNameServer.sh eth0`;",
            "nohup /config/waitThenRun.sh",
            "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`;",
            "HOSTNAME=`/usr/bin/curl -sS --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`;",
            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/onboard.js",
            "--log-level " + loglevel,
            "--wait-for NETWORK_CONFIG_DONE",
            "--signal ONBOARD_DONE",
            "-o /var/log/cloud/aws/onboard.log",
            "--host localhost",
            "--user",
            {"Ref": "adminUsername"},
            "--password-url file:///config/cloud/aws/.adminPassword",
            "--password-encrypted",
            "--hostname ${HOSTNAME}",
            "--ntp ",
            {"Ref": "ntpServer"},
            "--tz ",
            {"Ref": "timezone"},
            "--dns ${NAME_SERVER}",
            "--port 8443",
            "--ssl-port ",
            {"Ref": "managementGuiPort"},
            "--modules ",
            {"Ref": "bigIpModules"},
            # "--metrics \"cloudName:aws,region:${region},bigipVersion:13.1.0.2,customerId:${CUSTOMERID},deploymentId:${DEPLOYMENTID},templateName:f5-payg-autoscale-bigip-ltm.template,templateVersion:3.2.0,licenseType:payg\"",
            # "--metrics \"cloudName:aws,region:${region},bigipVersion:13.1.0.2,customerId:${CUSTOMERID},deploymentId:${DEPLOYMENTID},templateName:",
            # f5-payg-autoscale-bigip-ltm.template,
            # "templateVersion:3.2.0,licenseType:",
            # payg,
            # "\"",
            "--metrics \"cloudName:aws,region:${REGION},bigipVersion:" + BIGIP_VERSION + ",customerId:${CUSTOMERID},deploymentId:${DEPLOYMENTID},templateName:" + template_name + ",templateVersion:" + version + ",licenseType:" + license_type + "\"",
            "-d tm.tcpudptxchecksum:software-only ",
            "--ping",
            "&>> /var/log/cloud/aws/install.log < /dev/null",
            "&"
        ]
        onboard_BIG_IP = [
            "NAME_SERVER=`/config/cloud/aws/getNameServer.sh eth0`;",
            "nohup /config/waitThenRun.sh",
            "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`;",
            "HOSTNAME=`/usr/bin/curl -sS --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`;",
            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/onboard.js",
            "--log-level " + loglevel,
            "--wait-for NETWORK_CONFIG_DONE",
            "--signal ONBOARD_DONE",
            "-o /var/log/cloud/aws/onboard.log",
            "--host localhost",
            "--port 8443",
            "--user",
            {"Ref": "adminUsername"},
            "--password-url file:///config/cloud/aws/.adminPassword",
            "--password-encrypted",
            "--hostname ${HOSTNAME}",
            "--ntp ",
            {"Ref": "ntpServer"},
            "--tz ",
            {"Ref": "timezone"},
            "--dns ${NAME_SERVER}",
            "--ssl-port ",
            {"Ref": "managementGuiPort"},
            "--modules ",
            {"Ref": "bigIpModules"},
            "-d tm.tcpudptxchecksum:software-only ",
            "--ping",
            "&>> /var/log/cloud/aws/install.log < /dev/null",
            "&"
        ]
        onboard_lists = [onboard_BIG_IP_metrics, onboard_BIG_IP]

        if license_type == "bigiq":
            for list in onboard_lists:
                ping = list.index("--ping")
                list[ping:ping] = [
                    "--license-pool --cloud aws",
                    "--big-iq-host",
                    {
                        "Ref": "bigIqAddress"
                    },
                    "--big-iq-user ",
                    {
                        "Ref": "bigIqUsername"
                    },
                    "--big-iq-password-uri ",
                    {
                        "Ref": "bigIqPasswordS3Arn"
                    },
                    "--license-pool-name ",
                    {
                        "Ref": "bigIqLicensePoolName"
                    },
                    "--tenant ",
                    {
                        "Fn::If": [
                            "noTenant",
                            {
                                "Ref": "AWS::NoValue"
                            },
                            {
                                "Ref": "bigIqLicenseTenant"
                            }
                        ]
                    },
                    "--unit-of-measure ",
                    {
                        "Fn::If": [
                            "noUnitOfMeasure",
                            {
                                "Ref": "AWS::NoValue"
                            },
                            {
                                "Ref": "bigIqLicenseUnitOfMeasure"
                            }
                        ]
                    },
                    "--sku-keyword-1 ",
                    {
                        "Fn::If": [
                            "noSkuKeyword1",
                            {
                                "Ref": "AWS::NoValue"
                            },
                            {
                                "Ref": "bigIqLicenseSkuKeyword1"
                            }
                        ]
                    },
                    "--sku-keyword-2 ",
                    {
                        "Fn::If": [
                            "noSkuKeyword2",
                            {
                                "Ref": "AWS::NoValue"
                            },
                            {
                                "Ref": "bigIqLicenseSkuKeyword2"
                            }
                        ]
                    }
                ]

        custom_command = [
            "nohup /config/waitThenRun.sh",
            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
            "--log-level " + loglevel,
            "--file /config/cloud/aws/custom-config.sh",
            "--cwd /config/cloud/aws",
            "-o /var/log/cloud/aws/custom-config.log",
            "--wait-for ONBOARD_DONE",
            "&>> /var/log/cloud/aws/install.log < /dev/null",
            "&"
        ]

        commands = {
            '000-disable-1nicautoconfig': {'command': "/usr/bin/setdb provision.1nicautoconfig disable"},
            # '001-rest-provision-extramb': {'command': "/usr/bin/setdb provision.extramb 1000"},
            # '002-rest-use-extramb': {'command': "/usr/bin/setdb restjavad.useextramb true"},
            # '003-rest-post': {'command': "/usr/bin/curl -s -f -u admin: -H \"Content-Type: application/json\" -d '{\"maxMessageBodySize\":134217728}' -X POST http://localhost:8100/mgmt/shared/server/messaging/settings/8100 | jq ."},
            # '004-rest-restart': {'command': "bigstart restart restjavad restnoded"},
            '010-install-libs': {'command': {"Fn::Join": [" ", unpack_libs]}},
            '020-generate-password': {'command': {"Fn::Join": ["", generate_password]}},
            '030-create-admin-user': {'command': {"Fn::Join": ["", admin_user]}},
            '040-network-config': {'command': {"Fn::Join": [" ", network_config]}},
            '050-onboard-BIG-IP': {'command': {"Fn::If": ["optin", {"Fn::Join": [" ", onboard_BIG_IP_metrics]}, {"Fn::Join": [" ", onboard_BIG_IP]}]}},
            '060-custom-config': {'command': {"Fn::Join": [" ", custom_command]}},
        }

        commands['065-cluster'] = {'command': {"Fn::Join": [" ", cluster_command]}}
        commands['070-rm-password'] = {'command': {"Fn::Join": [" ", rm_password_command]}}

    return commands

def create_launch_config_metadata(ha_type, cloudlib_url, cloudlib_aws_url, as3_url, lines, cloudlibs_sh, waitthenrun_sh, get_nameserver, loglevel, components, license_type, BIGIP_VERSION, template_name, version, package_as3, runtime_init_url, package_runtime_init):
    mode = '000755'
    owner = 'root'
    group = 'root'

    onboard_config_vars = [
        "",
        "#!/bin/bash\n",
        "# Generated from " + version + "\n",
        "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`\n",
        "HOSTNAME=`/usr/bin/curl -sS --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`\n",
        "region='", {"Ref": "AWS::Region"}, "'\n",
        "deploymentName='", {"Ref": "deploymentName"}, "'\n",
        "adminUsername='", {"Ref": "adminUsername"}, "'\n",
        "managementGuiPort='", {"Ref": "managementGuiPort"}, "'\n",
        "timezone='", {"Ref": "timezone"}, "'\n",
        "ntpServer='", {"Ref": "ntpServer"}, "'\n",
        "virtualServicePort='", {"Ref": "virtualServicePort"}, "'\n",
        "applicationPort='", {"Ref": "applicationPort"}, "'\n",
        "appInternalDnsName='", {"Ref": "appInternalDnsName"}, "'\n",
        "applicationPoolTagKey='", {"Ref": "applicationPoolTagKey"}, "'\n",
        "applicationPoolTagValue='", {"Ref": "applicationPoolTagValue"}, "'\n",
        "s3Bucket='", {"Ref": "S3Bucket"}, "'\n",
        "sqsUrl='", {"Ref": "SQSQueue"}, "'\n",
        "declarationUrl='", {"Ref": "declarationUrl"}, "'\n",
        "allowPhoneHome='", {"Ref": "allowPhoneHome"}, "'\n"
    ]

    if 'nlb' in components:
        as3_service_type = "Service_HTTPS"
        as3_template_type = "https"
    else:
        as3_service_type = "Service_HTTP"
        as3_template_type = "http"

    if 'waf' in components:
        onboard_config_vars.extend([
            "policyLevel='", {"Ref": "policyLevel"}, "'\n",
            "passwd=$(f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/decryptDataFromFile.js --data-file /config/cloud/aws/.adminPassword)\n",
            "payload='{\"class\":\"ADC\",\"schemaVersion\":\"3.0.0\",\"label\":\"autoscale_waf\",\"id\":\"AUTOSCALE_WAF\",\"remark\":\"Autoscale WAF\",\"waf\":{\"class\":\"Tenant\",\"Shared\":{\"class\":\"Application\",\"template\":\"shared\",\"serviceAddress\":{\"class\":\"Service_Address\",\"virtualAddress\":\"0.0.0.0\"},\"policyWAF\":{\"class\":\"WAF_Policy\",\"file\":\"/tmp/as30-linux-medium.xml\"}},\"http\":{\"class\":\"Application\",\"template\":\"" + as3_template_type + "\",\"serviceMain\":{\"class\":\"" + as3_service_type + "\",\"virtualAddresses\":[{\"use\":\"/waf/Shared/serviceAddress\"}],\"serverTLS\":{\"bigip\":\"/Common/example-clientssl-profile\"},\"snat\":\"auto\",\"securityLogProfiles\":[{\"bigip\":\"/Common/Log illegal requests\"}],\"pool\":\"pool\",\"policyWAF\":{\"use\":\"/waf/Shared/policyWAF\"}},\"pool\":{\"class\":\"Pool\",\"monitors\":[\"http\"],\"members\":[{\"autoPopulate\":true,\"hostname\":\"demo.example.com\",\"servicePort\":80,\"addressDiscovery\":\"aws\",\"updateInterval\":15,\"tagKey\":\"applicationPoolTagKey\",\"tagValue\":\"applicationPoolTagValue\",\"addressRealm\":\"private\",\"region\":\"us-west-2\"}]}}}}'\n"
        ])
    else:
        onboard_config_vars.extend([
            "passwd=$(f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/decryptDataFromFile.js --data-file /config/cloud/aws/.adminPassword)\n",
            "payload='{\"class\":\"ADC\",\"schemaVersion\":\"3.0.0\",\"label\":\"autoscale_ltm\",\"id\":\"AUTOSCALE_LTM\",\"remark\":\"Autoscale LTM\",\"ltm\":{\"class\":\"Tenant\",\"Shared\":{\"class\":\"Application\",\"template\":\"shared\",\"serviceAddress\":{\"class\":\"Service_Address\",\"virtualAddress\":\"0.0.0.0\"}},\"http\":{\"class\":\"Application\",\"template\":\"" + as3_template_type + "\",\"serviceMain\":{\"class\":\"" + as3_service_type + "\",\"virtualAddresses\":[{\"use\":\"/ltm/Shared/serviceAddress\"}],\"serverTLS\":{\"bigip\":\"/Common/example-clientssl-profile\"},\"snat\":\"auto\",\"pool\":\"pool\"},\"pool\":{\"class\":\"Pool\",\"monitors\":[\"http\"],\"members\":[{\"autoPopulate\":true,\"hostname\":\"demo.example.com\",\"servicePort\":80,\"addressDiscovery\":\"aws\",\"updateInterval\":15,\"tagKey\":\"applicationPoolTagKey\",\"tagValue\":\"applicationPoolTagValue\",\"addressRealm\":\"private\",\"region\":\"us-west-2\"}]}}}}'\n"
        ])

    custom_sh_bigiq = ""
    run_autoscale_update_bigiq = []
    if license_type == "bigiq":
        onboard_config_vars_bigiq = [
            "bigIqAddress='", {"Ref": "bigIqAddress"}, "'\n",
            "bigIqUsername='", {"Ref": "bigIqUsername"}, "'\n",
            "bigIqPasswordS3Arn='", {"Ref": "bigIqPasswordS3Arn"}, "'\n",
            "bigIqLicensePoolName='", {"Ref": "bigIqLicensePoolName"}, "'\n",
            "bigIqLicenseTenant='", {"Ref": "bigIqLicenseTenant"}, "'\n",
            "bigIqLicenseUnitOfMeasure='", {"Ref": "bigIqLicenseUnitOfMeasure"}, "'\n",
            "bigIqLicenseSkuKeyword1='", {"Ref": "bigIqLicenseSkuKeyword1"}, "'\n",
            "bigIqLicenseSkuKeyword2='", {"Ref": "bigIqLicenseSkuKeyword2"}, "'\n"
        ]
        onboard_config_vars.extend(onboard_config_vars_bigiq)
        # set custom_sh partial statement
        custom_sh_bigiq = "--license-pool --big-iq-host ${bigIqAddress} --big-iq-user ${bigIqUsername} --big-iq-password-uri ${bigIqPasswordS3Arn} --license-pool-name ${bigIqLicensePoolName} "
        run_autoscale_update_bigiq = [
            " --license-pool --big-iq-host ",
            {"Ref": "bigIqAddress"},
            " --big-iq-user ",
            {"Ref": "bigIqUsername"},
            " --big-iq-password-uri ",
            {"Ref": "bigIqPasswordS3Arn"},
            " --license-pool-name ",
            {"Ref": "bigIqLicensePoolName"},
        ]
    custom_sh_dns = ""  # define
    if 'dns' in components:
        onboard_config_vars.extend([
            "dnsMemberIpType='", {"Fn::If": ["usePublicIP", {"Ref": "dnsMemberIpType"},"private"]}, "'\n",
            "dnsMemberPort='", {"Ref": "dnsMemberPort"}, "'\n",
            "dnsProviderHost='", {"Ref": "dnsProviderHost"}, "'\n",
            "dnsProviderPort='", {"Ref": "dnsProviderPort"}, "'\n",
            "dnsProviderUser='", {"Ref": "dnsProviderUser"}, "'\n",
            "dnsPasswordS3Arn='", {"Ref": "dnsPasswordS3Arn"}, "'\n",
            "dnsProviderPool='", {"Ref": "dnsProviderPool"}, "'\n",
            "dnsProviderDataCenter='", {"Ref": "dnsProviderDataCenter"}, "'\n"
        ])
        # set custom_sh partial statement
        custom_sh_dns = "--dns gtm --dns-ip-type ${dnsMemberIpType} --dns-app-port ${dnsMemberPort} --dns-provider-options host:${dnsProviderHost},port:${dnsProviderPort},user:${dnsProviderUser},passwordUrl:${dnsPasswordS3Arn},serverName:${deploymentName},poolName:${dnsProviderPool},datacenter:${dnsProviderDataCenter} "
    elif 'nlb' in components:
        onboard_config_vars.extend([
            "appCertificateS3Arn='", {"Ref": "appCertificateS3Arn"}, "'\n"
        ])

    custom_sh = [
        "",
        "#!/bin/bash\n",
        "# Generated from " + version + "\n",
        "date\n",
        ". /config/cloud/aws/onboard_config_vars\n",
        "if [[ $allowPhoneHome == \"No\" ]]; then\n",
        "    tmsh modify sys software update auto-phonehome disabled\n",
        "fi\n",
        "tmsh create sys icall script uploadMetrics definition { exec /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs-aws/scripts/reportMetrics.sh }\n",
        "tmsh create sys icall handler periodic /Common/metricUploadHandler { first-occurrence now interval 60 script /Common/uploadMetrics }\n",
        "tmsh save /sys config\n",
        "echo 'Attempting to Join or Initiate Autoscale Cluster' \n",
        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/autoscale.js --cloud aws --provider-options s3Bucket:${s3Bucket},sqsUrl:${sqsUrl},mgmtPort:${managementGuiPort} --host localhost --port ${managementGuiPort} --user ${adminUsername} --password-url file:///config/cloud/aws/.adminPassword --password-encrypted --device-group autoscale-group --block-sync -c join --log-level " + loglevel + " --output /var/log/cloud/aws/autoscale.log " + custom_sh_bigiq + custom_sh_dns + "\n",
        "if [ -f /config/cloud/master ]; then \n",
        "  if `jq '.ucsLoaded' < /config/cloud/master`; then \n",
        "    echo \"UCS backup loaded from backup folder in S3 bucket ${s3Bucket}.\"\n",
        "  else\n",
        "    echo 'SELF-SELECTED as Master ... Initiated Autoscale Cluster ... Loading default config'\n",
    ]
    if 'waf' in components:
        custom_sh.extend([
            "    tmsh modify cm device-group autoscale-group asm-sync enabled\n",
        ])
    if 'waf' in components:
        custom_sh.extend([
            "    source /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/waitForBigip.sh;wait-for-bigip\n",
        ])
    custom_sh.extend([
        "    ### START CUSTOM CONFIGURATION\n",
        "    deployed=\"no\"\n",
        "    url_regex=\"(http:\/\/|https:\/\/)?[a-z0-9]+([\\-\\.]{1}[a-z0-9]+)*\\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$\"\n",
        "    file_loc=\"/config/cloud/custom_config\"\n",
        "    if [[ $declarationUrl =~ $url_regex ]]; then\n",
        "       response_code=$(/usr/bin/curl -sk -w \"%{http_code}\" $declarationUrl -o $file_loc)\n",
        "       if [[ $response_code == 200 ]]; then\n",
        "           echo \"Custom config download complete; checking for valid JSON.\"\n",
        "           cat $file_loc | jq .class\n",
        "           if [[ $? == 0 ]]; then\n",
        "               response_code=$(/usr/bin/curl -svvu admin: -w \"%{http_code}\" -X POST -H \"Content-Type: application/json\" -H \"Expect:\" http://localhost:8100/mgmt/shared/appsvcs/declare -d @$file_loc -o /dev/null)\n",
        "           if [[ $response_code == 200 || $response_code == 502 ]]; then\n",
        "               echo \"Deployment of custom application succeeded.\"\n",
        "               deployed=\"yes\"\n",
        "           else\n",
        "               echo \"Failed to deploy custom application; continuing...\"\n",
        "           fi\n",
        "       else\n",
        "           echo \"Custom config was not valid JSON, continuing...\"\n",
        "       fi\n",
        "       else\n",
        "           echo \"Failed to download custom config; continuing...\"\n",
        "       fi\n",
        "   else\n",
        "      echo \"Custom config was not a URL, continuing...\"\n",
        "   fi\n",
        "   if [[ $deployed == \"no\" && $declarationUrl == \"default\" ]]; then\n",
    ])
    if 'waf' in components:
        custom_sh.extend([
            "        asm_policy=\"/config/cloud/asm-policy-linux-${policyLevel}.xml\"\n",
            "        payload=$(echo $payload | jq -c --arg asm_policy $asm_policy --arg pool_http_port $applicationPort --arg vs_http_port $virtualServicePort '.waf.Shared.policyWAF.file = $asm_policy | .waf.http.pool.members[0].servicePort = ($pool_http_port | tonumber) | .waf.http.serviceMain.virtualPort = ($vs_http_port | tonumber)')\n",
        ])
    else:
        custom_sh.extend([
            "       payload=$(echo $payload | jq -c --arg pool_http_port $applicationPort --arg vs_http_port $virtualServicePort '.ltm.http.pool.members[0].servicePort = ($pool_http_port | tonumber) | .ltm.http.serviceMain.virtualPort = ($vs_http_port | tonumber)')\n",
        ])
    if 'nlb' in components:
        custom_sh.extend([
            "       if [[ \"${appCertificateS3Arn}\" != \"default\" ]]; then\n",
            "           f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs-aws/scripts/getCertFromS3.js ${appCertificateS3Arn}\n",
            "           tmsh install sys crypto pkcs12 site.example.com from-local-file /config/ssl/ssl.key/${appCertificateS3Arn##*/}\n",
            "           tmsh create ltm profile client-ssl example-clientssl-profile cert site.example.com.crt key site.example.com.key\n",
            "       else\n",
            "           tmsh create ltm profile client-ssl example-clientssl-profile cert default.crt key default.key\n",
            "       fi\n",
        ])
    else:
        if 'waf' in components:
            custom_sh.extend([
                "    payload=$(echo $payload | jq -c 'del(.waf.http.serviceMain.serverTLS)')\n",
            ])
        else:
            custom_sh.extend([
                "    payload=$(echo $payload | jq -c 'del(.ltm.http.serviceMain.serverTLS)')\n",
            ])
    if 'waf' in components:
        custom_sh.extend([
            "        if [ \"${applicationPoolTagKey}\" != \"default\" ]\n",
            "        then\n",
            "            payload=$(echo $payload | jq -c 'del(.waf.http.pool.members[0].autoPopulate) | del(.waf.http.pool.members[0].hostname)')\n",
            "            payload=$(echo $payload | jq -c --arg tagKey $applicationPoolTagKey --arg tagValue $applicationPoolTagValue --arg region $region '.waf.http.pool.members[0].tagKey = $tagKey | .waf.http.pool.members[0].tagValue = $tagValue | .waf.http.pool.members[0].region = $region')\n",
            "        else\n",
            "            payload=$(echo $payload | jq -c 'del(.waf.http.pool.members[0].updateInterval) | del(.waf.http.pool.members[0].tagKey) | del(.waf.http.pool.members[0].tagValue) | del(.waf.http.pool.members[0].addressRealm) | del(.waf.http.pool.members[0].region)')\n",
            "            payload=$(echo $payload | jq -c --arg pool_member $appInternalDnsName '.waf.http.pool.members[0].hostname = $pool_member | .waf.http.pool.members[0].addressDiscovery = \"fqdn\"')\n",
            "        fi\n",
        ])
    else:
        custom_sh.extend([
            "       if [ \"${applicationPoolTagKey}\" != \"default\" ]\n",
            "       then\n",
            "           payload=$(echo $payload | jq -c 'del(.ltm.http.pool.members[0].autoPopulate) | del(.ltm.http.pool.members[0].hostname)')\n",
            "           payload=$(echo $payload | jq -c --arg tagKey $applicationPoolTagKey --arg tagValue $applicationPoolTagValue --arg region $region '.ltm.http.pool.members[0].tagKey = $tagKey | .ltm.http.pool.members[0].tagValue = $tagValue | .ltm.http.pool.members[0].region = $region')\n",
            "       else\n",
            "           payload=$(echo $payload | jq -c 'del(.ltm.http.pool.members[0].updateInterval) | del(.ltm.http.pool.members[0].tagKey) | del(.ltm.http.pool.members[0].tagValue) | del(.ltm.http.pool.members[0].addressRealm) | del(.ltm.http.pool.members[0].region)')\n",
            "           payload=$(echo $payload | jq -c --arg pool_member $appInternalDnsName '.ltm.http.pool.members[0].hostname = $pool_member | .ltm.http.pool.members[0].addressDiscovery = \"fqdn\"')\n",
            "       fi\n",
        ])

    custom_sh.extend([
        "        response_code=$(/usr/bin/curl -svvu admin: -w \"%{http_code}\" -X POST -H \"Content-Type: application/json\" -H \"Expect:\" http://localhost:8100/mgmt/shared/appsvcs/declare -d \"$payload\" -o /dev/null)\n",
        "        if [[ $response_code == 200 || $response_code == 502  ]]; then\n",
        "            echo 'Deployment of recommended application succeeded.'\n",
        "        else\n",
        "            echo 'Failed to deploy recommended application'\n",
        "            exit 1\n",
        "        fi\n",
        "    fi\n",
        "    ### END CUSTOM CONFIGURATION\n",
        "    tmsh save /sys config\n",
        "    f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/autoscale.js --cloud aws --provider-options s3Bucket:${s3Bucket},sqsUrl:${sqsUrl},mgmtPort:${managementGuiPort}",
        "      --host localhost --port ${managementGuiPort} --user ${adminUsername} --password-url file:///config/cloud/aws/.adminPassword --password-encrypted -c unblock-sync --log-level " + loglevel + " --output /var/log/cloud/aws/autoscale.log " + custom_sh_bigiq + "\n",
        "  fi\n",
        "fi\n",
        "(crontab -l 2>/dev/null; echo '*/1 * * * * /config/cloud/aws/run_autoscale_update.sh') | crontab -\n",
        "(crontab -l 2>/dev/null; echo '59 23 * * * /config/cloud/aws/run_autoscale_backup.sh') | crontab -\n",
        "tmsh save /sys config\n",
        "systemctl restart crond\n",
        "date\n",
        "echo 'custom-config.sh complete'\n"
    ])

    run_autoscale_update = [
        "",
        "#!/bin/bash\n",
        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/autoscale.js",
        " --cloud aws --provider-options '",
        "s3Bucket:",
        {"Ref": "S3Bucket"},
        ",sqsUrl:",
        {"Ref": "SQSQueue"},
        ",mgmtPort:",
        {"Ref": "managementGuiPort"},
        "'",
        " --host localhost",
        " --port ",
        {"Ref": "managementGuiPort"},
        " --user ",
        {"Ref": "adminUsername"},
        " --password-url file:///config/cloud/aws/.adminPassword",
        " --password-encrypted",
        " --device-group autoscale-group",
        " --cluster-action update",
        " --log-level " + loglevel + " --output /var/log/cloud/aws/autoscale.log "
    ] + run_autoscale_update_bigiq
    if 'dns' in components:
        run_autoscale_update.extend([
            " --dns gtm",
            " --dns-ip-type ",
            {"Ref": "dnsMemberIpType"},
            " --dns-app-port ",
            {"Ref": "dnsMemberPort"},
            " --dns-provider-options host:",
            {"Ref": "dnsProviderHost"},
            ",port:",
            {"Ref": "dnsProviderPort"},
            ",user:",
            {"Ref": "dnsProviderUser"},
            ",passwordUrl:",
            {"Ref": "dnsPasswordS3Arn"},
            ",serverName:",
            {"Ref": "deploymentName"},
            ",poolName:",
            {"Ref": "dnsProviderPool"},
            ",datacenter:",
            {"Ref": "dnsProviderDataCenter"},
        ])
    run_autoscale_backup = [
        "",
        "#!/bin/bash\n",
        "source /config/cloud/aws/onboard_config_vars\n",
        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/autoscale.js",
        " --cloud aws --provider-options '",
        "s3Bucket:",
        {"Ref": "S3Bucket"},
        ",sqsUrl:",
        {"Ref": "SQSQueue"},
        ",mgmtPort:",
        {"Ref": "managementGuiPort"},
        "'",
        " --host localhost",
        " --port ",
        {"Ref": "managementGuiPort"},
        " --user ",
        {"Ref": "adminUsername"},
        " --password-url file:///config/cloud/aws/.adminPassword",
        " --password-encrypted",
        " --device-group autoscale-group",
        " --cluster-action backup-ucs",
        " --log-level " + loglevel + " --output /var/log/cloud/aws/autoscale.log",
    ]

    # Modify lists received from main() if 'waf' in components

    cloudlibs_sh.insert(len(cloudlibs_sh) - 2, "tar xvfz /config/cloud/asm-policy-linux.tar.gz -C /config/cloud")

    files = {
        # source
        '/config/cloud/f5-cloud-libs.tar.gz': {'source': cloudlib_url},
        '/config/cloud/f5-cloud-libs-aws.tar.gz': {'source': cloudlib_aws_url},
        # content
        '/config/verifyHash': {'content': lines},  # target convert to /config/cloud after all fix?
        '/config/installCloudLibs.sh': {'content': cloudlibs_sh},  # target convert to /config/cloud after all fix?
        '/config/waitThenRun.sh': {'content': waitthenrun_sh},  # target convert to /config/cloud after non as fix
        '/config/cloud/aws/custom-config.sh': {'content': custom_sh},
        '/config/cloud/aws/getNameServer.sh': {'content': get_nameserver},
        '/config/cloud/aws/onboard_config_vars': {'content': onboard_config_vars},
        # '/config/cloud/aws/getNameServer.sh': {'content':'Join(\'\n\', ' + ','.join(get_nameserver) + ')'},
        # '/config/cloud/aws/rm-password.sh': {'content':'Join(\'\', ' + ','.join(rm_password_sh) + ')'},
    }
    if ha_type != 'autoscale':
        # source
        files['/config/cloud/aws/rm-srv-user.sh'] = {'content': 'Join(\'\', ' + ','.join(rm_password_sh) + ')'}
        # content

    if ha_type == 'autoscale':
        # source
        if 'waf' in components:
            files['/config/cloud/asm-policy-linux.tar.gz'] = {'source': 'http://cdn.f5.com/product/cloudsolutions/solution-scripts/asm-policy-linux.tar.gz'}
        # content
        files['/config/cloud/aws/run_autoscale_update.sh'] = {'content': run_autoscale_update}
        files['/config/cloud/aws/run_autoscale_backup.sh'] = {'content': run_autoscale_backup}

    # Build input for InitFile()
    init_files = {}
    for file, info in files.items():
        if list(info.keys())[0] == 'source':
            init_files[file] = InitFile(
                source=str(list(info.values())[0]),
                mode=mode,
                owner=owner,
                group=group
            )
        elif list(info.keys())[0] == 'content':
            init_files[file] = InitFile(
                content=Join(list(info.values())[0].pop(0), list(info.values())[0]),
                mode=mode,
                owner=owner,
                group=group
            )
    # Build input for init commands
    d = build_init_commands(ha_type, loglevel, components, license_type, BIGIP_VERSION, template_name, version, package_as3, runtime_init_url, package_runtime_init)

    metadata = Metadata(
        Init({
            'config': InitConfig(
                files=InitFiles(init_files),
                commands=d
            )
        })
    )
    return metadata


def add_resources_autoscale(ha_type, t, restrictedSrcAddress, managementGuiPort, restrictedSrcAddressApp, Vpc, cloudlib_url, cloudlib_aws_url, as3_url, lines, comment_out, loglevel, components, license_type, BIGIP_VERSION, template_name, version, package_as3, runtime_init_url, package_runtime_init, download_runtime_command, install_runtime_command):
    ud = Base64(Join('', [
                "#!/bin/bash -x\n",
                "mkdir -p /var/log/cloud /config/cloud /var/config/rest/downloads\n",
                "/usr/bin/setdb provision.extramb 1000\n",
                "/usr/bin/setdb restjavad.useextramb true\n",
                "cat << EOF >> /config/cloud/runtime-init-config.yaml\n",
                "controls:\n",
                "  logLevel: info\n",
                "  logFilename: /var/log/cloud/bigIpRuntimeInit.log\n",
                "extension_packages:\n",
                "  install_operations:\n",
                "    - extensionType: as3\n",
                "      extensionVersion: 3.34.0\n",
                "      extensionHash: 05a80ec0848dc5b8876b78a8fbee2980d5a1671d635655b3af604dc830d5fed4\n",
                "EOF\n",
                download_runtime_command,
                install_runtime_command,
                "f5-bigip-runtime-init --config-file /config/cloud/runtime-init-config.yaml --skip-telemetry\n",
                "/opt/aws/apitools/cfn-init/bin/cfn-init -v -s ",
                {
                    "Ref": "AWS::StackId"
                },
                " -r BigipLaunchConfig",
                " --region ",
                {
                    "Ref": "AWS::Region"
                },
                "\n"
                ]))

    bigipExternalSecurityGroup = add_security_group_resource(t, restrictedSrcAddress, managementGuiPort, restrictedSrcAddressApp, Vpc)
    add_security_group_ingress_resource(t, bigipExternalSecurityGroup, "bigipSecurityGroupIngressManagementGuiPort", "tcp", Ref(managementGuiPort), Ref(managementGuiPort))
    add_security_group_ingress_resource(t, bigipExternalSecurityGroup, "bigipSecurityGroupIngressConfigSync", "tcp", 4353, 4353)
    add_security_group_ingress_resource(t, bigipExternalSecurityGroup, "bigipSecurityGroupIngressAsmPolicySync", "tcp", 6123, 6128)
    t.add_resource(Bucket("S3Bucket", AccessControl=BucketOwnerFullControl,))
    t.add_resource(sqs.Queue("SQSQueue", MessageRetentionPeriod=3600,))
    t.add_resource(sns.Topic("SNSTopic", Subscription=[sns.Subscription(
                                                       Protocol="email",
                                                       Endpoint=Ref("notificationEmail")
                                                       )]))
    # build PolicyDocument statement list
    default_policy_document_statement = [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": {
                "Fn::Join": [
                    "",
                    [
                        "arn:*:s3:::",
                        {
                            "Ref": "S3Bucket"
                        }
                    ]
                ]
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": {
                "Fn::Join": [
                    "",
                    [
                        "arn:*:s3:::",
                        {
                            "Ref": "S3Bucket"
                        },
                        "/*"
                    ]
                ]
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage"
            ],
            "Resource": {
                "Fn::GetAtt": ["SQSQueue", "Arn"]
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:DescribeAutoScalingGroups",
                "autoscaling:DescribeAutoScalingInstances",
                "autoscaling:SetInstanceProtection",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeAddresses",
                "ec2:AssociateAddress",
                "ec2:DisassociateAddress",
                "ec2:DescribeSubnets",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeNetworkInterfaceAttribute",
                "ec2:DescribeRouteTables",
                "ec2:AssignPrivateIpAddresses",
                "ec2:DescribeTags",
                "ec2:CreateTags",
                "ec2:DeleteTags",
                "cloudwatch:PutMetricData",
                "cloudformation:ListStackResources",
                "cloudformation:SignalResource"
            ],
            "Resource": [
                "*"
            ]
        }
    ]

    if license_type == "bigiq":
        bigiq_action = [{
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": {
                "Ref": "bigIqPasswordS3Arn"
            }
        }]
        default_policy_document_statement.extend(bigiq_action)

    if 'dns' in components:
        dns_action = [{
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": {
                "Ref": "dnsPasswordS3Arn"
            }
        }]
        default_policy_document_statement.extend(dns_action)

    if 'nlb' in components:
        t.add_resource(iam.Role("BigipAutoScalingAccessRole",
                                AssumeRolePolicyDocument={
                                    "Version": "2012-10-17",
                                    "Statement": [
                                        {
                                            "Effect": "Allow",
                                            "Principal": {
                                                "Service": [
                                                    "ec2.amazonaws.com"
                                                ]
                                            },
                                            "Action": [
                                                "sts:AssumeRole"
                                            ]
                                        }
                                    ]
                                },
                                Path="/",
                                Policies=[
                                    If("useDefaultCert",
                                        iam.Policy(
                                            PolicyName="BigipAutoScalingAcccessPolicy",
                                            PolicyDocument={
                                                "Version": "2012-10-17",
                                                "Statement": default_policy_document_statement
                                            }
                                        ),
                                        iam.Policy(
                                            PolicyName="BigipAutoScalingAcccessPolicy",
                                            PolicyDocument={
                                                "Version": "2012-10-17",
                                                "Statement": default_policy_document_statement +
                                                [
                                                    {
                                                        "Action": [
                                                            "s3:GetObject"
                                                        ],
                                                        "Effect": "Allow",
                                                        "Resource": {
                                                            "Ref": "appCertificateS3Arn"
                                                        }
                                                    }
                                                ]
                                            }
                                        ))
                                ]))
    else:
        t.add_resource(iam.Role("BigipAutoScalingAccessRole",
                                AssumeRolePolicyDocument={
                                    "Version": "2012-10-17",
                                    "Statement": [
                                        {
                                            "Effect": "Allow",
                                            "Principal": {
                                                "Service": [
                                                    "ec2.amazonaws.com"
                                                ]
                                            },
                                            "Action": [
                                                "sts:AssumeRole"
                                            ]
                                        }
                                    ]
                                },
                                Path="/",
                                Policies=[
                                    iam.Policy(
                                        PolicyName="BigipAutoScalingAcccessPolicy",
                                        PolicyDocument={
                                            "Version": "2012-10-17",
                                            "Statement": default_policy_document_statement
                                        }
                                    ),
                                ]))
    t.add_resource(iam.InstanceProfile(
        "BigipAutoScalingInstanceProfile",
        Path="/",
        Roles=[Ref("BigipAutoScalingAccessRole")]
    ))

    # launch config metadata
    cloudlibs_sh = build_cloudlibs_sh('', comment_out,package_as3)
    waitthenrun_sh = build_waitthenrun_sh()
    get_nameserver = build_get_nameserver()
    get_lines = ["", lines]
    launch_config_metadata = create_launch_config_metadata(ha_type, cloudlib_url, cloudlib_aws_url, as3_url, get_lines, cloudlibs_sh, waitthenrun_sh, get_nameserver, loglevel, components, license_type, BIGIP_VERSION, template_name, version, package_as3, runtime_init_url, package_runtime_init)

    # set vars for add_resource
    if 'waf' in components:
        if license_type == "hourly":
            image_name = "Best"
        else:
            image_name = "AllTwoBootLocations"
        cooldown = "2400"
        health_check_grace_period = 1800
    else:
        image_name = Ref('imageName')
        cooldown = "1500"
        health_check_grace_period = 1800

    # build CFT statement for ImageId field in Autoscaling Launch Configuration metadata
    if license_type == "hourly":
        image_id = If("noCustomImageId",
                      FindInMap("BigipRegionMap",
                                Ref('AWS::Region'),
                                FindInMap("AWSBigipThrougput", Ref('throughput'), image_name)
                                ),
                      Ref("customImageId")
                      )
    elif license_type == "bigiq":
        image_id = If("noCustomImageId",
                      FindInMap("BigipRegionMap",
                                Ref('AWS::Region'),
                                image_name
                                ),
                      Ref("customImageId")
                      )

    t.add_resource(autoscaling.LaunchConfiguration(
        "BigipLaunchConfig",
        Metadata=launch_config_metadata,
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeType": "gp2"
                }
            },
            {
                "DeviceName": "/dev/xvdb",
                "NoDevice": True
            }
        ],
        AssociatePublicIpAddress=FindInMap('Transformations', 'Boolean', Ref('provisionPublicIP')),
        # ImageId=Ref("customImageId"),
        ImageId=image_id,
        InstanceMonitoring="false",
        InstanceType=Ref("instanceType"),
        IamInstanceProfile=Ref("BigipAutoScalingInstanceProfile"),
        KeyName=Ref("sshKey"),
        SecurityGroups=[Ref("bigipExternalSecurityGroup")],
        UserData=ud
    ))
    if 'dns' in components:
        t.add_resource(autoscaling.AutoScalingGroup(
            "BigipAutoscaleGroup",
            VPCZoneIdentifier=Ref("subnets"),
            CreationPolicy=CreationPolicy(
                ResourceSignal=ResourceSignal(Timeout='PT30M',
                                              Count=Ref("scalingMinSize"))
            ),
            Cooldown="1500",
            HealthCheckGracePeriod=1500,
            HealthCheckType="EC2",
            LaunchConfigurationName=Ref("BigipLaunchConfig"),
            MaxSize=Ref("scalingMaxSize"),
            MinSize=Ref("scalingMinSize"),
            DesiredCapacity=Ref("scalingMinSize"),
            MetricsCollection=[autoscaling.MetricsCollection(
                Granularity="1Minute"
            )],
            NotificationConfigurations=[
                autoscaling.NotificationConfigurations(
                    TopicARN=Ref("SNSTopic"),
                    NotificationTypes=[
                        "autoscaling:EC2_INSTANCE_LAUNCH",
                        "autoscaling:EC2_INSTANCE_LAUNCH_ERROR",
                        "autoscaling:EC2_INSTANCE_TERMINATE",
                        "autoscaling:EC2_INSTANCE_TERMINATE_ERROR"
                    ])],
            Tags=autoscaling.Tags(
                Name=Join("", ["BIG-IP Autoscale Instance: ", Ref("deploymentName")]),
                Application=Ref("application"),
                Environment=Ref("environment"),
                Group=Ref("group"),
                Owner=Ref("owner"),
                Costcenter=Ref("costcenter")
            ),
            UpdatePolicy=UpdatePolicy(
                AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                    PauseTime='PT30M',
                    MinInstancesInService=1,
                    MaxBatchSize=1
                )
            )
        ))
    elif 'nlb' in components:
        t.add_resource(autoscaling.AutoScalingGroup(
            "BigipAutoscaleGroup",
            VPCZoneIdentifier=Ref("subnets"),
            Cooldown="1500",
            TargetGroupARNs=[
                If("noTargetGroup",
                    Ref("AWS::NoValue"),
                    Ref("bigipNetworkLoadBalancerTargetGroupsArns")
                   )
            ],
            CreationPolicy=CreationPolicy(
                ResourceSignal=ResourceSignal(Timeout='PT30M',
                                              Count=Ref("scalingMinSize"))
            ),
            HealthCheckGracePeriod=1500,
            HealthCheckType="EC2",
            LaunchConfigurationName=Ref("BigipLaunchConfig"),
            MaxSize=Ref("scalingMaxSize"),
            MinSize=Ref("scalingMinSize"),
            DesiredCapacity=Ref("scalingMinSize"),
            MetricsCollection=[autoscaling.MetricsCollection(
                Granularity="1Minute"
            )],
            NotificationConfigurations=[
                autoscaling.NotificationConfigurations(
                    TopicARN=Ref("SNSTopic"),
                    NotificationTypes=[
                        "autoscaling:EC2_INSTANCE_LAUNCH",
                        "autoscaling:EC2_INSTANCE_LAUNCH_ERROR",
                        "autoscaling:EC2_INSTANCE_TERMINATE",
                        "autoscaling:EC2_INSTANCE_TERMINATE_ERROR"
                    ]
                )],
            Tags=autoscaling.Tags(
                Name=Join("", ["BIG-IP Autoscale Instance: ", Ref("deploymentName")]),
                Application=Ref("application"),
                Environment=Ref("environment"),
                Group=Ref("group"),
                Owner=Ref("owner"),
                Costcenter=Ref("costcenter")
            ),
            UpdatePolicy=UpdatePolicy(
                AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                    PauseTime='PT30M',
                    MinInstancesInService=1,
                    MaxBatchSize=1
                ))
        ))
    else:
        t.add_resource(autoscaling.AutoScalingGroup(
            "BigipAutoscaleGroup",
            VPCZoneIdentifier=Ref("subnets"),
            Cooldown="1500",
            CreationPolicy=CreationPolicy(
                ResourceSignal=ResourceSignal(Timeout='PT30M',
                                              Count=Ref("scalingMinSize"))
            ),
            LoadBalancerNames=[
                Ref("bigipElasticLoadBalancer")
            ],
            HealthCheckGracePeriod=1500,
            HealthCheckType="EC2",
            LaunchConfigurationName=Ref("BigipLaunchConfig"),
            MaxSize=Ref("scalingMaxSize"),
            MinSize=Ref("scalingMinSize"),
            DesiredCapacity=Ref("scalingMinSize"),
            MetricsCollection=[autoscaling.MetricsCollection(
                Granularity="1Minute"
            )],
            NotificationConfigurations=[
                autoscaling.NotificationConfigurations(
                    TopicARN=Ref("SNSTopic"),
                    NotificationTypes=[
                        "autoscaling:EC2_INSTANCE_LAUNCH",
                        "autoscaling:EC2_INSTANCE_LAUNCH_ERROR",
                        "autoscaling:EC2_INSTANCE_TERMINATE",
                        "autoscaling:EC2_INSTANCE_TERMINATE_ERROR"
                    ]
                )],
            Tags=autoscaling.Tags(
                Name=Join("", ["BIG-IP Autoscale Instance: ", Ref("deploymentName")]),
                Application=Ref("application"),
                Environment=Ref("environment"),
                Group=Ref("group"),
                Owner=Ref("owner"),
                Costcenter=Ref("costcenter")
            ),
            UpdatePolicy=UpdatePolicy(
                AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                    PauseTime='PT30M',
                    MinInstancesInService=1,
                    MaxBatchSize=1
                ))
        ))

    t.add_resource(autoscaling.ScalingPolicy(
        "BigipScaleUpPolicy",
        AdjustmentType="ChangeInCapacity",
        AutoScalingGroupName=Ref("BigipAutoscaleGroup"),
        Cooldown="1500",
        ScalingAdjustment=1,

    ))
    t.add_resource(autoscaling.ScalingPolicy(
        "BigipScaleDownPolicy",
        AdjustmentType="ChangeInCapacity",
        AutoScalingGroupName=Ref("BigipAutoscaleGroup"),
        Cooldown="1500",
        ScalingAdjustment=-1,

    ))
    t.add_resource(
        Alarm(
            "BigipHighbytesAlarm",
            DependsOn="BigipAutoscaleGroup",
            ActionsEnabled=True,
            AlarmActions=[Ref("BigipScaleUpPolicy")],
            AlarmDescription="Throughput exceeds average threshold after 1 successive interval of 1 minute",
            ComparisonOperator="GreaterThanThreshold",
            EvaluationPeriods=1,
            MetricName="throughput-per-sec",
            Namespace=Ref("BigipAutoscaleGroup"),
            Period=60,
            Statistic="Average",
            Threshold=Ref("scaleUpBytesThreshold")
        ))
    t.add_resource(
        Alarm(
            "BigipLowbytesAlarm",
            DependsOn="BigipAutoscaleGroup",
            ActionsEnabled=True,
            AlarmActions=[Ref("BigipScaleDownPolicy")],
            AlarmDescription="Throughput below average threshold for 10 successive intervals of 5 minutes",
            ComparisonOperator="LessThanThreshold",
            EvaluationPeriods=10,
            MetricName="throughput-per-sec",
            Namespace=Ref("BigipAutoscaleGroup"),
            Period=300,
            Statistic="Average",
            Threshold=Ref("scaleDownBytesThreshold")
        ))
    t.add_resource(
        Alarm(
            "BigipHighCpuAlarm",
            DependsOn="BigipAutoscaleGroup",
            ActionsEnabled=True,
            AlarmActions=[Ref("BigipScaleUpPolicy")],
            AlarmDescription="CPU usage percentage exceeds average threshold after 1 successive interval of 1 minute",
            ComparisonOperator="GreaterThanThreshold",
            EvaluationPeriods=1,
            MetricName="tmm-stat",
            Namespace=Ref("BigipAutoscaleGroup"),
            Period=60,
            Statistic="Average",
            Threshold=Ref("highCpuThreshold")
        ))
    t.add_resource(
        Alarm(
            "BigipLowCpuAlarm",
            DependsOn="BigipAutoscaleGroup",
            ActionsEnabled=True,
            AlarmActions=[Ref("BigipScaleDownPolicy")],
            AlarmDescription="CPU usage percentage below average threshold after 10 successive interval of 5 minutes",
            ComparisonOperator="LessThanThreshold",
            EvaluationPeriods=10,
            MetricName="tmm-stat",
            Namespace=Ref("BigipAutoscaleGroup"),
            Period=300,
            Statistic="Average",
            Threshold=Ref("lowCpuThreshold")
        ))

def main():

    # RFE: Use Metadata / AWS::CloudFormation::Interface/  "ParameterGroups"
    # to clean up Presentation Layer

    PARAMETERS = {}
    MAPPINGS = {}
    CONDITIONS = {}
    RESOURCES = {}
    OUTPUTS = {}

    parser = OptionParser()
    parser.add_option("-s", "--stack", action="store", type="string", dest="stack", help="Stack: network, security_groups, infra, full or existing")
    parser.add_option("-a", "--num-azs", action="store", type="int", dest="num_azs", default=1, help="Number of Availability Zones")
    parser.add_option("-b", "--num-bigips", action="store", type="int", dest="num_bigips", default=1, help="Number of BIG-IPs")
    parser.add_option("-n", "--nics", action="store", type="int", dest="num_nics", default=1, help="Number of NICs: 1, 2, 3 or 8")
    parser.add_option("-l", "--license", action="store", type="string", dest="license_type", default="hourly", help="Type of License: hourly, byol, or bigiq")
    parser.add_option("-c", "--components", action="store", type="string", dest="components", help="Comma seperated list of components: ex. WAF")
    parser.add_option("-H", "--ha-type", action="store", type="string", dest="ha_type", default="standalone", help="HA Type: standalone, same-az, across-az")
    parser.add_option("-M", "--marketplace", action="store", type="string", dest="marketplace", default="no", help="Marketplace: no, Good25Mbps, Good200Mbps, Good1000Mbps, Good5000Mbps, Better25Mbps, Better200Mbps, Better1000Mbps, Better5000Mbps, Best25Mbps, Best200Mbps, Best1000Mbps, Best5000Mbps")
    parser.add_option("-T", "--template-name", action="store", type="string", dest="template_name", default="", help="Template Name: pass approprate template name.")
    (options, args) = parser.parse_args()

    num_nics = options.num_nics
    license_type = options.license_type
    stack = options.stack
    num_bigips = options.num_bigips
    ha_type = options.ha_type
    num_azs = options.num_azs
    marketplace = options.marketplace
    template_name = options.template_name

    # 1st BIG-IP will always be cluster seed
    CLUSTER_SEED = 1

    # May need to include AWS Creds for various deployments: cluster, auto-scale, etc.
    aws_creds = False

    if ha_type == "same-az":
        num_azs = 1
        num_bigips = 2
        aws_creds = False

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

    not_full_stacks = "existing", "prod"
    if stack in not_full_stacks:
        network = False
        security_groups = True
        webserver = False
        bigip = True

    # Need static private IP addresses
    reference_stacks = ("network", "security_groups", "infra", "full")
    consolidated_stacks = ("standalone", "same-az", "across-az", "autoscale")
    need_static_ip_addr = (ha_type == "standalone" and num_nics < 4 and stack not in reference_stacks)
    need_optional_public_ip = (ha_type in consolidated_stacks and stack not in reference_stacks and stack == "existing")

    # Build variables used for QA
    # Log level
    loglevel = 'silly'
    # Template Version
    version = '5.17.0'
    # Big-IP mapped
    BIGIP_VERSION = '16.1.2.2-0.0.28'
    # Cloudlib Branch
    branch_cloud = 'v4.27.0'
    branch_aws = 'v2.10.1'
    # AS3 branch and package
    branch_as3 = 'v3.31.0'
    package_as3 = 'f5-appsvcs-3.31.0-6.noarch.rpm'
    # Runtime Init
    branch_runtime_init = 'v1.4.2'
    package_runtime_init = 'f5-bigip-runtime-init-1.4.2-1.gz.run'
    runtime_init_url = 'http://cdn.f5.com/product/cloudsolutions/f5-bigip-runtime-init/' + branch_runtime_init + '/dist/' + package_runtime_init
    # Build verifyHash file from published verifyHash on CDN
    urls = ['https://cdn.f5.com/product/cloudsolutions/f5-cloud-libs/' + str(branch_cloud) + '/verifyHash']
    for url in urls:
        try:
            urllib3.disable_warnings()
            vh = requests.get(
                url,
                verify=False)
            with open('../build/verifyHash', 'w') as hash:
                hash.write(vh.text)
            with open('../build/verifyHash', 'r') as vhash:
                lines = vhash.read()
        except requests.exceptions.RequestException as e:
            print(e)
    # Files URL's
    cfe_version = "1.9.0"
    cfe_sufix = "-0"
    cfe_name = "f5-cloud-failover-" + str(cfe_version + cfe_sufix) + ".noarch.rpm"
    cfe = "/var/config/rest/downloads/" + str(cfe_name)
    if ha_type != "standalone":
        ilx_package = "--install-ilx-package file:///var/config/rest/downloads/" + str(package_as3) + " --install-ilx-package file://" + cfe
    else:
        ilx_package = "--install-ilx-package file:///var/config/rest/downloads/" + str(package_as3)

    cloudlib_url = "http://cdn.f5.com/product/cloudsolutions/f5-cloud-libs/" + str(branch_cloud) + "/f5-cloud-libs.tar.gz"
    cloudlib_url_china = "http://cdn.f5.com/product/cloudsolutions/f5-cloud-libs/" + str(branch_cloud) + "/f5-cloud-libs.tar.gz"
    cloudlib_aws_url = "http://cdn.f5.com/product/cloudsolutions/f5-cloud-libs-aws/" + str(branch_aws) + "/f5-cloud-libs-aws.tar.gz"
    cloudlib_aws_url_china = "http://cdn.f5.com/product/cloudsolutions/f5-cloud-libs-aws/" + str(branch_aws) + "/f5-cloud-libs-aws.tar.gz"

    as3_url = "http://cdn.f5.com/product/cloudsolutions/f5-appsvcs-extension/" + str(branch_as3) + "/" + str(package_as3)
    as3_url_china = "http://cdn.f5.com/product/cloudsolutions/f5-appsvcs-extension/" + str(branch_as3) + "/" + str(package_as3)

    # add hashmark to skip cloudlib verification script.
    if ha_type == "same-az" or ha_type == "across-az":
        comment_out = ""
    else:
        comment_out = ""
    # Begin Template
    t = Template()
    # add template version
    t.set_version("2010-09-09")
    # build description
    description = "Template v" + str(version) + ": "
    if stack == "network":
        description += "AWS CloudFormation Template for creating network components for a " + str(num_azs) + " Availability Zone VPC"
    elif stack == "security_groups":
        description += "AWS CloudFormation Template for creating security groups for a " + str(num_nics) + "NIC BIG-IP"
    elif stack == "infra":
        description += "AWS CloudFormation Template for creating a " + str(num_azs) + " Availability Zone VPC, subnets, security groups and a webserver (Bitnami LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
    elif stack == "full":
        if ha_type == "standalone":
            description += "AWS CloudFormation Template for creating a full stack with a " + str(num_nics) + "NIC BIG-IP, a " + str(num_azs) + " Availability Zone VPC, subnets, security groups and a webserver (Bitnami LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
        if ha_type == "same-az":
            description += "AWS CloudFormation Template for creating a full stack with a Same-AZ cluster of " + str(num_nics) + "NIC BIG-IPs, a " + str(num_azs) + " Availability Zone VPC, subnets, security groups and a webserver (Bitnami LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
        if ha_type == "across-az":
            description += "AWS CloudFormation Template for creating a full stack with a Across-AZs cluster of " + str(num_nics) + "NIC BIG-IPs, a " + str(num_azs) + " Availability Zone VPC, subnets, security groups and a webserver (Bitnami LAMP stack with username bitnami **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
    elif stack in not_full_stacks:
        if ha_type == "autoscale":
            description += add_template_description_autoscale(license_type, components)
            # if license_type == "bigiq":
            #     if 'waf' in components:
            #         description += "Deploys an AWS Auto Scaling group of F5 WAF BYOL instances licensed by BIG-IQ. Example scaling policies and CloudWatch alarms are associated with the Auto Scaling group."
            #     else:
            #         description += "Deploys an AWS Auto Scaling group of F5 LTM BYOL instances licensed by BIG-IQ. Example scaling policies and CloudWatch alarms are associated with the Auto Scaling group."
            # elif license_type == "hourly":
            #     if 'waf' in components:
            #         description += "Deploys an AWS Auto Scaling group of F5 WAF PAYG instances. Example scaling policies and CloudWatch alarms are associated with the Auto Scaling group."
            #     else:
            #         description += "Deploys an AWS Auto Scaling group of F5 LTM PAYG instances. Example scaling policies and CloudWatch alarms are associated with the Auto Scaling group."
        if ha_type == "standalone":
            description += "AWS CloudFormation Template for creating a " + str(num_nics) + "NIC BIG-IP in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
        if ha_type == "same-az":
            description += "AWS CloudFormation Template for creating a Same-AZ cluster of " + str(num_nics) + "NIC BIG-IPs in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
        if ha_type == "across-az":
            description += "AWS CloudFormation Template for creating a Across-AZs cluster of " + str(num_nics) + "NIC BIG-IPs in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template."
    # add description
    t.set_description(description)
    # Build Labels and add to metadata
    bigiq_label = ""
    bigiq_parms = []
    bigiq_label_params = {}
    bigiq_parameter_labels = []
    if ha_type == "autoscale":
        instance_config_parameters = [
            "sshKey",
            "instanceType",
            "throughput",
            "imageName",
            "customImageId",
            "adminUsername",
            "managementGuiPort",
            "timezone",
            "ntpServer"
        ]
        vs_config_parameters = ["virtualServicePort", "applicationPort", "appInternalDnsName", "applicationPoolTagKey", "applicationPoolTagValue", "declarationUrl"]

        policy_level_parameter_label = ""  # define
        if 'waf' in components:
            # modify vs_config
            vs_config_parameters.append("policyLevel")
            policy_level_parameter_label = {
                "default": "Web Application Firewall Policy Level"
            }
            # modify instance_config
            instance_config_parameters.remove("imageName")

        parameter_labels = {}  # define

        network_config_parameters = ["Vpc", "availabilityZones", "subnets", "restrictedSrcAddress", "restrictedSrcAddressApp"]
        if 'dns' in components:
            network_config_parameters.extend(["dnsMemberIpType", "dnsMemberPort", "dnsProviderHost", "dnsProviderPort", "dnsProviderUser", "dnsPasswordS3Arn", "dnsProviderPool", "dnsProviderDataCenter"])
            parameter_labels.update({
                "dnsMemberIpType": {
                    "default": "DNS Member IP Type (public | private)"
                },
                "dnsMemberPort": {
                    "default": "DNS Member Port"
                },
                "dnsProviderHost": {
                    "default": "BIG-IP DNS Management IP address (or hostname)"
                },
                "dnsProviderPort": {
                    "default": "BIG-IP DNS Management Port"
                },
                "dnsProviderUser": {
                    "default": "BIG-IP DNS user for updating DNS"
                },
                "dnsPasswordS3Arn": {
                    "default": "S3 ARN of the BIG-IP DNS Password File"
                },
                "dnsProviderPool": {
                    "default": "GSLB Pool on BIG-IP DNS"
                },
                "dnsProviderDataCenter": {
                    "default": "GSLB Datacenter on BIG-IP DNS"
                }
            })
        elif 'nlb' in components:
            network_config_parameters.append("bigipNetworkLoadBalancerTargetGroupsArns")
            vs_config_parameters.insert(1, "appCertificateS3Arn")
            parameter_labels.update({
                "bigipNetworkLoadBalancerTargetGroupsArns": {
                    "default": "Target Group(s) of Network Load Balancer for BIG-IP VEs"
                },
                "appCertificateS3Arn": {
                    "default": "S3 ARN of the SSL Certificate used for Application"
                }
            })
        else:
            network_config_parameters.append("bigipElasticLoadBalancer")
            parameter_labels.update({
                "bigipElasticLoadBalancer": {
                    "default": "Elastic Load Balancer for BIG-IP VEs"
                }
            })

        parameter_labels.update({
            "deploymentName": {
                "default": "Deployment Name"
            },
            "Vpc": {
                "default": "VPC ID"
            },
            "allowUsageAnalytics": {
                "default": "Send Anonymous Template Statistics to F5"
            },
            "allowPhoneHome": {
                "default": "Send Anonymous Device Statistics to F5"
            },
            "availabilityZones": {
                "default": "Availability Zone(s)"
            },
            "subnets": {
                "default": "Subnet ID(s)"
            },
            "restrictedSrcAddress": {
                "default": "Restricted Source Address to BIG-IP"
            },
            "restrictedSrcAddressApp": {
                "default": "Restricted Source Address to Application"
            },
            "sshKey": {
                "default": "SSH Key Name"
            },
            "instanceType": {
                "default": "AWS Instance Size"
            },
            "throughput": {
                "default": "Maximum Throughput"
            },
            "customImageId": {
                "default": "Custom Image Id"
            },
            "imageName": {
                "default": "F5 Image Name"
            },
            "adminUsername": {
                "default": "BIG-IP Admin User for clustering"
            },
            "managementGuiPort": {
                "default": "Management Port"
            },
            "timezone": {
                "default": "Timezone (Olson)"
            },
            "ntpServer": {
                "default": "NTP Server"
            },
            "bigIpModules": {
                "default": "BIG-IP Modules"
            },
            "scalingMinSize": {
                "default": "Minimum Instances"
            },
            "scalingMaxSize": {
                "default": "Maximum Instances"
            },
            "scaleDownBytesThreshold": {
                "default": "Scale Down Bytes Threshold"
            },
            "scaleUpBytesThreshold": {
                "default": "Scale Up Bytes Threshold"
            },
            "highCpuThreshold": {
                "default": "High CPU Percentage Threshold"
            },
            "lowCpuThreshold": {
                "default": "Low CPU Percentage Threshold"
            },
            "notificationEmail": {
                "default": "Notification Email"
            },
            "virtualServicePort": {
                "default": "Virtual Service Port"
            },
            "applicationPort": {
                "default": "Application Pool Member Port"
            },
            "appInternalDnsName": {
                "default": "Application Pool DNS"
            },
            "applicationPoolTagKey": {
                "default": "Application Pool Tag Key"
            },
            "applicationPoolTagValue": {
                "default": "Application Pool Tag Value"
            },
            "policyLevel": policy_level_parameter_label,
            "application": {
                "default": "Application"
            },
            "environment": {
                "default": "Environment"
            },
            "group": {
                "default": "Group"
            },
            "owner": {
                "default": "Owner"
            },
            "costcenter": {
                "default": "Cost Center"
            },
            "declarationUrl": {
                "default": "AS3 Declaration URL"
            }
        })
    elif need_static_ip_addr:
        vs_config_parameters = ["declarationUrl"]

        parameter_labels = {
            "Vpc": {
                "default": "VPC"
            },
            "managementSubnetAz1": {
                "default": "Management Subnet AZ1"
            },
            "managementSubnetAz1Address": {
                "default": "Management Subnet AZ1 Static IP Address"
            },
            "managementSubnetAz2": {
                "default": "Management Subnet AZ2"
            },
            "subnet1Az1": {
                "default": "Subnet1 in AZ1"
            },
            "subnet1Az1Address": {
                "default": "Subnet1 AZ1 Static IP Addresses"
            },
            "subnet1Az2": {
                "default": "Subnet1 in AZ2"
            },
            "subnet2Az1": {
                "default": "Subnet2 in AZ1"
            },
            "subnet2Az1Address": {
                "default": "Subnet2 AZ1 Static IP Address"
            },
            "subnet2Az2": {
                "default": "Subnet2 in AZ2"
            },
            "availabilityZone1": {
                "default": "Availability Zone 1"
            },
            "availabilityZone2": {
                "default": "Availability Zone 2"
            },
            "imageName": {
                "default": "BIG-IP Image Name"
            },
            "customImageId": {
                "default": "Custom Image Id"
            },
            "instanceType": {
                "default": "AWS Instance Size"
            },
            "applicationInstanceType": {
                "default": "Application Instance Type"
            },
            "licenseKey1": {
                "default": "License Key 1"
            },
            "licenseKey2": {
                "default": "License Key 2"
            },
            "restrictedSrcAddress": {
                "default": "Source Address(es) for Management Access"
            },
            "restrictedSrcAddressApp": {
                "default": "Source Address(es) for Web Application Access (80/443)"
            },
            "managementGuiPort": {
                "default": "BIG-IP Management Port"
            },
            "sshKey": {
                "default": "SSH Key"
            },
            "application": {
                "default": "Application"
            },
            "environment": {
                "default": "Environment"
            },
            "group": {
                "default": "Group"
            },
            "owner": {
                "default": "Owner"
            },
            "costcenter": {
                "default": "Cost Center"
            },
            "ntpServer": {
                "default": "NTP Server"
            },
            "timezone": {
                "default": "Timezone (Olson)"
            },
            "bigIpModules": {
                "default": "BIG-IP Modules"
            },
            "allowUsageAnalytics": {
                "default": "Send Anonymous Template Statistics to F5"
            },
            "allowPhoneHome": {
                "default": "Send Anonymous Device Statistics to F5"
            },
            "numberOfAdditionalNics": {
                "default": "Number Of Additional NICs"
            },
            "additionalNicLocation": {
                "default": "Additional NIC Location"
            },
            "declarationUrl": {
                "default": "AS3 Declaration URL"
            }
        }
    else:
        vs_config_parameters = ["declarationUrl"]

        parameter_labels = {
            "Vpc": {
                "default": "VPC"
            },
            "managementSubnetAz1": {
                "default": "Management Subnet AZ1"
            },
            "managementSubnetAz2": {
                "default": "Management Subnet AZ2"
            },
            "subnet1Az1": {
                "default": "Subnet1 in AZ1"
            },
            "subnet1Az2": {
                "default": "Subnet1 in AZ2"
            },
            "subnet2Az1": {
                "default": "Subnet2 in AZ1"
            },
            "subnet2Az2": {
                "default": "Subnet2 in AZ2"
            },
            "availabilityZone1": {
                "default": "Availability Zone 1"
            },
            "availabilityZone2": {
                "default": "Availability Zone 2"
            },
            "imageName": {
                "default": "BIG-IP Image Name"
            },
            "customImageId": {
                "default": "Custom Image Id"
            },
            "instanceType": {
                "default": "AWS Instance Size"
            },
            "applicationInstanceType": {
                "default": "Application Instance Type"
            },
            "licenseKey1": {
                "default": "License Key 1"
            },
            "licenseKey2": {
                "default": "License Key 2"
            },
            "restrictedSrcAddress": {
                "default": "Source Address(es) for Management Access"
            },
            "restrictedSrcAddressApp": {
                "default": "Source Address(es) for Web Application Access (80/443)"
            },
            "managementGuiPort": {
                "default": "BIG-IP Management Port"
            },
            "sshKey": {
                "default": "SSH Key"
            },
            "application": {
                "default": "Application"
            },
            "environment": {
                "default": "Environment"
            },
            "group": {
                "default": "Group"
            },
            "owner": {
                "default": "Owner"
            },
            "costcenter": {
                "default": "Cost Center"
            },
            "ntpServer": {
                "default": "NTP Server"
            },
            "timezone": {
                "default": "Timezone (Olson)"
            },
            "bigIpModules": {
                "default": "BIG-IP Modules"
            },
            "allowUsageAnalytics": {
                "default": "Send Anonymous Template Statistics to F5"
            },
            "allowPhoneHome": {
                "default": "Send Anonymous Device Statistics to F5"
            },
            "numberOfAdditionalNics": {
                "default": "Number Of Additional NICs"
            },
            "additionalNicLocation": {
                "default": "Additional NIC Location"
            },
            "declarationUrl": {
                "default": "AS3 Declaration URL"
            }
        }
    if need_optional_public_ip:
        parameter_labels.update({
            "provisionPublicIP": {
                "default": "Provision Public IP addresses for the BIG-IP interfaces"
            },
        })

    if license_type == "bigiq":
        bigiq_label = "BIG-IQ LICENSING CONFIGURATION"
        bigiq_parms = [
            "bigIqAddress",
            "bigIqUsername",
            "bigIqPasswordS3Arn",
            "bigIqLicensePoolName",
            "bigIqLicenseTenant",
            "bigIqLicenseUnitOfMeasure",
            "bigIqLicenseSkuKeyword1",
            "bigIqLicenseSkuKeyword2"
        ]

        bigiq_label_params = {
            "Label": {
                "default": bigiq_label
            },
            "Parameters": bigiq_parms
        }

        bigiq_parameter_labels = {
            "bigIqAddress": {
                "default": "BIG-IQ address (private)"
            },
            "bigIqLicensePoolName": {
                "default": "BIG-IQ License Pool Name"
            },
            "bigIqUsername": {
                "default": "BIG-IQ user with Licensing Privileges"
            },
            "bigIqPasswordS3Arn": {
                "default": "S3 ARN of the BIG-IQ Password File"
            },
            "bigIqLicenseTenant": {
                "default": "BIG-IQ Tenant"
            },
            "bigIqLicenseUnitOfMeasure": {
                "default": "BIG-IQ Unit Of Measure"
            },
            "bigIqLicenseSkuKeyword1": {
                "default": "BIG-IQ SKU Keyword 1"
            },
            "bigIqLicenseSkuKeyword2": {
                "default": "BIG-IQ SKU Keyword 2"
            }
        }

        parameter_labels.update(bigiq_parameter_labels)

    if ha_type == "autoscale":
        if need_optional_public_ip:
            network_config_parameters.append("provisionPublicIP")

        template_metadata = {
            "Version": str(version),
            "AWS::CloudFormation::Interface": {
                "ParameterGroups": [
                    {
                        "Label": {
                            "default": "DEPLOYMENT"
                        },
                        "Parameters": [
                            "deploymentName"
                        ]
                    },
                    {
                        "Label": {
                            "default": "NETWORKING CONFIGURATION"
                        },
                        "Parameters": network_config_parameters
                    },
                    {
                        "Label": {
                            "default": "INSTANCE CONFIGURATION"
                        },
                        "Parameters": [
                            "sshKey",
                            "instanceType",
                            "throughput",
                            "imageName",
                            "customImageId",
                            "adminUsername",
                            "managementGuiPort",
                            "timezone",
                            "ntpServer",
                            "bigIpModules"
                        ]
                    },
                    {
                        "Label": {
                            "default": "AUTO SCALING CONFIGURATION"
                        },
                        "Parameters": [
                            "scalingMinSize",
                            "scalingMaxSize",
                            "scaleDownBytesThreshold",
                            "scaleUpBytesThreshold",
                            "lowCpuThreshold",
                            "highCpuThreshold",
                            "notificationEmail"
                        ]
                    },
                    {
                        "Label": {
                            "default": "VIRTUAL SERVICE CONFIGURATION"
                        },
                        "Parameters": vs_config_parameters
                    },
                    {
                        "Label": {
                            "default": "TAGS"
                        },
                        "Parameters": [
                            "application",
                            "environment",
                            "group",
                            "owner",
                            "costcenter"
                        ]
                    },
                    bigiq_label_params,
                    {
                        "Label": {
                            "default": "TEMPLATE ANALYTICS"
                        },
                        "Parameters": [
                            "allowUsageAnalytics",
                            "allowPhoneHome"
                        ]
                    }
                ],
                "ParameterLabels": parameter_labels
            }
        }
        t.set_metadata(template_metadata)
    elif need_static_ip_addr:
        networking_parameters = [
            "Vpc",
            "managementSubnetAz1",
            "managementSubnetAz1Address",
            "managementSubnetAz2",
            "subnet1Az1",
            "subnet1Az1Address",
            "subnet1Az2",
            "subnet2Az1",
            "subnet2Az1Address",
            "subnet2Az2",
            "availabilityZone1",
            "availabilityZone2",
            "numberOfAdditionalNics",
            "additionalNicLocation"
        ]
        if need_optional_public_ip:
            networking_parameters.append("provisionPublicIP")

        t.set_metadata({
            "Version": str(version),
            "AWS::CloudFormation::Interface": {
                "ParameterGroups": [
                    {
                        "Label": {
                            "default": "NETWORKING CONFIGURATION"
                        },
                        "Parameters": networking_parameters
                    },
                    {
                        "Label": {
                            "default": "INSTANCE CONFIGURATION"
                        },
                        "Parameters": [
                            "imageName",
                            "customImageId",
                            "instanceType",
                            "applicationInstanceType",
                            "licenseKey1",
                            "licenseKey2",
                            "managementGuiPort",
                            "sshKey",
                            "restrictedSrcAddress",
                            "restrictedSrcAddressApp",
                            "ntpServer",
                            "timezone",
                            "bigIpModules"
                        ]
                    },
                    {
                        "Label": {
                            "default": "TAGS"
                        },
                        "Parameters": [
                            "application",
                            "environment",
                            "group",
                            "owner",
                            "costcenter"
                        ]
                    },
                    bigiq_label_params,
                    {
                        "Label": {
                            "default": "TEMPLATE ANALYTICS"
                        },
                        "Parameters": [
                            "allowUsageAnalytics",
                            "allowPhoneHome"
                        ]
                    },
                    {
                        "Label": {
                            "default": "VIRTUAL SERVICE CONFIGURATION"
                        },
                        "Parameters": vs_config_parameters
                    },
                ],
                "ParameterLabels": parameter_labels
            }
        }
        )
    else:
        networking_parameters = [
            "Vpc",
            "managementSubnetAz1",
            "managementSubnetAz2",
            "subnet1Az1",
            "subnet1Az2",
            "subnet2Az1",
            "subnet2Az2",
            "availabilityZone1",
            "availabilityZone2",
            "numberOfAdditionalNics",
            "additionalNicLocation"
        ]
        if need_optional_public_ip:
            networking_parameters.append("provisionPublicIP")

        t.set_metadata({
            "Version": str(version),
            "AWS::CloudFormation::Interface": {
                "ParameterGroups": [
                    {
                        "Label": {
                            "default": "NETWORKING CONFIGURATION"
                        },
                        "Parameters": networking_parameters
                    },
                    {
                        "Label": {
                            "default": "INSTANCE CONFIGURATION"
                        },
                        "Parameters": [
                            "imageName",
                            "customImageId",
                            "instanceType",
                            "applicationInstanceType",
                            "licenseKey1",
                            "licenseKey2",
                            "managementGuiPort",
                            "sshKey",
                            "restrictedSrcAddress",
                            "restrictedSrcAddressApp",
                            "ntpServer",
                            "timezone",
                            "bigIpModules"
                        ]
                    },
                    {
                        "Label": {
                            "default": "TAGS"
                        },
                        "Parameters": [
                            "application",
                            "environment",
                            "group",
                            "owner",
                            "costcenter"
                        ]
                    },
                    bigiq_label_params,
                    {
                        "Label": {
                            "default": "TEMPLATE ANALYTICS"
                        },
                        "Parameters": [
                            "allowUsageAnalytics",
                            "allowPhoneHome"
                        ]
                    },
                    {
                        "Label": {
                            "default": "VIRTUAL SERVICE CONFIGURATION"
                        },
                        "Parameters": vs_config_parameters
                    },
                ],
                "ParameterLabels": parameter_labels
            }
        }
        )

    # BEGIN PARAMETERS (Common)
    customImageId = t.add_parameter(Parameter(
        "customImageId",
        ConstraintDescription="Must be a valid AMI Id",
        Default="OPTIONAL",
        Description="If you would like to deploy using a custom BIG-IP image, provide the AMI Id.  **Note**: Unless specifically required, leave the default of **OPTIONAL**",
        MaxLength=255,
        MinLength=1,
        Type="String"
    ))
    allowUsageAnalytics = t.add_parameter(Parameter(
        "allowUsageAnalytics",
        Default="Yes",
        Type="String",
        Description="This deployment can send anonymous template statistics to F5 to help us determine how to improve our solutions. If you select **No** statistics are not sent.",
        AllowedValues=[
                "Yes",
                "No",
        ]
    ))
    allowPhoneHome = t.add_parameter(Parameter(
        "allowPhoneHome",
        Default="Yes",
        Type="String",
        Description="This deployment can send anonymous device statistics to F5 to help us determine how to improve our solutions. If you select **No** statistics are not sent.",
        AllowedValues=[
                "Yes",
                "No",
        ]
    ))
    application = t.add_parameter(Parameter(
        "application",
        Description="Name of the Application Tag",
        Default="f5app",
        Type="String",
    ))
    environment = t.add_parameter(Parameter(
        "environment",
        Description="Name of the Environment Tag",
        Default="f5env",
        Type="String",
    ))
    group = t.add_parameter(Parameter(
        "group",
        Description="Name of the Group Tag",
        Default="f5group",
        Type="String",
    ))
    owner = t.add_parameter(Parameter(
        "owner",
        Description="Name of the Owner Tag",
        Default="f5owner",
        Type="String",
    ))
    costcenter = t.add_parameter(Parameter(
        "costcenter",
        Description="Name of the Cost Center Tag",
        Default="f5costcenter",
        Type="String",
    ))
    if 'waf' in components:
        bigIpModules = t.add_parameter(Parameter(
            "bigIpModules",
            Description="Comma separated list of modules and levels to provision, for example: ltm:nominal,asm:nominal",
            Default="ltm:nominal,asm:nominal",
            Type="String",
        ))
    else:
        bigIpModules = t.add_parameter(Parameter(
            "bigIpModules",
            Description="Comma separated list of modules and levels to provision, for example: ltm:nominal,asm:nominal",
            Default="ltm:nominal",
            Type="String",
        ))

    # Static private IP addresses
    ExternalSubnetStaticIpAddress = ""
    managementSubnetStaticIpAddress = ""
    InternalSubnetStaticIpAddress = ""

    if stack != "network":
        restrictedSrcAddress = t.add_parameter(Parameter(
            "restrictedSrcAddress",
            ConstraintDescription="Must be a valid IP CIDR range of the form x.x.x.x/x.",
            Description=" The IP address range used to SSH and access managment GUI on the EC2 instances",
            MinLength="9",
            AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
            MaxLength="18",
            Type="String",
        ))
        restrictedSrcAddressApp = t.add_parameter(Parameter(
            "restrictedSrcAddressApp",
            ConstraintDescription="Must be a valid IP CIDR range of the form x.x.x.x/x.",
            Description=" The IP address range that can be used to access web traffic (80/443) to the EC2 instances",
            MinLength="9",
            AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
            MaxLength="18",
            Type="String",
        ))
        # if ha_type != "autoscale":
        #     restrictedSrcAddressApp = t.add_parameter(Parameter(
        #         "restrictedSrcAddressApp",
        #         ConstraintDescription="Must be a valid IP CIDR range of the form x.x.x.x/x.",
        #         Description=" The IP address range that can be used to access web traffic (80/443) to the EC2 instances",
        #         MinLength="9",
        #         AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
        #         MaxLength="18",
        #         Type="String",
        #     ))
    if stack != "network" and stack != "security_groups":
        sshKey = t.add_parameter(Parameter(
            "sshKey",
            Type="AWS::EC2::KeyPair::KeyName",
            Description="EC2 KeyPair to enable SSH access to the BIG-IP instance",
        ))
    if network:
        for INDEX in range(num_azs):
            AvailabilityZone = "availabilityZone" + str(INDEX + 1)
            PARAMETERS[AvailabilityZone] = t.add_parameter(Parameter(
                AvailabilityZone,
                Type="AWS::EC2::AvailabilityZone::Name",
                Description="Name of an Availability Zone in this Region",
            ))
    if webserver:
        applicationInstanceType = t.add_parameter(Parameter(
            "applicationInstanceType",
            Default="t1.micro",
            ConstraintDescription="Must be a valid EC2 instance type",
            Type="String",
            Description="Webserver EC2 instance type",
            AllowedValues=["t1.micro", "m3.medium", "m3.xlarge", "m2.xlarge", "m3.2xlarge", "c3.large", "c3.xlarge"],
        ))
    if bigip or security_groups:
        if num_nics == 1:
            managementGuiPort = t.add_parameter(Parameter(
                "managementGuiPort",
                Default="8443",
                ConstraintDescription="Must be a valid, unused port on the BIG-IP.",
                Type="Number",
                Description="Port for the BIG-IP management Configuration utility",
            ))
    if bigip:
        ntpServer = t.add_parameter(Parameter(
            "ntpServer",
            Description="NTP server for this implementation",
            Default="0.pool.ntp.org",
            Type="String"
        ))
        timezone = t.add_parameter(Parameter(
            "timezone",
            Description="Enter the Olson timezone string from /usr/share/zoneinfo. The default is 'UTC'. See the TZ column here (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for legal values. For example, 'US/Eastern'.",
            Default="UTC",
            Type="String"
        ))
        allowedvalues = []
        defaultinstance = "m5.xlarge"
        if 'waf' in components:
            allowedvalues.extend([
                "m3.2xlarge",
                "m4.xlarge",
                "m4.2xlarge",
                "m4.4xlarge",
                "m4.10xlarge",
                "m5.large",
                "t3.large",
                "m5.xlarge",
                "m5.2xlarge",
                "m5.4xlarge",
                "c3.4xlarge",
                "c3.8xlarge",
                "c4.4xlarge",
                "c4.8xlarge",
                "c5.large",
                "c5.xlarge",
                "c5.2xlarge",
                "c5.4xlarge",
                "cc2.8xlarge",
                "c5n.2xlarge",
                "c5n.4xlarge"
            ])
            # Default to 2xlarge
            instanceType = t.add_parameter(Parameter(
                "instanceType",
                Default="m3.2xlarge",
                ConstraintDescription="Must be a valid EC2 instance type for BIG-IP",
                Type="String",
                Description="AWS instance type",
                AllowedValues=allowedvalues,
            ))
        else:
            allowedvalues.extend([
                "m5.xlarge",
                "m5.4xlarge",
                "m5.large",
                "m5.12xlarge",
                "m4.xlarge",
                "m4.large",
                "m4.4xlarge",
                "m4.2xlarge",
                "m4.16xlarge",
                "m4.10xlarge",
                "m3.xlarge",
                "m3.medium",
                "m3.large",
                "t3.large",
                "m3.2xlarge",
                "cc2.8xlarge",
                "c5.xlarge",
                "c5.large",
                "c5.4xlarge",
                "c5.9xlarge",
                "c4.xlarge",
                "c4.8xlarge",
                "c4.4xlarge",
                "c4.2xlarge",
                "c3.xlarge",
                "c3.8xlarge",
                "c3.4xlarge",
                "c3.2xlarge",
                "c5n.2xlarge",
                "c5n.4xlarge"
            ])
            if num_nics >= 3:
                allowedvalues[:] = []
                allowedvalues.extend([
                    "m5.xlarge",
                    "m5.4xlarge",
                    "m5.large",
                    "m5.12xlarge",
                    "m4.xlarge",
                    "m4.large",
                    "m4.4xlarge",
                    "m4.2xlarge",
                    "m4.16xlarge",
                    "m4.10xlarge",
                    "m3.xlarge",
                    "m3.medium",
                    "m3.large",
                    "t3.large",
                    "m3.2xlarge",
                    "cc2.8xlarge",
                    "c5.xlarge",
                    "c5.large",
                    "c5.4xlarge",
                    "c5.9xlarge",
                    "c4.xlarge",
                    "c4.8xlarge",
                    "c4.4xlarge",
                    "c4.2xlarge",
                    "c3.xlarge",
                    "c3.8xlarge",
                    "c3.4xlarge",
                    "c3.2xlarge",
                    "c5n.2xlarge",
                    "c5n.4xlarge"
                ])
            if num_nics >= 8:
                defaultinstance = "m5.4xlarge"
                allowedvalues[:] = []
                allowedvalues.extend([
                    "m5.12xlarge",
                    "m5.4xlarge",
                    "m4.4xlarge",
                    "m4.16xlarge",
                    "m4.10xlarge",
                    "cc2.8xlarge",
                    "c5.9xlarge",
                    "c5.4xlarge",
                    "c4.8xlarge",
                    "c4.4xlarge",
                    "c3.8xlarge",
                    "c3.4xlarge",
                    "c5n.4xlarge"
                ])
            if '5000' in marketplace:
                defaultinstance = "m4.10xlarge"
                allowedvalues[:] = []
                allowedvalues.extend([
                    "c3.8xlarge",
                    "c4.8xlarge",
                    "c5.large",
                    "t3.large",
                    "c5.xlarge",
                    "c5.2xlarge",
                    "c5.4xlarge",
                    "m4.10xlarge",
                    "m4.16xlarge",
                    "m5.large",
                    "m5.xlarge",
                    "m5.2xlarge",
                    "m5.4xlarge",
                    "c5n.2xlarge",
                    "c5n.4xlarge"
                ])
            if '1000' in marketplace:
                allowedvalues[:] = []
                allowedvalues.extend([
                    "c3.xlarge",
                    "c3.2xlarge",
                    "c3.4xlarge",
                    "c3.8xlarge",
                    "c4.xlarge",
                    "c4.2xlarge",
                    "c4.4xlarge",
                    "c4.8xlarge",
                    "c5.large",
                    "t3.large",
                    "c5.xlarge",
                    "c5.2xlarge",
                    "c5.4xlarge",
                    "m3.large",
                    "m3.xlarge",
                    "m3.2xlarge",
                    "m4.large",
                    "m4.xlarge",
                    "m4.2xlarge",
                    "m4.4xlarge",
                    "m4.10xlarge",
                    "m4.16xlarge",
                    "m5.large",
                    "m5.xlarge",
                    "m5.2xlarge",
                    "m5.4xlarge",
                    "c5n.2xlarge",
                    "c5n.4xlarge"
                ])
            if '200' in marketplace or '25' in marketplace:
                allowedvalues[:] = []
                allowedvalues.extend([
                    "c3.xlarge",
                    "c3.2xlarge",
                    "c3.4xlarge",
                    "c3.8xlarge",
                    "c4.xlarge",
                    "c4.2xlarge",
                    "c4.4xlarge",
                    "c4.8xlarge",
                    "c5.large",
                    "t3.large",
                    "c5.xlarge",
                    "c5.2xlarge",
                    "c5.4xlarge",
                    "m3.large",
                    "m3.xlarge",
                    "m3.2xlarge",
                    "m4.large",
                    "m4.xlarge",
                    "m4.2xlarge",
                    "m4.4xlarge",
                    "m4.10xlarge",
                    "m4.16xlarge",
                    "m5.large",
                    "m5.xlarge",
                    "m5.2xlarge",
                    "m5.4xlarge",
                    "c5n.2xlarge",
                    "c5n.4xlarge"
                ])
            instanceType = t.add_parameter(Parameter(
                "instanceType",
                Default=defaultinstance,
                ConstraintDescription="Must be a valid EC2 instance type for BIG-IP",
                Type="String",
                Description="Size of the F5 BIG-IP Virtual Instance",
                AllowedValues=allowedvalues,
            ))
        # BYOL and BIG-IQ license types
        if (license_type != "hourly" and ha_type != "autoscale"):
            if ha_type in ("same-az", "across-az"):
                imageName = t.add_parameter(Parameter(
                    "imageName",
                    Default="AllTwoBootLocations",
                    ConstraintDescription="Must be a valid F5 BIG-IP VE image type",
                    Type="String",
                    Description="Image names starting with All have all BIG-IP modules available. Image names starting with LTM have only the LTM module available.  Use Two Boot Locations if you expect to upgrade the BIG-IP VE in the future (the Two Boot Location options are only applicable to BIG-IP v13.1.1 or later).",
                    AllowedValues=["AllTwoBootLocations", "LTMTwoBootLocations"]
                ))
            else:
                imageName = t.add_parameter(Parameter(
                    "imageName",
                    Default="AllTwoBootLocations",
                    ConstraintDescription="Must be a valid F5 BIG-IP VE image type",
                    Type="String",
                    Description="Image names starting with All have all BIG-IP modules available. Image names starting with LTM have only the LTM module available.  Use Two Boot Locations if you expect to upgrade the BIG-IP VE in the future (the Two Boot Location options are only applicable to BIG-IP v13.1.1 or later). If you do not need room to upgrade (if you intend to create a new instance when a new version of BIG-IP VE is released), use one Boot Location.",
                    AllowedValues=["AllOneBootLocation", "AllTwoBootLocations", "LTMOneBootLocation", "LTMTwoBootLocations"],
                ))
        # Autoscale
        elif (ha_type == "autoscale" and 'waf' not in components):
            # BIGIQ license type
            if (license_type != "hourly"):
                imageName = t.add_parameter(Parameter(
                    "imageName",
                    Default="LTMTwoBootLocations",
                    ConstraintDescription="Must be a valid F5 BIG-IP VE image type",
                    Type="String",
                    Description="Image names starting with LTM have only the LTM module available.  Use Two Boot Locations if you expect to upgrade the BIG-IP VE in the future (the Two Boot Location options are only applicable to BIG-IP v13.1.1 or later). If you do not need room to upgrade (if you intend to create a new instance when a new version of BIG-IP VE is released), use one Boot Location.",
                    AllowedValues=["LTMOneBootLocation", "LTMTwoBootLocations"]
                ))
            # PAYG license type
            else:
                imageName = t.add_parameter(Parameter(
                    "imageName",
                    Default="Best",
                    ConstraintDescription="Must be a valid F5 BIG-IP VE image type",
                    Type="String",
                    Description="F5 BIG-IP Performance Type",
                    AllowedValues=["Better", "Best", "Good", "PerAppVeLtm"]
                ))
        elif (ha_type == "autoscale" and 'waf' in components):
            if (license_type != "hourly"):
                imageName = t.add_parameter(Parameter(
                    "imageName",
                    Default="AllTwoBootLocations",
                    ConstraintDescription="Must be a valid F5 BIG-IP VE image type",
                    Type="String",
                    Description="Image names starting with All have all BIG-IP modules available.  Use Two Boot Locations if you expect to upgrade the BIG-IP VE in the future (the Two Boot Location options are only applicable to BIG-IP v13.1.1 or later). If you do not need room to upgrade (if you intend to create a new instance when a new version of BIG-IP VE is released), use one Boot Location.",
                    AllowedValues=["AllOneBootLocation", "AllTwoBootLocations"]
                ))
            else:
                imageName = t.add_parameter(Parameter(
                    "imageName",
                    Default="Best",
                    ConstraintDescription="Must be a valid F5 BIG-IP VE image type",
                    Type="String",
                    Description="F5 BIG-IP Performance Type",
                    AllowedValues=["Best", "AdvancedWaf", "PerAppVeAwaf"]
                ))
        # Stand-alone and cluster
        elif license_type == "hourly" and 'waf' not in components and marketplace == "no":
            if ha_type == "standalone":
                imageName = t.add_parameter(Parameter(
                    "imageName",
                    Default="Best1000Mbps",
                    ConstraintDescription="Must be a valid F5 BIG-IP VE image type",
                    Type="String",
                    Description="F5 BIG-IP Performance Type",
                    AllowedValues=[
                        "Good25Mbps",
                        "Good200Mbps",
                        "Good1000Mbps",
                        "Good5000Mbps",
                        "Good10000Mbps",
                        "Good16vCPU",
                        "Better25Mbps",
                        "Better200Mbps",
                        "Better1000Mbps",
                        "Better5000Mbps",
                        "Better10000Mbps",
                        "Best25Mbps",
                        "Best200Mbps",
                        "Best1000Mbps",
                        "Best5000Mbps",
                        "Best10000Mbps",
                        "AdvancedWaf25Mbps",
                        "AdvancedWaf200Mbps",
                        "PerAppVeAwaf25Mbps",
                        "PerAppVeAwaf200Mbps",
                        "PerAppVeLtm25Mbps",
                        "PerAppVeLtm200Mbps"
                    ]
                ))
            else:
                imageName = t.add_parameter(Parameter(
                    "imageName",
                    Default="Best1000Mbps",
                    ConstraintDescription="Must be a valid F5 BIG-IP VE image type",
                    Type="String",
                    Description="F5 BIG-IP Performance Type",
                    AllowedValues=[
                        "Good25Mbps",
                        "Good200Mbps",
                        "Good1000Mbps",
                        "Good5000Mbps",
                        "Good10000Mbps",
                        "Good16vCPU",
                        "Better25Mbps",
                        "Better200Mbps",
                        "Better1000Mbps",
                        "Better5000Mbps",
                        "Better10000Mbps",
                        "Best25Mbps",
                        "Best200Mbps",
                        "Best1000Mbps",
                        "Best5000Mbps",
                        "Best10000Mbps",
                        "AdvancedWaf25Mbps",
                        "AdvancedWaf200Mbps"
                    ]
                ))
        elif license_type == "hourly" and 'waf' in components and marketplace == "no" and ha_type != "autoscale":
            imageName = t.add_parameter(Parameter(
                "imageName",
                Default="Best1000Mbps",
                ConstraintDescription="Must be a valid F5 BIG-IP VE image type",
                Type="String",
                Description="F5 BIG-IP Performance Type",
                AllowedValues=[
                    "Best25Mbps",
                    "Best200Mbps",
                    "Best1000Mbps",
                    "Best5000Mbps",
                    "Best10000Mbps",
                    "AdvancedWaf25Mbps",
                    "AdvancedWaf200Mbps",
                    "PerAppVeAwaf25Mbps",
                    "PerAppVeAwaf200Mbps",
                    "PerAppVeLtm25Mbps",
                    "PerAppVeLtm200Mbps"
                ]
            ))

        if license_type == "byol":
            for BIGIP_INDEX in range(num_bigips):
                licenseKey = "licenseKey" + str(BIGIP_INDEX + 1)
                PARAMETERS[licenseKey] = t.add_parameter(Parameter(
                    licenseKey,
                    Type="String",
                    Description="F5 BYOL license key",
                    MinLength="1",
                    AllowedPattern="([\\x41-\\x5A][\\x41-\\x5A|\\x30-\\x39]{4})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{5})\\-([\\x41-\\x5A|\\x30-\\x39]{7})",
                    MaxLength="255",
                    ConstraintDescription="Verify your F5 BYOL regkey.",
                ))
        if license_type == "bigiq":
            bigIqAddress = t.add_parameter(Parameter(
                "bigIqAddress",
                MinLength="1",
                ConstraintDescription="Verify the private IP address of the BIG-IQ device that contains the pool of licenses",
                Type="String",
                Description="Private IP address of the BIG-IQ device that contains the pool of BIG-IP licenses",
                MaxLength="255",
            ))
            bigIqUsername = t.add_parameter(Parameter(
                "bigIqUsername",
                MinLength="1",
                ConstraintDescription="Verify the BIG-IQ user with privileges to license BIG-IP. Can be Admin, Device Manager, or Licensing Manager",
                Type="String",
                Description="BIG-IQ user with privileges to license BIG-IP. Must be 'Admin', 'Device Manager', or 'Licensing Manager'",
                MaxLength="255",
            ))
            bigIqPasswordS3Arn = t.add_parameter(Parameter(
                "bigIqPasswordS3Arn",
                Type="String",
                # Description="S3 ARN of the BIG-IQ Password file. e.g. arn:aws:s3:::bucket_name/full_path_to_file for public regions or arn:aws-us-gov:s3:::bucket_name/full_path_to_file) for GovCloud (US)",
                Description="S3 ARN of the BIG-IQ Password file. e.g. arn:aws:s3:::bucket_name/full_path_to_file for public regions. For GovCloud (US) region, start with arn:aws-us-gov:s3. For China region, start with arn:aws-cn:s3.",
                MinLength="1",
                MaxLength="255",
                ConstraintDescription="Verify the S3 ARN of BIG-IQ Password file",
            ))
            bigIqLicensePoolName = t.add_parameter(Parameter(
                "bigIqLicensePoolName",
                MinLength="1",
                ConstraintDescription="Verify the Name of BIG-IQ License Pool",
                Type="String",
                Description="Name of the pool on BIG-IQ that contains the BIG-IP licenses",
                MaxLength="255",
            ))
            bigIqLicenseTenant = t.add_parameter(Parameter(
                "bigIqLicenseTenant",
                Default="OPTIONAL",
                MinLength="1",
                ConstraintDescription="Verify the BIGIQ Licenses tenant value",
                Type="String",
                Description="The BIG-IQ license tenant to use during BIG-IP licensing via BIG-IQ. Note: This is only required when licensing with an ELA/subscription (utility) pool on the BIG-IQ, if not using this pool type leave the default of OPTIONAL.",
                MaxLength="255",
            ))
            bigIqLicenseUnitOfMeasure = t.add_parameter(Parameter(
                "bigIqLicenseUnitOfMeasure",
                Default="OPTIONAL",
                MinLength="1",
                ConstraintDescription="Verify the BIG-IQ License Unit Of Measure",
                Type="String",
                Description="The BIG-IQ license unit of measure to use during BIG-IP licensing via BIG-IQ, for example yearly, monthly, daily or hourly. Note: This is only required when licensing with an ELA/subscription (utility) pool on the BIG-IQ, if not using this pool type leave the default of OPTIONAL.",
                MaxLength="255",
            ))
            bigIqLicenseSkuKeyword1 = t.add_parameter(Parameter(
                "bigIqLicenseSkuKeyword1",
                Default="OPTIONAL",
                MinLength="1",
                ConstraintDescription="Verify the BIG-IQ license filter to use for sku keyword 1",
                Type="String",
                Description="The BIG-IQ license filter (based on SKU keyword) you want to use for licensing the BIG-IPs from the BIG-IQ, for example LTM, BR, BT, ASM or LTMASM. Note: This is only required when licensing with an ELA/subscription (utility) pool on the BIG-IQ, if not using this pool type leave the default of OPTIONAL.",
                MaxLength="255",
            ))
            bigIqLicenseSkuKeyword2 = t.add_parameter(Parameter(
                "bigIqLicenseSkuKeyword2",
                Default="OPTIONAL",
                MinLength="1",
                ConstraintDescription="Verify the BIG-IQ license filter to use for sku keyword 2",
                Type="String",
                Description="The BIG-IQ license filter (based on SKU keyword) you want to use for licensing the BIG-IPs from the BIG-IQ, for example LTM, BR, BT, ASM or LTMASM. Note: This is only required when licensing with an ELA/subscription (utility) pool on the BIG-IQ, if not using this pool type leave the default of OPTIONAL.",
                MaxLength="255",
            ))
    if stack in not_full_stacks or stack == "security_groups":
            Vpc = t.add_parameter(Parameter(
                "Vpc",
                ConstraintDescription="This must be an existing VPC within the working region.",
                Type="AWS::EC2::VPC::Id",
            ))

    if ha_type != 'autoscale':
        t.add_parameter(Parameter(
            "declarationUrl",
            AllowedPattern="^(http:\\/\\/|https:\\/\\/)?[a-z0-9]+([\\-\\.]{1}[a-z0-9]+)*\\.[a-z]{2,5}(:[0-9]{1,5})?(\\/.*)?$|^none$",
            Type="String",
            Description="URL for the AS3 declaration JSON file to be deployed. Leave as **none** to deploy without a service configuration.",
            Default="none"
        ))
    if need_optional_public_ip:
        provisionPublicIP = t.add_parameter(Parameter(
        "provisionPublicIP",
        Default="Yes",
        Type="String",
        Description="Whether or not to provision Public IP Addresses for the BIG-IP Network Interfaces. By Default no Public IP addresses are provisioned.",
        AllowedValues=[
                "Yes",
                "No",
        ]
    ))
    if ha_type == 'autoscale':
        if 'waf' in components:
            t.add_parameter(Parameter(
                            "policyLevel",
                            Default="high",
                            ConstraintDescription="Select the WAF Policy Level you want to use",
                            Type="String",
                            Description="WAF Policy Level you want to use to protect the applications",
                            AllowedValues=["low", "medium", "high"],
                            ))
        t.add_parameter(Parameter(
            "adminUsername",
            ConstraintDescription="Verify your BIG-IP admin username. Note that the user name can contain only alphanumeric characters, periods ( . ), underscores ( _ ), or hyphens ( - ). The user name cannot be any of the following: adm, apache, bin, daemon, guest, lp, mail, manager, mysql, named, nobody, ntp, operator, partition, password, pcap, postfix, radvd, root, rpc, rpm, sshd, syscheck, tomcat, uucp, or vcsa.",
            Type="String",
            Description="BIG-IP Admin User for clustering",
            MaxLength=255,
            MinLength=1,
            AllowedPattern="[a-zA-Z0-9._-]+",
            Default="cluster-admin",
        ))
        t.add_parameter(Parameter(
            "declarationUrl",
            AllowedPattern="^(http:\\/\\/|https:\\/\\/)?[a-z0-9]+([\\-\\.]{1}[a-z0-9]+)*\\.[a-z]{2,5}(:[0-9]{1,5})?(\\/.*)?$|^none$|^default$",
            Type="String",
            Description="URL for the AS3 declaration JSON file to be deployed. If left at **default**, the recommended F5 application service configuration will be applied. Enter **none** to deploy without a service configuration.",
            Default="default"
        ))
        t.add_parameter(Parameter(
            "appInternalDnsName",
            Type="String",
            Description="DNS name poolapp.example.com for the application pool.  This is not required if you are using the Service Discovery feature.",
            Default="www.example.com"
        ))
        t.add_parameter(Parameter(
            "applicationPoolTagKey",
            Type="String",
            Description="This is used for the Service Discovery feature. If you specify a non-default value here, the template automatically discovers the pool members you have tagged with this key and the value you specify next.",
            Default="default"
        ))
        t.add_parameter(Parameter(
            "applicationPoolTagValue",
            Type="String",
            Description="This is used for the Service Discovery feature. If you specify a non-default value here, the template automatically discovers the pool members you have tagged with the key you specified and this value.",
            Default="default"
        ))
        t.add_parameter(Parameter(
            "applicationPort",
            ConstraintDescription="Must be a valid port number (1-65535).",
            Type="Number",
            Description="Port for the application pool member on BIG-IP VE",
            Default=80,
            MaxValue=65535,
            MinValue=1
        ))
        t.add_parameter(Parameter(
            "availabilityZones",
            Type="List<AWS::EC2::AvailabilityZone::Name>",
            Description="Availability Zones where you want to deploy BIG-IP VEs (we recommend at least 2)",
        ))

        if 'dns' in components:
            t.add_parameter(Parameter(
                "dnsMemberIpType",
                Type="String",
                Description="The IP type (public | private) to add as the record when updating the DNS provider."
            ))
            t.add_parameter(Parameter(
                "dnsMemberPort",
                Type="Number",
                Description="The port for the DNS member to use for monitoring the members status."
            ))
            t.add_parameter(Parameter(
                "dnsProviderHost",
                Type="String",
                Description="The management IP address (or hostname) for the DNS provider to use when updating DNS."
            ))
            t.add_parameter(Parameter(
                "dnsProviderPort",
                Type="Number",
                Description="The management port for the DNS provider to use when updating DNS."
            ))
            t.add_parameter(Parameter(
                "dnsProviderUser",
                Type="String",
                Description="The management username for the DNS provider to use when updating DNS."
            ))
            t.add_parameter(Parameter(
                "dnsPasswordS3Arn",
                # Type="String",
                # Description="BIG-IP DNS management password to use when updating DNS.",
                # NoEcho=True
                Type="String",
                Description="S3 ARN of the BIG-IP DNS management password file. e.g. arn:aws:s3:::bucket_name/full_path_to_file for public regions. For GovCloud (US) region, start with arn:aws-us-gov:s3. For China region, start with arn:aws-cn:s3.",
                MinLength="1",
                MaxLength="255",
                ConstraintDescription="Verify the S3 ARN of BIG-IP DNS management password file",
            ))
            t.add_parameter(Parameter(
                "dnsProviderPool",
                Type="String",
                Description="The GSLB pool on the BIG-IP DNS system to populate."
            ))
            t.add_parameter(Parameter(
                "dnsProviderDataCenter",
                Type="String",
                Description="The GSLB datacenter on the BIG-IP DNS system to use when creating GSLB server(s). Note: If the datacenter provided does not exist the template will create one with the value given."
            ))
            t.add_parameter(Parameter(
                "virtualServicePort",
                ConstraintDescription="Must be a valid port number (1-65535).",
                Type="Number",
                Description="Port for the virtual service on BIG-IP VE",
                Default=80,
                MaxValue=65535,
                MinValue=1
            ))
        elif 'nlb' in components:
            t.add_parameter(Parameter(
                "bigipNetworkLoadBalancerTargetGroupsArns",
                Type="String",
                Description="ARN of target group(s) for AWS Network Load Balancer for the BIG-IP VEs",
                Default="none"
            ))
            t.add_parameter(Parameter(
                "virtualServicePort",
                ConstraintDescription="Must be a valid port number (1-65535) except port 80.",
                Type="Number",
                Description="Port for the virtual service on BIG-IP VE. Must be a valid port number (1-65535) except port 80.",
                Default=443,
                MaxValue=65535,
                MinValue=1
            ))
            t.add_parameter(Parameter(
                "appCertificateS3Arn",
                ConstraintDescription="Verify S3 ARN of pfx ssl certificate used for application",
                Type="String",
                Description="S3 ARN of pfx ssl certificate used for application - ex. arn:aws:s3:::my_corporate_bucket/website.pfx for public regions. For GovCloud (US) region, start with arn:aws-us-gov:s3. For China region, start with arn:aws-cn:s3.",
                Default="default",
                MaxLength=255,
                MinLength=1
            ))
        else:
            t.add_parameter(Parameter(
                "bigipElasticLoadBalancer",
                Type="String",
                Description="Name of the AWS Elastic Load Balancer for the BIG-IP VEs",
                Default="ExampleBigipELB"
            ))
            t.add_parameter(Parameter(
                "virtualServicePort",
                ConstraintDescription="Must be a valid port number (1-65535).",
                Type="Number",
                Description="Port for the virtual service on BIG-IP VE",
                Default=80,
                MaxValue=65535,
                MinValue=1
            ))

        t.add_parameter(Parameter(
            "deploymentName",
            Type="String",
            Description="Name the template uses to create object names",
            MaxLength=25,
            Default='example'
        ))
        t.add_parameter(Parameter(
            "highCpuThreshold",
            ConstraintDescription="Select a value between 0 to 100",
            Type="Number",
            Description="High CPU Percentage threshold to begin scaling up BIG-IP VE instances",
            Default=80,
            MaxValue=100,
            MinValue=0,
        ))
        t.add_parameter(Parameter(
            "lowCpuThreshold",
            ConstraintDescription="Select a value between 0 to 100",
            Type="Number",
            Description="Low CPU Percentage threshold to begin scaling down BIG-IP VE instances",
            Default=0,
            MaxValue=100,
            MinValue=0,
        ))
        t.add_parameter(Parameter(
            "notificationEmail",
            ConstraintDescription="Must be a valid email address.",
            Type="String",
            Description="Valid email address to send Auto Scaling event notifications",
            AllowedPattern=".+@.+",
        ))
        t.add_parameter(Parameter(
            "scaleDownBytesThreshold",
            Type="Number",
            Description="Incoming bytes threshold to begin scaling down BIG-IP VE instances",
            Default=10000,
        ))
        t.add_parameter(Parameter(
            "scaleUpBytesThreshold",
            Type="Number",
            Description="Incoming bytes threshold to begin scaling up BIG-IP VE instances",
            Default=35000,
        ))
        t.add_parameter(Parameter(
            "scalingMaxSize",
            ConstraintDescription="Must be a number between 2-8",
            Type="Number",
            Description="Maximum number of BIG-IP instances (2-8) that can be created in the Auto Scale Group",
            Default=3,
            MaxValue=8,
            MinValue=2
        ))
        t.add_parameter(Parameter(
            "scalingMinSize",
            ConstraintDescription="Must be a number between 1-8",
            Type="Number",
            Description="Minimum number of BIG-IP instances (1-8) you want available in the Auto Scale Group",
            Default=1,
            MaxValue=8,
            MinValue=1
        ))
        t.add_parameter(Parameter(
            "subnets",
            ConstraintDescription="The subnet IDs must be within an existing VPC",
            Type="List<AWS::EC2::Subnet::Id>",
            Description="Public or external subnets for the availability zones",
        ))
        t.add_parameter(Parameter(
            "throughput",
            ConstraintDescription="Select the BIG-IP throughput you want to use",
            Type="String",
            Description="Maximum amount of throughput for BIG-IP VE",
            Default="1000Mbps",
            AllowedValues=["25Mbps", "200Mbps", "1000Mbps", "5000Mbps"],
        ))
    elif stack in not_full_stacks:
        for INDEX in range(num_azs):
            # External subnet param
            ExternalSubnet = "subnet1" + "Az" + str(INDEX + 1)
            PARAMETERS[ExternalSubnet] = t.add_parameter(Parameter(
                ExternalSubnet,
                ConstraintDescription="The subnet ID must be within an existing VPC",
                Type="AWS::EC2::Subnet::Id",
                Description="Public or External subnet",
            ))
            if need_static_ip_addr:
                # External private IP address param
                ExternalSubnetStaticIpAddress = ExternalSubnet + "Address"
                PARAMETERS[ExternalSubnetStaticIpAddress] = t.add_parameter(Parameter(
                    ExternalSubnetStaticIpAddress,
                    Type="String",
                    Default="DYNAMIC",
                    Description="Optional. If you want to assign static IP address(es) in the subnet, type them here.  Separate multiple IP addresses with a comma (the first is the Primary IP address, all others are Secondary).  Otherwise leave DYNAMIC and a dynamic address is assigned based on the subnet you specified.",
                ))
        if num_nics > 1:
            for INDEX in range(num_azs):
                # Management subnet param
                managementSubnet = "managementSubnet" + "Az" + str(INDEX + 1)
                PARAMETERS[managementSubnet] = t.add_parameter(Parameter(
                    managementSubnet,
                    ConstraintDescription="The subnet ID must be within an existing VPC",
                    Type="AWS::EC2::Subnet::Id",
                    Description="Management Subnet ID",
                ))
                if need_static_ip_addr:
                    # Management private IP address param
                    managementSubnetStaticIpAddress = managementSubnet + "Address"
                    PARAMETERS[managementSubnetStaticIpAddress] = t.add_parameter(Parameter(
                        managementSubnetStaticIpAddress,
                        Type="String",
                        Default="DYNAMIC",
                        Description="Optional. If you want to assign a static IP address in the subnet, type it here.  Otherwise leave DYNAMIC and a dynamic address is assigned based on the subnet you specified.",
                    ))
        if num_nics > 2:
            for INDEX in range(num_azs):
                # Internal subnet param
                InternalSubnet = "subnet2" + "Az" + str(INDEX + 1)
                PARAMETERS[InternalSubnet] = t.add_parameter(Parameter(
                    InternalSubnet,
                    ConstraintDescription="The subnet ID must be within an existing VPC",
                    Type="AWS::EC2::Subnet::Id",
                    Description="Private or Internal subnet ID",
                ))
                if need_static_ip_addr:
                    # Internal private IP address param
                    InternalSubnetStaticIpAddress = InternalSubnet + "Address"
                    PARAMETERS[InternalSubnet] = t.add_parameter(Parameter(
                        InternalSubnetStaticIpAddress,
                        Type="String",
                        Default="DYNAMIC",
                        Description="Optional. If you want to assign a static IP address in the subnet, type it here.  Otherwise leave DYNAMIC and a dynamic address is assigned based on the subnet you specified.",
                    ))
        if num_nics > 3:
            for INDEX in range(num_azs):
                PARAMETERS["numberOfAdditionalNics"] = t.add_parameter(Parameter(
                    "numberOfAdditionalNics",
                    Default="1",
                    ConstraintDescription="Must be a number between 1-5.",
                    Type="Number",
                    MaxValue="5",
                    MinValue="1",
                    Description="By default this solution deploys the BIG-IP in a 3 NIC configuration, however it can also add a select number (1-5) of additional NICs to the BIG-IP using this parameter",
                ))
                PARAMETERS["additionalNicLocation"] = t.add_parameter(Parameter(
                    "additionalNicLocation",
                    Description="This parameter specifies where the additional NICs should go.  This value must be a comma delimited string of subnets, equal to the number of additional NICs you are deploying.  For example, for 2 additional NICs: **subnet01,subnet02**. NOTE: Ensure that there are no spaces and that the correct number of subnets are provided based on the value you specify in the **Number of Additional NICs** field. IMPORTANT: The subnet you provide for each additional NIC MUST be unique.",
                    Type="CommaDelimitedList"
                ))
    # BEGIN REGION MAPPINGS FOR AMI IDS
    if bigip:
        if license_type == "hourly" and marketplace == "Good25Mbps":
            with open("../build/marketplace/cached-good25Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Good25Mbps"
        if license_type == "hourly" and marketplace == "Good200Mbps":
            with open("../build/marketplace/cached-good200Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Good200Mbps"
        if license_type == "hourly" and marketplace == "Good1000Mbps":
            with open("../build/marketplace/cached-good1000Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Good1000Mbps"
        if license_type == "hourly" and marketplace == "Good5000Mbps":
            with open("../build/marketplace/cached-good5000Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Good5000Mbps"
        if license_type == "hourly" and marketplace == "Better25Mbps":
            with open("../build/marketplace/cached-better25Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Better25Mbps"
        if license_type == "hourly" and marketplace == "Better200Mbps":
            with open("../build/marketplace/cached-better200Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Better200Mbps"
        if license_type == "hourly" and marketplace == "Better1000Mbps":
            with open("../build/marketplace/cached-better1000Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Better1000Mbps"
        if license_type == "hourly" and marketplace == "Better5000Mbps":
            with open("../build/marketplace/cached-better5000Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Better5000Mbps"
        if license_type == "hourly" and marketplace == "Best25Mbps":
            with open("../build/marketplace/cached-best25Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Best25Mbps"
        if license_type == "hourly" and marketplace == "Best200Mbps":
            with open("../build/marketplace/cached-best200Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Best200Mbps"
        if license_type == "hourly" and marketplace == "Best1000Mbps":
            with open("../build/marketplace/cached-best1000Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Best1000Mbps"
        if license_type == "hourly" and marketplace == "Best5000Mbps":
            with open("../build/marketplace/cached-best5000Mbps-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            imageidref = "Best5000Mbps"
        if license_type == "hourly" and marketplace == "no":
            with open("cached-payg-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            # RegionMap = {"Name" : "AWS::Include", "Parameters" : {"Location" : "s3://f5-cft/ami-maps/bigip/v13.x/13.1.0.2-hourly-bigip.json"}}
            if (ha_type == "autoscale" and 'waf' in components):
                # do nothing
                imageidref = ""
            else:
                imageidref = Ref(imageName)
        if license_type != "hourly":
            with open("cached-byol-region-map.json") as json_file:
                RegionMap = json.load(json_file)
            # RegionMap = {"Name" : "AWS::Include", "Parameters" : {"Location" : "s3://f5-cft/ami-maps/bigip/v13.x/13.1.0.2-byol-bigip.json"}}
            imageidref = Ref(imageName)
        # t.add_transform({"Name" : "AWS::Include", "Parameters" : {"Location" : "s3://f5-cft/includes/hourly.json"}})
        t.add_mapping("BigipRegionMap", RegionMap)
        # t.add_mapping("Fn::Transform", RegionMap )

        if ha_type == "autoscale":
            # Add 'Transformations' mapping to easily convert 'Yes' -> 'true' & 'No' -> 'false'
            t.add_mapping("Transformations", {
                "Boolean": {
                    "Yes": "true",
                    "No": "false"
                }
            })
            if license_type == "hourly":
                if 'waf' in components:
                    aws_bigip_throughput = {
                        "25Mbps": {
                            "Best": "Best25Mbps",
                            "AdvancedWaf": "AdvancedWaf25Mbps",
                            "PerAppVeAwaf": "PerAppVeAwaf25Mbps"
                        },
                        "200Mbps": {
                            "Best": "Best200Mbps",
                            "AdvancedWaf": "AdvancedWaf200Mbps",
                            "PerAppVeAwaf": "PerAppVeAwaf200Mbps"
                        },
                        "1000Mbps": {
                            "Best": "Best1000Mbps",
                            "AdvancedWaf": "AdvancedWaf1000Mbps",
                            "PerAppVeAwaf": "PerAppVeAwaf1000Mbps"
                        },
                        "5000Mbps": {
                            "Best": "Best5000Mbps"
                        }
                    }
                else:
                    aws_bigip_throughput = {
                        "25Mbps": {
                            "Best": "Best25Mbps",
                            "Better": "Better25Mbps",
                            "Good": "Good25Mbps",
                            "PerAppVeLtm": "PerAppVeLtm25Mbps"
                        },
                        "200Mbps": {
                            "Best": "Best200Mbps",
                            "Better": "Better200Mbps",
                            "Good": "Good200Mbps",
                            "PerAppVeLtm": "PerAppVeLtm200Mbps"
                        },
                        "1000Mbps": {
                            "Best": "Best1000Mbps",
                            "Better": "Better1000Mbps",
                            "Good": "Good1000Mbps",
                            "PerAppVeLtm": "PerAppVeLtm1000Mbps"
                        },
                        "5000Mbps": {
                            "Best": "Best5000Mbps",
                            "Better": "Better5000Mbps",
                            "Good": "Good5000Mbps",
                            "PerAppVeLtm": "PerAppVeLtm5000Mbps"
                        }
                    }
                t.add_mapping("AWSBigipThrougput", aws_bigip_throughput)

    # WEB SERVER MAPPING
    if webserver:
        with open("cached-webserver-region-map.json") as json_file:
            RegionMap = json.load(json_file)
        t.add_mapping("WebserverRegionMap", RegionMap)

    # BEGIN CONDITIONALS
    optin = t.add_condition(
        "optin",
        condition=Equals("Yes", Ref(allowUsageAnalytics)),
    )
    noCustomImageId = t.add_condition(
        "noCustomImageId",
        condition=Equals("OPTIONAL", Ref(customImageId)),
    )
    if need_static_ip_addr:
        # Use static private IP addresses
        t.add_condition(
            "useDynamicExternalIpAddr",
            condition=Or(
                Equals("DYNAMIC", Ref(ExternalSubnetStaticIpAddress)),
                Equals("", Ref(ExternalSubnetStaticIpAddress)))
        )
        t.add_condition(
            "useStaticExternalIpAddr",
            condition=Not(Or(
                Equals("DYNAMIC", Ref(ExternalSubnetStaticIpAddress)),
                Equals("", Ref(ExternalSubnetStaticIpAddress))))
        )

        if num_nics > 1:
            t.add_condition(
                "useDynamicManagementIpAddr",
                condition=Or(
                    Equals("DYNAMIC", Ref(managementSubnetStaticIpAddress)),
                    Equals("", Ref(managementSubnetStaticIpAddress)))
            )
            t.add_condition(
                "useStaticManagementIpAddr",
                condition=Not(Or(
                    Equals("DYNAMIC", Ref(managementSubnetStaticIpAddress)),
                    Equals("", Ref(managementSubnetStaticIpAddress))))
            )

        if num_nics > 2:
            t.add_condition(
                "useDynamicInternalIpAddr",
                condition=Or(
                    Equals("DYNAMIC", Ref(InternalSubnetStaticIpAddress)),
                    Equals("", Ref(InternalSubnetStaticIpAddress)))
            )
            t.add_condition(
                "useStaticInternalIpAddr",
                condition=Not(Or(
                    Equals("DYNAMIC", Ref(InternalSubnetStaticIpAddress)),
                    Equals("", Ref(InternalSubnetStaticIpAddress))))
            )


    # BYOL and BIG-IQ license types
    if (license_type != "hourly" and license_type != "bigiq" and ha_type != "autoscale"):
        t.add_condition(
            "useChinaRegion",
            condition=Or(
                Equals("cn-north-1", Ref('AWS::Region')),
                Equals("cn-northwest-1", Ref('AWS::Region'))
            )
        )
    # Typically, only gate publicIP parameters by need_optional_public_ip
    if (need_optional_public_ip and (ha_type != 'autoscale' or (ha_type == 'autoscale' and 'dns' in components))):
        t.add_condition(
            "usePublicIP",
            condition=Equals("Yes", Ref(provisionPublicIP)),
        )

    if 'nlb' in components:
        noTargetGroup = t.add_condition(
            "noTargetGroup",
            condition=Equals("none", Ref("bigipNetworkLoadBalancerTargetGroupsArns")),
        )
        useDefaultCert = t.add_condition(
            "useDefaultCert",
            condition=Equals("default", Ref("appCertificateS3Arn")),
        )

    if license_type == "bigiq":
        noTenant = t.add_condition(
            "noTenant",
            condition=Equals("OPTIONAL", Ref(bigIqLicenseTenant)),
        )
        noUnitOfMeasure = t.add_condition(
            "noUnitOfMeasure",
            condition=Equals("OPTIONAL", Ref(bigIqLicenseUnitOfMeasure)),
        )
        noSkuKeyword1 = t.add_condition(
            "noSkuKeyword1",
            condition=Equals("OPTIONAL", Ref(bigIqLicenseSkuKeyword1)),
        )
        noSkuKeyword2 = t.add_condition(
            "noSkuKeyword2",
            condition=Equals("OPTIONAL", Ref(bigIqLicenseSkuKeyword2)),
        )
    if num_nics > 3:
        # Build EQUAL conditions
        for equalCondition in range(1, 6):
            # equalConditions[equalCondition]="Equals("+str(equalCondition)+", Ref(numberOfAdditionalNics) ), "
            t.add_condition(str(equalCondition), condition=Equals(str(equalCondition), Ref("numberOfAdditionalNics")))

        for number in range(3, 7):
            conditionName = "createNic" + str(number)
            equalConditions = {}
            for nAdditionalNic in range(number - 2, 6):
                # Build inputs of EQUAL conditions for OR condition
                # equalConditions[nAdditionalNic]="{\"Fn::Equals\" : [{Ref : \"numberOfAdditionalNics\"}, "+str(nAdditionalNic)+"]},"
                # Save equal conditions in tuple
                equalConditions[nAdditionalNic] = Condition(str(nAdditionalNic))
            # Build OR condition
            # print equalConditions
            # orCondition={ conditionName: Or({"Fn::Equals" : [{"Ref" : "numberOfAdditionalNics"}, "1"]},{"Fn::Equals" : [{"Ref" : "numberOfAdditionalNics"}, "2"]},)}
            orCondition = {conditionName: Or(*equalConditions.values())}
            t.add_condition(
                conditionName,
                orCondition[conditionName],
            )
        t.add_condition(
            "createNic7",
            Condition("5"),
            # condition=Equals("5", Ref("numberOfAdditionalNics") ),
        )

    # BEGIN RESOURCES
    if ha_type == "autoscale":            
        download_runtime_command = "/usr/bin/curl -fv --retry 1 --connect-timeout 5 -L " + runtime_init_url + " -o " + "/var/config/rest/downloads/" + package_runtime_init + "\n"
        install_runtime_command = "bash " + "/var/config/rest/downloads/" + package_runtime_init + " -- '--cloud aws'\n"
        add_resources_autoscale(ha_type, t, restrictedSrcAddress, managementGuiPort, restrictedSrcAddressApp, Vpc, cloudlib_url, cloudlib_aws_url, as3_url, lines, comment_out, loglevel, components, license_type, BIGIP_VERSION, template_name, version, package_as3, runtime_init_url, package_runtime_init, download_runtime_command, install_runtime_command)
    else:
        if network:
            Vpc = t.add_resource(VPC(
                "Vpc",
                EnableDnsSupport="true",
                CidrBlock="10.0.0.0/16",
                EnableDnsHostnames="true",
                Tags=Tags(
                    Name=Join("", ["Vpc: ", Ref("AWS::StackName")]),
                    Application=Ref("application"),
                    Environment=Ref("environment"),
                    Group=Ref("group"),
                    Owner=Ref("owner"),
                    Costcenter=Ref("costcenter"),
                ),
            ))
            defaultGateway = t.add_resource(InternetGateway(
                "InternetGateway",
                Tags=Tags(
                    Name=Join("", ["InternetGateway: ", Ref("AWS::StackName")]),
                    Application=Ref(application),
                    Environment=Ref(environment),
                    Group=Ref(group),
                    Owner=Ref(owner),
                    Costcenter=Ref(costcenter),
                ),
            ))
            AttachGateway = t.add_resource(VPCGatewayAttachment(
                "AttachGateway",
                VpcId=Ref(Vpc),
                InternetGatewayId=Ref(defaultGateway),
            ))
            octet = 1
            for INDEX in range(num_azs):
                ExternalSubnet = "subnet1" + "Az" + str(INDEX + 1)
                RESOURCES[ExternalSubnet] = t.add_resource(Subnet(
                    ExternalSubnet,
                    Tags=Tags(
                        Name=Join("", ["Az", str(INDEX + 1), " External Subnet:", Ref("AWS::StackName")]),
                        Application=Ref("application"),
                        Environment=Ref("environment"),
                        Group=Ref("group"),
                        Owner=Ref("owner"),
                        Costcenter=Ref("costcenter"),
                    ),
                    VpcId=Ref(Vpc),
                    CidrBlock="10.0." + str(octet) + ".0/24",
                    AvailabilityZone=Ref("availabilityZone" + str(INDEX + 1)),
                ))
                octet += 10
            ExternalRouteTable = t.add_resource(RouteTable(
                "ExternalRouteTable",
                VpcId=Ref(Vpc),
                Tags=Tags(
                    Name=Join("", ["External Route Table", Ref("AWS::StackName")]),
                    Application=Ref("application"),
                    Environment=Ref("environment"),
                    Group=Ref("group"),
                    Owner=Ref("owner"),
                    Costcenter=Ref("costcenter"),
                    Network="External"
                ),
            ))
            ExternalDefaultRoute = t.add_resource(Route(
                "ExternalDefaultRoute",
                DependsOn="AttachGateway",
                GatewayId=Ref(defaultGateway),
                DestinationCidrBlock="0.0.0.0/0",
                RouteTableId=Ref(ExternalRouteTable),
            ))
            if ha_type != "standalone":
                ExampleRoute = t.add_resource(Route(
                    "ExampleRoute",
                    DependsOn="AttachGateway",
                    GatewayId=Ref(defaultGateway),
                    DestinationCidrBlock="192.0.2.0/24",
                    RouteTableId=Ref(ExternalRouteTable),
                ))
                ExternalRouteTable.Tags = Tags(f5_cloud_failover_label=Ref("AWS::StackName"))
            for INDEX in range(num_azs):
                ExternalSubnetRouteTableAssociation = "Az" + str(INDEX + 1) + "ExternalSubnetRouteTableAssociation"

                RESOURCES[ExternalSubnetRouteTableAssociation] = t.add_resource(SubnetRouteTableAssociation(
                    ExternalSubnetRouteTableAssociation,

                    SubnetId=Ref("subnet1" + "Az" + str(INDEX + 1)),
                    RouteTableId=Ref(ExternalRouteTable),
                ))
            if num_nics > 1:
                octet = 0
                for INDEX in range(num_azs):
                    managementSubnet = "managementSubnet" + "Az" + str(INDEX + 1)
                    RESOURCES[managementSubnet] = t.add_resource(Subnet(
                        managementSubnet,

                        Tags=Tags(
                            Name=Join("", ["Az", str(INDEX + 1), " Management Subnet:", Ref("AWS::StackName")]),
                            Application=Ref("application"),
                            Environment=Ref("environment"),
                            Group=Ref("group"),
                            Owner=Ref("owner"),
                            Costcenter=Ref("costcenter"),
                        ),
                        VpcId=Ref(Vpc),
                        CidrBlock="10.0." + str(octet) + ".0/24",
                        AvailabilityZone=Ref("availabilityZone" + str(INDEX + 1)),
                    ))
                    octet += 10
                ManagementRouteTable = t.add_resource(RouteTable(
                    "ManagementRouteTable",
                    VpcId=Ref(Vpc),
                    Tags=Tags(
                        Name=Join("", ["Management Route Table", Ref("AWS::StackName")]),
                        Application=Ref("application"),
                        Environment=Ref("environment"),
                        Group=Ref("group"),
                        Owner=Ref("owner"),
                        Costcenter=Ref("costcenter"),
                        Network="Mgmt",
                    ),
                ))
                # Depends On
                # https://forums.aws.amazon.com/thread.jspa?threadID=100750
                ManagementDefaultRoute = t.add_resource(Route(
                    "ManagementDefaultRoute",
                    DependsOn="AttachGateway",
                    GatewayId=Ref(defaultGateway),
                    DestinationCidrBlock="0.0.0.0/0",
                    RouteTableId=Ref(ManagementRouteTable),
                ))
                for INDEX in range(num_azs):
                    ManagementSubnetRouteTableAssociation = "Az" + str(INDEX + 1) + "ManagementSubnetRouteTableAssociation"
                    RESOURCES[ManagementSubnetRouteTableAssociation] = t.add_resource(SubnetRouteTableAssociation(
                        ManagementSubnetRouteTableAssociation,
                        SubnetId=Ref("managementSubnet" + "Az" + str(INDEX + 1)),
                        RouteTableId=Ref(ManagementRouteTable),
                    ))
            if num_nics > 2:
                octet = 2
                for INDEX in range(num_azs):
                    InternalSubnet = "subnet2" + "Az" + str(INDEX + 1)
                    RESOURCES[InternalSubnet] = t.add_resource(Subnet(
                        InternalSubnet,
                        Tags=Tags(
                            Name=Join("", ["Az", str(INDEX + 1), " Internal Subnet:", Ref("AWS::StackName")]),
                            Application=Ref("application"),
                            Environment=Ref("environment"),
                            Group=Ref("group"),
                            Owner=Ref("owner"),
                            Costcenter=Ref("costcenter"),
                        ),
                        VpcId=Ref(Vpc),
                        CidrBlock="10.0." + str(octet) + ".0/24",
                        AvailabilityZone=Ref("availabilityZone" + str(INDEX + 1)),
                    ))
                    octet += 10
                InternalRouteTable = t.add_resource(RouteTable(
                    "InternalRouteTable",
                    VpcId=Ref(Vpc),
                    Tags=Tags(
                        Name=Join("", ["Internal Route Table:", Ref("AWS::StackName")]),
                        Application=Ref("application"),
                        Environment=Ref("environment"),
                        Group=Ref("group"),
                        Owner=Ref("owner"),
                        Costcenter=Ref("costcenter"),
                        Network="Internal",
                    ),
                ))
                InternalDefaultRoute = t.add_resource(Route(
                    "InternalDefaultRoute",
                    DependsOn="AttachGateway",
                    GatewayId=Ref(defaultGateway),
                    DestinationCidrBlock="0.0.0.0/0",
                    RouteTableId=Ref(InternalRouteTable),
                ))
                for INDEX in range(num_azs):
                    InternalSubnetRouteTableAssociation = "Az" + str(INDEX + 1) + "InternalSubnetRouteTableAssociation"
                    RESOURCES[InternalSubnetRouteTableAssociation] = t.add_resource(SubnetRouteTableAssociation(
                        InternalSubnetRouteTableAssociation,
                        SubnetId=Ref("subnet2" + "Az" + str(INDEX + 1)),
                        RouteTableId=Ref(InternalRouteTable),

                    ))
            octet = 3
            for INDEX in range(num_azs):
                ApplicationSubnet = "Az" + str(INDEX + 1) + "ApplicationSubnet"
                RESOURCES[ApplicationSubnet] = t.add_resource(Subnet(
                    ApplicationSubnet,
                    Tags=Tags(
                        Name=Join("", ["Az", str(INDEX + 1), " Application Subnet:", Ref("AWS::StackName")]),
                        Application=Ref("application"),
                        Environment=Ref("environment"),
                        Group=Ref("group"),
                        Owner=Ref("owner"),
                        Costcenter=Ref("costcenter"),
                    ),
                    VpcId=Ref(Vpc),
                    CidrBlock="10.0." + str(octet) + ".0/24",
                    AvailabilityZone=Ref("availabilityZone" + str(INDEX + 1)),
                ))
                octet += 10
            ApplicationRouteTable = t.add_resource(RouteTable(
                "ApplicationRouteTable",
                VpcId=Ref(Vpc),
                Tags=Tags(
                    Name=Join("", ["Application Route Table:", Ref("AWS::StackName")]),
                    Application=Ref("application"),
                    Environment=Ref("environment"),
                    Group=Ref("group"),
                    Owner=Ref("owner"),
                    Costcenter=Ref("costcenter"),
                    Network="Application",
                ),
            ))
            ApplicationDefaultRoute = t.add_resource(Route(
                "ApplicationDefaultRoute",
                DependsOn="AttachGateway",
                GatewayId=Ref(defaultGateway),
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
        if security_groups:
            # 1 Nic has consolidated rules
            if num_nics == 1:
                bigipExternalSecurityGroup = add_security_group_resource(t, restrictedSrcAddress, managementGuiPort, restrictedSrcAddressApp, Vpc)
                if license_type == "bigiq":
                    # ALLOW BIG-IQ to configure license
                    bigipSecurityGroupIngressBigiqLic = t.add_resource(SecurityGroupIngress(
                        "bigipSecurityGroupIngressBigiqLic",
                        GroupId=Ref(bigipExternalSecurityGroup),
                        IpProtocol="tcp",
                        FromPort=Ref(managementGuiPort),
                        ToPort=Ref(managementGuiPort),
                        CidrIp=Join("", [Ref(bigIqAddress), "/32"]),
                    ))
            if num_nics > 1:
                bigipExternalSecurityGroup = t.add_resource(SecurityGroup(
                    "bigipExternalSecurityGroup",
                    SecurityGroupIngress=[
                        # Example port for Virtual Server
                        SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort=80,
                            ToPort=80,
                            CidrIp=Ref(restrictedSrcAddressApp),
                        ),
                        # Example port for Virtual Server
                        SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort=443,
                            ToPort=443,
                            CidrIp=Ref(restrictedSrcAddressApp),
                        ),
                    ],
                    VpcId=Ref(Vpc),
                    GroupDescription="Public or external interface rules",
                    Tags=Tags(
                        Name=Join("", ["Bigip External Security Group:", Ref("AWS::StackName")]),
                        Application=Ref("application"),
                        Environment=Ref("environment"),
                        Group=Ref("group"),
                        Owner=Ref("owner"),
                        Costcenter=Ref("costcenter"),
                    ),
                ))
                bigipManagementSecurityGroup = t.add_resource(SecurityGroup(
                    "bigipManagementSecurityGroup",
                    SecurityGroupIngress=[
                        SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort=22,
                            ToPort=22,
                            CidrIp=Ref(restrictedSrcAddress),
                        ),
                        SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort=443,
                            ToPort=443,
                            CidrIp=Ref(restrictedSrcAddress),
                        ),
                    ],
                    VpcId=Ref(Vpc),
                    GroupDescription="BIG-IP management interface policy",
                    Tags=Tags(
                        Name=Join("", ["Bigip Management Security Group:", Ref("AWS::StackName")]),
                        Application=Ref("application"),
                        Environment=Ref("environment"),
                        Group=Ref("group"),
                        Owner=Ref("owner"),
                        Costcenter=Ref("costcenter"),
                    ),
                ))
                if license_type == "bigiq":
                    # ALLOW BIG-IQ to configure license
                    bigipSecurityGroupIngressBigiqLic = t.add_resource(SecurityGroupIngress(
                        "bigipSecurityGroupIngressBigiqLic",
                        GroupId=Ref(bigipManagementSecurityGroup),
                        IpProtocol="tcp",
                        FromPort=443,
                        ToPort=443,
                        CidrIp=Join("", [Ref(bigIqAddress), "/32"]),
                    ))
            # If a 3 nic with additional Internal interface.
            if num_nics > 2:
                bigipInternalSecurityGroup = t.add_resource(SecurityGroup(
                    "bigipInternalSecurityGroup",
                    VpcId=Ref(Vpc),
                    GroupDescription="Allow All from Intra-VPC only",
                    Tags=Tags(
                        Name=Join("", ["Bigip Internal Security Group:", Ref("AWS::StackName")]),
                        Application=Ref("application"),
                        Environment=Ref("environment"),
                        Group=Ref("group"),
                        Owner=Ref("owner"),
                        Costcenter=Ref("costcenter"),
                    ),
                ))
            if 'waf' in components:
                # ASM SYNC
                bigipSecurityGroupIngressAsmPolicySync = t.add_resource(SecurityGroupIngress(
                    "bigipSecurityGroupIngressAsmPolicySync",
                    GroupId=Ref(bigipExternalSecurityGroup),
                    IpProtocol="tcp",
                    FromPort="6123",
                    ToPort="6128",
                    SourceSecurityGroupId=Ref(bigipExternalSecurityGroup),
                ))
            if ha_type != "standalone":
                if num_nics == 2:
                    # Required Device Service Clustering (DSC) & GTM DNS for external interface
                    bigipSecurityGroupIngressConfigSync = t.add_resource(SecurityGroupIngress(
                        "bigipSecurityGroupIngressConfigSync",
                        GroupId=Ref(bigipExternalSecurityGroup),
                        IpProtocol="tcp",
                        FromPort=4353,
                        ToPort=4353,
                        SourceSecurityGroupId=Ref(bigipExternalSecurityGroup),
                    ))
                    # Required for DSC Network Heartbeat on external interface
                    bigipSecurityGroupIngressHa = t.add_resource(SecurityGroupIngress(
                        "bigipSecurityGroupIngressHa",
                        GroupId=Ref(bigipExternalSecurityGroup),
                        IpProtocol="udp",
                        FromPort=1026,
                        ToPort=1026,
                        SourceSecurityGroupId=Ref(bigipExternalSecurityGroup),
                    ))
                if num_nics > 2:
                    # Required Device Service Clustering (DSC) & GTM DNS for internal interface
                    bigipSecurityGroupIngressConfigSync = t.add_resource(SecurityGroupIngress(
                        "bigipSecurityGroupIngressConfigSync",
                        GroupId=Ref(bigipInternalSecurityGroup),
                        IpProtocol="tcp",
                        FromPort=4353,
                        ToPort=4353,
                        SourceSecurityGroupId=Ref(bigipInternalSecurityGroup),
                    ))
                    # Required for DSC Network Heartbeat on external interface
                    bigipSecurityGroupIngressHa = t.add_resource(SecurityGroupIngress(
                        "bigipSecurityGroupIngressHa",
                        GroupId=Ref(bigipInternalSecurityGroup),
                        IpProtocol="udp",
                        FromPort=1026,
                        ToPort=1026,
                        SourceSecurityGroupId=Ref(bigipInternalSecurityGroup),
                    ))
                if ha_type == "same-az":
                    # Required for initial cluster configuration
                    bigipSecurityGroupIngressManagmentSame = t.add_resource(SecurityGroupIngress(
                        "bigipSecurityGroupIngressManagmentSame",
                        GroupId=Ref(bigipManagementSecurityGroup),
                        IpProtocol="tcp",
                        FromPort=443,
                        ToPort=443,
                        SourceSecurityGroupId=Ref(bigipManagementSecurityGroup),
                    ))
                if ha_type == "across-az":
                    if num_nics == 2:
                        bigipSecurityGroupIngressManagmentAcross = t.add_resource(SecurityGroupIngress(
                            "bigipSecurityGroupIngressManagmentAcross",
                            GroupId=Ref(bigipManagementSecurityGroup),
                            IpProtocol="tcp",
                            FromPort=443,
                            ToPort=443,
                            SourceSecurityGroupId=Ref(bigipExternalSecurityGroup),
                        ))
                    elif num_nics > 2:
                        bigipSecurityGroupIngressManagmentAcross = t.add_resource(SecurityGroupIngress(
                            "bigipSecurityGroupIngressManagmentAcross",
                            GroupId=Ref(bigipManagementSecurityGroup),
                            IpProtocol="tcp",
                            FromPort=443,
                            ToPort=443,
                            SourceSecurityGroupId=Ref(bigipInternalSecurityGroup),
                        ))
            if webserver:
                WebserverSecurityGroup = t.add_resource(SecurityGroup(
                    "WebserverSecurityGroup",
                    SecurityGroupIngress=[
                        SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort=22,
                            ToPort=22,
                            CidrIp=Ref(restrictedSrcAddress),
                        ),
                        SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort=80,
                            ToPort=80,
                            CidrIp=Ref(restrictedSrcAddressApp)
                        ),
                        SecurityGroupRule(
                            IpProtocol="tcp",
                            FromPort=443,
                            ToPort=443,
                            CidrIp=Ref(restrictedSrcAddress),
                        ),
                    ],
                    VpcId=Ref(Vpc),
                    GroupDescription="Enable Access to Webserver",
                    Tags=Tags(
                        Name=Join("", ["Webserver Security Group:", Ref("AWS::StackName")]),
                        Application=Ref("application"),
                        Environment=Ref("environment"),
                        Group=Ref("group"),
                        Owner=Ref("owner"),
                        Costcenter=Ref("costcenter"),
                    ),
                ))

        if webserver:
            Webserver = t.add_resource(Instance(
                "Webserver",
                UserData=Base64(Join("\n", [
                    "#cloud-config",
                    "runcmd:",
                    " - sudo docker run --name demo -p 80:80 -d f5devcentral/f5-demo-app:latest"
                ])),
                Tags=Tags(
                    Name=Join("", ["Webserver:", Ref("AWS::StackName")]),
                    Application=Ref("application"),
                    Environment=Ref("environment"),
                    Group=Ref("group"),
                    Owner=Ref("owner"),
                    Costcenter=Ref("costcenter"),
                ),
                ImageId=FindInMap("WebserverRegionMap", Ref("AWS::Region"), "AMI"),
                KeyName=Ref(sshKey),
                InstanceType=Ref(applicationInstanceType),
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
        if bigip:
            # Build IAM ROLE and POLICY
            discovery_actions = ["ec2:DescribeInstances", "ec2:DescribeInstanceStatus", "ec2:DescribeAddresses", "ec2:AssociateAddress", "ec2:DisassociateAddress", "ec2:DescribeNetworkInterfaces", "ec2:DescribeNetworkInterfaceAttribute", "ec2:DescribeRouteTables", "ec2:DescribeSubnets", "ec2:AssignPrivateIpAddresses" ]
            cfe_actions = ["s3:ListAllMyBuckets", "ec2:UnassignPrivateIpAddresses", "ec2:AssignIpv6Addresses", "ec2:UnassignIpv6Addresses"]
            if ha_type != "standalone":
                discovery_actions.extend(cfe_actions)
            discovery_policy = [{"Effect": "Allow", "Action": discovery_actions, "Resource": ["*"]}]
            if license_type == "bigiq":
                discovery_policy.append({"Effect": "Allow", "Action": ["s3:GetObject"], "Resource": {"Ref": "bigIqPasswordS3Arn"}, })
            if ha_type != "standalone":
                discovery_policy.append({"Effect": "Allow", "Action": ["s3:ListBucket","s3:GetBucketTagging", "s3:GetBucketLocation"], "Resource": {"Fn::Join": ["", ["arn:*:s3:::", {"Ref": "S3Bucket"}]]}, },)
                discovery_policy.append({"Effect": "Allow", "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"], "Resource": {"Fn::Join": ["", ["arn:*:s3:::", {"Ref": "S3Bucket"}, "/*"]]}},)
                discovery_policy.append({"Effect": "Allow", "Action": ["ec2:CreateRoute", "ec2:ReplaceRoute"], "Resource": {"Fn::Join": ["", ["arn:*:ec2:", {"Ref": "AWS::Region"}, ":", {"Ref": "AWS::AccountId"}, ":route-table/*"]]}, "Condition": {"StringEquals": {"ec2:ResourceTag/f5_cloud_failover_label": {"Ref":"AWS::StackName"}}}})
                s3bucket = t.add_resource(Bucket("S3Bucket", AccessControl=BucketOwnerFullControl,Tags=Tags(f5_cloud_failover_label=Ref("AWS::StackName"))))
            if (license_type != "hourly" and license_type != "bigiq" and ha_type != "autoscale"):
                bigipServiceDiscoveryAccessRole = t.add_resource(iam.Role(
                    "bigipServiceDiscoveryAccessRole",
                    Path="/",
                    AssumeRolePolicyDocument=Policy(
                        Version="2012-10-17",
                        Statement=[
                            Statement(
                                Effect=Allow,
                                Action=[AssumeRole],
                                Principal=Principal("Service",
                                [
                                    {
                                      "Fn::If": [
                                        "useChinaRegion",
                                        "ec2.amazonaws.com.cn",
                                        "ec2.amazonaws.com"
                                      ]
                                    }
                                ])
                            )
                        ]
                    ),
                    Policies=[
                        iam.Policy(
                            PolicyName="BigipServiceDiscoveryPolicy",
                            PolicyDocument={
                                "Version": "2012-10-17",
                                "Statement":
                                    discovery_policy

                            }
                        ),
                    ],
                ))
            else:
               bigipServiceDiscoveryAccessRole = t.add_resource(iam.Role(
                    "bigipServiceDiscoveryAccessRole",
                    Path="/",
                    AssumeRolePolicyDocument=Policy(
                        Version="2012-10-17",
                        Statement=[
                            Statement(
                                Effect=Allow,
                                Action=[AssumeRole],
                                Principal=Principal("Service", ["ec2.amazonaws.com"])
                            )
                        ]
                    ),
                    Policies=[
                        iam.Policy(
                            PolicyName="BigipServiceDiscoveryPolicy",
                            PolicyDocument={
                                "Version": "2012-10-17",
                                "Statement":
                                    discovery_policy

                            }
                        ),
                    ],
                ))
            bigipServiceDiscoveryProfile = t.add_resource(iam.InstanceProfile(
                "bigipServiceDiscoveryProfile",
                Path="/",
                Roles=[Ref(bigipServiceDiscoveryAccessRole)]
            ))
            # Build variables for BIGIP's
            ExternalSubnet = ""
            managementSubnet = ""
            InternalSubnet = ""
            ExternalSubnetStaticIpAddress = ""
            managementSubnetStaticIpAddress = ""
            InternalSubnetStaticIpAddress = ""
            for BIGIP_INDEX in range(num_bigips):
                licenseKey = "licenseKey" + str(BIGIP_INDEX + 1)
                BigipInstance = "Bigip" + str(BIGIP_INDEX + 1) + "Instance"
                if num_azs > 1:
                    ExternalSubnet = "subnet1" + "Az" + str(BIGIP_INDEX + 1)
                    managementSubnet = "managementSubnet" + "Az" + str(BIGIP_INDEX + 1)
                    InternalSubnet = "subnet2" + "Az" + str(BIGIP_INDEX + 1)
                else:
                    ExternalSubnet = "subnet1Az1"
                    managementSubnet = "managementSubnetAz1"
                    InternalSubnet = "subnet2Az1"
                #
                ExternalSubnetStaticIpAddress = ExternalSubnet + "Address"
                managementSubnetStaticIpAddress = managementSubnet + "Address"
                InternalSubnetStaticIpAddress = InternalSubnet + "Address"

                ExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + str(ExternalSubnet) + "Interface"
                StaticExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "Static" + str(ExternalSubnet) + "Interface"
                if need_static_ip_addr:
                    # Build BIGIP External Interface Resource
                    RESOURCES[ExternalInterface] = t.add_resource(NetworkInterface(
                        ExternalInterface,
                        Condition="useDynamicExternalIpAddr",
                        SubnetId=Ref(ExternalSubnet),
                        GroupSet=[Ref(bigipExternalSecurityGroup)],
                        Description="Public External Interface for the BIG-IP",
                        SecondaryPrivateIpAddressCount=1
                    ))
                    # Build BIGIP Static External Interface Resource
                    RESOURCES[StaticExternalInterface] = t.add_resource(NetworkInterface(
                        StaticExternalInterface,
                        Condition="useStaticExternalIpAddr",
                        SubnetId=Ref(ExternalSubnet),
                        GroupSet=[Ref(bigipExternalSecurityGroup)],
                        Description="Public External Interface for the BIG-IP",
                        PrivateIpAddresses=[
                            PrivateIpAddressSpecification(
                                PrivateIpAddress=Select("0", Split(',', Ref(ExternalSubnetStaticIpAddress))),
                                Primary=True),
                            PrivateIpAddressSpecification(
                                PrivateIpAddress=Select("1", Split(',', Ref(ExternalSubnetStaticIpAddress))),
                                Primary=False)]
                    ))
                else:
                    RESOURCES[ExternalInterface] = t.add_resource(NetworkInterface(
                        ExternalInterface,
                        SubnetId=Ref(ExternalSubnet),
                        GroupSet=[Ref(bigipExternalSecurityGroup)],
                        Description="Public External Interface for the BIG-IP",
                        SecondaryPrivateIpAddressCount=1
                    ))
                if ha_type == "across-az" or ha_type == "same-az":
                    RESOURCES[ExternalInterface].Tags = Tags(f5_cloud_failover_label=Ref("AWS::StackName"), f5_cloud_failover_nic_map="external")
                if (stack != "prod" or ha_type == "standalone"):
                    ExternalSelfEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + str(ExternalSubnet) + "SelfEipAddress"
                    ExternalSelfEipAssociation = "Bigip" + str(BIGIP_INDEX + 1) + str(ExternalSubnet) + "SelfEipAssociation"
                    # Build EIP Resources
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
                        if need_optional_public_ip:
                            RESOURCES[ExternalSelfEipAddress] = t.add_resource(EIP(
                                ExternalSelfEipAddress,
                                Domain="vpc",
                                Condition="usePublicIP"
                            ))
                        else:
                            RESOURCES[ExternalSelfEipAddress] = t.add_resource(EIP(
                                ExternalSelfEipAddress,
                                Domain="vpc",
                            ))
                        if not need_static_ip_addr and not need_optional_public_ip:
                            RESOURCES[ExternalSelfEipAssociation] = t.add_resource(EIPAssociation(
                                ExternalSelfEipAssociation,
                                NetworkInterfaceId=Ref(ExternalInterface),
                                AllocationId=GetAtt(ExternalSelfEipAddress, "AllocationId"),
                                PrivateIpAddress=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress")
                            ))
                        if need_static_ip_addr and not need_optional_public_ip:
                            RESOURCES[ExternalSelfEipAssociation] = t.add_resource(EIPAssociation(
                                ExternalSelfEipAssociation,
                                NetworkInterfaceId=If(
                                    "useDynamicExternalIpAddr",
                                    Ref(ExternalInterface),
                                    Ref(StaticExternalInterface)),
                                AllocationId=GetAtt(ExternalSelfEipAddress, "AllocationId"),
                                PrivateIpAddress=If("useDynamicExternalIpAddr",
                                                    GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
                                                    GetAtt(StaticExternalInterface, "PrimaryPrivateIpAddress"))
                            ))
                        if need_static_ip_addr and need_optional_public_ip:
                            RESOURCES[ExternalSelfEipAssociation] = t.add_resource(EIPAssociation(
                                ExternalSelfEipAssociation,
                                NetworkInterfaceId=If(
                                    "useDynamicExternalIpAddr",
                                    Ref(ExternalInterface),
                                    Ref(StaticExternalInterface)),
                                AllocationId=GetAtt(ExternalSelfEipAddress, "AllocationId"),
                                PrivateIpAddress=If("useDynamicExternalIpAddr",
                                                    GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
                                                    GetAtt(StaticExternalInterface, "PrimaryPrivateIpAddress")),
                                Condition="usePublicIP"
                            ))
                        if not need_static_ip_addr and need_optional_public_ip:
                            RESOURCES[ExternalSelfEipAssociation] = t.add_resource(EIPAssociation(
                                ExternalSelfEipAssociation,
                                NetworkInterfaceId=Ref(ExternalInterface),
                                AllocationId=GetAtt(ExternalSelfEipAddress, "AllocationId"),
                                PrivateIpAddress=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
                                Condition="usePublicIP"
                            ))
                if num_nics > 1:
                    ManagementInterface = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementInterface"
                    StaticManagementInterface = "Bigip" + str(BIGIP_INDEX + 1) + "StaticManagementInterface"

                    if need_static_ip_addr:
                        RESOURCES[ManagementInterface] = t.add_resource(NetworkInterface(
                            ManagementInterface,
                            Condition="useDynamicManagementIpAddr",
                            SubnetId=Ref(managementSubnet),
                            GroupSet=[Ref(bigipManagementSecurityGroup)],
                            Description="Management Interface for the BIG-IP",
                        ))

                        RESOURCES[StaticManagementInterface] = t.add_resource(NetworkInterface(
                            StaticManagementInterface,
                            Condition="useStaticManagementIpAddr",
                            SubnetId=Ref(managementSubnet),
                            GroupSet=[Ref(bigipManagementSecurityGroup)],
                            PrivateIpAddress=Ref(managementSubnetStaticIpAddress),
                            Description="Management Interface for the BIG-IP"
                        ))
                    else:
                        RESOURCES[ManagementInterface] = t.add_resource(NetworkInterface(
                            ManagementInterface,
                            SubnetId=Ref(managementSubnet),
                            GroupSet=[Ref(bigipManagementSecurityGroup)],
                            Description="Management Interface for the BIG-IP",
                        ))
                    if (stack != "prod" or ha_type == "standalone"):
                        # Build EIP resources
                        VipEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "VipEipAddress"
                        VipEipAssociation = "Bigip" + str(BIGIP_INDEX + 1) + "VipEipAssociation"
                        ManagementEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementEipAddress"
                        ManagementEipAssociation = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementEipAssociation"
                        if ha_type == "standalone" or (BIGIP_INDEX + 1) == CLUSTER_SEED:
                            if stack == "full":
                                RESOURCES[VipEipAddress] = t.add_resource(EIP(
                                    VipEipAddress,
                                    DependsOn="AttachGateway",
                                    Domain="vpc",
                                ))
                                if ha_type == "across-az":
                                    RESOURCES[VipEipAddress].Tags = Tags(f5_cloud_failover_label=Ref("AWS::StackName"), f5_cloud_failover_vips=Join(",", [Select("0", GetAtt("Bigip1subnet1Az1Interface", "SecondaryPrivateIpAddresses")), Select("0", GetAtt("Bigip2subnet1Az2Interface", "SecondaryPrivateIpAddresses"))]))
                                RESOURCES[VipEipAssociation] = t.add_resource(EIPAssociation(
                                    VipEipAssociation,
                                    DependsOn="AttachGateway",
                                    NetworkInterfaceId=Ref(ExternalInterface),
                                    AllocationId=GetAtt(VipEipAddress, "AllocationId"),
                                    PrivateIpAddress=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                                ))
                            else:
                                if need_optional_public_ip:
                                    RESOURCES[VipEipAddress] = t.add_resource(EIP(
                                    VipEipAddress,
                                    Domain="vpc",
                                    Condition="usePublicIP",
                                    ))
                                    if ha_type == "across-az":
                                        RESOURCES[VipEipAddress].Tags = Tags(f5_cloud_failover_label=Ref("AWS::StackName"), f5_cloud_failover_vips=Join(",", [Select("0", GetAtt("Bigip1subnet1Az1Interface", "SecondaryPrivateIpAddresses")), Select("0", GetAtt("Bigip2subnet1Az2Interface", "SecondaryPrivateIpAddresses"))]))
                                else:
                                    RESOURCES[VipEipAddress] = t.add_resource(EIP(
                                        VipEipAddress,
                                        Domain="vpc",
                                    ))
                                    if ha_type == "across-az":
                                        RESOURCES[VipEipAddress].Tags = Tags(f5_cloud_failover_label=Ref("AWS::StackName"), f5_cloud_failover_vips=Join(",", [Select("0", GetAtt("Bigip1subnet1Az1Interface", "SecondaryPrivateIpAddresses")), Select("0", GetAtt("Bigip2subnet1Az2Interface", "SecondaryPrivateIpAddresses"))]))
                                if need_static_ip_addr:
                                    if need_optional_public_ip:
                                        RESOURCES[VipEipAssociation] = t.add_resource(EIPAssociation(
                                            VipEipAssociation,
                                            NetworkInterfaceId=If(
                                                "useDynamicExternalIpAddr",
                                                Ref(ExternalInterface),
                                                Ref(StaticExternalInterface)),
                                            AllocationId=GetAtt(VipEipAddress, "AllocationId"),
                                            Condition="usePublicIP",
                                            PrivateIpAddress=If("useDynamicExternalIpAddr",
                                                                Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                                                                Select("0", GetAtt(StaticExternalInterface, "SecondaryPrivateIpAddresses")))
                                        ))
                                    else:
                                        RESOURCES[VipEipAssociation] = t.add_resource(EIPAssociation(
                                            VipEipAssociation,
                                            NetworkInterfaceId=If(
                                                "useDynamicExternalIpAddr",
                                                Ref(ExternalInterface),
                                                Ref(StaticExternalInterface)),
                                            AllocationId=GetAtt(VipEipAddress, "AllocationId"),
                                            PrivateIpAddress=If("useDynamicExternalIpAddr",
                                                                Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                                                                Select("0", GetAtt(StaticExternalInterface, "SecondaryPrivateIpAddresses")))
                                        ))
                                else:
                                    if need_optional_public_ip:
                                        RESOURCES[VipEipAssociation] = t.add_resource(EIPAssociation(
                                            VipEipAssociation,
                                            NetworkInterfaceId=Ref(ExternalInterface),
                                            AllocationId=GetAtt(VipEipAddress, "AllocationId"),
                                            PrivateIpAddress=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                                            Condition="usePublicIP"
                                        ))
                                    else:
                                        RESOURCES[VipEipAssociation] = t.add_resource(EIPAssociation(
                                            VipEipAssociation,
                                            NetworkInterfaceId=Ref(ExternalInterface),
                                            AllocationId=GetAtt(VipEipAddress, "AllocationId"),
                                            PrivateIpAddress=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses"))
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
                            if need_optional_public_ip:
                                RESOURCES[ManagementEipAddress] = t.add_resource(EIP(
                                    ManagementEipAddress,
                                    Domain="vpc",
                                    Condition="usePublicIP"
                                ))
                            else:
                                RESOURCES[ManagementEipAddress] = t.add_resource(EIP(
                                    ManagementEipAddress,
                                    Domain="vpc",
                                ))
                            if need_static_ip_addr:
                                if need_optional_public_ip:
                                    RESOURCES[ManagementEipAssociation] = t.add_resource(EIPAssociation(
                                        ManagementEipAssociation,
                                        NetworkInterfaceId=If(
                                            "useDynamicManagementIpAddr",
                                            Ref(ManagementInterface),
                                            Ref(StaticManagementInterface)),
                                        AllocationId=GetAtt(ManagementEipAddress, "AllocationId"),
                                        Condition="usePublicIP"
                                    ))
                                else:
                                    RESOURCES[ManagementEipAssociation] = t.add_resource(EIPAssociation(
                                        ManagementEipAssociation,
                                        NetworkInterfaceId=If(
                                            "useDynamicManagementIpAddr",
                                            Ref(ManagementInterface),
                                            Ref(StaticManagementInterface)),
                                        AllocationId=GetAtt(ManagementEipAddress, "AllocationId"),
                                    ))
                            else:
                                if need_optional_public_ip:
                                    RESOURCES[ManagementEipAssociation] = t.add_resource(EIPAssociation(
                                        ManagementEipAssociation,
                                        NetworkInterfaceId=Ref(ManagementInterface),
                                        AllocationId=GetAtt(ManagementEipAddress, "AllocationId"),
                                        Condition="usePublicIP"
                                    ))
                                else:
                                    RESOURCES[ManagementEipAssociation] = t.add_resource(EIPAssociation(
                                        ManagementEipAssociation,
                                        NetworkInterfaceId=Ref(ManagementInterface),
                                        AllocationId=GetAtt(ManagementEipAddress, "AllocationId")
                                    ))
                    if num_nics > 2:
                        InternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "InternalInterface"
                        StaticInternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "StaticInternalInterface"
                        if need_static_ip_addr:
                            RESOURCES[InternalInterface] = t.add_resource(NetworkInterface(
                                InternalInterface,
                                Condition="useDynamicInternalIpAddr",
                                SubnetId=Ref(InternalSubnet),
                                GroupSet=[Ref(bigipInternalSecurityGroup)],
                                Description="Internal Interface for the BIG-IP"
                            ))

                            RESOURCES[StaticInternalInterface] = t.add_resource(NetworkInterface(
                                StaticInternalInterface,
                                Condition="useStaticInternalIpAddr",
                                SubnetId=Ref(InternalSubnet),
                                GroupSet=[Ref(bigipInternalSecurityGroup)],
                                PrivateIpAddress=Ref(InternalSubnetStaticIpAddress),
                                Description="Internal Interface for the BIG-IP"
                            ))
                        else:
                            RESOURCES[InternalInterface] = t.add_resource(NetworkInterface(
                                InternalInterface,
                                SubnetId=Ref(InternalSubnet),
                                GroupSet=[Ref(bigipInternalSecurityGroup)],
                                Description="Internal Interface for the BIG-IP"
                            ))

                        if ha_type == "across-az" or ha_type == "same-az":
                            RESOURCES[InternalInterface].Tags = Tags(f5_cloud_failover_label=Ref("AWS::StackName"), f5_cloud_failover_nic_map="internal")
                    if num_nics > 3:
                        nics = {}
                        for number in range(3, 8):
                            nics[number] = "Bigip" + str(BIGIP_INDEX + 1) + "Interface" + str(number)
                            t.add_resource(NetworkInterface(
                                nics[number],
                                Condition="createNic" + str(number),
                                SubnetId=Select(str(number - 3), Ref("additionalNicLocation")),
                                GroupSet=[Ref(bigipInternalSecurityGroup)],
                                Description="Interface " + str(number) + " for the BIG-IP",
                            ))
                # build variables for metadata
                # variable used to add byol license if flagged for byol
                license_byol = [
                    "--license ",
                    Ref(licenseKey),
                ]
                # bigiq logic
                if license_type == "bigiq":
                    license_bigiq = [
                        "--license-pool --cloud aws",
                        "--big-iq-host",
                        Ref(bigIqAddress),
                        "--big-iq-user",
                        Ref(bigIqUsername),
                        "--license-pool-name",
                        Ref(bigIqLicensePoolName),
                        "--big-iq-password-uri",
                        Ref(bigIqPasswordS3Arn),
                        "--tenant ",
                        {
                            "Fn::If": [
                                "noTenant",
                                {"Ref": "AWS::NoValue"},
                                {"Ref": "bigIqLicenseTenant"}
                            ]
                        },
                        "--unit-of-measure",
                        {
                            "Fn::If": [
                                'noUnitOfMeasure',
                                {"Ref": "AWS::NoValue"},
                                {"Ref": "bigIqLicenseUnitOfMeasure"}
                            ]
                        },
                        "--sku-keyword-1",
                        {
                            "Fn::If": [
                                'noSkuKeyword1',
                                {"Ref": "AWS::NoValue"},
                                {"Ref": "bigIqLicenseSkuKeyword1"}
                            ]
                        },
                        "--sku-keyword-2",
                        {
                            "Fn::If": [
                                'noSkuKeyword2',
                                {"Ref": "AWS::NoValue"},
                                {"Ref": "bigIqLicenseSkuKeyword2"}
                            ]
                        },
                    ]
                    # if num_nics == 1:
                    #     license_bigiq += [
                    #                     "--big-iq-password-uri file:///config/cloud/aws/.bigiq ",
                    #                     ]
                    # else:
                    #     license_bigiq += [
                    #                     "--big-iq-password-uri ",
                    #                     Ref(bigIqPasswordS3Arn),
                    #                     ]

                # variable used to provision asm
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
                # begin building custom-config.sh
                cfe_verify = ""
                cfe = "/config/cloud/f5-cloud-libs.tar.gz"
                cfe_url = "http://cdn.f5.com/product/cloudsolutions/f5-cloud-libs/" + str(branch_cloud) + "/f5-cloud-libs.tar.gz"
                cfe_url_china = "http://cdn.f5.com/product/cloudsolutions/f5-cloud-libs/" + str(branch_cloud) + "/f5-cloud-libs.tar.gz"

                if ha_type != "standalone":
                    cfe_verify = " \"/var/config/rest/downloads/" + str(cfe_name) + "\""
                    cfe = "/var/config/rest/downloads/" + str(cfe_name)
                    cfe_url = "https://github.com/F5Networks/f5-cloud-failover-extension/releases/download/v" + str(cfe_version) + "/" + str(cfe_name)
                    cfe_url_china = "http://cdn.f5.com/product/cloudsolutions/f5-cloud-failover-extension/v" + str(cfe_version) + "/" + str(cfe_name)

                cloudlibs_sh = [
                    "#!/bin/bash",
                    "echo about to execute",
                    "checks=0",
                    "while [ $checks -lt 120 ]; do echo checking mcpd",
                    "    tmsh -a show sys mcp-state field-fmt | grep -q running",
                    "    if [ $? == 0 ]; then",
                    "        echo mcpd ready",
                    "        break",
                    "    fi",
                    "    echo mcpd not ready yet",
                    "    let checks=checks+1",
                    "    sleep 10",
                    "done",
                    "echo loading verifyHash script",
                    str(comment_out) + "if ! tmsh load sys config merge file /config/verifyHash; then",
                    str(comment_out) + "    echo cannot validate signature of /config/verifyHash",
                    str(comment_out) + "    exit",
                    str(comment_out) + "fi",
                    str(comment_out) + "echo loaded verifyHash",
                    str(comment_out) + "declare -a filesToVerify=(\"/config/cloud/f5-cloud-libs.tar.gz\" \"/config/cloud/f5-cloud-libs-aws.tar.gz\")",
                    str(comment_out) + "for fileToVerify in \"${filesToVerify[@]}\"",
                    str(comment_out) + "do",
                    str(comment_out) + "    echo verifying \"$fileToVerify\"",
                    str(comment_out) + "    if ! tmsh run cli script verifyHash \"$fileToVerify\"; then",
                    str(comment_out) + "        echo \"$fileToVerify\" is not valid",
                    str(comment_out) + "        exit 1",
                    str(comment_out) + "    fi",
                    str(comment_out) + "    echo verified \"$fileToVerify\"",
                    str(comment_out) + "done",
                    "mkdir -p /config/cloud/aws/node_modules/@f5devcentral",
                    "echo expanding f5-cloud-libs.tar.gz",
                    "tar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/aws/node_modules/@f5devcentral",
                ]

                cloudlibs_sh += [
                    "echo installing dependencies",
                    "tar xvfz /config/cloud/f5-cloud-libs-aws.tar.gz -C /config/cloud/aws/node_modules/@f5devcentral",
                    "echo cloud libs install complete",
                ]
                cloudlibs_sh += [
                    "touch /config/cloud/cloudLibsReady"
                ]
                waitthenrun_sh = [
                    "#!/bin/bash",
                    "while true; do echo \"waiting for cloud libs install to complete\"",
                    "    if [ -f /config/cloud/cloudLibsReady ]; then",
                    "        break",
                    "    else",
                    "        sleep 10",
                    "    fi",
                    "done",
                    "\"$@\""
                ]
                get_nameserver = [
                    "INTERFACE=$1",
                    "INTERFACE_MAC=`ifconfig ${INTERFACE} | egrep ether | awk '{print tolower($2)}'`",
                    "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`",
                    "VPC_CIDR_BLOCK=`/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${INTERFACE_MAC}/vpc-ipv4-cidr-block`",
                    "VPC_NET=${VPC_CIDR_BLOCK%/*}",
                    "NAME_SERVER=`echo ${VPC_NET} | awk -F. '{ printf \"%d.%d.%d.%d\", $1, $2, $3, $4+2 }'`",
                    "echo $NAME_SERVER"
                ]
                get_management_gateway = [
                    "INTERFACE=$1",
                    "GATEWAY_MAC=`ifconfig ${INTERFACE} | egrep ether | awk '{print tolower($2)}'`",
                    "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`",
                    "GATEWAY_CIDR_BLOCK=`/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC}/subnet-ipv4-cidr-block`",
                    "GATEWAY_NET=${GATEWAY_CIDR_BLOCK%/*}",
                    "GATEWAY=`echo ${GATEWAY_NET} | awk -F. '{ print $1\".\"$2\".\"$3\".\"$4+1 }'`",
                    "echo $GATEWAY"
                ]
                create_user = [
                    "#!/bin/bash",
                    "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/generatePassword --file /config/cloud/aws/.adminPassword --include-special-characters",
                    "PASSWORD=$(/bin/sed -e $'s:[\\'\"%{};/|#\\x20\\\\\\\\]:\\\\\\\\&:g' < /config/cloud/aws/.adminPassword)",
                    "if [ \"$1\" = admin ]; then",
                    "    tmsh modify auth user \"$1\" password ${PASSWORD}",
                    "else",
                    "    tmsh create auth user \"$1\" password ${PASSWORD} shell bash partition-access replace-all-with { all-partitions { role admin } }",
                    "fi"
                ]
                generate_password = [
                    "nohup /config/waitThenRun.sh",
                    " f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
                    " --signal PASSWORD_CREATED",
                    " --file f5-rest-node",
                    " --cl-args '/config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/generatePassword --file /config/cloud/aws/.adminPassword --encrypt'",
                    " --log-level " + loglevel,
                    " -o /var/log/cloud/aws/generatePassword.log",
                    " &>> /var/log/cloud/aws/install.log < /dev/null",
                    " &"
                ]
                admin_user = [
                    "nohup /config/waitThenRun.sh",
                    " f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
                ]
                admin_user += [
                    " --wait-for PASSWORD_CREATED",
                    " --signal ADMIN_CREATED",
                    " --file /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/createUser.sh",
                    " --cl-args '--user srv_user",
                    " --password-file /config/cloud/aws/.adminPassword",
                    " --password-encrypted",
                    "'",
                    " --log-level " + loglevel,
                    " -o /var/log/cloud/aws/createUser.log",
                    " &>> /var/log/cloud/aws/install.log < /dev/null",
                    " &"
                ]
                               
                download_runtime_command = "/usr/bin/curl -fv --retry 1 --connect-timeout 5 -L " + runtime_init_url + " -o " + "/var/config/rest/downloads/" + package_runtime_init + "\n"
                install_runtime_command = "bash " + "/var/config/rest/downloads/" + package_runtime_init + " -- '--cloud aws'\n"

                unpack_libs = [
                    "mkdir -p /var/log/cloud/aws;",
                    "nohup /config/installCloudLibs.sh",
                    "&>> /var/log/cloud/aws/install.log < /dev/null &"
                ]

                onboard_BIG_IP = [
                ]
                one_nic_setup = [
                ]
                cluster_BIG_IP = [
                ]
                custom_command = [
                    "nohup /config/waitThenRun.sh",
                    "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
                    "--file /config/cloud/aws/custom-config.sh",
                    "--cwd /config/cloud/aws",
                    "-o /var/log/cloud/aws/custom-config.log",
                    "--log-level " + loglevel,
                    "--wait-for ONBOARD_DONE",
                    "--signal CUSTOM_CONFIG_DONE",
                    "&>> /var/log/cloud/aws/install.log < /dev/null &"
                ]
                cfe_command =[]
                # if num_nics == 1 and license_type == "bigiq":
                #     custom_command +=   [
                #                         "--wait-for RERUN_NETWORK_CONFIG_DONE",
                #                     ]
                # else:
                #     custom_command +=   [
                #                         "--wait-for ONBOARD_DONE",
                #                     ]
                # custom_command +=   [
                #                     "&>> /var/log/cloud/aws/install.log < /dev/null &"
                #                 ]
                cluster_command = []
                cfe_file = [
                    "{\n",
                    "    \"class\":\"Cloud_Failover\",\n",
                    "    \"controls\":{\n",
                    "      \"class\":\"Controls\",\n",
                    "      \"logLevel\":\"silly\"\n",
                    "    },\n",
                    "    \"environment\":\"aws\",\n",
                    "    \"externalStorage\":{\n",
                    "      \"scopingTags\":{\n",
                    "      \"f5_cloud_failover_label\":\"",
                    {
                        "Ref": "AWS::StackName"
                    },
                    "\"\n",
                    "      }\n",
                    "    },\n",
                    "    \"failoverAddresses\":{\n",
                    "      \"scopingTags\":{\n",
                    "      \"f5_cloud_failover_label\":\"",
                    {
                        "Ref": "AWS::StackName"
                    },
                    "\"\n",
                    "      }\n",
                    "    },\n",
                    "    \"failoverRoutes\":{\n",
                    "      \"scopingTags\":{\n",
                    "      \"f5_cloud_failover_label\":\"",
                    {
                        "Ref": "AWS::StackName"
                    },
                    "\"\n",
                    "      },\n",
                    "      \"scopingAddressRanges\":[\n",
                    "           {\n",
                    "             \"range\":\"192.0.2.0\/24\"\n",
                    "           }\n",
                    "       ],\n",
                    "      \"defaultNextHopAddresses\":{\n",
                    "        \"discoveryType\":\"static\",\n",
                    "        \"items\":[\n",
                    "              \"",
                    GetAtt("Bigip1subnet1Az1Interface", "PrimaryPrivateIpAddress"),
                    "\",\n",
                ]
                if ha_type == "across-az":
                    cfe_file += [
                        "              \"",
                        GetAtt("Bigip2subnet1Az2Interface", "PrimaryPrivateIpAddress"),
                        "\"\n",
                        "         ]\n",
                            "       }\n",
                        "     }\n",
                        "}"
                    ]
                elif ha_type == "same-az":
                    cfe_file += [
                        "              \"",
                        GetAtt("Bigip2subnet1Az1Interface", "PrimaryPrivateIpAddress"),
                        "\"\n",
                        "         ]\n",
                            "       }\n",
                        "     }\n",
                        "}"
                    ]
                rm_password_sh = [
                    "#!/bin/bash\n",
                    "PROGNAME=$(basename $0)\n",
                    "function error_exit {\n",
                    "echo \"${PROGNAME}: ${1:-\"Unknown Error\"}\" 1>&2\n",
                    "exit 1\n",
                    "}\n",
                    "date\n",
                    "echo 'starting rm-srv-user.sh'\n",
                    "declare -a tmsh=()\n",
                ]
                rm_password_sh += [
                    "tmsh+=(\"rm /config/cloud/aws/.adminPassword\")\n",
                    "for CMD in \"${tmsh[@]}\"\n",
                    "do\n",
                    "  if $CMD;then\n",
                    "      echo \"command $CMD successfully executed.\"\n",
                    "  else\n",
                    "      error_exit \"$LINENO: An error has occurred while executing $CMD. Aborting!\"\n",
                    "  fi\n",
                    "done\n",
                    "date\n",
                ]
                if ( ha_type != "autoscale" and (BIGIP_INDEX) == CLUSTER_SEED) or ha_type != "standalone":
                    rm_password_sh += [
                        "flag=true\n",
                        "while $flag\n",
                        "do\n",
                        "response=$(tmsh show cm sync-status)\n",
                        "if echo $response | grep 'All devices in the device group are in sync' ; then\n",
                        "flag=false\n",
                        "tmsh delete auth user srv_user\n",
                        "fi\n",
                        "done\n",
                    ]
                rm_password_command = [
                    "nohup /config/waitThenRun.sh",
                    "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
                    "--file /config/cloud/aws/rm-srv-user.sh",
                    "-o /var/log/cloud/aws/rm-srv-user.log",
                    "--log-level " + loglevel,
                ]
                if ha_type == "standalone":
                    rm_password_command += [
                        "--wait-for CUSTOM_CONFIG_DONE",
                        "--signal SRV_USER_REMOVED",
                        "&>> /var/log/cloud/aws/install.log < /dev/null &"
                    ]
                if ha_type != "standalone" and (BIGIP_INDEX) == CLUSTER_SEED:
                    rm_password_command += [
                        "--wait-for CFE_CONFIG_DONE",
                        "--signal SRV_USER_REMOVED",
                        "&>> /var/log/cloud/aws/install.log < /dev/null &"
                    ]
                    cluster_command += [
                        "nohup /config/waitThenRun.sh",
                        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/cluster.js",
                        "--wait-for CUSTOM_CONFIG_DONE",
                        "--signal CLUSTER_DONE",
                        "-o /var/log/cloud/aws/cluster.log",
                        "--log-level " + loglevel,
                        "--host localhost",
                        "--delete-remote-primary-creds",
                        "--user srv_user",
                        "--delete-local-creds",
                        "--password-url file:///config/cloud/aws/.adminPassword",
                        "--password-encrypted",
                        "--cloud aws",
                        "--provider-options 's3Bucket:", Ref(s3bucket), "'",
                    ]
                    cfe_command = [
                        "nohup /config/waitThenRun.sh",
                        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
                        "--file /config/cloud/aws/cfe-config.sh",
                        "--cwd /config/cloud/aws",
                        "-o /var/log/cloud/aws/cfe-config.log",
                        "--log-level " + loglevel,
                        "--wait-for CLUSTER_DONE",
                        "--signal CFE_CONFIG_DONE",
                        "&>> /var/log/cloud/aws/install.log < /dev/null &"
                    ]

                    if num_nics > 2:
                        cluster_command += [
                            "--config-sync-ip", GetAtt("Bigip2InternalInterface", "PrimaryPrivateIpAddress"),
                        ]
                    else:
                        cluster_command += [
                            "--config-sync-ip", GetAtt("Bigip2subnet1Az" + str(num_azs) + "Interface", "PrimaryPrivateIpAddress"),
                        ]

                    if ha_type == "across-az":
                        cluster_command += [
                            "--join-group",
                            "--device-group across_az_failover_group",
                            "--remote-host ", GetAtt("Bigip1ManagementInterface", "PrimaryPrivateIpAddress"),
                            "&>> /var/log/cloud/aws/install.log < /dev/null &"
                        ]
                    else:
                        cluster_command += [
                            "--join-group",
                            "--device-group same_az_failover_group",
                            "--remote-host ", GetAtt("Bigip1ManagementInterface", "PrimaryPrivateIpAddress"),
                            "&>> /var/log/cloud/aws/install.log < /dev/null &"
                        ]
                if ha_type != "standalone" and (BIGIP_INDEX + 1) == CLUSTER_SEED:
                    rm_password_command += [
                        "--wait-for CFE_CONFIG_DONE",
                        "--signal SRV_USER_REMOVED",
                        "&>> /var/log/cloud/aws/install.log < /dev/null &"
                    ]
                    cfe_command = [
                        "nohup /config/waitThenRun.sh",
                        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js",
                        "--file /config/cloud/aws/cfe-config.sh",
                        "--cwd /config/cloud/aws",
                        "-o /var/log/cloud/aws/cfe-config.log",
                        "--log-level " + loglevel,
                        "--wait-for CLUSTER_DONE",
                        "--signal CFE_CONFIG_DONE",
                        "&>> /var/log/cloud/aws/install.log < /dev/null &"
                    ]
                    cluster_command += [
                        "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`;",
                        "HOSTNAME=`/usr/bin/curl -sS -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`;",
                        "nohup /config/waitThenRun.sh",
                        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/cluster.js",
                        "--wait-for CUSTOM_CONFIG_DONE",
                        "--signal CLUSTER_DONE",
                        "-o /var/log/cloud/aws/cluster.log",
                        "--log-level " + loglevel,
                        "--host localhost",
                        "--delete-remote-primary-creds",
                        "--user srv_user",
                        "--delete-local-creds",
                        "--password-url file:///config/cloud/aws/.adminPassword",
                        "--password-encrypted",
                        "--cloud aws",
                        "--provider-options 's3Bucket:", Ref(s3bucket), "'",
                        "--primary",
                    ]
                    if num_nics > 2:
                        cluster_command += [
                            "--config-sync-ip", GetAtt("Bigip1InternalInterface", "PrimaryPrivateIpAddress"),
                        ]
                    else:
                        cluster_command += [
                            "--config-sync-ip", GetAtt("Bigip1subnet1Az1Interface", "PrimaryPrivateIpAddress"),
                        ]
                    if ha_type == "across-az":
                        cluster_command += [
                            "--create-group",
                            "--device-group across_az_failover_group",
                            "--sync-type sync-failover",
                            "--network-failover",
                            "--device ${HOSTNAME}",
                            "--auto-sync",
                            "&>> /var/log/cloud/aws/install.log < /dev/null &"
                        ]
                    else:
                        cluster_command += [
                            "--create-group",
                            "--device-group same_az_failover_group",
                            "--sync-type sync-failover",
                            "--network-failover",
                            "--device ${HOSTNAME}",
                            "--auto-sync",
                            "&>> /var/log/cloud/aws/install.log < /dev/null &"
                        ]

                onboard_BIG_IP_metrics = [
                    "REGION=\"",
                    {
                        "Ref": "AWS::Region"
                    },
                    "\";",
                    "DEPLOYMENTID=`echo \"",
                    {
                        "Ref": "AWS::StackId"
                    },
                    "\"|sha512sum|cut -d \" \" -f 1`;",
                    "CUSTOMERID=`echo \"",
                    {
                        "Ref": "AWS::AccountId"
                    },
                    "\"|sha512sum|cut -d \" \" -f 1`;",

                ]
                # Global Settings
                if num_nics == 1:
                    network_config = [
                        "nohup /config/waitThenRun.sh ",
                        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js ",
                        "--file /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/aws/1nicSetup.sh ",
                        "--cwd /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/aws ",
                        "--log-level " + loglevel + " ",
                        "-o /var/log/cloud/aws/1nicSetup.log ",
                        "--signal NETWORK_CONFIG_DONE ",
                        "&>> /var/log/cloud/aws/install.log < /dev/null &"
                    ]
                    onboard_BIG_IP += [
                        "NAME_SERVER=`/config/cloud/aws/getNameServer.sh mgmt`;",
                        "nohup /config/waitThenRun.sh",
                        "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`;",
                        "HOSTNAME=`/usr/bin/curl -sS --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`;",
                        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/onboard.js",
                        "--port 8443",
                        "--ssl-port ", Ref(managementGuiPort),
                        "--wait-for NETWORK_CONFIG_DONE",
                        "--signal ONBOARD_DONE",
                    ]
                    # if license_type == "bigiq":
                    #     onboard_BIG_IP += [
                    #                     "--wait-for BIGIQ_CONFIG_DONE",
                    #     ]
                    #     bigiq_config = [
                    #                     "nohup /config/waitThenRun.sh ",
                    #                     "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/runScript.js ",
                    #                     "--file /config/bigiqConfig.sh ",
                    #                     "--cwd /config/ ",
                    #                     "--log-level silly ",
                    #                     "-o /var/log/cloud/aws/bigiqConfig.log ",
                    #                     "--wait-for NETWORK_CONFIG_DONE ",
                    #                     "--signal BIGIQ_CONFIG_DONE ",
                    #                     "&>> /var/log/install.log < /dev/null &"
                    #     ]
                    # else:
                    #     onboard_BIG_IP += [
                    #                     "--wait-for NETWORK_CONFIG_DONE",
                    #     ]

                if num_nics > 1:
                    onboard_BIG_IP += [
                        "NAME_SERVER=`/config/cloud/aws/getNameServer.sh eth0`;",
                        "nohup /config/waitThenRun.sh",
                        "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`;",
                        "HOSTNAME=`/usr/bin/curl -sS --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`;",
                        "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/onboard.js",
                        "--wait-for NETWORK_CONFIG_DONE",
                        "--signal ONBOARD_DONE",
                    ]
                onboard_BIG_IP += [
                    "-o /var/log/cloud/aws/onboard.log",
                    "--log-level " + loglevel,
                    "--no-reboot",
                    "--host localhost",
                    "--hostname ${HOSTNAME}",
                    "--ntp ", Ref(ntpServer),
                    "--tz ", Ref(timezone),
                    "--dns ${NAME_SERVER}",
                    "--modules ",
                    {"Ref": "bigIpModules"},
                ]

                # Build Scripts
                custom_sh = [
                    "#!/bin/bash\n",
                    "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`\n",
                ]
                if stack == "full":
                    custom_sh += [
                        "POOLMEM='", GetAtt('Webserver', 'PrivateIp'), "'\n",
                        "POOLMEMPORT=80\n",
                        "APPNAME='demo-app-1'\n",
                        "VIRTUALSERVERPORT=80\n",
                    ]
                if ha_type != "standalone":
                    custom_sh += [
                        "EXTIP='", GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"), "'\n",
                        "EXTPRIVIP='", Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")), "'\n",
                        "HOSTNAME=`/usr/bin/curl -sS -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN http://169.254.169.254/latest/meta-data/hostname`\n",
                    ]
                    if num_nics > 2:
                        custom_sh += [
                            "INTIP='", GetAtt(InternalInterface, "PrimaryPrivateIpAddress"), "'\n",
                        ]
                if ha_type != "standalone" and (BIGIP_INDEX + 1) == CLUSTER_SEED:
                    if num_nics > 1:
                        if ha_type == "across-az":
                            custom_sh += [
                                "PEER_EXTPRIVIP='", Select("0", GetAtt("Bigip" + str(BIGIP_INDEX + 2) + "subnet1" + "Az" + str(BIGIP_INDEX + 2) + "Interface", "SecondaryPrivateIpAddresses")), "'\n"
                            ]
                            if stack == "full":
                                custom_sh += [
                                    "VIPEIP='", Ref(VipEipAddress), "'\n",
                                ]
                            else:
                                custom_sh += [
                                    "VIPEIP='", If("usePublicIP", Ref(VipEipAddress), Ref("AWS::NoValue")), "'\n",
                                ]
                            if num_nics > 2:
                                custom_sh += [
                                    "GATEWAY_MAC2=`cat /config/cloud/net2_mac | awk '{print tolower($2)}'`\n",
                                    "GATEWAY_CIDR_BLOCK2=`/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC2}/subnet-ipv4-cidr-block`\n",
                                    "GATEWAY_NET2=${GATEWAY_CIDR_BLOCK2%/*}\n",
                                    "GATEWAY2=`echo ${GATEWAY_NET2} | awk -F. '{ print $1\".\"$2\".\"$3\".\"$4+1 }'`\n",
                                    "VPC_CIDRS=$(/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC2}/vpc-ipv4-cidr-blocks/); ",
                                ]
                        if ha_type == "same-az":
                            if stack == "existing" or stack == "full":
                                custom_sh += [
                                    "PEER_EXTPRIVIP='", Select("0", GetAtt("Bigip" + str(BIGIP_INDEX + 2) + "subnet1" + "Az1Interface", "SecondaryPrivateIpAddresses")), "'\n",
                                ]
                            elif stack == "prod":
                                custom_sh += [
                                    "PEER_EXTPRIVIP='", Select("0", GetAtt("Bigip" + str(BIGIP_INDEX + 2) + "subnet1" + "Az1Interface", "SecondaryPrivateIpAddresses")), "'\n",
                                ]
                if ha_type != "standalone" and (BIGIP_INDEX) == CLUSTER_SEED and num_nics > 2 and ha_type == "across-az":
                        custom_sh += [
                            "GATEWAY_MAC2=`cat /config/cloud/net2_mac | awk '{print tolower($2)}'`\n",
                            "GATEWAY_CIDR_BLOCK2=`/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC2}/subnet-ipv4-cidr-block`\n",
                            "GATEWAY_NET2=${GATEWAY_CIDR_BLOCK2%/*}\n",
                            "GATEWAY2=`echo ${GATEWAY_NET2} | awk -F. '{ print $1\".\"$2\".\"$3\".\"$4+1 }'`\n",
                            "VPC_CIDRS=$(/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC2}/vpc-ipv4-cidr-blocks/); ",
                        ]
                custom_sh += [
                    "PROGNAME=$(basename $0)\n",
                    "function error_exit {\n",
                    "echo \"${PROGNAME}: ${1:-\\\"Unknown Error\\\"}\" 1>&2\n",
                    "exit 1\n",
                    "}\n",
                    "declare -a tmsh=()\n",
                    "echo 'starting custom-config.sh'\n",
                    "source /config/cloud/aws/onboard_config_vars\n",
                    "if [[ $allowPhoneHome == \"No\" ]]; then\n",
                    "    tmsh+=(\n",
                    "    \"tmsh modify sys software update auto-phonehome disabled\")\n",
                    "fi\n",
                ]
                if num_nics == 1:
                    if license_type == "bigiq":
                        custom_sh += [
                            "echo `date` 'Waiting for \"Tmm ready - links up\"'\n",
                            "while [ $(grep -c 'Tmm ready - links up' /var/log/ltm) -lt 2 ]; do continue; done;echo `date` 'Tmm ready - links up'\n",
                            "tmsh+=(\n",
                        ]
                    else:
                        custom_sh += [
                            "tmsh+=(\n",
                        ]
                    # Sync and Failover ( UDP 1026 and TCP 4353 already included in self-allow defaults )
                    if 'waf' in components:
                        custom_sh += [
                            "\"tmsh modify net self-allow defaults add { tcp:6123 tcp:6124 tcp:6125 tcp:6126 tcp:6127 tcp:6128 }\"\n",
                        ]
                else:
                    custom_sh += [
                        "tmsh+=(\n",
                    ]
                # Network Settings

                if num_nics > 1:
                    vlans = ""
                    network_config = [
                        "GATEWAY_MAC=`cat /config/cloud/net1_mac | awk '{print tolower($2)}'`\n",
                        "sleep 30 && TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`\n",
                        "GATEWAY_CIDR_BLOCK=`/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC}/subnet-ipv4-cidr-block`; ",
                        "GATEWAY_NET=${GATEWAY_CIDR_BLOCK%/*}; ",
                        "GATEWAY_PREFIX=${GATEWAY_CIDR_BLOCK#*/}; ",
                        "GATEWAY=`echo ${GATEWAY_NET} | awk -F. '{ print $1\".\"$2\".\"$3\".\"$4+1 }'`; ",
                    ]
                    if ha_type == "across-az":
                        network_config += [
                            "NAME_SERVER=`/config/cloud/aws/getNameServer.sh eth0`; ",
                            "MGMT_GATEWAY=`/config/cloud/aws/getManagementGateway.sh eth0`; ",
                        ]
                    if num_nics > 2:
                        network_config += [
                            "GATEWAY_MAC2=`cat /config/cloud/net2_mac | awk '{print tolower($2)}'`\n",
                            "GATEWAY_CIDR_BLOCK2=`/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC2}/subnet-ipv4-cidr-block`; ",
                            "GATEWAY_PREFIX2=${GATEWAY_CIDR_BLOCK2#*/}; ",
                        ]
                        if ha_type == "across-az":
                            network_config += [
                                "GATEWAY_NET2=${GATEWAY_CIDR_BLOCK2%/*}; ",
                                "GATEWAY2=`echo ${GATEWAY_NET2} | awk -F. '{ print $1\".\"$2\".\"$3\".\"$4+1 }'`; ",
                                "VPC_CIDRS=$(/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC}/vpc-ipv4-cidr-blocks/); ",
                            ]
                    if num_nics > 3:
                        for number in range(3, 8):
                            network_config += [
                                If("createNic" + str(number),
                                    "GATEWAY_MAC" + str(number) + "=`cat /config/cloud/net" + str(number) +"_mac | awk '{print tolower($2)}'`;GATEWAY_CIDR_BLOCK" + str(number) + "=`/usr/bin/curl -s -f --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/network/interfaces/macs/${GATEWAY_MAC" + str(number) + "}/subnet-ipv4-cidr-block`;GATEWAY_PREFIX" + str(number) + "=${GATEWAY_CIDR_BLOCK" + str(number) + "#*/};",
                                    ""
                                    )
                            ]
                    if ha_type != "standalone":
                        network_config += [
                            "nohup /config/waitThenRun.sh ",
                            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js ",
                            "--host localhost ",
                            "-o /var/log/cloud/aws/network.log ",
                            "--log-level " + loglevel + " ",
                            "--wait-for ADMIN_CREATED ",
                            "--signal NETWORK_CONFIG_DONE ",
                            "--vlan name:external,nic:1.1 ",
                            "--default-gw ${GATEWAY} ",
                        ]
                    else:
                        network_config += [
                            "nohup /config/waitThenRun.sh ",
                            "f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/network.js ",
                            "--host localhost ",
                            "-o /var/log/cloud/aws/network.log ",
                            "--log-level " + loglevel + " ",
                            "--signal NETWORK_CONFIG_DONE ",
                            "--vlan name:external,nic:1.1 ",
                            "--default-gw ${GATEWAY} ",
                            ]
                    if ha_type == "across-az":
                        network_config += [
                            "--mgmt-route name:dns_route,gw:${MGMT_GATEWAY},network:${NAME_SERVER}/32 ",
                        ]
                    if ha_type == "standalone":
                        if 'waf' not in components:
                            if num_nics < 4 and stack not in reference_stacks:
                                network_config += [
                                    "--self-ip name:external-self,address:",
                                    If("useDynamicExternalIpAddr",
                                        GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
                                        GetAtt(StaticExternalInterface, "PrimaryPrivateIpAddress")),
                                    "/${GATEWAY_PREFIX},vlan:external ",
                                ]
                                if num_nics > 2:
                                    network_config += [
                                        "--vlan name:internal,nic:1.2 ",
                                        "--self-ip name:internal-self,address:",
                                        If("useDynamicInternalIpAddr",
                                            GetAtt(InternalInterface, "PrimaryPrivateIpAddress"),
                                            GetAtt(StaticInternalInterface, "PrimaryPrivateIpAddress")),
                                        "/${GATEWAY_PREFIX2},vlan:internal "
                                    ]
                            else:
                                network_config += [
                                    "--self-ip name:external-self,address:",
                                    GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
                                    "/${GATEWAY_PREFIX},vlan:external ",
                                ]
                                if num_nics > 2:
                                    network_config += [
                                        "--vlan name:internal,nic:1.2 ",
                                        "--self-ip name:internal-self,address:",
                                        GetAtt(InternalInterface, "PrimaryPrivateIpAddress"),
                                        "/${GATEWAY_PREFIX2},vlan:internal "
                                    ]
                            if num_nics > 3:
                                for number in range(3, 8):
                                    network_config += [
                                        If("createNic" + str(number),
                                            Join(
                                                "",
                                                [
                                                    "--vlan name:net" + str(number) + ",nic:1." + str(number) + " ",
                                                    "--self-ip name:interface" + str(number) + "-self,address:",
                                                    {
                                                        "Fn::GetAtt": [
                                                            nics[number],
                                                            "PrimaryPrivateIpAddress"
                                                        ]
                                                    },
                                                    "/${GATEWAY_PREFIX" + str(number) + "},vlan:net" + str(number) + " ",
                                                ]),
                                            "")]
                        if 'waf' in components:
                            network_config += [
                                "--self-ip 'name:external-self,address:", GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"), "/'${GATEWAY_PREFIX}',vlan:external,allow:tcp:6123 tcp:6124 tcp:6125 tcp:6126 tcp:6127 tcp:6128' ",
                            ]
                            if num_nics > 2:
                                network_config += [
                                    "--vlan name:internal,nic:1.2 ",
                                    "--self-ip 'name:internal-self,address:", GetAtt(InternalInterface, "PrimaryPrivateIpAddress"), "/'${GATEWAY_PREFIX2}',vlan:internal,allow:tcp:6123 tcp:6124 tcp:6125 tcp:6126 tcp:6127 tcp:6128' "
                                ]
                    if ha_type != "standalone" and num_nics == 2:
                        if 'waf' not in components:
                            network_config += [
                                "--self-ip 'name:external-self,address:", GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"), "/'${GATEWAY_PREFIX}',vlan:external,allow:tcp:4353 udp:1026' ",
                            ]
                        if 'waf' in components:
                            network_config += [
                                "--self-ip 'name:external-self,address:", GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"), "/'${GATEWAY_PREFIX}',vlan:external,allow:tcp:4353 udp:1026 tcp:6123 tcp:6124 tcp:6125 tcp:6126 tcp:6127 tcp:6128' ",
                            ]
                        if ha_type == "across-az":
                            network_config += [
                                "--local-only ",
                            ]
                    if ha_type != "standalone" and num_nics > 2:
                        if 'waf' not in components:
                            network_config += [
                                "--self-ip name:external-self,address:", GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"), "/${GATEWAY_PREFIX},vlan:external,allow:none ",
                                "--vlan name:internal,nic:1.2 ",
                                "--self-ip 'name:internal-self,address:", GetAtt(InternalInterface, "PrimaryPrivateIpAddress"), "/'${GATEWAY_PREFIX2}',vlan:internal,allow:tcp:4353 udp:1026' ",
                            ]
                        if 'waf' in components:
                            network_config += [
                                "--self-ip name:external-self,address:", GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"), "/${GATEWAY_PREFIX},vlan:external,allow:none ",
                                "--vlan name:internal,nic:1.2 ",
                                "--self-ip 'name:internal-self,address:", GetAtt(InternalInterface, "PrimaryPrivateIpAddress"), "/'${GATEWAY_PREFIX2}',vlan:internal,allow:tcp:4353 udp:1026 tcp:6123 tcp:6124 tcp:6125 tcp:6126 tcp:6127 tcp:6128' ",
                            ]
                        if ha_type == "across-az":
                            network_config += [
                                "--local-only ",
                            ]
                # Set Gateway

                if num_nics > 1:
                    network_config += [
                        "&>> /var/log/cloud/aws/install.log < /dev/null &"
                    ]
                # Disable DHCP if clustering.
                if ha_type != "standalone":
                    if num_nics == 2:
                        custom_sh += [
                            "\"tmsh modify sys db dhclient.mgmt { value disable }\"\n",
                            "\"tmsh modify cm device ${HOSTNAME} unicast-address { { effective-ip ${EXTIP} effective-port 1026 ip ${EXTIP} } }\"\n",
                        ]
                    if num_nics > 2:
                        if ha_type == "same-az":
                            custom_sh += [
                                "\"tmsh modify sys db dhclient.mgmt { value disable }\"\n",
                                "\"tmsh modify cm device ${HOSTNAME} unicast-address { { effective-ip ${INTIP} effective-port 1026 ip ${INTIP} } }\"\n",
                            ]
                        if ha_type == "across-az":
                            custom_sh += [
                                "\"tmsh modify sys db dhclient.mgmt { value disable }\"\n",
                                "\"tmsh modify cm device ${HOSTNAME} unicast-address { { effective-ip ${INTIP} effective-port 1026 ip ${INTIP} } }\")\n",
                                "for CIDR in ${VPC_CIDRS}; do\n",
                                "   SUFFIX=$(echo ${CIDR} | tr -d '., /')\n",
                                "   tmsh+=(\n",
                                "   \"tmsh create /net route /LOCAL_ONLY/int-rt-${SUFFIX} gw ${GATEWAY2} network ${CIDR}\")\n",
                                "done\n",
                                "tmsh+=(\n",
                            ]
                # License Device
                if license_type == "byol":
                    onboard_BIG_IP += license_byol
                elif license_type == "bigiq":
                    onboard_BIG_IP += license_bigiq
                # Wait until licensing finishes
                if license_type == "hourly":
                    custom_sh += [
                    ]
                # Provision Modules
                if 'waf' in components:
                    onboard_BIG_IP += [
                        "--module asm:nominal",
                    ]
                onboard_BIG_IP_metrics += onboard_BIG_IP
                onboard_BIG_IP_metrics += [
                    "--metrics \"cloudName:aws,region:${REGION},bigIpVersion:" + BIGIP_VERSION + ",customerId:${CUSTOMERID},deploymentId:${DEPLOYMENTID},templateName:" + template_name + ",templateVersion:" + version + ",licenseType:" + license_type + "\"",
                    "-d tm.tcpudptxchecksum:software-only ",
                    "--ping",
                    "&>> /var/log/cloud/aws/install.log < /dev/null &"
                ]
                onboard_BIG_IP += [
                    "-d tm.tcpudptxchecksum:software-only ",
                    "--ping",
                    "&>> /var/log/cloud/aws/install.log < /dev/null &"
                ]
                # Cluster Devices if Cluster Seed
                if ha_type == "standalone" or (BIGIP_INDEX + 1) == CLUSTER_SEED:
                    if stack not in not_full_stacks:
                        # Add Pool
                        custom_sh += [
                            "\"tmsh create ltm pool ${APPNAME}-pool members add { ${POOLMEM}:${POOLMEMPORT} } monitor http\"\n",
                        ]
                        # Add virtual service with simple URI-Routing ltm policy
                        if 'waf' not in components:
                            custom_sh += [
                                "\"tmsh create ltm policy uri-routing-policy controls add { forwarding } requires add { http } strategy first-match legacy\"\n",
                                "\"tmsh modify ltm policy uri-routing-policy rules add { service1.example.com { conditions add { 0 { http-uri host values { service1.example.com } } } actions add { 0 { forward select pool ${APPNAME}-pool } } ordinal 1 } }\"\n",
                                "\"tmsh modify ltm policy uri-routing-policy rules add { service2.example.com { conditions add { 0 { http-uri host values { service2.example.com } } } actions add { 0 { forward select pool ${APPNAME}-pool } } ordinal 2 } }\"\n",
                                "\"tmsh modify ltm policy uri-routing-policy rules add { apiv2 { conditions add { 0 { http-uri path starts-with values { /apiv2 } } } actions add { 0 { forward select pool ${APPNAME}-pool } } ordinal 3 } }\"\n",
                            ]
                            if ha_type != "across-az":
                                if num_nics == 1:
                                    custom_sh += [
                                        "\"tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination 0.0.0.0:${VIRTUALSERVERPORT} mask any ip-protocol tcp pool /Common/${APPNAME}-pool policies replace-all-with { uri-routing-policy { } } profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\"\n",
                                    ]
                                if num_nics > 1:
                                    custom_sh += [
                                        "\"tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp pool /Common/${APPNAME}-pool policies replace-all-with { uri-routing-policy { } } profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\"\n",
                                    ]
                            if ha_type == "across-az":
                                custom_sh += [
                                    "\"tmsh create ltm virtual /Common/AZ1-${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp pool /Common/${APPNAME}-pool policies replace-all-with { uri-routing-policy { } } profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\"\n",
                                    "\"tmsh create ltm virtual /Common/AZ2-${APPNAME}-${VIRTUALSERVERPORT} { destination ${PEER_EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp pool /Common/${APPNAME}-pool policies replace-all-with { uri-routing-policy { } } profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\"\n",
                                    "\"tmsh modify ltm virtual-address ${EXTPRIVIP} traffic-group none\"\n",
                                    "\"tmsh modify ltm virtual-address ${PEER_EXTPRIVIP} traffic-group none\"\n",
                                ]
                    if 'waf' in components:
                        # 12.1.0 requires "first match legacy"
                        custom_sh += [
                            "\"/usr/bin/curl -s -f --retry 20 -o /home/admin/asm-policy-linux-high.xml http://cdn.f5.com/product/templates/utils/asm-policy-linux-high.xml\"\n",
                            "\"tmsh load asm policy file /home/admin/asm-policy-linux-high.xml\"\n",
                            "\"tmsh modify asm policy /Common/linux-high active\"\n",
                            "\"tmsh create ltm policy app-ltm-policy strategy first-match legacy\"\n",
                            "\"tmsh modify ltm policy app-ltm-policy controls add { asm }\"\n",
                            "\"tmsh modify ltm policy app-ltm-policy rules add { associate-asm-policy { actions replace-all-with { 0 { asm request enable policy /Common/linux-high } } } }\"\n",
                        ]
                        if stack not in not_full_stacks:
                            if ha_type != "across-az":
                                if num_nics == 1:
                                    custom_sh += [
                                        "\"tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination 0.0.0.0:${VIRTUALSERVERPORT} mask any ip-protocol tcp policies replace-all-with { app-ltm-policy { } } pool /Common/${APPNAME}-pool profiles replace-all-with { http { } tcp { } websecurity { } } security-log-profiles replace-all-with { \"Log illegal requests\" } source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled}\"\n",
                                    ]

                                if num_nics > 1:
                                    custom_sh += [
                                        "\"tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp policies replace-all-with { app-ltm-policy { } } pool /Common/${APPNAME}-pool profiles replace-all-with { http { } tcp { } websecurity { } } security-log-profiles replace-all-with { \"Log illegal requests\" } source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled}\"\n",
                                    ]
                            if ha_type == "across-az":
                                custom_sh += [
                                    "\"tmsh create ltm virtual /Common/AZ1-${APPNAME}-${VIRTUALSERVERPORT} { destination ${EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp policies replace-all-with { app-ltm-policy { } } pool /Common/${APPNAME}-pool profiles replace-all-with { http { } tcp { } websecurity { } } security-log-profiles replace-all-with { \"Log illegal requests\" } source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled}\"\n",
                                    "\"tmsh create ltm virtual /Common/AZ2-${APPNAME}-${VIRTUALSERVERPORT} { destination ${PEER_EXTPRIVIP}:${VIRTUALSERVERPORT} mask 255.255.255.255 ip-protocol tcp policies replace-all-with { app-ltm-policy { } } pool /Common/${APPNAME}-pool profiles replace-all-with { http { } tcp { } websecurity { } } security-log-profiles replace-all-with { \"Log illegal requests\" } source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled}\"\n",
                                    "\"tmsh modify ltm virtual-address ${EXTPRIVIP} traffic-group none\"\n",
                                    "\"tmsh modify ltm virtual-address ${PEER_EXTPRIVIP} traffic-group none\"\n",
                                ]
                # If ASM, Need to use overwite Config (SOL16509 / BZID: 487538 )
                if ha_type != "standalone" and (BIGIP_INDEX + 1) == CLUSTER_SEED:
                    if 'waf' in components:
                        custom_sh += [
                            "\"tmsh modify cm device-group datasync-global-dg devices modify { ${HOSTNAME} { set-sync-leader } }\"\n",
                            "\"tmsh run cm config-sync to-group datasync-global-dg\"\n",
                        ]
                    onboard_config_vars = [
                        "",
                        "#!/bin/bash\n",
                        "# Generated from " + version + "\n",
                        "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`\n",
                        "HOSTNAME=`/usr/bin/curl -sS --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`\n",
                        "region='", {"Ref": "AWS::Region"}, "'\n",
                        "adminUsername='srv_user'\n",
                        "managementGuiPort='443'\n",
                        "timezone='", {"Ref": "timezone"}, "'\n",
                        "ntpServer='", {"Ref": "ntpServer"}, "'\n",
                        "declarationUrl='", {"Ref": "declarationUrl"}, "'\n",
                        "allowPhoneHome='", {"Ref": "allowPhoneHome"}, "'\n",
                        "passwd=$(f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/decryptDataFromFile.js --data-file /config/cloud/aws/.adminPassword)\n",
                    ]

                    # add back once cfe bz resolved - currently more then one virtual-address causes cfe to fail.
                    #if ha_type == "same-az":
                     #   custom_sh += [
                      #      "\"tmsh create ltm virtual-address ",
                       #     Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                        #    " address ",
                         #   Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                          #  "\"\n",
                    #    ]
                    custom_sh += [
                        "\"tmsh save /sys config\")\n",
                        "for CMD in \"${tmsh[@]}\"\n",
                        "do\n",
                        "  \"/config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/waitForMcp.sh\"\n",
                        "    if $CMD;then\n",
                        "        echo \"command $CMD successfully executed.\"\n",
                        "    else\n",
                        "        error_exit \"$LINENO: An error has occurred while executing $CMD. Aborting!\"\n",
                        "    fi\n",
                        "done\n"
                    ]
                    custom_sh += [
                        "date\n",
                        "### START CUSTOM CONFIGURATION\n",
                        "deployed=\"no\"\n",
                        "url_regex=\"(http:\\/\\/|https:\\/\\/)?[a-z0-9]+([\\-\\.]{1}[a-z0-9]+)*\\.[a-z]{2,5}(:[0-9]{1,5})?(\\/.*)?$\"\n",
                        "file_loc=\"/config/cloud/custom_config\"\n",
                        "if [[ $declarationUrl =~ $url_regex ]]; then\n",
                        "  response_code=$(/usr/bin/curl -sk -w \"%{http_code}\" $declarationUrl -o $file_loc)\n",
                        "  if [[ $response_code == 200 ]]; then\n",
                        "    echo \"Custom config download complete; checking for valid JSON.\"\n",
                        "    cat $file_loc | jq .class\n",
                        "    if [[ $? == 0 ]]; then\n",
                        "      response_code=$(/usr/bin/curl -svvu admin: -w \"%{http_code}\" -X POST -H \"Content-Type: application/json\" -H \"Expect:\" http://localhost:8100/mgmt/shared/appsvcs/declare -d @$file_loc -o /dev/null)\n",
                        "      if [[ $response_code == 200 || $response_code == 502 ]]; then\n",
                        "        echo \"Deployment of custom application succeeded.\"\n",
                        "        deployed=\"yes\"\n",
                        "      else\n",
                        "         echo \"Failed to deploy custom application; continuing...\"\n",
                        "      fi\n",
                        "    else\n",
                        "      echo \"Custom config was not valid JSON, continuing...\"\n",
                        "    fi\n",
                        "  else\n",
                        "    echo \"Failed to download custom config; continuing...\"\n",
                        "  fi\n",
                        "else\n",
                        "  echo \"Custom config was not a URL, continuing...\"\n",
                        "fi\n",
                    ]
                if ha_type != "standalone" and (BIGIP_INDEX) == CLUSTER_SEED:
                    if ha_type == "same-az":
                        custom_sh += [
                            "\"tmsh create ltm virtual-address ",
                            Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                            " address ",
                            Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                            "\"\n",
                        ]
                    custom_sh += [
                        "\"tmsh save /sys config\")\n",
                        "for CMD in \"${tmsh[@]}\"\n",
                        "do\n",
                        "  \"/config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/waitForMcp.sh\"\n",
                        "    if $CMD;then\n",
                        "        echo \"command $CMD successfully executed.\"\n",
                        "    else\n",
                        "        error_exit \"$LINENO: An error has occurred while executing $CMD. Aborting!\"\n",
                        "    fi\n",
                        "done\n",
                        "date\n",
                    ]
                if ha_type != "standalone":
                    cfe_sh = [
                        "#!/bin/bash\n",
                        "source /config/cloud/aws/onboard_config_vars\n",
                        "cfe_file_loc=\"/config/cloud/cfe_config.json\"\n",
                        "cfe_response_code=$(/usr/bin/curl -svvu admin: -w \"%{http_code}\" -X POST -H \"Content-Type: application/json\" http://localhost:8100/mgmt/shared/cloud-failover/declare -d @$cfe_file_loc -o /dev/null)\n",
                        "if [[ $cfe_response_code == 200 || $cfe_response_code == 502 ]]; then\n",
                        "    echo \"Deployment of CFE application succeeded.\"\n",
                        "    cfe_deployed=\"yes\"\n",
                        "else\n",
                        "    echo \"Failed to deploy CFE application; continuing...\"\n",
                        "fi\n",
                        "#Disable built-in script\n"
                        "mount -o remount,rw /usr\n",
                        "mv /usr/libexec/aws/aws-failover-tgactive.sh /usr/libexec/aws/aws-failover-tgactive.sh.disabled\n",
                        "mv /usr/libexec/aws/aws-failover-tgrefresh.sh /usr/libexec/aws/aws-failover-tgrefresh.sh.disabled\n",
                        "mount -o remount,ro /usr\n",
                    ]
                    custom_sh += [
                        "### END CUSTOM CONFIGURATION",
                    ]

                if ha_type == "standalone":
                    onboard_config_vars = [
                        "",
                        "#!/bin/bash\n",
                        "# Generated from " + version + "\n",
                        "TOKEN=`/usr/bin/curl -sS --retry 20 -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 120'`\n",
                        "HOSTNAME=`/usr/bin/curl -sS --retry 20 -H 'X-aws-ec2-metadata-token: '$TOKEN'' http://169.254.169.254/latest/meta-data/hostname`\n",
                        "region='", {"Ref": "AWS::Region"}, "'\n",
                        "adminUsername='srv_user'\n",
                        "timezone='", {"Ref": "timezone"}, "'\n",
                        "ntpServer='", {"Ref": "ntpServer"}, "'\n",
                        "declarationUrl='", {"Ref": "declarationUrl"}, "'\n",
                        "allowPhoneHome='", {"Ref": "allowPhoneHome"}, "'\n",
                        "passwd=$(f5-rest-node /config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/decryptDataFromFile.js --data-file /config/cloud/aws/.adminPassword)\n",
                    ]
                    if num_nics == 1:
                        onboard_config_vars += ["managementGuiPort='", {"Ref": "managementGuiPort"}, "'\n", ]
                    else:
                        onboard_config_vars += ["managementGuiPort='443'\n", ]
                    custom_sh += [
                        "\"tmsh save /sys config\")\n",
                        "for CMD in \"${tmsh[@]}\"\n",
                        "do\n",
                        "  \"/config/cloud/aws/node_modules/@f5devcentral/f5-cloud-libs/scripts/waitForMcp.sh\"\n",
                        "    if $CMD;then\n",
                        "        echo \"command $CMD successfully executed.\"\n",
                        "    else\n",
                        "        error_exit \"$LINENO: An error has occurred while executing $CMD. Aborting!\"\n",
                        "    fi\n",
                        "done\n",
                        "date\n",
                        "### START CUSTOM CONFIGURATION\n",
                        "deployed=\"no\"\n",
                        "url_regex=\"(http:\\/\\/|https:\\/\\/)?[a-z0-9]+([\\-\\.]{1}[a-z0-9]+)*\\.[a-z]{2,5}(:[0-9]{1,5})?(\\/.*)?$\"\n",
                        "file_loc=\"/config/cloud/custom_config\"\n",
                        "if [[ $declarationUrl =~ $url_regex ]]; then\n",
                        "  response_code=$(/usr/bin/curl -sk -w \"%{http_code}\" $declarationUrl -o $file_loc)\n",
                        "  if [[ $response_code == 200 ]]; then\n",
                        "    echo \"Custom config download complete; checking for valid JSON.\"\n",
                        "    cat $file_loc | jq .class\n",
                        "    if [[ $? == 0 ]]; then\n",
                        "      response_code=$(/usr/bin/curl -svvu admin: -w \"%{http_code}\" -X POST -H \"Content-Type: application/json\" -H \"Expect:\" http://localhost:8100/mgmt/shared/appsvcs/declare -d @$file_loc -o /dev/null)\n",
                        "      if [[ $response_code == 200 || $response_code == 502 ]]; then\n",
                        "        echo \"Deployment of custom application succeeded.\"\n",
                        "        deployed=\"yes\"\n",
                        "      else\n",
                        "         echo \"Failed to deploy custom application; continuing...\"\n",
                        "      fi\n",
                        "    else\n",
                        "      echo \"Custom config was not valid JSON, continuing...\"\n",
                        "    fi\n",
                        "  else\n",
                        "    echo \"Failed to download custom config; continuing...\"\n",
                        "  fi\n",
                        "else\n",
                        "  echo \"Custom config was not a URL, continuing...\"\n",
                        "fi\n",
                        "### END CUSTOM CONFIGURATION"
                    ]

                # Set commands dictionary
                d = {}
                d["000-disable-1nicautoconfig"] = {
                    "command": "/usr/bin/setdb provision.1nicautoconfig disable"
                }
                # d["001-rest-provision-extramb"] = {
                #     "command": "/usr/bin/setdb provision.extramb 1000"
                # }
                # d["002-rest-use-extramb"] = {
                #     "command": "/usr/bin/setdb restjavad.useextramb true"
                # }
                # d["003-rest-post"] = {
                #     "command": "/usr/bin/curl -s -f -u admin: -H \"Content-Type: application/json\" -d '{\"maxMessageBodySize\":134217728}' -X POST http://localhost:8100/mgmt/shared/server/messaging/settings/8100 | jq ."
                # }
                # d["004-rest-restart"] = {
                #     "command": "bigstart restart restjavad restnoded"
                # }
                d["010-install-libs"] = {
                    "command": {
                        "Fn::Join": [
                            " ", unpack_libs
                        ]
                    }
                }
                if ha_type != 'standalone':
                    d["020-generate-password"] = {
                        "command": {
                            "Fn::Join": [
                                "", generate_password
                            ]
                        }
                    }
                    d["030-create-admin-user"] = {
                        "command": {
                            "Fn::Join": [
                                "", admin_user
                            ]
                        }
                    }
                d["040-network-config"] = {
                    "command": {
                        "Fn::Join": [
                            "", network_config
                        ]
                    }
                }
                d["050-onboard-BIG-IP"] = {
                    "command": {
                        "Fn::If": [
                            "optin",
                            {"Fn::Join": [
                                " ", onboard_BIG_IP_metrics
                            ]},
                            {"Fn::Join": [
                                " ", onboard_BIG_IP
                            ]},
                        ]
                    }
                }
                d["055-custom-config"] = {
                    "command": {
                        "Fn::Join": [
                            " ", custom_command
                        ]
                    }
                }
                d["060-cluster"] = {
                    "command": {
                        "Fn::Join": [
                            " ", cluster_command
                        ]
                    }
                }
                d["065-cfe"] = {
                    "command": {
                        "Fn::Join": [
                            " ", cfe_command
                        ]
                    }
                }
                if ha_type != 'standalone':
                    d["070-rm-password"] = {
                        "command": {
                            "Fn::Join": [
                                " ", rm_password_command
                            ]
                        }
                    }

                init_dict = {
                    '/config/cloud/f5-cloud-libs.tar.gz': InitFile(
                        source=cloudlib_url,
                        mode='000755',
                        owner='root',
                        group='root'
                    ),
                    '/config/cloud/f5-cloud-libs-aws.tar.gz': InitFile(
                        source=cloudlib_aws_url,
                        mode='000755',
                        owner='root',
                        group='root'
                    ),
                    '/config/verifyHash': InitFile(
                        content=lines,
                        mode='000755',
                        owner='root',
                        group='root'
                    ),
                    '/config/installCloudLibs.sh': InitFile(
                        content=Join('\n', cloudlibs_sh),
                        mode='000755',
                        owner='root',
                        group='root'
                    ),
                    '/config/waitThenRun.sh': InitFile(
                        content=Join('\n', waitthenrun_sh),
                        mode='000755',
                        owner='root',
                        group='root'
                    ),
                    '/config/cloud/aws/custom-config.sh': InitFile(
                        content=Join('', custom_sh),
                        mode='000755',
                        owner='root',
                        group='root'
                    ),
                    '/config/cloud/aws/getNameServer.sh': InitFile(
                        content=Join('\n', get_nameserver),
                        mode='000755',
                        owner='root',
                        group='root'
                    ),

                    '/config/cloud/aws/onboard_config_vars': InitFile(
                        content=Join('', onboard_config_vars),
                        mode='000755',
                        owner='root',
                        group='root'
                    )
                }
                if ha_type != 'standalone':
                    init_dict.update({
                        '/config/cloud/aws/rm-srv-user.sh': InitFile(
                        content=Join('', rm_password_sh),
                        mode='000755',
                        owner='root',
                        group='root'
                        )
                    })
                if ha_type == "across-az":
                    init_dict.update({
                        '/config/cloud/aws/getManagementGateway.sh': InitFile(
                            content=Join('\n', get_management_gateway),
                            mode='000755',
                            owner='root',
                            group='root'
                        )})
                if ha_type != "standalone":
                    init_dict.update({
                        '/config/cloud/aws/cfe-config.sh': InitFile(
                            content=Join('', cfe_sh),
                            mode='000755',
                            owner='root',
                            group='root'
                        ),
                        '/config/cloud/cfe_config.json': InitFile(
                            content=Join('', cfe_file),
                            mode='000755',
                            owner='root',
                            group='root'
                        )})
                if (license_type != "hourly" and license_type != "bigiq" and ha_type != "autoscale"):
                    init_dict.update({
                        '/config/cloud/f5-cloud-libs.tar.gz': InitFile(
                            source=If("useChinaRegion", cloudlib_url_china, cloudlib_url),
                            mode='000755',
                            owner='root',
                            group='root'
                        ),
                        '/config/cloud/f5-cloud-libs-aws.tar.gz': InitFile(
                            source=If("useChinaRegion", cloudlib_aws_url_china, cloudlib_aws_url),
                            mode='000755',
                            owner='root',
                            group='root'
                        )})

                metadata = Metadata(
                    Init({
                        'config': InitConfig(
                            files=InitFiles(init_dict),
                            commands=d
                        )
                    })
                )
                NetworkInterfaces = []
                if need_static_ip_addr:
                    if num_nics == 1:
                        NetworkInterfaces = [
                            NetworkInterfaceProperty(
                                DeviceIndex="0",
                                NetworkInterfaceId=If(
                                    "useDynamicExternalIpAddr",
                                    Ref(ExternalInterface),
                                    Ref(StaticExternalInterface)),
                                Description="Public or External Interface",
                            ),
                        ]
                    if num_nics > 1:
                        NetworkInterfaces = [
                            NetworkInterfaceProperty(
                                DeviceIndex="0",
                                NetworkInterfaceId=If(
                                    "useDynamicManagementIpAddr",
                                    Ref(ManagementInterface),
                                    Ref(StaticManagementInterface)),
                                Description="Management Interface"
                            ),
                            NetworkInterfaceProperty(
                                DeviceIndex="1",
                                NetworkInterfaceId=If(
                                    "useDynamicExternalIpAddr",
                                    Ref(ExternalInterface),
                                    Ref(StaticExternalInterface)),
                                Description="Public or External Interface"
                            ),
                        ]
                    if num_nics > 2:
                        NetworkInterfaces.append(
                            NetworkInterfaceProperty(
                                DeviceIndex="2",
                                NetworkInterfaceId=If(
                                    "useDynamicInternalIpAddr",
                                    Ref(InternalInterface),
                                    Ref(StaticInternalInterface)),
                                Description="Private or Internal Interface"
                            )
                        )
                else:
                    if num_nics == 1:
                        NetworkInterfaces = [
                            NetworkInterfaceProperty(
                                DeviceIndex="0",
                                NetworkInterfaceId=Ref(ExternalInterface),
                                Description="Public or External Interface",
                            ),
                        ]
                    if num_nics > 1:
                        NetworkInterfaces = [
                            NetworkInterfaceProperty(
                                DeviceIndex="0",
                                NetworkInterfaceId=Ref(ManagementInterface),
                                Description="Management Interface"
                            ),
                            NetworkInterfaceProperty(
                                DeviceIndex="1",
                                NetworkInterfaceId=Ref(ExternalInterface),
                                Description="Public or External Interface"
                            ),
                        ]
                    if num_nics > 2:
                        NetworkInterfaces.append(
                            NetworkInterfaceProperty(
                                DeviceIndex="2",
                                NetworkInterfaceId=Ref(InternalInterface),
                                Description="Private or Internal Interface"
                            )
                        )
                if num_nics > 3:
                    for number in range(3, 8):
                        NetworkInterfaces.append(
                            If("createNic" + str(number),
                                NetworkInterfaceProperty(
                                    DeviceIndex=str(number),
                                    NetworkInterfaceId=Ref(nics[number]),
                                    Description="Interface " + str(number)),
                                Ref("AWS::NoValue"))
                        )
                if ha_type != "standalone" and (BIGIP_INDEX + 1) == CLUSTER_SEED:
                    RESOURCES[BigipInstance] = t.add_resource(Instance(
                        BigipInstance,
                        Metadata=metadata,
                        UserData=Base64(Join("", [
                                        "#!/bin/bash\n",
                                        "mkdir -p /var/log/cloud /config/cloud /var/config/rest/downloads\n",
                                        "/usr/bin/setdb provision.extramb 1000\n", 
                                        "/usr/bin/setdb restjavad.useextramb true\n", 
                                        "cat << EOF >> /config/cloud/runtime-init-config.yaml\n",
                                        "controls:\n",
                                        "  logLevel: info\n",
                                        "  logFilename: /var/log/cloud/bigIpRuntimeInit.log\n",
                                        "pre_onboard_enabled:\n",
                                        "  - name: get_ifconfig\n",
                                        "    type: inline\n",
                                        "    commands:\n",
                                        "      - ifconfig eth1 | grep ether > /config/cloud/net1_mac || exit 0\n",
                                        "      - ifconfig eth2 | grep ether > /config/cloud/net2_mac || exit 0\n",
                                        "extension_packages:\n",
                                        "  install_operations:\n",
                                        "    - extensionType: as3\n",
                                        "      extensionVersion: 3.34.0\n",
                                        "      extensionHash: 05a80ec0848dc5b8876b78a8fbee2980d5a1671d635655b3af604dc830d5fed4\n",
                                        "    - extensionType: cf\n",
                                        "      extensionVersion: 1.11.0\n",
                                        "      extensionHash: f3c7aca8a19d0dc01e529d38aa0d235b4dfad34beec2584f8402aa9a92c34699\n",
                                        "EOF\n",
                                        download_runtime_command, 
                                        install_runtime_command, 
                                        "f5-bigip-runtime-init --config-file /config/cloud/runtime-init-config.yaml --skip-telemetry\n", 
                                        "/opt/aws/apitools/cfn-init/bin/cfn-init -v -s ", Ref("AWS::StackId"), " -r ", BigipInstance, " --region ", Ref("AWS::Region"), "\n"
                                        ])),
                        Tags=Tags(
                            Name=Join("", ["Big-IP" + str(BIGIP_INDEX + 1) + ": ", Ref("AWS::StackName")]),
                            Application=Ref(application),
                            Environment=Ref(environment),
                            Group=Ref(group),
                            Owner=Ref(owner),
                            Costcenter=Ref(costcenter),
                        ),
                        ImageId=If(
                            "noCustomImageId",
                            FindInMap("BigipRegionMap", Ref('AWS::Region'), imageidref),
                            Ref(customImageId)
                        ),
                        BlockDeviceMappings=[
                            ec2.BlockDeviceMapping(
                                DeviceName="/dev/xvda",
                                Ebs=ec2.EBSBlockDevice(
                                    DeleteOnTermination=True,
                                    VolumeType="gp2",
                                    VolumeSize=100
                                )
                            ),
                            ec2.BlockDeviceMapping(
                                DeviceName="/dev/xvdb",
                                NoDevice={}
                            )
                        ],
                        IamInstanceProfile=Ref(bigipServiceDiscoveryProfile),
                        KeyName=Ref(sshKey),
                        InstanceType=Ref(instanceType),
                        NetworkInterfaces=NetworkInterfaces
                    ))
                if ha_type != "standalone" and (BIGIP_INDEX) == CLUSTER_SEED:
                    RESOURCES[BigipInstance] = t.add_resource(Instance(
                        BigipInstance,
                        DependsOn="Bigip" + str(BIGIP_INDEX) + "Instance",
                        Metadata=metadata,
                        UserData=Base64(Join("", [
                                        "#!/bin/bash\n",
                                        "mkdir -p /var/log/cloud /config/cloud /var/config/rest/downloads\n",
                                        "/usr/bin/setdb provision.extramb 1000\n", 
                                        "/usr/bin/setdb restjavad.useextramb true\n",
                                        "cat << EOF >> /config/cloud/runtime-init-config.yaml\n",
                                        "controls:\n",
                                        "  logLevel: info\n",
                                        "  logFilename: /var/log/cloud/bigIpRuntimeInit.log\n",
                                        "pre_onboard_enabled:\n",
                                        "  - name: get_ifconfig\n",
                                        "    type: inline\n",
                                        "    commands:\n",
                                        "      - ifconfig eth1 | grep ether > /config/cloud/net1_mac || exit 0\n",
                                        "      - ifconfig eth2 | grep ether > /config/cloud/net2_mac || exit 0\n",
                                        "extension_packages:\n",
                                        "  install_operations:\n",
                                        "    - extensionType: as3\n",
                                        "      extensionVersion: 3.34.0\n",
                                        "      extensionHash: 05a80ec0848dc5b8876b78a8fbee2980d5a1671d635655b3af604dc830d5fed4\n",
                                        "    - extensionType: cf\n",
                                        "      extensionVersion: 1.10.0\n",
                                        "      extensionHash: d758c985cac4dbef4b0732fe5900317ae97e67c6efca621a5b2b02c8c4bbeace\n",
                                        "EOF\n", 
                                        download_runtime_command, 
                                        install_runtime_command, 
                                        "f5-bigip-runtime-init --config-file /config/cloud/runtime-init-config.yaml --skip-telemetry\n", 
                                        "/opt/aws/apitools/cfn-init/bin/cfn-init -v -s ", Ref("AWS::StackId"), " -r ", BigipInstance, " --region ", Ref("AWS::Region"), "\n"
                                        ])),
                        Tags=Tags(
                            Name=Join("", ["Big-IP" + str(BIGIP_INDEX + 1) + ": ", Ref("AWS::StackName")]),
                            Application=Ref(application),
                            Environment=Ref(environment),
                            Group=Ref(group),
                            Owner=Ref(owner),
                            Costcenter=Ref(costcenter),
                        ),
                        ImageId=If(
                            "noCustomImageId",
                            FindInMap("BigipRegionMap", Ref('AWS::Region'), imageidref),
                            Ref(customImageId)
                        ),
                        BlockDeviceMappings=[
                            ec2.BlockDeviceMapping(
                                DeviceName="/dev/xvda",
                                Ebs=ec2.EBSBlockDevice(
                                    DeleteOnTermination=True,
                                    VolumeType="gp2",
                                    VolumeSize=100
                                )
                            ),
                            ec2.BlockDeviceMapping(
                                DeviceName="/dev/xvdb",
                                NoDevice={}
                            )
                        ],
                        IamInstanceProfile=Ref(bigipServiceDiscoveryProfile),
                        KeyName=Ref(sshKey),
                        InstanceType=Ref(instanceType),
                        NetworkInterfaces=NetworkInterfaces
                    ))
                if ha_type == "standalone" and marketplace == "no":
                    RESOURCES[BigipInstance] = t.add_resource(Instance(
                        BigipInstance,
                        Metadata=metadata,
                        UserData=Base64(Join("", [
                                        "#!/bin/bash\n",
                                        "mkdir -p /var/log/cloud /config/cloud /var/config/rest/downloads\n", 
                                        "/usr/bin/setdb provision.extramb 1000\n", 
                                        "/usr/bin/setdb restjavad.useextramb true\n",
                                        "cat << EOF >> /config/cloud/runtime-init-config.yaml\n",
                                        "controls:\n",
                                        "  logLevel: info\n",
                                        "  logFilename: /var/log/cloud/bigIpRuntimeInit.log\n",
                                        "pre_onboard_enabled:\n",
                                        "  - name: get_ifconfig\n",
                                        "    type: inline\n",
                                        "    commands:\n",
                                        "      - ifconfig eth1 | grep ether > /config/cloud/net1_mac || exit 0\n",
                                        "      - ifconfig eth2 | grep ether > /config/cloud/net2_mac || exit 0\n",
                                        "      - ifconfig eth3 | grep ether > /config/cloud/net3_mac || exit 0\n",
                                        "      - ifconfig eth4 | grep ether > /config/cloud/net4_mac || exit 0\n",
                                        "      - ifconfig eth5 | grep ether > /config/cloud/net5_mac || exit 0\n",
                                        "      - ifconfig eth6 | grep ether > /config/cloud/net6_mac || exit 0\n",
                                        "      - ifconfig eth7 | grep ether > /config/cloud/net7_mac || exit 0\n",
                                        "extension_packages:\n",
                                        "  install_operations:\n",
                                        "    - extensionType: as3\n",
                                        "      extensionVersion: 3.34.0\n",
                                        "      extensionHash: 05a80ec0848dc5b8876b78a8fbee2980d5a1671d635655b3af604dc830d5fed4\n",
                                        "EOF\n",
                                        download_runtime_command, 
                                        install_runtime_command, 
                                        "f5-bigip-runtime-init --config-file /config/cloud/runtime-init-config.yaml --skip-telemetry\n", 
                                        "/opt/aws/apitools/cfn-init/bin/cfn-init -v -s ", Ref("AWS::StackId"), " -r ", BigipInstance, " --region ", Ref("AWS::Region"), "\n"
                                        ])),
                        Tags=Tags(
                            Name=Join("", ["Big-IP: ", Ref("AWS::StackName")]),
                            Application=Ref(application),
                            Environment=Ref(environment),
                            Group=Ref(group),
                            Owner=Ref(owner),
                            Costcenter=Ref(costcenter),
                        ),
                        ImageId=If(
                            "noCustomImageId",
                            FindInMap("BigipRegionMap", Ref('AWS::Region'), imageidref),
                            Ref(customImageId)
                        ),
                        BlockDeviceMappings=[
                            ec2.BlockDeviceMapping(
                                DeviceName="/dev/xvda",
                                Ebs=ec2.EBSBlockDevice(
                                    DeleteOnTermination=True,
                                    VolumeType="gp2",
                                    VolumeSize=100
                                )
                            ),
                            ec2.BlockDeviceMapping(
                                DeviceName="/dev/xvdb",
                                NoDevice={}
                            )
                        ],
                        IamInstanceProfile=Ref(bigipServiceDiscoveryProfile),
                        KeyName=Ref(sshKey),
                        InstanceType=Ref(instanceType),
                        NetworkInterfaces=NetworkInterfaces
                    ))

    # BEGIN OUTPUT
    if ha_type == "autoscale":
        # t.add_output(Output(
        #     "bigipAutoscaleGroup",
        #     Description="BIG-IP Auto Scaling group",
        #     Value=Ref(BigipAutoscaleGroup),
        # ))
        # t.add_output(Output(
        #     "bigipSecurityGroup",
        #     Description="BIG-IP Security group",
        #     Value=Ref(bigipSecurityGroup),
        # ))
        t.add_output(Output(
            "bigipAutoscaleGroup",
            Description="BIG-IP Autoscale Group",
            Value=Ref("BigipAutoscaleGroup"),
        ))
        t.add_output(Output(
            "bigipExternalSecurityGroup",
            Description="BIG-IP Security Group (External or Public)",
            Value=Ref("bigipExternalSecurityGroup"),
        ))
        t.add_output(Output(
            "s3Bucket",
            Description="BIG-IP S3 Bucket",
            Value=Ref("S3Bucket"),
        ))
    else:
        if network:
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
                    Description="Az" + str(INDEX + 1) + "Application Subnet Id",
                    Value=Ref(ApplicationSubnet),
                ))
            for INDEX in range(num_azs):
                ExternalSubnet = "subnet1" + "Az" + str(INDEX + 1)
                OUTPUTS[ExternalSubnet] = t.add_output(Output(
                    ExternalSubnet,
                    Description="Az" + str(INDEX + 1) + "External Subnet Id",
                    Value=Ref(ExternalSubnet),
                ))
            if num_nics > 1:
                for INDEX in range(num_azs):
                    managementSubnet = "managementSubnet" + "Az" + str(INDEX + 1)
                    OUTPUTS[managementSubnet] = t.add_output(Output(
                        managementSubnet,
                        Description="Az" + str(INDEX + 1) + "Management Subnet Id",
                        Value=Ref(managementSubnet),
                    ))
            if num_nics > 2:
                for INDEX in range(num_azs):
                    InternalSubnet = "subnet2" + "Az" + str(INDEX + 1)

                    OUTPUTS[InternalSubnet] = t.add_output(Output(
                        InternalSubnet,
                        Description="Az" + str(INDEX + 1) + "Internal Subnet Id",
                        Value=Ref(InternalSubnet),
                    ))
        if security_groups:
            bigipExternalSecurityGroup = t.add_output(Output(
                "bigipExternalSecurityGroup",
                Description="Public or External Security Group",
                Value=Ref(bigipExternalSecurityGroup),
            ))
            if num_nics > 1:
                bigipManagementSecurityGroup = t.add_output(Output(
                    "bigipManagementSecurityGroup",
                    Description="Management Security Group",
                    Value=Ref(bigipManagementSecurityGroup),
                ))
            if num_nics > 2:
                bigipInternalSecurityGroup = t.add_output(Output(
                    "bigipInternalSecurityGroup",
                    Description="Private or Internal Security Group",
                    Value=Ref(bigipInternalSecurityGroup),
                ))
        if bigip:
            for BIGIP_INDEX in range(num_bigips):
                ExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + str(ExternalSubnet) + "Interface"
                StaticExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "Static" + str(ExternalSubnet) + "Interface"
                if ha_type == "across-az":
                    ExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "subnet1" + "Az" + str(BIGIP_INDEX + 1) + "Interface"
                    ExternalSelfEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "subnet1" + "Az" + str(BIGIP_INDEX + 1) + "SelfEipAddress"
                    ExternalSelfEipAssociation = "Bigip" + str(BIGIP_INDEX + 1) + "subnet1" + "Az" + str(BIGIP_INDEX + 1) + "SelfEipAssociation"
                    VipPrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "VipPrivateIp"
                if ha_type == "same-az":
                    ExternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "subnet1" + "Az1Interface"
                    if stack != "prod":
                        ExternalSelfEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "subnet1" + "Az1SelfEipAddress"
                        ExternalSelfEipAssociation = "Bigip" + str(BIGIP_INDEX + 1) + "subnet1" + "Az1SelfEipAssociation"
                ExternalInterfacePrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "ExternalInterfacePrivateIp"
                BigipInstance = "Bigip" + str(BIGIP_INDEX + 1) + "Instance"
                BigipInstanceId = "Bigip" + str(BIGIP_INDEX + 1) + "InstanceId"
                BigipUrl = "Bigip" + str(BIGIP_INDEX + 1) + "Url"
                AvailabilityZone = "availabilityZone" + str(BIGIP_INDEX + 1)
                OUTPUTS[BigipInstanceId] = t.add_output(Output(
                    BigipInstanceId,
                    Description="Instance Id of BIG-IP in Amazon",
                    Value=Ref(BigipInstance),
                ))
                OUTPUTS[AvailabilityZone] = t.add_output(Output(
                    AvailabilityZone,
                    Description="Availability Zone",
                    Value=GetAtt(BigipInstance, "AvailabilityZone"),
                ))
                if need_static_ip_addr:
                    OUTPUTS[ExternalInterface] = t.add_output(Output(
                        ExternalInterface,
                        Description="External interface Id on BIG-IP",
                        Value=If(
                            "useDynamicExternalIpAddr",
                            Ref(ExternalInterface),
                            Ref(StaticExternalInterface))
                    ))
                    OUTPUTS[ExternalInterfacePrivateIp] = t.add_output(Output(
                        ExternalInterfacePrivateIp,
                        Description="Internally routable IP of the public interface on BIG-IP",
                        Value=If(
                            "useDynamicExternalIpAddr",
                            GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
                            GetAtt(StaticExternalInterface, "PrimaryPrivateIpAddress"))
                    ))
                else:
                    OUTPUTS[ExternalInterface] = t.add_output(Output(
                        ExternalInterface,
                        Description="External interface Id on BIG-IP",
                        Value=Ref(ExternalInterface)
                    ))
                    OUTPUTS[ExternalInterfacePrivateIp] = t.add_output(Output(
                        ExternalInterfacePrivateIp,
                        Description="Internally routable IP of the public interface on BIG-IP",
                        Value=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress")
                    ))
                if (stack != "prod" or ha_type == "standalone"):
                    if need_optional_public_ip:
                        OUTPUTS[ExternalSelfEipAddress] = t.add_output(Output(
                            ExternalSelfEipAddress,
                            Description="IP Address of the External interface attached to BIG-IP",
                            Value=Ref(ExternalSelfEipAddress),
                            Condition="usePublicIP"
                        ))
                    else:
                        OUTPUTS[ExternalSelfEipAddress] = t.add_output(Output(
                            ExternalSelfEipAddress,
                            Description="IP Address of the External interface attached to BIG-IP",
                            Value=Ref(ExternalSelfEipAddress),
                        ))
                    if num_nics == 1:
                        if need_optional_public_ip:
                            VipEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "VipEipAddress"
                            OUTPUTS[BigipUrl] = t.add_output(Output(
                                BigipUrl,
                                Description="BIG-IP Management GUI",
                                Value=Join("", ["https://", GetAtt(BigipInstance, "PublicIp"), ":", Ref(managementGuiPort)]),
                                Condition="usePublicIP"
                            ))
                            OUTPUTS[VipEipAddress] = t.add_output(Output(
                                VipEipAddress,
                                Description="EIP address for VIP",
                                Value=Join("", ["http://", GetAtt(BigipInstance, "PublicIp"), ":80"]),
                                Condition="usePublicIP"
                            ))
                        else:
                            VipEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "VipEipAddress"
                            OUTPUTS[BigipUrl] = t.add_output(Output(
                                BigipUrl,
                                Description="BIG-IP Management GUI",
                                Value=Join("", ["https://", GetAtt(BigipInstance, "PublicIp"), ":", Ref(managementGuiPort)]),
                            ))
                            OUTPUTS[VipEipAddress] = t.add_output(Output(
                                VipEipAddress,
                                Description="EIP address for VIP",
                                Value=Join("", ["http://", GetAtt(BigipInstance, "PublicIp"), ":80"]),
                            ))
                    if num_nics > 1:
                        ManagementInterface = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementInterface"
                        StaticManagementInterface = "Bigip" + str(BIGIP_INDEX + 1) + "StaticManagementInterface"
                        ManagementInterfacePrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementInterfacePrivateIp"
                        ManagementEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "ManagementEipAddress"
                        VipPrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "VipPrivateIp"
                        VipEipAddress = "Bigip" + str(BIGIP_INDEX + 1) + "VipEipAddress"
                        if need_optional_public_ip:
                            OUTPUTS[BigipUrl] = t.add_output(Output(
                                BigipUrl,
                                Description="BIG-IP Management GUI",
                                Value=Join("", ["https://", GetAtt(BigipInstance, "PublicIp")]),
                                Condition="usePublicIP"
                            ))
                        else:
                            OUTPUTS[BigipUrl] = t.add_output(Output(
                                BigipUrl,
                                Description="BIG-IP Management GUI",
                                Value=Join("", ["https://", GetAtt(BigipInstance, "PublicIp")]),
                            ))
                        if need_optional_public_ip:
                            OUTPUTS[ManagementEipAddress] = t.add_output(Output(
                                ManagementEipAddress,
                                Description="IP address of the management port on BIG-IP",
                                Value=Ref(ManagementEipAddress),
                                Condition="usePublicIP"
                            ))
                        else:
                            OUTPUTS[ManagementEipAddress] = t.add_output(Output(
                                ManagementEipAddress,
                                Description="IP address of the management port on BIG-IP",
                                Value=Ref(ManagementEipAddress),
                            ))
                        if ha_type == "standalone":
                            if num_nics < 4 and stack not in reference_stacks:
                                if need_optional_public_ip:
                                    OUTPUTS[ManagementInterface] = t.add_output(Output(
                                        ManagementInterface,
                                        Description="Management interface ID on BIG-IP",
                                        Condition="usePublicIP",
                                        Value=If(
                                            "useDynamicManagementIpAddr",
                                            Ref(ManagementInterface),
                                            Ref(StaticManagementInterface))
                                    ))
                                    OUTPUTS[ManagementInterfacePrivateIp] = t.add_output(Output(
                                        ManagementInterfacePrivateIp,
                                        Description="Internally routable IP of the management interface on BIG-IP",
                                        Condition="usePublicIP",
                                        Value=If(
                                            "useDynamicManagementIpAddr",
                                            GetAtt(ManagementInterface, "PrimaryPrivateIpAddress"),
                                            GetAtt(StaticManagementInterface, "PrimaryPrivateIpAddress"))
                                    ))
                                    OUTPUTS[VipPrivateIp] = t.add_output(Output(
                                        VipPrivateIp,
                                        Description="VIP on External Interface Secondary IP 1",
                                        Condition="usePublicIP",
                                        Value=If(
                                            "useDynamicExternalIpAddr",
                                            Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                                            Select("0", GetAtt(StaticExternalInterface, "SecondaryPrivateIpAddresses")))
                                    ))
                                else:
                                    OUTPUTS[ManagementInterface] = t.add_output(Output(
                                        ManagementInterface,
                                        Description="Management interface ID on BIG-IP",
                                        Value=If(
                                            "useDynamicManagementIpAddr",
                                            Ref(ManagementInterface),
                                            Ref(StaticManagementInterface))
                                    ))
                                    OUTPUTS[ManagementInterfacePrivateIp] = t.add_output(Output(
                                        ManagementInterfacePrivateIp,
                                        Description="Internally routable IP of the management interface on BIG-IP",
                                        Value=If(
                                            "useDynamicManagementIpAddr",
                                            GetAtt(ManagementInterface, "PrimaryPrivateIpAddress"),
                                            GetAtt(StaticManagementInterface, "PrimaryPrivateIpAddress"))
                                    ))
                                    OUTPUTS[VipPrivateIp] = t.add_output(Output(
                                        VipPrivateIp,
                                        Description="VIP on External Interface Secondary IP 1",
                                        Value=If(
                                            "useDynamicExternalIpAddr",
                                            Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses")),
                                            Select("0", GetAtt(StaticExternalInterface, "SecondaryPrivateIpAddresses")))
                                    ))
                            else:
                                if stack != "prod":
                                    OUTPUTS[ManagementInterface] = t.add_output(Output(
                                        ManagementInterface,
                                        Description="Management interface ID on BIG-IP",
                                        Value=Ref(ManagementInterface)
                                    ))
                                    OUTPUTS[VipPrivateIp] = t.add_output(Output(
                                        VipPrivateIp,
                                        Description="VIP on External Interface Secondary IP 1",
                                        Value=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses"))
                                    ))
                                if need_optional_public_ip:
                                    OUTPUTS[ManagementInterfacePrivateIp] = t.add_output(Output(
                                        ManagementInterfacePrivateIp,
                                        Description="Internally routable IP of the management interface on BIG-IP",
                                        Value=GetAtt(ManagementInterface, "PrimaryPrivateIpAddress"),
                                        Condition="usePublicIP"
                                    ))
                                else:
                                    OUTPUTS[ManagementInterfacePrivateIp] = t.add_output(Output(
                                        ManagementInterfacePrivateIp,
                                        Description="Internally routable IP of the management interface on BIG-IP",
                                        Value=GetAtt(ManagementInterface, "PrimaryPrivateIpAddress")
                                    ))
                            if need_optional_public_ip:
                                OUTPUTS[VipEipAddress] = t.add_output(Output(
                                    VipEipAddress,
                                    Description="EIP address for VIP",
                                    Value=Join("", ["http://", Ref(VipEipAddress), ":80"]),
                                    Condition="usePublicIP"
                                ))
                            else:
                                OUTPUTS[VipEipAddress] = t.add_output(Output(
                                    VipEipAddress,
                                    Description="EIP address for VIP",
                                    Value=Join("", ["http://", Ref(VipEipAddress), ":80"]),
                                ))
                        else:
                            OUTPUTS[ManagementInterface] = t.add_output(Output(
                                ManagementInterface,
                                Description="Management interface ID on BIG-IP",
                                Value=Ref(ManagementInterface)
                            ))
                            OUTPUTS[ManagementInterfacePrivateIp] = t.add_output(Output(
                                ManagementInterfacePrivateIp,
                                Description="Internally routable IP of the management interface on BIG-IP",
                                Value=GetAtt(ManagementInterface, "PrimaryPrivateIpAddress")
                            ))
                            # if clustered, needs to be cluster seed
                            OUTPUTS[VipPrivateIp] = t.add_output(Output(
                                VipPrivateIp,
                                Description="Secondary IP 1 on BIG-IP" + str(BIGIP_INDEX + 1) + "'s External Interface.",
                                Value=Select("0", GetAtt(ExternalInterface, "SecondaryPrivateIpAddresses"))
                            ))
                            if (BIGIP_INDEX + 1) == CLUSTER_SEED:
                                if need_optional_public_ip:
                                    OUTPUTS[VipEipAddress] = t.add_output(Output(
                                        VipEipAddress,
                                        Description="EIP address for VIP",
                                        Value=Join("", ["http://", Ref(VipEipAddress), ":80"]),
                                        Condition="usePublicIP"
                                    ))
                                else:
                                    OUTPUTS[VipEipAddress] = t.add_output(Output(
                                        VipEipAddress,
                                        Description="EIP address for VIP",
                                        Value=Join("", ["http://", Ref(VipEipAddress), ":80"]),
                                    ))
                if num_nics > 2:
                    InternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "InternalInterface"
                    StaticInternalInterface = "Bigip" + str(BIGIP_INDEX + 1) + "StaticInternalInterface"
                    InternalInterfacePrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "InternalInterfacePrivateIp"

                    if need_static_ip_addr:
                        OUTPUTS[InternalInterface] = t.add_output(Output(
                            InternalInterface,
                            Description="Internal interface ID on BIG-IP",
                            Value=If(
                                "useDynamicInternalIpAddr",
                                Ref(InternalInterface),
                                Ref(StaticInternalInterface))
                        ))

                        OUTPUTS[InternalInterfacePrivateIp] = t.add_output(Output(
                            InternalInterfacePrivateIp,
                            Description="Internally routable IP of internal interface on BIG-IP",
                            Value=If(
                                "useDynamicInternalIpAddr",
                                GetAtt(InternalInterface, "PrimaryPrivateIpAddress"),
                                GetAtt(StaticInternalInterface, "PrimaryPrivateIpAddress"))
                        ))
                    else:
                        OUTPUTS[InternalInterface] = t.add_output(Output(
                            InternalInterface,
                            Description="Internal interface ID on BIG-IP",
                            Value=Ref(InternalInterface)
                        ))

                        OUTPUTS[InternalInterfacePrivateIp] = t.add_output(Output(
                            InternalInterfacePrivateIp,
                            Description="Internally routable IP of internal interface on BIG-IP",
                            Value=GetAtt(InternalInterface, "PrimaryPrivateIpAddress")
                        ))

                if num_nics > 3:
                    for number in range(3, 8):
                        InterfacePrivateIp = "Bigip" + str(BIGIP_INDEX + 1) + "Interface" + str(number) + "PrivateIp"
                        OUTPUTS[nics[number]] = t.add_output(Output(
                            nics[number],
                            Description="Interface" + str(number) + " ID on BIG-IP",
                            Value=Ref(nics[number]),
                            Condition="createNic" + str(number)
                        ))
                        OUTPUTS[InterfacePrivateIp] = t.add_output(Output(
                            InterfacePrivateIp,
                            Description="Internally routable IP of interface" + str(number) + " on BIG-IP",
                            Value=GetAtt(nics[number], "PrimaryPrivateIpAddress"),
                            Condition="createNic" + str(number)
                        ))

        if webserver:
            webserverPrivateIp = t.add_output(Output(
                "webserverPrivateIp",
                Description="Private IP for Webserver",
                Value=GetAtt(Webserver, "PrivateIp"),
            ))

            WebserverPublicIp = t.add_output(Output(
                "WebserverPublicIp",
                Description="Public IP for Webserver",
                Value=GetAtt(Webserver, "PublicIp"),
            ))

            WebserverPublicUrl = t.add_output(Output(
                "WebserverPublicUrl",
                Description="Public URL for the Webserver",
                Value=Join("", ["http://", GetAtt(Webserver, "PublicIp")]),
            ))

    #BEGIN RULES
    if ha_type == "autoscale" and "dns" in components:
        rule = {
            "RuleCondition":  {
                "Fn::Equals": [
                    "No",
                    {
                        "Ref": "provisionPublicIP"
                    }
                ]
            },
            "Assertions": [
                {
                    "Assert": {"Fn::Equals": [{"Ref": "dnsMemberIpType"}, "private"]},
                    "AssertDescription": "The type cannot be public when public IP is not provision (provisionPublicIP is required)"
                }
            ]
        }
        t.add_rule("ValidateDnsMemberIPType", rule)
    if stack == "full":
        print(t.to_json(indent=1))
    else:
        print(t.to_json(indent=1))
if __name__ == "__main__":
    main()
