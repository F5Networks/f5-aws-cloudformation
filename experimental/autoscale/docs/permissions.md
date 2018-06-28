AWS Permissions
===============

To use this solution, you must have access to the following resources.

  - S3 Bucket<br>
    The S3 bucket acts as persistent storage for the cluster database. It contains:
      - *Records*<br>
      Records, named for the instance ID contain metadata for each instance. For example  ```{"privateIp":"10.0.11.190","mgmtIp":"10.0.11.190","hostname":"ip-10-0-11-190.ec2.internal","isMaster":true}```<br>
      Newly launched instances query this bucket for an existing cluster and use information found here to join the cluster. If it it the first member launched in the group, it creates a record with "is Master":true. Otherwise, it enters itself as "isMaster":false.
      - *Auto-generated credentials for clustering*<br>
      The S3 bucket also contains auto-generated credentials for clustering, for example 
      ```
      {"username":"custom-admin","password":"J#\"?}$YDgb8c=L>>P8#FzmS$WB9EYzx3<"}
      ```
  - IAM Role<br>
  The IAM Role is used to create Instance Profile. The instance profile allows the auto scaled BIG-IP VE instances to access / update the S3 Bucket, query the Auto Scale Group, and upload metrics to Cloudwatch.
  
  - SNS Topic<br>
  The SNS topic is used to notify the admin via email of Scale Up / Down events.
  - Cloudwatch Alarms<br>
  These alarms are used to trigger scale Up / Down events.
  
  - Auto Scaling Group<br>
  By default, the number of auto scaled instances is set to 1 and the Max is set to 8. We recommend you launch the solution with 1 instance to start. 

