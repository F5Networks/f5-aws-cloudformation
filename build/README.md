# BUILD

This directory contains files used to generate all the Cloudformation templates. It is really just for the maintainers of this project and not meant for end-users. It exists now as a useful reference of how to customize/update templates, track releases, etc. but may be removed one day.

### master_template.py 

the main troposphere script

https://github.com/cloudtools/troposphere

used to generate all the Cloudformation templates.


### image_finder.py

helper script used to generate region maps in the templates. You provide it a version and it will generate the the various cache files (ex. cached-byol-region-map.json) used by master-template.py (vs run every time). Generally only run this when a new release comes out. 

### build.sh

a simple bash wrapper for running all the iterations from master-template.py. 

The above two files may eventually be incorporated directly into the master_template.py.


### /files

the files directory contains files the templates reference or source. 