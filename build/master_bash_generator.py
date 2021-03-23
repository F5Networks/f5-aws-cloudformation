#/usr/bin/python env
# This class exists to automate the creation of bash deployment scripts (example: deploy_via_bash.sh for all supported templates)
from optparse import OptionParser
from collections import defaultdict
import copy
def main():
    # parser instance for command line arguments passed in when running this script (master_bash_generator.py)
    cli_argument_parser = parse_args()

    # set up step: read in base file.
    output_string = read_all_file_lines("base.deploy_via_bash.sh")
    # set up step: create all parameters that will be needed for a script to deploy the type of stack specified 
    # in the command line arguments user to run this generator
    all_parameters = create_all_parameters(cli_argument_parser)

    # get strings for tag replacement in base.deploy_via_bash.sh
    example_parameters = create_example_command_parameters(all_parameters)
    example_command = create_example_command(example_parameters)
    required_parameters = create_required_parameters(example_parameters)
    case_statements = create_case_statements(all_parameters)
    byol_license_key_prompt = create_license_key_prompt(cli_argument_parser)
    byol_template_url = create_template_url(cli_argument_parser, "byol")
    hourly_template_url = create_template_url(cli_argument_parser, "hourly")
    create_stack_byol = create_stack_command(all_parameters, "byol")
    create_stack_hourly = create_stack_command(all_parameters, "hourly")

    # replace tags in base.deploy_via_bash.sh with script code
    output_string = output_string.replace("<EXAMPLE_CMD>", example_command)
    output_string = output_string.replace("<CASE_STATEMENTS>", case_statements)
    output_string = output_string.replace("<REQUIRED_PARAMETERS>", required_parameters)
    output_string = output_string.replace("<WHILE_LICENSE_NOT_ENTERED>", byol_license_key_prompt)
    output_string = output_string.replace("<BYOL_TEMPLATE>", byol_template_url)
    output_string = output_string.replace("<HOURLY_TEMPLATE>", hourly_template_url)
    output_string = output_string.replace("<DEPLOY_BYOL>", create_stack_byol)
    output_string = output_string.replace("<DEPLOY_HOURLY>", create_stack_hourly)

    # writes deploy_via_bash.sh file to the location from which this generator is run
    write_all_bash_lines("deploy_via_bash.sh", output_string)

def read_all_file_lines(file_name):
    input_file = open(file_name, "r")
    input_lines = input_file.readlines()
    output_string = ""

    for line in input_lines:
        output_string += line

    input_file.close()
    
    return output_string

def write_all_bash_lines(file_name, output_string):
    output_file = open(file_name, "w")
    output_file.write(output_string)
    output_file.close()

    return output_file

def parse_args():
    # Including all differentiating options here so that it will be easy to extend the functionality of this script to create scripts 
    # for experimental templates. 
    parser = OptionParser()
    parser.add_option("-s", "--stack", action="store", type="string", dest="stack")
    parser.add_option("-a", "--num-azs", action="store", type="int", dest="num_azs", default=1)
    parser.add_option("-b", "--num-bigips", action="store", type="int", dest="num_bigips")
    parser.add_option("-n", "--nics", action="store", type="int", dest="num_nics", default=1)
    parser.add_option("-l", "--license", action="store", type="string", dest="license_type", default="hourly", help="Type of License: hourly, BYOL, or BIG-IQ" )
    parser.add_option("-c", "--components", action="store", type="string", dest="components")
    parser.add_option("-H", "--ha-type", action="store", type="string", dest="ha_type", default="standalone")
    
    (options, args) = parser.parse_args()

    # if standalone, and num_bigips unset 
    if(options.ha_type != "standalone" and options.num_bigips is None):
        options.num_bigips = 2
    
    return options

def create_all_parameters(cli_argument_parser):
    # for 1 nic standalone hourly, the parameters will be as below, no additions. 
    default_substitute = "<value>"
    parameters = {}

    # set all values in the dictionary to the default
    parameters = defaultdict(lambda: default_substitute, parameters)
    # create the keys for all baseline parameters that exist in all stacks
    parameters["licenseType"]
    parameters["imageName"]
    parameters["instanceType"]
    parameters["sshKey"]
    parameters["subnet1Az1"]
    parameters["Vpc"]
    parameters["stackName"]
    parameters["licenseKey1"]
    parameters["restrictedSrcAddress"]
    parameters["restrictedSrcAddressApp"]
    # add differentiating parameters
    if(cli_argument_parser.num_nics == 3):
        parameters["subnet2Az1"]
    if(cli_argument_parser.num_nics >=2):
        parameters["managementSubnetAz1"]
    if(cli_argument_parser.num_nics == 2 and cli_argument_parser.ha_type == "across-az"):
        parameters["managementSubnetAz2"]
        parameters["subnet1Az2"]
        parameters["licenseKey2"]
            
    return parameters

def create_example_command_parameters(all_parameters):
    example_parameters = copy.deepcopy(all_parameters)
    remove_parameter("licenseKey1", example_parameters)
    remove_parameter("licenseKey2", example_parameters)
    example_parameters["licenseType"] = "Hourly" 
    example_parameters["imageName"] = "Good200Mbps"
    example_parameters["instanceType"] = "t2.medium"
    
    return example_parameters


def create_example_command(required_parameters):
    command_builder = "./deploy_via_bash.sh"
    for parameter in required_parameters:
        command_builder += " --" + str(parameter) + " " + str(required_parameters[parameter])

    return command_builder

def create_case_statements(all_parameters):
    output = ""
    whitespace = "\n\t\t\t"
    boilerplate = "--<parameter_name>)" + whitespace + "<parameter_name>=$2" + whitespace + "shift 2;;\n"
    num_replacements = 2
    for parameter in all_parameters:
        output += boilerplate.replace("<parameter_name>", parameter, num_replacements)
        output += "\t\t"

    return output

def create_required_parameters(example_parameters):
    required_parameter_list = example_parameters.keys()
    required_parameter_string = ""
    for parameter in required_parameter_list:
        required_parameter_string += parameter + " "
        
    return '"' + required_parameter_string + '"'

def create_license_key_prompt(cli_argument_parser):
    boilerplate = (
    """while [ -z $licenseKey<num> ]
    do
        read -p "Please enter value for licenseKey<num>:" licenseKey<num>
    done
    """)
    output = ""
    num_replacements = 3
    if(cli_argument_parser.ha_type == "standalone"):
        output = boilerplate.replace("<num>", "1", num_replacements)
    else:
        for i in range (cli_argument_parser.num_bigips):
            output += boilerplate.replace("<num>", str(i + 1), num_replacements)
        
    return output

def create_template_url(cli_argument_parser, license_type):
    boilerplate = "https://f5-cft.s3.amazonaws.com/f5-existing-stack-<ha_type>-cluster-<license_type>-<num_nics>nic-bigip.template"

    output = boilerplate.replace("<license_type>", license_type)
    
    output = output.replace("<num_nics>", str(cli_argument_parser.num_nics))

    if(cli_argument_parser.ha_type == "standalone"):
        output = output.replace("-<ha_type>-cluster", "")
    else:
        output = output.replace("<ha_type>", cli_argument_parser.ha_type)
    
    return output

def create_stack_command(all_parameters, license_type):
    remove_parameter("stackName", all_parameters)
    
    output = ""
    boilerplate = "ParameterKey=<key>,ParameterValue=<value> "
    if(license_type == "byol"):
        remove_parameter("licenseType", all_parameters)
        output = populate_boilerplate(all_parameters, boilerplate)
       
    elif(license_type == "hourly"):
        hourly_parameters = create_example_command_parameters(all_parameters)
        remove_parameter("licenseType", hourly_parameters)
        output = populate_boilerplate(hourly_parameters, boilerplate)

    #TODO: for future, add license types for experimental templates (BIG-IQ, etc)

    return output

def populate_boilerplate(all_parameters, boilerplate):
    output = ""
    for parameter in all_parameters:
        temp = boilerplate.replace("<key>", parameter).replace("<value>", "$" + parameter)
        output += temp
    return output

def remove_parameter(parameter, dictionary):
    if(parameter in dictionary):
        dictionary.pop(parameter)

if __name__ == "__main__":
    main()