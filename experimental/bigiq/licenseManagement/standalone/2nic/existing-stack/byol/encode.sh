#!/bin/bash

# Base 64 encode to temporary file, which will be included in template
cat init.sh | base64 -w 0 > initEncoded