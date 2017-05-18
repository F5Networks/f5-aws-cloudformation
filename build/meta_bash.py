#/usr/bin/python env

# TODO: remove the build command examples below
# python master_template.py -s existing -n 1 -l hourly > ../supported/standalone/1nic/f5-existing-stack-hourly-1nic-bigip.template
# python master_template.py -s existing -n 2 -l hourly > ../supported/standalone/2nic/f5-existing-stack-hourly-2nic-bigip.template

# python master_template.py -s existing -n 1 -l byol > ../supported/standalone/1nic/f5-existing-stack-byol-1nic-bigip.template
# python master_template.py -s existing -n 2 -l byol > ../supported/standalone/2nic/f5-existing-stack-byol-2nic-bigip.template

# Cluster/HA
# python master_template.py -s existing -n 2 -l hourly -H same-az > ../supported/cluster/2nic/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template
# python master_template.py -s existing -n 2 -l byol -H same-az > ../supported/cluster/2nic/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template

def main():
    output_string = read_all_file_lines("base.deploy_via_bash.sh")

    example_command = create_example_command({}) #TODO: empty dict passed so script would run
    
    # TODO: string replacements via tags, TODO: possibly refactor the replacements into own method 
    output_string = output_string.replace("<EXAMPLE_CMD>", example_command)

    write_all_bash_lines("deploy_via_bash.sh", output_string)
    #TODO; mv the deploy via bash to the right places in the build script for this. 

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

def parse_args(meta_template_cli_args):
    # Including all options here so that it will be easy to extend the functionality of this 
    # script to create scripts for experimental templates. 
    parser = OptionParser()
    parser.add_option("-s", "--stack", action="store", type="string", dest="stack")
    parser.add_option("-a", "--num-azs", action="store", type="int", dest="num_azs", default=1)
    parser.add_option("-b", "--num-bigips", action="store", type="int", dest="num_bigips")
    parser.add_option("-n", "--nics", action="store", type="int", dest="num_nics", default=1)
    parser.add_option("-c", "--components", action="store", type="string", dest="components")
    parser.add_option("-H", "--ha-type", action="store", type="string", dest="ha_type", default="standalone")

    (options, args) = parser.parse_args()
    parameters = {}

#havent decided where cli_args will be passead into here from 
def create_example_command(meta_template_cli_args):
    
    params_in_common_defaults = {
        "licenseType" : "Hourly", 
        "imageName" : "Good200Mbps", 
        "instanceType" : "t2.medium", 
        "bigipExternalSecurityGroup" : "<value>",
        "sshKey" : "<value>",
        "subnet1AZ1" : "<value>",
        "vpc" : "<value>",
        "stackName" : "<value>"
        }

    # TODO; add additional uncommon parameters 
    unique_to_template = {}
    

    command_builder = "./deploy_via_bash.sh"
    for parameter in params_in_common_defaults:
        command_builder += " --" + str(parameter) + " " + str(params_in_common_defaults[parameter])

    return command_builder

#todo: there has to be a way to seek filepointer to a word or a tag i create in the base.deploy_via_bash.sh file 
# to insert changes to the boilerplate as needed. 
#todo: decide if pulling templates from s3 or from repo

main()