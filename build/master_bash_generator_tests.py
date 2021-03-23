# This unit test class exists solely to test basic functionality of master_bash_generator.py, some more advanced tests may be added 
# General test cases: 
# Example command 
# Case statements
# Required parameters
# License key prompt
# Template URLs
# Create stack command 


import unittest
from master_bash_generator import *

class arguments(object):
        pass 

class test_bash_generator(unittest.TestCase):
    
    # -----EXAMPLE COMMAND TESTS-----    
    def test_1nic_standalone_example_command(self):
        args = arguments()
        setattr(args, 'num_nics', 1)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.example_string = create_example_command(self.example_parameters)

        correct_command = "./deploy_via_bash.sh --stackName <value> --licenseType Hourly --sshKey <value> --subnet1Az1 <value> --bigipExternalSecurityGroup <value> --imageName Good200Mbps --Vpc <value> --instanceType t2.medium"

        self.assertEqual(self.example_string, correct_command)
    
    def test_2nic_standalone_example_command(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.example_string = create_example_command(self.example_parameters)

        correct_command = "./deploy_via_bash.sh --stackName <value> --licenseType Hourly --managementSubnetAz1 <value> --sshKey <value> --bigipManagementSecurityGroup <value> --subnet1Az1 <value> --bigipExternalSecurityGroup <value> --instanceType t2.medium --Vpc <value> --imageName Good200Mbps"

        self.assertEqual(self.example_string, correct_command)
    
    def test_3nic_standalone_example_command(self):
        args = arguments()
        setattr(args, 'num_nics', 3)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.example_string = create_example_command(self.example_parameters)

        correct_command = "./deploy_via_bash.sh --stackName <value> --licenseType Hourly --bigipManagementSecurityGroup <value> --sshKey <value> --subnet2Az1 <value> --managementSubnetAz1 <value> --subnet1Az1 <value> --bigipExternalSecurityGroup <value> --instanceType t2.medium --bigipInternalSecurityGroup <value> --Vpc <value> --imageName Good200Mbps"

        self.assertEqual(self.example_string, correct_command)
    
    def test_2nic_cluster_same_az_example_command(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'same-az')
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.example_string = create_example_command(self.example_parameters)
        correct_command = "./deploy_via_bash.sh --stackName <value> --licenseType Hourly --managementSubnetAz1 <value> --sshKey <value> --bigipManagementSecurityGroup <value> --subnet1Az1 <value> --bigipExternalSecurityGroup <value> --instanceType t2.medium --Vpc <value> --imageName Good200Mbps"

        self.assertEqual(self.example_string, correct_command)
    
    def test_2nic_cluster_across_az_example_command(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'across-az')
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.example_string = create_example_command(self.example_parameters)
        correct_command = "./deploy_via_bash.sh --stackName <value> --licenseType Hourly --bigipManagementSecurityGroup <value> --sshKey <value> --managementSubnetAz2 <value> --managementSubnetAz1 <value> --subnet1Az1 <value> --bigipExternalSecurityGroup <value> --subnet1Az2 <value> --Vpc <value> --instanceType t2.medium --imageName Good200Mbps"

        self.assertEqual(self.example_string, correct_command)


    # -----END EXAMPLE COMMAND TESTS-----

    # # -----CASE STATEMENT TESTS----
    def test_1nic_standalone_case_statements(self):
        args = arguments()
        setattr(args, 'num_nics', 1)
        self.all_parameters = create_all_parameters(args)
        self.case_statements = create_case_statements(self.all_parameters)

        correct_cases = (
        """
        --licenseKey1)
			licenseKey1=$2
			shift 2;;
		--licenseType)
			licenseType=$2
			shift 2;;
		--sshKey)
			sshKey=$2
			shift 2;;
		--subnet1Az1)
			subnet1Az1=$2
			shift 2;;
		--bigipExternalSecurityGroup)
			bigipExternalSecurityGroup=$2
			shift 2;;
		--stackName)
			stackName=$2
			shift 2;;
		--imageName)
			imageName=$2
			shift 2;;
		--Vpc)
			Vpc=$2
			shift 2;;
		--instanceType)
			instanceType=$2
			shift 2;;
            """)

        self.assertEqual(''.join(self.case_statements.split()), ''.join(correct_cases.split()))

    def test_2nic_standalone_case_statements(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.case_statements = create_case_statements(self.all_parameters)

        correct_cases = (
        """
        --licenseKey1)
			licenseKey1=$2
			shift 2;;
		--licenseType)
			licenseType=$2
			shift 2;;
		--managementSubnetAz1)
			managementSubnetAz1=$2
			shift 2;;
		--sshKey)
			sshKey=$2
			shift 2;;
		--licenseKey2)
			licenseKey2=$2
			shift 2;;
		--bigipManagementSecurityGroup)
			bigipManagementSecurityGroup=$2
			shift 2;;
		--subnet1Az1)
			subnet1Az1=$2
			shift 2;;
		--bigipExternalSecurityGroup)
			bigipExternalSecurityGroup=$2
			shift 2;;
		--stackName)
			stackName=$2
			shift 2;;
		--imageName)
			imageName=$2
			shift 2;;
		--Vpc)
			Vpc=$2
			shift 2;;
		--instanceType)
			instanceType=$2
			shift 2;;
            """)

        self.assertEqual(''.join(self.case_statements.split()), ''.join(correct_cases.split()))

    def test_3nic_standalone_case_statements(self):
        args = arguments()
        setattr(args, 'num_nics', 3)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.case_statements = create_case_statements(self.all_parameters)

        correct_cases = ("""
        --licenseKey1)
			licenseKey1=$2
			shift 2;;
		--licenseType)
			licenseType=$2
			shift 2;;
		--managementSubnetAz1)
			managementSubnetAz1=$2
			shift 2;;
        --bigipInternalSecurityGroup)
            bigipInternalSecurityGroup=$2
            shift 2;;
		--sshKey)
			sshKey=$2
			shift 2;;
		--licenseKey2)
			licenseKey2=$2
			shift 2;;
        --subnet2Az1)
            subnet2Az1=$2
            shift 2;;
		--bigipManagementSecurityGroup)
			bigipManagementSecurityGroup=$2
			shift 2;;
		--subnet1Az1)
			subnet1Az1=$2
			shift 2;;
		--bigipExternalSecurityGroup)
			bigipExternalSecurityGroup=$2
			shift 2;;
		--stackName)
			stackName=$2
			shift 2;;
		--imageName)
			imageName=$2
			shift 2;;
		--Vpc)
			Vpc=$2
			shift 2;;
		--instanceType)
			instanceType=$2
			shift 2;;
        """)

        self.assertEqual(''.join(self.case_statements.split()), ''.join(correct_cases.split()))


    def test_2nic_cluster_same_az_case_statements(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'same-az')
        self.all_parameters = create_all_parameters(args)
        self.case_statements = create_case_statements(self.all_parameters)
    
        correct_cases = (
        """
        --licenseKey1)
			licenseKey1=$2
			shift 2;;
		--licenseType)
			licenseType=$2
			shift 2;;
		--managementSubnetAz1)
			managementSubnetAz1=$2
			shift 2;;
		--sshKey)
			sshKey=$2
			shift 2;;
		--licenseKey2)
			licenseKey2=$2
			shift 2;;
		--bigipManagementSecurityGroup)
			bigipManagementSecurityGroup=$2
			shift 2;;
		--subnet1Az1)
			subnet1Az1=$2
			shift 2;;
		--bigipExternalSecurityGroup)
			bigipExternalSecurityGroup=$2
			shift 2;;
		--stackName)
			stackName=$2
			shift 2;;
		--imageName)
			imageName=$2
			shift 2;;
		--Vpc)
			Vpc=$2
			shift 2;;
		--instanceType)
			instanceType=$2
			shift 2;;
            """)

        self.assertEqual(''.join(self.case_statements.split()), ''.join(correct_cases.split()))

    def test_2nic_cluster_across_az_case_statements(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'across-az')
        self.all_parameters = create_all_parameters(args)
        self.case_statements = create_case_statements(self.all_parameters)
        
        correct_cases = (
        """
        --licenseKey1)
			licenseKey1=$2
			shift 2;;
		--licenseType)
			licenseType=$2
			shift 2;;
		--managementSubnetAz1)
			managementSubnetAz1=$2
			shift 2;;
		--sshKey)
			sshKey=$2
			shift 2;;
		--licenseKey2)
			licenseKey2=$2
			shift 2;;
		--managementSubnetAz2)
			managementSubnetAz2=$2
			shift 2;;
		--bigipManagementSecurityGroup)
			bigipManagementSecurityGroup=$2
			shift 2;;
		--subnet1Az1)
			subnet1Az1=$2
			shift 2;;
		--bigipExternalSecurityGroup)
			bigipExternalSecurityGroup=$2
			shift 2;;
		--subnet1Az2)
			subnet1Az2=$2
			shift 2;;
		--stackName)
			stackName=$2
			shift 2;;
		--imageName)
			imageName=$2
			shift 2;;
		--Vpc)
			Vpc=$2
			shift 2;;
		--instanceType)
			instanceType=$2
			shift 2;;
            """)

        self.assertEqual(''.join(self.case_statements.split()), ''.join(correct_cases.split()))

    # -----END CASE STATEMENT TESTS
        
    # -----REQUIRED PARAMETER TESTS
    def test_1nic_standalone_required_parameters(self):
        args = arguments()
        setattr(args, 'num_nics', 1)
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.required_parameters = create_required_parameters(self.example_parameters)

        correct_parameters = '"stackName licenseType sshKey subnet1Az1 bigipExternalSecurityGroup imageName Vpc instanceType "'

        self.assertEqual(self.required_parameters, correct_parameters)

    def test_2nic_standalone_required_parameters(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.required_parameters = create_required_parameters(self.example_parameters)

        correct_parameters = '"stackName licenseType managementSubnetAz1 sshKey bigipManagementSecurityGroup subnet1Az1 bigipExternalSecurityGroup instanceType Vpc imageName "'

        self.assertEqual(self.required_parameters, correct_parameters)
        
    def test_3nic_standalone_required_parameters(self):
        args = arguments()
        setattr(args, 'num_nics', 3)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.required_parameters = create_required_parameters(self.example_parameters)

        correct_parameters = '"stackName licenseType bigipManagementSecurityGroup sshKey subnet2Az1 managementSubnetAz1 subnet1Az1 bigipExternalSecurityGroup instanceType bigipInternalSecurityGroup Vpc imageName "'

        self.assertEqual(self.required_parameters, correct_parameters)
    def test_2nic_cluster_same_az_required_parameters(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'same-az')
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.required_parameters = create_required_parameters(self.example_parameters)

        correct_parameters = '"stackName licenseType managementSubnetAz1 sshKey bigipManagementSecurityGroup subnet1Az1 bigipExternalSecurityGroup instanceType Vpc imageName "'

        self.assertEqual(self.required_parameters, correct_parameters)


    def test_2nic_cluster_across_az_required_parameters(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'across-az')
        self.all_parameters = create_all_parameters(args)
        self.example_parameters = create_example_command_parameters(self.all_parameters)
        self.required_parameters = create_required_parameters(self.example_parameters)

        correct_parameters = '"stackName licenseType bigipManagementSecurityGroup sshKey managementSubnetAz2 managementSubnetAz1 subnet1Az1 bigipExternalSecurityGroup subnet1Az2 Vpc instanceType imageName "'

        self.assertEqual(self.required_parameters, correct_parameters)

    # -----END REQUIRED PARAMETER TESTS-----

    # -----LICENSE KEY PROMPT TESTS-----

    def test_standalone_license_prompt(self):
        args = arguments()
        setattr(args, 'ha_type', 'standalone')
        self.license_prompt = create_license_key_prompt(args)

        correct_prompt = ("""while [ -z $licenseKey1 ]
    do
        read -p "Please enter value for licenseKey1:" licenseKey1
    done
    """)

        self.assertEqual(self.license_prompt, correct_prompt)

    def test_cluster_license_prompt(self):
        args = arguments()
        setattr(args, 'ha_type', '')
        setattr(args, 'num_bigips', 2)
        self.license_prompt = create_license_key_prompt(args)

        correct_prompt = ("""while [ -z $licenseKey1 ]
    do
        read -p "Please enter value for licenseKey1:" licenseKey1
    done
    while [ -z $licenseKey2 ]
    do
        read -p "Please enter value for licenseKey2:" licenseKey2
    done
    """)

        self.assertEqual(self.license_prompt, correct_prompt)
        
    # -----END LICENSE KEY PROMPT TESTS-----
    
    #-----URL TESTS-----

    def test_byol_standalone_1nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-byol-1nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 1)
        setattr(args, 'ha_type', 'standalone')

        self.generated_url = create_template_url(args, "byol")

        self.assertEqual(self.generated_url, correct_url)

    def test_hourly_standalone_1nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-hourly-1nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 1)
        setattr(args, 'ha_type', 'standalone')

        self.generated_url = create_template_url(args, "hourly")
        self.assertEqual(self.generated_url, correct_url)
        

    def test_byol_standalone_2nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-byol-2nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'standalone')

        self.generated_url = create_template_url(args, "byol")
        self.assertEqual(self.generated_url, correct_url)

    def test_hourly_standalone_2nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-hourly-2nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'standalone')

        self.generated_url = create_template_url(args, "hourly")

        self.assertEqual(self.generated_url, correct_url)

    def test_byol_standalone_3nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-byol-3nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 3)
        setattr(args, 'ha_type', 'standalone')

        self.generated_url = create_template_url(args, "byol")
        self.assertEqual(self.generated_url, correct_url)

    def test_hourly_standalone_3nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-hourly-3nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 3)
        setattr(args, 'ha_type', 'standalone')

        self.generated_url = create_template_url(args, "hourly")

        self.assertEqual(self.generated_url, correct_url)
        

    def test_byol_cluster_same_az_2nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'same-az')

        self.generated_url = create_template_url(args, "byol")

        self.assertEqual(self.generated_url, correct_url)
        

    def test_hourly_cluster_same_az_2nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'same-az')

        self.generated_url = create_template_url(args, "hourly")

        self.assertEqual(self.generated_url, correct_url)
        

    def test_byol_cluster_across_az_2nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-across-az-cluster-byol-2nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'across-az')

        self.generated_url = create_template_url(args, "byol")

        self.assertEqual(self.generated_url, correct_url)
        

    def test_hourly_cluster_across_az_2nic_url(self):
        correct_url = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-across-az-cluster-hourly-2nic-bigip.template"

        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'across-az')

        self.generated_url = create_template_url(args, "hourly")

        self.assertEqual(self.generated_url, correct_url)
        
    # -----END URL TESTS-----

    # -----CREATE-STACK TESTS-----
    def test_byol_standalone_1nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 1)
        setattr(args, 'ha-type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "byol")
        
        correct_command = "ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=imageName,ParameterValue=$imageName ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=instanceType,ParameterValue=$instanceType "
        self.assertEqual(self.command_string, correct_command)
    
    def test_hourly_standalone_1nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 1)
        setattr(args, 'ha-type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "hourly")

        correct_command = "ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=imageName,ParameterValue=$imageName ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=instanceType,ParameterValue=$instanceType "
        self.assertEqual(self.command_string, correct_command)

    def test_byol_standalone_2nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "byol")

        correct_command = "ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=licenseKey2,ParameterValue=$licenseKey2 ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=imageName,ParameterValue=$imageName ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=instanceType,ParameterValue=$instanceType "
        self.assertEqual(self.command_string, correct_command)
    
    def test_hourly_standalone_2nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "hourly")

        correct_command = "ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=imageName,ParameterValue=$imageName "
        self.assertEqual(self.command_string, correct_command)

    def test_byol_standalone_3nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 3)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "byol")

        correct_command = "ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=bigipInternalSecurityGroup,ParameterValue=$bigipInternalSecurityGroup ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=licenseKey2,ParameterValue=$licenseKey2 ParameterKey=subnet2Az1,ParameterValue=$subnet2Az1 ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=imageName,ParameterValue=$imageName ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=instanceType,ParameterValue=$instanceType "
        self.assertEqual(self.command_string, correct_command)
    
    def test_hourly_standalone_3nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 3)
        setattr(args, 'ha_type', 'standalone')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "hourly")

        correct_command = "ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=subnet2Az1,ParameterValue=$subnet2Az1 ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=bigipInternalSecurityGroup,ParameterValue=$bigipInternalSecurityGroup ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=imageName,ParameterValue=$imageName "
        self.assertEqual(self.command_string, correct_command)
    
    def test_byol_cluster_same_az_2nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'same-az')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "byol")

        correct_command = "ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=licenseKey2,ParameterValue=$licenseKey2 ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=imageName,ParameterValue=$imageName ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=instanceType,ParameterValue=$instanceType "
        self.assertEqual(self.command_string, correct_command)
        
    
    def test_hourly_cluster_same_az_2nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'same-az')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "hourly")

        correct_command = "ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=imageName,ParameterValue=$imageName "
        self.assertEqual(self.command_string, correct_command)
    
    def test_byol_cluster_across_az_2nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'across-az')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "byol")

        correct_command = "ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=licenseKey2,ParameterValue=$licenseKey2 ParameterKey=managementSubnetAz2,ParameterValue=$managementSubnetAz2 ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=subnet1Az2,ParameterValue=$subnet1Az2 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=instanceType,ParameterValue=$instanceType "
        self.assertEqual(self.command_string, correct_command)
    
    def test_hourly_cluster_across_az_2nic_command(self):
        args = arguments()
        setattr(args, 'num_nics', 2)
        setattr(args, 'ha_type', 'across-az')
        self.all_parameters = create_all_parameters(args)
        self.command_string = create_stack_command(self.all_parameters, "hourly")

        correct_command = "ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=managementSubnetAz2,ParameterValue=$managementSubnetAz2 ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=subnet1Az2,ParameterValue=$subnet1Az2 ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=imageName,ParameterValue=$imageName "
        self.assertEqual(self.command_string, correct_command)
    # -----END CREATE-STACK TESTS-----

if __name__ == '__main__':
    unittest.main()
