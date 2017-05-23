# TODO: remove the build command examples below
# python master_template.py -s existing -n 1 -l hourly > ../supported/standalone/1nic/f5-existing-stack-hourly-1nic-bigip.template
# python master_template.py -s existing -n 2 -l hourly > ../supported/standalone/2nic/f5-existing-stack-hourly-2nic-bigip.template

# python master_template.py -s existing -n 1 -l byol > ../supported/standalone/1nic/f5-existing-stack-byol-1nic-bigip.template
# python master_template.py -s existing -n 2 -l byol > ../supported/standalone/2nic/f5-existing-stack-byol-2nic-bigip.template

# Cluster/HA
# python master_template.py -s existing -n 2 -l hourly -H same-az > ../supported/cluster/2nic/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template
# python master_template.py -s existing -n 2 -l byol -H same-az > ../supported/cluster/2nic/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template
from optparse import OptionParser
import copy


def main():
    cli_argument_parser = parse_args()

    output_string = read_all_file_lines("base.deploy_via_bash.sh")
    all_parameters = create_all_parameters(cli_argument_parser)
    example_parameters = create_example_parameters(all_parameters)
    example_command = create_example_command(example_parameters)
    required_parameters = create_required_parameters(example_parameters)
    case_statements = create_case_stataments(all_parameters)
    byol_license_key_prompt = create_license_key_prompt(cli_argument_parser)
    byol_template_url = create_template_url(cli_argument_parser, "byol")
    hourly_template_url = create_template_url(cli_argument_parser, "hourly")
    create_stack_byol = create_stack_command(all_parameters, "byol") #TODO
    create_stack_hourly = create_stack_command(all_parameters, "hourly") #TODO

    # TODO: string replacements via tags, TODO: possibly refactor the replacements into own method 
    output_string = output_string.replace("<EXAMPLE_CMD>", example_command)
    output_string = output_string.replace("<CASE_STATEMENTS>", case_statements)
    output_string = output_string.replace("<REQUIRED_PARAMETERS>", required_parameters)
    output_string = output_string.replace("<WHILE_LICENSE_NOT_ENTERED>", byol_license_key_prompt)
    output_string = output_string.replace("<BYOL_TEMPLATE>", byol_template_url)
    output_string = output_string.replace("<HOURLY_TEMPLATE>", hourly_template_url)
    output_string = output_string.replace("<DEPLOY_BYOL>", create_stack_byol)
    output_string = output_string.replace("<DEPLOY_HOURLY>", create_stack_hourly)


    write_all_bash_lines("deploy_via_bash.sh", output_string)

def read_all_file_lines(file_name):
    base_file = open(file_name, "r")
    base_lines = base_file.readlines()
    output_string = ""

    for line in base_lines:
        output_string += line

    base_file.close()
    
    return output_string

def write_all_bash_lines(file_name, output_string):
    output_file = open(file_name, "w")
    output_file.write(output_string)
    output_file.close()

    return output_file

def parse_args():
    # Including all differentiating options here (AKA not license type because that is handled in the deploy_via_bash scripts
    # so that it will be easy to extend the functionality of this script to create scripts for experimental templates. 
    parser = OptionParser()
    parser.add_option("-s", "--stack", action="store", type="string", dest="stack")
    parser.add_option("-a", "--num-azs", action="store", type="int", dest="num_azs", default=1)
    parser.add_option("-b", "--num-bigips", action="store", type="int", dest="num_bigips")
    parser.add_option("-n", "--nics", action="store", type="int", dest="num_nics", default=1)
    parser.add_option("-l", "--license", action="store", type="string", dest="license_type", default="hourly", help="Type of License: hourly, BYOL, or BIG-IQ" )
    parser.add_option("-c", "--components", action="store", type="string", dest="components")
    parser.add_option("-H", "--ha-type", action="store", type="string", dest="ha_type", default="standalone")
    

    (options, args) = parser.parse_args()

    # if standalone, and num_bigips unset (i.e. default int value 0)
    if(options.ha_type != "standalone" and options.num_bigips is None):
        options.num_bigips = 2
    
    return options

def create_all_parameters(cli_argument_parser):
    # for 1 nic standalone hourly, the parameters will be as below, no additions. 
    default_substitute = "<value>"
    parameters = {
        "licenseType" : "Hourly", 
        "imageName" : default_substitute, 
        "instanceType" : "t2.medium", 
        "bigipExternalSecurityGroup" : default_substitute,
        "sshKey" : default_substitute,
        "subnet1Az1" : default_substitute,
        "Vpc" : default_substitute,
        "stackName" : default_substitute,
        "licenseKey1" : default_substitute
        }

    if(cli_argument_parser.num_nics == 2):
        #implicitly, if hourly and/or cluster or standalone... then
        parameters["bigipManagementSecurityGroup"] = default_substitute
        parameters["licenseKey2"] = default_substitute
        parameters["managementSubnetAz1"] = default_substitute
        if(cli_argument_parser.ha_type == "across-az"):
            parameters["managementSubnetAz2"] = default_substitute
            parameters["subnet1Az2"] = default_substitute
        
    return parameters

def create_example_parameters(all_parameters):
    example_parameters = copy.deepcopy(all_parameters)
    remove_parameter("licenseKey1", example_parameters)
    remove_parameter("licenseKey2", example_parameters)
    example_parameters["imageName"] = "Good200Mbps"
    
    return example_parameters

def create_required_parameters(example_parameters):
    required_parameter_list = example_parameters.keys()
    required_parameter_string = ""
    for parameter in required_parameter_list:
        required_parameter_string += parameter + " "
        
    return '"' + required_parameter_string + '"'

#havent decided where cli_args will be passead into here from 
def create_example_command(required_parameters):
    command_builder = "./deploy_via_bash.sh"
    for parameter in required_parameters:
        command_builder += " --" + str(parameter) + " " + str(required_parameters[parameter])

    return command_builder

def create_license_key_prompt(cli_argument_parser):
    boilerplate = (
    """while [ -z $licenseKey<num> ]
    do
        read -p "Please enter value for licenseKey<num>:" licenseKey<num>
    done"""
    )
    otuput = ""

    if(cli_argument_parser.ha_type == "standalone"):
        output = boilerplate.replace("<num>", "1", 3)
    
    else:
        for i in range (cli_argument_parser.num_bigips):
            output = boilerplate.replace("<num>", str(i), 3)
        
    return output

def create_template_url(cli_argument_parser, license_type):
    boilerplate = "https://s3.amazonaws.com/f5-cft/f5-existing-stack-<ha_type>-cluster-<license_type>-<num_nics>nic-bigip.template"

    output = boilerplate.replace("<license_type>", license_type)
    
    output = output.replace("<num_nics>", str(cli_argument_parser.num_nics))

    if(cli_argument_parser.ha_type == "standalone"):
        output = output.replace("-<ha_type>-cluster", "")
    else:
        output = output.replace("<ha_type>", cli_argument_parser.ha_type)
    
    return output

def create_case_stataments(required_parameters):
    output = ""
    whitespace = "\n\t\t\t"
    boilerplate = "-<alpha>|--<parameter_name>)" + whitespace + "<parameter_name>=$2" + whitespace + "shift 2;;\n"
    alphabets = "a b c d e f g h i j k l m n o p q r s t u v w x y z aa bb cc dd ee ff gg hh ii jj kk ll mm nn oo pp"
    case_switch = alphabets.split();

    index = 0
    for parameter in required_parameters:
        output += boilerplate.replace("<alpha>", case_switch[index]).replace("<parameter_name>", parameter, 2)
        output += "\t\t"
        index += 1

    output += "--)" + whitespace + "shift" + whitespace + "break;;"

    return output

def create_stack_command(all_parameters, license_type):
    remove_parameter("stackName", all_parameters)
    remove_parameter("licenseType", all_parameters)
    
    output = ""
    boilerplate = "ParameterKey=<key>,ParameterValue=<value> "
    if(license_type == "byol"):
        output = populate_boilerplate(all_parameters, boilerplate)
       
    elif(license_type == "hourly"):
        newthing = create_example_parameters(all_parameters)
        output = populate_boilerplate(newthing, boilerplate)

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

main()