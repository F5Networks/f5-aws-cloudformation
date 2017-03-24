Log in to BIG-IP VE
===================

After BIG-IP VE is initialized, if you want to access the BIG-IP web-based Configuration utility, you must first SSH to the instance and set a password for the admin user. This user can log in to the Configuration utility.

  - Find the IP address of the BIG-IP VE<br> Go to the Instances tab of the Auto Scaling Group created by the template. (From the AWS console, click **EC2 > Auto Scaling > Auto Scaling Groups > Instances tab > Instance ID**)

  - SSH to the instance IP or Public IP address by using the following syntax:<br>``` >ssh -i ~/.ssh/<YOUR-PRIVATE-SSH-KEY-HERE> admin@<INSTANCE IP> ```
  
  - Create a custom admin user by using the following syntax:<br> ``` #tmsh create auth user my-custom-admin partition-access add { all-partitions { role admin } } prompt-for-password```
 
Log in to the Configuration utility by using this URL: **https://(IP Address of the instance):8443**

You can now configure the BIG-IP VE as needed. See the BIG-IP documentation for details (https://support.f5.com/csp/tech-documents).
