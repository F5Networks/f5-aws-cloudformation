# Cloud factory top-level Makefile

CUR_DIR := $(cwd)
PROJECT_DIR := .
LINK_CHECK_DIR := cloud-tools/link_checker
CRAWLER_DIR := cloud-tools/crawler
SMOKE_TEST_DIR := cloud-tools/linters
PARSER_DIR := cloud-tools/parameter-parser
DIFF_VAR :=`diff ${PARSER_DIR}/parameters_diff_expected.yaml ${PARSER_DIR}/parameters_diff.yaml`
DIFF_VAR_OUTPUTS :=`diff ${PARSER_DIR}/outputs_diff_expected.yaml ${PARSER_DIR}/outputs_diff.yaml`


.PHONY: help
help:
	@echo "Check MakeFile"

link_check:
	echo "Running link checker against all markdown files";
	cd ${LINK_CHECK_DIR} && npm install && cd ${CUR_DIR};
	${LINK_CHECK_DIR}/link_checker.sh ${PROJECT_DIR} "cloud-tools node_modules archived" link_checker_config.json

link_check_release:
	echo "Running link checker against all markdown files";
	cd ${LINK_CHECK_DIR} && npm install && cd ${CUR_DIR};
	${LINK_CHECK_DIR}/link_checker.sh ${PROJECT_DIR} "cloud-tools node_modules archived" link_checker_config_release.json

run_crawler:
	echo "Running crawler against cloud factory artifacts";
	cd ${CRAWLER_DIR} && bash ./run_crawler.sh && cd ${CUR_DIR};
	echo "Updated file: ${CRAWLER_DIR}/data.json"

run_smoke_tests: run_crawler
	echo "Running smoke tests";
	pip install -r cloud-tools/linters/requirements.txt;
	pytest ${SMOKE_TEST_DIR} --full-trace -v;
