#!/usr/bin/python
# Import hashlib library (md5 method is part of it)
import os
import hashlib
checksums = ""
type = ""
module = ""
nics = ""
license = ""
ha = ""
for dirpath,subdirs,files in os.walk(r'../supported'):
    for file in files:
        if file.endswith('.template'):
            temp = os.path.join(dirpath, file)
            with open(temp, 'rb') as file_to_check:
                # read contents of the file
                data = file_to_check.read()
                # pipe contents of the file through
                sh512_returned = hashlib.sha512(data).hexdigest()
            # compare original MD5 with freshly calculated
            if 'across' in file:
                ha = " - Across AZs"
            elif 'same' in file:
                ha = " - Same Azs"
            else:
                ha = ""
            if 'byol' in file:
                license = " - BYOL"
            elif 'hourly' in file:
                license = " - HOURLY"
            else:
                license = " - BIGIQ"
            if '1nic' in file:
                nics = "1 NIC"
            elif '2nic' in file:
                nics = "2 NIC"
            elif '3nic' in file:
                nics = '3 NIC'
            else:
                nics = ""
            if 'autoscale' in file:
                type = "Auto Scale"
                if '1000' in file:
                    license = " - AWS Marketplace - 1000Mbps"
                elif '200' in file:
                    license = " - AWS Marketplace - 200Mbps"
                elif '25' in file:
                    license = " - AWS Marketplace - 25Mbps"
                else:
                    license = ""
                if 'ltm' in file:
                    module = " LTM"
                else:
                    module = " WAF"
            elif 'cluster' in file:
                type = "Cluster"
                module =""
            else:
                type = "Standalone"
                module = ""
            checksums += '**'+ str(type) + str(module) + ':' + str(ha) + str(nics) + str(license) + '**(' + str(file) + ')\n\'' + str(sh512_returned) + '\'\n'
f = open('../build/sha512_checksums.txt', 'w')
f.write( checksums )
f.close()