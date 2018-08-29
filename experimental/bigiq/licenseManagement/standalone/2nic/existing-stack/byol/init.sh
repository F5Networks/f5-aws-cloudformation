#!/bin/bash

### Configure default values
log_level="info"
help=false
skip_verify=false
script_dir=$(dirname $0)

TMSH=/usr/bin/tmsh
CURL=/usr/bin/curl
NODE=/usr/bin/node

### Functions - These should go into seperate file(s)
# usage: log message
function log() {
    echo "$(date '+%Y-%m-%dT%H:%M:%SZ'): $1"
}
# usage: get_version
function get_version() {
    ret=$($TMSH show sys version | grep -i product | awk '{print $2}')
    echo ${ret,,}
}
# usage: jsonify key:value,key1:value1
function jsonify() {
    list=$(echo $1 | tr ',' ' ')
    json='{}'
    for i in $list ; do
        kv=($(echo $i | tr ':' ' '))
        json=$(echo $json | jq --arg k ${kv[0]} --arg v ${kv[1]} '. | .[$k]=$v')
    done  
    echo $json
}
# usage: get_val json_object key
function get_val() {
    ret=$(echo $1 | jq .$2 -r)
    echo $ret
}
# usage: mcp_running
function mcp_running {
    checks=0
    while [ $checks -lt 120 ] ; do
        $TMSH -a show sys mcp-state field-fmt | grep -q running
        if [ $? == 0 ]; then
            log "MCPD ready"
            break
        fi
        log "MCPD not ready: $checks"
        let checks=checks+1
        sleep 5
    done
}
# usage: base_config_available - resolves issue found in 6.0.0 versions of big-iq
function base_config_available {
    checks=0
    while [ $checks -lt 120 ] ; do
        $TMSH -a show sys mcp-state field-fmt | grep -q running
        if [ -f /config/bigip_base.conf ]; then
            log "Base Config file present; saving config"
            tmsh save sys config
            cat /config/bigip_base.conf
            break
        fi
        log "Base config file not yet present: $checks"
        let checks=checks+1
        sleep 5
    done
}
# usage: get_net_info eth0 ns|gw include_cidr
function get_net_info() {
    cidr_block_uri="vpc-ipv4-cidr-block"
    add_int=2
    # If getting gateway, update necessary vars
    if [[ $2 == "gw" ]] ; then cidr_block_uri="subnet-ipv4-cidr-block" ; add_int=1 ; fi
    IF_MAC=$(ifconfig $1 | grep -i hwaddr | awk '{print tolower($5)}')
    CIDR_BLOCK=$(curl -sf --retry 20 http://169.254.169.254/latest/meta-data/network/interfaces/macs/${IF_MAC}/${cidr_block_uri})
    RET=$(echo ${CIDR_BLOCK%/*} | awk -F. '{ printf "%d.%d.%d.%d", $1, $2, $3, $4+'${add_int}' }')
    # Include mask in response if requested
    if [[ -n "$3" ]] ; then echo ${RET}/${CIDR_BLOCK#*/} ; else echo $RET ; fi
}

read -r -d '' USAGE << EOM
    Usage: $0
        --help                      Print usage message and exit
        --log-level <string>        Level of logging desired: error, warn, info, debug
        --cloud <string>            Cloud environment executed against: aws
        --skip-verify <string>      Skip verification of dependencies
        --license <string>          License for the device
        --ntp <string>              NTP for the device
        --timezone <string>         Timezone for the device
        --data-interface <string>   Primary interface to use for data-plane
        --vlan <string>             VLAN(s) to create on the device (; for multiple) 'n:ext,nic:1.1'
        --self-ip <string>          Self IP(s) to create on the device (; for multiple): 'n:ext,a:x.x.x.x,v:ext,i:eth1'
        --usage-analytics <string>  Usage analytics to send: 'cN:val,r:val,cI:val,dI:val,lT:val,bIV:val,tN:val,tV:val,send:yes'
        --create-license-pool       Creates license pool, send: name:reg_key
        --create-reg-key-pool       Creates a regkey pool, send: name:reg_key_list 

EOM

### Parse command line arguments
while [[ $# -gt 0 ]] ; do
    case "$1" in
        --help)
            help=true;
            shift ;;
        --log-level)
            log_level="$2"
            shift 2 ;;
        --cloud)
            cloud="$2"
            shift 2 ;;
        --skip-verify)
            skip_verify=true
            shift ;;
        --license)
            license="$2"
            shift 2 ;;
        --ntp)
            ntp="$2"
            shift 2 ;;
        --timezone)
            timezone="$2"
            shift 2 ;;
        --data-interface)
            data_interface="$2"
            shift 2 ;;
        --usage-analytics)
            usage_analytics="$2"
            shift ;;
        --vlan)
            vlan="$2"
            shift 2 ;;
        --self-ip)
            self_ip="$2"
            shift 2 ;;
        --create-license-pool)
            license_pool="$2"
            shift 2 ;;
        --create-reg-key-pool)
            reg_key_pool="$2"
            shift 2 ;;
        *|--)
            shift
            break ;;
    esac
done

if $help ; then
    echo "$USAGE"
    exit
fi

# Verify required parameters
required=("cloud")
for i in ${required[@]} ; do
    if [ -z ${!i} ] ; then
        log "A required parameter is missing: $i"
        exit
    fi
done
# Check for valid parameter values
if [[ $cloud != "aws" ]] ; then
    log "Unsupported cloud: $cloud"
    exit 1
fi
# Check for "Do Not Create" in create pool parmeters
shopt -s nocasematch
if [[ $license_pool == "Do_Not_Create" ]] ; then
    log "Setting licensing pool to null as 'Do_Not_Create' has been specified: $licensing_pool"
    license_pool=""
fi
if [[ $reg_key_pool == "Do_Not_Create" ]] ; then
    log "Setting reg key pool to null as 'Do_Not_Create' has been specified: $licensing_pool"
    reg_key_pool=""
fi
shopt -u nocasematch

### Install dependencies ###
base_url="https://raw.githubusercontent.com/F5Networks"
base_dir="/config/cloud"
base_log_dir="/var/log/cloud/${cloud}"
base_dependency_dir="${base_dir}/${cloud}/node_modules/@f5devcentral"

## Download
fcl_tag="v4.3.0"
fcl_cloud_tag="v2.2.0"
dependencies=("${base_url}/f5-cloud-libs/${fcl_tag}/dist/f5-cloud-libs.tar.gz")
dependencies+=("${base_url}/f5-cloud-libs-${cloud}/${fcl_cloud_tag}/dist/f5-cloud-libs-${cloud}.tar.gz")
dependencies+=("${base_url}/f5-cloud-libs/${fcl_tag}/dist/verifyHash")

for i in ${dependencies[@]} ; do
    log "Downloading dependency: $i"
    f=$(basename $i)
    $CURL -ksf --retry 5 --retry-delay 5 --retry-max-time 10 -o ${base_dir}/$f $i
done

## Verify
# MCP must be running first
mcp_running
base_config_available

if ! $skip_verify ; then
    verify_script="${base_dir}/verifyHash"
    if ! $TMSH load sys config merge file $verify_script ; then
        log "CLI verification script is not valid: $verify_script"
        exit 1
    fi

    for i in ${dependencies[@]} ; do
        f=$(basename $i)
        if [[ $f != "verifyHash" ]] ; then
            log "Verifying dependency: $f"
            if ! $TMSH run cli script verifyHash "/config/cloud/$f" ; then
                log "Dependency is not valid: $f"
                exit 1
            fi
        fi
    done
else
    log "Warning: Skipping dependency verification"
fi

## Install
mkdir -p $base_dependency_dir
for i in ${dependencies[@]} ; do
    f=$(basename $i)
    log "Installing dependency: $f"
    if [[ $f == *".tar"* ]] ; then
        tar xfz ${base_dir}/${f} -C $base_dependency_dir
    fi
done

## Signal
touch "${base_dir}/cloudLibsReady"

### Provision Device ###
mkdir -p $base_log_dir
hostname=$($CURL -sf --retry 20 http://169.254.169.254/latest/meta-data/hostname)
host="localhost"
separator=";"

# Could use a generic --onboard|--network|etc for optional arguments
# instead, at least for now implement the additional abstraction

## Onboard
onboard_args=""
if [ -n "$license" ] ; then onboard_args+="--license ${license} " ; fi
if [ -n "$ntp" ] ; then onboard_args+="--ntp ${ntp} " ; fi
if [ -n "$timezone" ] ; then onboard_args+="--tz ${timezone} " ; fi
if [ -n "$license_pool" ] ; then 
    # Check for mulitiple license pools
    OIFS=$IFS
    IFS=",";
    licenseArray=($license_pool);
    for i in ${licenseArray[@]}; do
        flag=' --create-license-pool '
        cat_args="${cat_args}${flag}$i"
    done
    IFS=$OIFS;
    onboard_args+="${cat_args} " ; fi
if [ -n "$reg_key_pool" ] ; then onboard_args+="--create-reg-key-pool ${reg_key_pool} " ; fi
if [ -n "$data_interface" ] ; then onboard_args+="--dns $(get_net_info $data_interface ns) " ; fi
if [[ "$(get_version)" == "big-iq" ]] ; then onboard_args+="--set-master-key " ; fi
if [ -n "$usage_analytics" ] ; then
    o=$(jsonify $usage_analytics)
    # Obfuscate sensitive information
    cI=$(echo $(get_val "$o" cI) | sha512sum | cut -d " " -f 1)
    dI=$(echo $(get_val "$o" dI) | sha512sum | cut -d " " -f 1)
    metrics+="cloudName:$(get_val "$o" cN),region:$(get_val "$o" r),customerId:${cI}"
    metrics+=",deploymentId:${dI},licenseType:$(get_val "$o" lT),bigIpVersion:$(get_val "$o" bIV)"
    metrics+=",templateName:$(get_val "$o" tN),templateVersion:$(get_val "$o" tV) "
    send_analytics=$(get_val "$o" send)
    if [[ "${send_analytics,,}" == "yes" ]] ; then onboard_args+="--metrics $metrics " ; fi
fi

nohup $NODE "${base_dependency_dir}/f5-cloud-libs/scripts/onboard.js" --host $host --log-level $log_level \
    --output "${base_log_dir}/onboard.log" --signal ONBOARD_DONE --hostname $hostname $onboard_args &>> ${base_log_dir}/install.log < /dev/null &

# TODO: Race condition between onboard/network - Using auth token results in 403 "not authorized"
# if network call immediately follows onboard.  Use following placeholder until fixed in f5-cloud-libs
# adding --wait-for signal for network call.
# wait_time=15
# log "Waiting: $wait_time"
# sleep $wait_time

## Network
network_args=""
if [ -n "$data_interface" ] ; then network_args+="--default-gw $(get_net_info $data_interface gw) " ; fi
if [ -n "$vlan" ] ; then
    for i in $(echo $vlan | tr "$separator" ' ') ; do
        o=$(jsonify $i)
        network_args+="--vlan name:$(get_val "$o" n),nic:$(get_val "$o" nic) "
    done
fi
if [ -n "$self_ip" ] ; then
    for i in $(echo $self_ip | tr "$separator" ' ') ; do
        o=$(jsonify $i)
        gw=$(get_net_info $(get_val "$o" i) gw cidr)
        network_args+="--self-ip name:$(get_val "$o" n),address:$(get_val "$o" a)/${gw#*/},vlan:$(get_val "$o" v) "
    done
fi

nohup $NODE "${base_dependency_dir}/f5-cloud-libs/scripts/network.js" --host $host --log-level $log_level \
    --output "${base_log_dir}/network.log" --wait-for SLEEP_DONE --signal NETWORK_DONE $network_args &>> ${base_log_dir}/install.log < /dev/null &

# Adding a sleep between commands
echo $'#!/bin/bash\necho "$(date \'+%Y-%m-%dT%H:%M:%SZ\'):wait timer running for 30 seconds"\nsleep 30' > /config/cloud/sleep.sh && chmod +x /config/cloud/sleep.sh
nohup $NODE "${base_dependency_dir}/f5-cloud-libs/scripts/runScript.js" --file /config/cloud/sleep.sh --log-level $log_level \
    --output "${base_log_dir}/sleep.log" --wait-for ONBOARD_DONE --signal SLEEP_DONE &>> ${base_log_dir}/install.log < /dev/null &

### Finally ###
#install_log="${script_dir}/install.log"
#if [ -e "$install_log" ]; then
#    log "Copying installation log to $base_log_dir"
#    cp $install_log $base_log_dir
#fi