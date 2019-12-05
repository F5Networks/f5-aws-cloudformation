#!/bin/bash

# NEED TO HAVE $LOCALDB_USERNAME & $LOCALDB_PASSWORD set in ENV to run 
# ex. LOCALDB_USERNAME=example LOCALDB_PASSWORD=mysecret bash /config/cloud/apm-local-db.sh

BACKUP_FILE="/var/apm/localdb/mysql_bkup.sql"
MYSQL_PW=`perl -MPassCrypt -nle 'print PassCrypt::decrypt_password($_)' /var/db/mysqlpw`
MYSQL="/usr/bin/mysql -uroot --password=${MYSQL_PW} --database=f5authdb"
SALT="$(openssl rand -base64 3)"
SHA1=$(printf "$LOCALDB_PASSWORD$SALT" | openssl dgst -binary -sha1 | sed 's#$#'"$SALT"'#' | base64);
PASSWORD_ENCRYPTED="{SSHA}$SHA1"
ADD_USER="INSERT INTO  auth_user (uid, uname, instance, password, user_groups, lockout_start, ttl ) VALUES ('100', '${LOCALDB_USERNAME}', '/Common/my_local_db', '${PASSWORD_ENCRYPTED}', '', '0', '0')"
${MYSQL} -e "${ADD_USER}"

# MYSQL_QUERY="SHOW tables;"
# MYSQL_QUERY2="SELECT * FROM auth_user;"
# MYSQL_QUERY3="SELECT * FROM auth_user_details;"
# ${MYSQL} -e "${MYSQL_QUERY}"
# ${MYSQL} -e "${MYSQL_QUERY2}"
# ${MYSQL} -e "${MYSQL_QUERY3}"