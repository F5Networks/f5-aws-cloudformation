#!make
current_dir := $(shell pwd)
# Create an environmental script and refernce it here (.gitignore set to ignore env.sh)
# example: export GOOGLE_PROJECT_ID=my_project_id
# option 1 all env variables refrenced in rules need be defined in env.sh
# option 2 have env vars set prior to running make rule
include env.sh
.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo " 'gce_standalone' using dewdrop docker image:stable, runs standalone test defined in env varable GCP_TEMPLATE_TEST_URL/GCP_TEMPLATE_TEST_PARMS"
	@echo " 'gce_failover_api' using dewdrop docker image:stable, runs standalone test defined in env varable GCP_TEMPLATE_TEST_URL_API/GCP_TEMPLATE_TEST_PARAMS_API"
	@echo " 'gce_failover_lb' using dewdrop docker image:stable, runs standalone test defined in env varable GCP_TEMPLATE_TEST_URL_LB/GCP_TEMPLATE_TEST_PARAMS_LB"

.PHONY: gce
env:
	env
# AWS V1
aws_standalone:
	docker run -it -v ${current_dir}:/automated-test-scripts -v ${current_dir}/../supported:/supported -e SSH_KEY="${DEWPT_PRIVATE_KEY}" -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" -e STACK_TYPE="${STACK_TYPE}" -e TEMPLATE_URL="${AWS_TEMPLATE_TEST_URL}" -e TEMPLATE_PARAMETERS="${AWS_TEMPLATE_TEST_PARAMS}" artifactory.f5net.com/ecosystems-cloudsolutions-docker-dev/dewdrop:stable
aws_standalone_china:
	docker run -it -v ${current_dir}:/automated-test-scripts -v ${current_dir}:/../supported:/supported -e AWS_DEFAULT_REGION="${AWS_CHINA_DEFAULT_REGION}" -e SSH_KEY="${DEWPT_PRIVATE_KEY}" -e AWS_ACCESS_KEY_ID="${AWS_CHINA_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="${AWS_CHINA_SECRET_ACCESS_KEY}" -e STACK_TYPE="${STACK_TYPE}" -e TEMPLATE_URL="${AWS_TEMPLATE_TEST_URL_CHINA}" -e TEMPLATE_PARAMETERS="${AWS_TEMPLATE_TEST_PARAMS_CHINA}" artifactory.f5net.com/ecosystems-cloudsolutions-docker-dev/dewdrop:stable
aws_failover:
	docker run -it -v ${current_dir}:/automated-test-scripts -v ${current_dir}:/../supported:/supported -e SSH_KEY="${DEWPT_PRIVATE_KEY}" -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" -e STACK_TYPE="${STACK_TYPE}" -e TEMPLATE_URL="${AWS_TEMPLATE_TEST_URL_FAILOVER}" -e TEMPLATE_PARAMETERS="${AWS_TEMPLATE_TEST_PARAMS_FAILOVER}" artifactory.f5net.com/ecosystems-cloudsolutions-docker-dev/dewdrop:stable
aws_failover_china:
	docker run -it -v ${current_dir}:/automated-test-scripts -v ${current_dir}:/../supported:/supported -e AWS_DEFAULT_REGION="${AWS_CHINA_DEFAULT_REGION}" -e SSH_KEY="${DEWPT_PRIVATE_KEY}" -e AWS_ACCESS_KEY_ID="${AWS_CHINA_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="${AWS_CHINA_SECRET_ACCESS_KEY}" -e STACK_TYPE="${STACK_TYPE}" -e TEMPLATE_URL="${AWS_TEMPLATE_TEST_URL_FAILOVER_CHINA}" -e TEMPLATE_PARAMETERS="${AWS_TEMPLATE_TEST_PARAMS_FAILOVER_CHINA}" artifactory.f5net.com/ecosystems-cloudsolutions-docker-dev/dewdrop:stable
aws_autoscale:
	docker run -it -v ${current_dir}:/automated-test-scripts -v ${current_dir}:/../supported:/supported -e SSH_KEY="${DEWPT_PRIVATE_KEY}" -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" -e STACK_TYPE="${STACK_TYPE}" -e TEMPLATE_URL="${AWS_TEMPLATE_TEST_URL_AUTOSCALE}" -e TEMPLATE_PARAMETERS="${AWS_TEMPLATE_TEST_PARAMS_AUTOSCALE}" artifactory.f5net.com/ecosystems-cloudsolutions-docker-dev/dewdrop:stable
aws_autoscale2_bigiq:
	docker run -it -v ${current_dir}:/automated-test-scripts -v ${current_dir}:/../supported:/supported -e SSH_KEY="${DEWPT_PRIVATE_KEY}" -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" -e STACK_TYPE="${STACK_TYPE}" -e TEMPLATE_URL="${AWS_TEMPLATE_TEST_URL_AUTOSCALE_V2_BIGIQ}" -e TEMPLATE_PARAMETERS="${AWS_TEMPLATE_TEST_PARAMS_AUTOSCALE_V2_BIGIQ}" artifactory.f5net.com/ecosystems-cloudsolutions-docker-dev/dewdrop:stable
