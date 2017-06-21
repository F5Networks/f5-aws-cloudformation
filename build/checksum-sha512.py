#!/usr/bin/python
# Import hashlib library (md5 method is part of it)
import os
import hashlib
checksums = ""
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
           checksums += str(temp) + '\n' + str(sh512_returned) + '\n'
f = open('../build/sha512_checksums.txt', 'w')
f.write( checksums )
f.close()
