# F5 iApp Migration

All v1 iApp templates have been deprecated and removed from F5 Cloudformation templates. This guide provides mappings between the f5.service_discovery and f5.cloud_logger iApp templates and example declarations that can be used with F5 Application Services 3 Extension and F5 Telemetry Services Extension.

## Service Discovery iApp

```bash
tmsh list sys application service sd
```

```tcl
sys application service sd.app/sd {
    device-group none
    inherited-devicegroup true
    inherited-traffic-group true
    template f5.service_discovery
    traffic-group traffic-group-1
    variables {
        basic__advanced {
            value no
        }
        basic__display_help {
            value hide
        }
        cloud__aws_bigip_in_ec2 {
            value yes
        }
        cloud__aws_external_id {
            value <externalid>
        }
        cloud__aws_region {
            value <region>
        }
        cloud__aws_role_arn {
            value <rolename>
        }
        cloud__aws_use_role {
            value yes
        }
        cloud__cloud_provider {
            value aws
        }
        monitor__frequency {
            value <monitor_frequency>
        }
        monitor__http_method {
            value <http_method>
        }
        monitor__http_version {
            value <http_version>
        }
        monitor__monitor {
            value "/#create_new#"
        }
        monitor__response { 
            value <monitor_response>
        }
        monitor__type {
            value <monitor_type>
        }
        monitor__uri {
            value <monitor_uri>
        }
        pool__interval {
            value <discovery_interval>
        }
        pool__member_conn_limit {
            value <connection_limit>
        }
        pool__member_port {
            value <member_port>
        }
        pool__pool_to_use {
            value "/#create_new#"
        }
        pool__public_private {
            value <ip_type>
        }
        pool__tag_key {
            value <tag_key>
        }
        pool__tag_value {
            value <tag_value>
        }
    }
}
```

### Example AS3 declaration - Creates dynamically populated pool based on AWS resource tags
To send this declaration to AS3, use the POST method to the URI https://<BIG-IP>/mgmt/shared/appsvcs/declare and put the declaration in the body of the post. A Postman collection for AS3 can be found on the f5-appsvcs-extension [releases page.](https://github.com/F5Networks/f5-appsvcs-extension/releases/)

```json
{
    "webPool": {
        "class": "Pool",
        "members": [
            {
                "servicePort": <member_port>,
                "addressDiscovery": "aws",
                "updateInterval": <discovery_interval>,
                "tagKey": "<tag_key>",
                "tagValue": "<tag_value>",
                "addressRealm": "<ip_type>",
                "region": "<region>",
                "externalId": "<externalid>",
                "roleARN": "<rolename>"
            }
        ],
        "monitors": [
            { "use": "httpMonitor" }
        ]
    },
    "httpMonitor": {
        "class": "Monitor",
        "label": "http monitor",
        "monitorType": "<monitor_type>",
        "send": "<http_method> <monitor_uri> <http_version>",
        "receive": "<monitor_response>",
        "interval": <monitor_frequency>,
        "connectionLimit": <connection_limit>
    }
}
```


## Cloud Logger iApp

```bash
tmsh list sys application service logger
```

```tcl
sys application service s3_logger.app/s3_logger {
    device-group none
    inherited-devicegroup true
    inherited-traffic-group true
    lists {
        logging_config__ltm_req_log_options {
            value { CLIENT_IP SERVER_IP HTTP_METHOD HTTP_URI VIRTUAL_NAME }
        }
    }
    template f5.cloud_logger.v1.0.0
    traffic-group traffic-group-1
    variables {
        analytics_config__access_key {
            value <accesskey>
        }
        analytics_config__analytics_solution {
            value aws_s3
        }
        analytics_config__aws_region {
            value <region>
        }
        analytics_config__s3_bucket_name {
            value <bucketname>
        }
        analytics_config__secret_key {
            encrypted yes
            value <secretkey>
        }
        basic__advanced {
            value no
        }
        basic__help {
            value hide
        }
        internal_config__hostname {
            value custom
        }
        internal_config__mgmt_hostname {
            value <mgmt_hostname>
        }
        internal_config__mgmt_port {
            value <mgmt_port>
        }
        internal_config__port {
            value custom
        }
        logging_config__ltm_req_log_choice {
            value yes
        }
    }
}

sys application service cloudwatch_logger.app/cloudwatch_logger {
    device-group none
    inherited-devicegroup true
    inherited-traffic-group true
    lists {
        logging_config__ltm_req_log_options {
            value { CLIENT_IP SERVER_IP HTTP_METHOD HTTP_URI VIRTUAL_NAME }
        }
    }
    template f5.cloud_logger.v1.0.0
    traffic-group traffic-group-1
    variables {
        analytics_config__access_key {
            value <accesskey>
        }
        analytics_config__analytics_solution {
            value aws_cw
        }
        analytics_config__aws_region {
            value <region>
        }
        analytics_config__log_group_name {
            value <stream>
        }
        analytics_config__log_stream_name {
            value <group>
        }
        analytics_config__secret_key {
            encrypted yes
            value <secretkey>
        }
        basic__advanced {
            value no
        }
        basic__help {
            value hide
        }
        internal_config__hostname {
            value custom
        }
        internal_config__mgmt_hostname {
            value <mgmt_hostname>
        }
        internal_config__mgmt_port {
            value <mgmt_port>
        }
        internal_config__port {
            value custom
        }
        logging_config__ltm_req_log_choice {
            value yes
        }
    }
}
```

### Example TS declaration
To send this declaration to Telemetry Streaming, use the POST method to the URI https://<BIG-IP>/mgmt/telemetry/declare and put the declaration in the body of the post. A Postman collection for TS can be found on the f5-telemetry-streaming [releases page.](https://github.com/F5Networks/f5-telemetry-streaming/releases/)

```json
{
    "class": "Telemetry",
    "My_System": {
        "class": "Telemetry_System",
        "host": "<mgmt_hostname>",
        "port": <mgmt_port>,
        "systemPoller": {
            "interval": 60
        }
    },
    "My_Listener": {
        "class": "Telemetry_Listener",
        "port": 6514
    },
    "My_S3_Consumer": {
        "class": "Telemetry_Consumer",
        "type": "AWS_S3",
        "region": "<region>",
        "bucket": "<bucketname>",
        "username": "<accesskey>",
        "passphrase": {
            "cipherText": "<secretkey>"
        }
    },
    "My_Cloudwatch_Consumer": {
        "class": "Telemetry_Consumer",
        "type": "AWS_CloudWatch",
        "region": "<region>",
        "logGroup": "<group>",
        "logStream": "<stream>",
        "username": "<accesskey>",
        "passphrase": {
            "cipherText": "<secretkey>"
        }
    }
}
```