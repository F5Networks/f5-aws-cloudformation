# deploy_stacks.py

"""
Short python script to deploy CloudFormation templates.
See README.md for usage.

Created: Wed Dec 16 10:59:26 PST 2015
Author: c.mutzel@f5.com, a.applebaum@f5.com

See usage in README.md

"""

from optparse import OptionParser
import ConfigParser
import boto3
import time
import json
import sys
import os

STACK_WAIT_TIMEOUT = 600

class DeploymentManager:
    """Class to simplify management of a deployment composed of multiple CFTs"""

    def __init__(self, deployment_name, region):
        self.region = region
        self.deployment_name = deployment_name
        self.client = boto3.client('cloudformation', self.region)
        self.namespace = {}

    def get_stack_name(self, template_name):
        """Ensures our stack names are deterministic"""
        return '{}-{}'.format(self.deployment_name, template_name)

    def get_stack_status(self, stack_name):
        """Queries boto3 api for the stack status """
        stacks = self.client.list_stacks()['StackSummaries']
        for stack in stacks:
            if stack['StackName'].lower() == stack_name.lower():
                return stack
        return None

    def wait_for_stack_status(self, stack_name,
                              timeout=STACK_WAIT_TIMEOUT, poll_interval=10,
                              allowed_final_statuses=['CREATE_COMPLETE'],
                              allowed_wait_statuses=['CREATE_IN_PROGRESS']):
        """Waits for a stack to reach one of states in @allowed_final_status"""
        slept = 0
        while slept < timeout:
            stack_status = self.get_stack_status(stack_name)
            if not stack_status:
                raise Exception(("Could not retrieve status for {}, "
                                 "Does it exist?").format(stack_name))
            elif stack_status['StackStatus'] in allowed_final_statuses:
                return
            elif stack_status['StackStatus'] in allowed_wait_statuses:
                print ("Sleeping for {} seconds while stack "
                       "deployment completes.").format(poll_interval)
                time.sleep(poll_interval)
                slept += poll_interval
            else:
                raise Exception(("Fatal error while waiting for stack"
                                 "deployment, stack {} is in state {}").format(stack_name,
                                    stack_status['StackStatus']))
        raise Exception(("Timeout while waiting for stack deployment "
                         "to complete.  Last status was {}").format(stack_status))

    def get_stack_parameters(self, template_name):
        """Builds the inputs we need to deploy a stack in this deployment"""

        template_parameters = json.loads(self.read_template(template_name))['Parameters']
        stack_parameters = []
        for k in template_parameters.keys():
            # assign variables for those which we have in our 'namespace'
            if k in dm.namespace:
                new_param = {'ParameterKey': k, 'ParameterValue': dm.namespace[k]}
                stack_parameters.append(new_param)
        return stack_parameters

    def read_template(self, template_name):
        """
             Reads a CFT template from a file.
             Return whole template as string
        """
        with open(TEMPLATES_DIR + '/' + template_name + ".template") as template_fp:
            return template_fp.read()

    def create_or_update_stack(self, template_name):
        """
            Deploys a stack from a given template.
            Does not update CF stacks if the template has changed.
        """
        stack_name = self.get_stack_name(template_name)
        stack_parameters = self.get_stack_parameters(template_name)
        template_body = self.read_template(template_name)

        # check if the stack exists
        status = self.get_stack_status(stack_name)

        # otherwise, deploy it
        if status and status['StackStatus'] == 'CREATE_COMPLETE':
            pass
        elif not status or status['StackStatus'] in ['DELETE_COMPLETE']:
            create_response = self.client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=stack_parameters)
            self.wait_for_stack_status(stack_name)
        elif status['StackStatus'] in ['CREATE_IN_PROGRESS']:
            self.wait_for_stack_status(stack_name)
        else:
            raise Exception(
                'not sure what to do...stack is in state {}'.format(
                    status['StackStatus']))

        # keep track of variables that are outputs from each stack
        stack = self.describe_stack(template_name)
        self.add_outputs_to_namespace(stack)

        return stack

    def describe_stack(self, template_name):
        stack_name = self.get_stack_name(template_name)
        return self.client.describe_stacks(StackName=stack_name)['Stacks'][0]

    def add_vars_to_namespace(self, to_add):
        """
            Adds variables provided within the function arguments to the
            namespace for this deployment.
            Use to keep track of all variables for a deployment.
        """
        for k, v in to_add.iteritems():
            if v:
                self.namespace[k] = v

    def add_outputs_to_namespace(self, stack):
        """
            Adds outputs of a stack to the
            namespace for this deployment.
            Use to keep track of all variables for a deployment.
        """
        if 'Outputs' in stack:
            for item in stack['Outputs']:
                self.namespace[item['OutputKey']] = item['OutputValue']



parser = OptionParser()
parser.add_option("-t", "--templates", action="store", type="string", dest="templates", help="REQUIRED: Comma separated list of templates" )
parser.add_option("-d", "--dir", action="store", type="string", dest="template_dir", help="directory containing templates" )
parser.add_option("-r", "--regkeys", action="store", type="string", dest="regkeys", help="Comma seperated list of regkeys. List must match # of templates" )
parser.add_option("-c", "--config", action="store", type="string", dest="config_file", help="Config file used" )


parser.set_defaults(template_dir='../experimental')
(options, args) = parser.parse_args()

# CFT stacknames restricted 
# ex. stackName failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]* 
# so will construct stack names from file's base name
TEMPLATES_DIR = options.template_dir

# define set of templates we are deploying
file_list = []
template_list = []
if not options.templates:
    parser.error("-t <template or list of templates> required. Type -h for help")
else:
    file_list = options.templates.split(',')
    for file in file_list: 
        template_list.append(os.path.splitext(os.path.basename(file))[0])

# create list of regkeys (should be indexed same as list of input templates)
# if there's a non-byol bigip template in the beginning or middle, add a comma space
# ex. --regkeys ,NURSI-GMLZW-VYDKC-CLEHO-BHRQQHI,XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
# ex. --regkeys NURSI-GMLZW-VYDKC-CLEHO-BHRQQHI,,XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
regkey_list = []
# Assumes regkeys will match number of templates
if options.regkeys:
    regkey_list = options.regkeys.split(',')
else: 
    # just populate to match template index
    for template in template_list:
        regkey_list.append("")

if len(regkey_list) != len(template_list):
    parser.error(
"Number of regkey entries needs to match number of templates.\n \
ex. 2 templates should have 2 regkey entries:\n \
   --regkeys XXXXX-XXXXX-XXXXX-XXXXX-XXXXX,XXXXX-XXXXX-XXXXX-XXXXX-XXXXX\n \
   --regkeys XXXXX-XXXXX-XXXXX-XXXXX-XXXXX,\n \
   --regkeys ,XXXXX-XXXXX-XXXXX-XXXXX-XXXXX\n\n \
Type -h for help.\n \
"
)


# # load variables provided by user
configParser = ConfigParser.ConfigParser()

if options.config_file:
    configParser.read(options.config_file)
else:
    configParser.read('config.ini')

# Prefix added to all stacks
DeploymentName = configParser.get('vars', 'DeploymentName')

# Common
Region = configParser.get('vars', 'Region')
KeyName = configParser.get('vars', 'KeyName')
SSHLocation = configParser.get('vars', 'SSHLocation')
BigipInstanceType = configParser.get('vars', 'BigipInstanceType')
BigipPerformanceType = configParser.get('vars', 'BigipPerformanceType')
BigipAdminUsername = configParser.get('vars', 'BigipAdminUsername')
BigipAdminPassword = configParser.get('vars', 'BigipAdminPassword')

# For full stacks
AvailabilityZone1 = configParser.get('vars', 'AvailabilityZone1')
AvailabilityZone2 = configParser.get('vars', 'AvailabilityZone2')

# For Sinlge nics Big-IPs
BigipManagementGuiPort = configParser.get('vars', 'BigipManagementGuiPort')

#For Big-IQ License Pools
BigiqUsername = configParser.get('vars', 'BigiqUsername')
BigiqPassword = configParser.get('vars', 'BigiqPassword')
BigiqAddress = configParser.get('vars', 'BigiqAddress')
BigiqLicensePoolUUID = configParser.get('vars', 'BigiqLicensePoolUUID')

# For full stacks
WebserverInstanceType = configParser.get('vars', 'WebserverInstanceType')
# For clusters or AutoScale Groups
IamAccessKey = configParser.get('vars', 'IamAccessKey')
IamSecretKey = configParser.get('vars', 'IamSecretKey')
# For ELB stacks
CertificateId = configParser.get('vars', 'CertificateId')


dm = DeploymentManager(DeploymentName, Region)
dm.add_vars_to_namespace({
    'KeyName': KeyName,
    'SSHLocation': SSHLocation,
    'AvailabilityZone1': AvailabilityZone1,
    'AvailabilityZone2': AvailabilityZone2,
    'BigipAdminUsername': BigipAdminUsername,    
    'BigipAdminPassword': BigipAdminPassword,
    'BigipInstanceType': BigipInstanceType,
    'BigipPerformanceType': BigipPerformanceType,
    'BigipManagementGuiPort': BigipManagementGuiPort,
    'BigiqUsername': BigiqUsername,
    'BigiqPassword': BigiqPassword,
    'BigiqAddress': BigiqAddress,
    'BigiqLicensePoolUUID': BigiqLicensePoolUUID,
    'WebserverInstanceType': WebserverInstanceType,
    'IamAccessKey': IamAccessKey,
    'IamSecretKey': IamSecretKey,
    'CertificateId': CertificateId
})

# deploy all of the cloudformation templates
for i in range(len(template_list)):
    # To make BigipLicenseKey unique to each template
    dm.add_vars_to_namespace({ 'Bigip1LicenseKey': regkey_list[i] })

    print 'Deploying {} template'.format(template_list[i])
    dm.create_or_update_stack(template_list[i])


# print 'Finished deployment of CFTs'
# print 'Info:'
# for k in ['BigipELBDnsName', 'ByolBigipInstance', 'BigipAutoscaleGroup']:
#     print '  {}: {}'.format(k, dm.namespace[k])
