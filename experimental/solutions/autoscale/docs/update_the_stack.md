Update the stack
================

Certain elements of this deployment can be updated with the CloudFormation stack itself. This is referred to as *updating the Stack*. For instance, anything that causes the Auto Scale Launch Configuration to update, like changing the AMI IDs (to upgrade from one BIG-IP version to another), instance sizes, scaling thresholds, and many others, requires updating the stack. 

Clustering is only done within a Launch Configuration ID basis, so any changes that result in a new Launch Configuration require the following procedure.

  1.  Backup your BIG-IP configuration (ideally the cluster primary, but must be run on an instance created from the original stack configuration) by creating a [UCS](https://support.f5.com/csp/article/K13132) archive and store it in a secure location (such as the S3 bucket created by this solution):<br> ```# tmsh save /sys ucs /var/tmp/original.ucs```
  
  2.  On AWS, take note of the Instance IDs in your existing Auto Scaling Group. This is optional, but helps to differentiate the new Instances from the existing ones after you update the stack in step 3. To view the existing Instance IDs, click Auto Scaling Groups and then click the Auto Scale group that was created. This name uses the syntax *(deployment-name)-bigip-BigipAutoscaleGroup-("id")*, such as **my-deployment-autoscale-bigip-BigipAutoscaleGroup-1V6U160O0Q2UM**.  Click the Instances tab, and then note the Instance IDs and the Launch Configuration Name.  

  3. Update the Stack in AWS (click **CloudFormation > Action > Update Stack**).  

  4. If you have modified the BIG-IP configuration from the original launch configuration, remove the first instance that launches from the new Launch Configuration. This is only required if you have manually modified the BIG-IP configuration.<br> **Important** After you click Update Stack, you have 60 minutes to upload the UCS archive to the new machine before the old one is deleted. Use the following procedure.

     - Identify the new instance<br>
     Click **Auto Scaling Groups** and then click the new Auto Scale group that was just created. Click the Instances tab, and then note the Instance ID with new Launch Configuration Name.  
  
     -  Temporarily remove the instance from the ELB by clicking **Load Balancers** and then the name of the ELB you used for this deployment. Click the Instances tab,  and then click the newly created instance with the new Instance ID, and then click **Remove from Load Balancer**
     -  After performing steps 5 and 6, you add the instance back in step 7.

  5. From the BIG-IP, upload the UCS to the new instance created by the updated stack configuration and run the UCS Update Utility using the following command:<br> ```# python /config/cloud/aws/node_modules/f5-cloud-libs/scripts/updateAutoScaleUcs --original-ucs original.ucs --updated-ucs updated.ucs```

  6. On the new instance, load the updated UCS:<br> ```tmsh load /sys ucs /shared/tmp/updated.ucs no-license```

  7. If you removed the instance from the load balancer in step 4, you must add new instance back to the ELB.<br>
  From the AWS console, click **Load Balancers > Name of your ELB > Instances tab > Edit Instances** and then click the button for the new instance to add it back to ELB and click Save.
