# BUILD

This directory contains files used to generate all the Cloudformation templates. It is really just for the maintainers of this project and not meant for end-users. It exists now as a useful reference of how to customize/update templates, track releases, etc. but may be removed one day.

## master_template.py

The master template, which uses [troposphere](https://github.com/cloudtools/troposphere) to generate all the Cloudformation templates.

## cloud-tools/image-finder/image_finder.py

helper script used to generate region maps in the templates. You provide it a version and it will generate the the various cache files (ex. cached-byol-region-map.json) used by master-template.py (vs run every time). Generally only run this when a new release comes out.<br>
flags include:<br>
-p, --bigip-version, help='Optionally provide BIG-IP Version to generate AMI Map for'<br>
-q, --bigiq-version, help='Optionally provide BIG-IQ Version to generate AMI Map for'<br>
-u, --profile, help='Optionally provide cli profile to use when querying images in US aws'<br>
-c, --china_profile, help='Optionally provide cli profile to use when querying images in china aws'<br>
-g, --gov_profile, help='Optionally provide cli login profile to use when querying images in us gov aws'<br>

Outputs:
- AMI Maps: A directory of BIG-IP version-specific directories containing separate byol/payg AMI maps that can be copied directly to the root of the v1 f5-aws-cloudformation project; individual map files can be copied to the build/ directory prior to running the master template generator script
- AMI Maps BIGIQ: A directory of BIG-IQ version-specific directories containing AMI maps
- AMI Maps Quickstart: A directory of BIG-IP version-specific directories containing combined byol/payg AMI maps that can be added to the v2 Quickstart templates

Requires Python 3.9+ and configuration and credential profiles be configured prior to running: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html<br>

Example credential and configuration files:<br>

 ~/.aws/config<br>
[default]
region = us-west-1

[profile china]
region = cn-northwest-1

[profile gov]
region = us-gov-west-1


~/.aws/credentials<br>
[default]
aws_access_key_id = <key>
aws_secret_access_key = <secret>

[china]
aws_access_key_id = <key>
aws_secret_access_key = <secret>

[gov]
aws_access_key_id = <key>
aws_secret_access_key = <secret>


## build.sh

a simple bash wrapper for running all the iterations from master-template.py.

The above two files may eventually be incorporated directly into the master_template.py.

## /files

the files directory contains files the templates reference or source.