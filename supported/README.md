## Template Types
F5 Networks has created templates grouped into the following categories.

  - **Standalone** <br>These templates deploy an individual BIG-IP VE. Standalone BIG-IP VEs are primarily used for Dev/Test/Staging, Replacing/Upgrading individual instances in traditional failover clusters (see Failover), and/or scaling out (for deployments where the configuration is managed remotely as opposed to relying on the synchronization functionality (config-sync)  of the cluster).

  - **Failover** <br> These templates deploy more than one BIG-IP VE in a <a href="http://www.f5.com/pdf/white-papers/scalen-elastic-infrastructure-white-paper.pdf">ScaleN cluster</a> (a traditional High Availability Pair in most cases). Failover clusters are primarily used to replicate traditional Active/Standby BIG-IP deployments. <br>  
  In these deployments, an individual BIG-IP VE in the cluster owns (or is Active for) a particular IP address. For example, the BIG-IP VEs will fail over services from one instance to another by remapping IP addresses, routes, etc. based on Active/Standby status. In some solutions, failover is implemented via API (API calls to the cloud platform vs. network protocols like Gratuitous ARP, route updates, and so on). In other solutions, failover is implemented via an upstream service (like a native load balancer) which will only send traffic to the Active Instance for that service based on a health monitor. For more information, see the failover README files. In all cases, a single BIG-IP VE will be active for a single IP address.   <br>  
  These deployments also have a similar BIG-IP lifecycle (where upgrades are done in place via live installs) and instances are replaced/upgraded by restoring the BIG-IP VE backup file (called a UCS).<br>  
  Failover templates include same-net, where instances in the cluster are deployed on the same subnet (L3), and across-net where instances in cluster are deployed across L3 subnets.  




  - **Autoscale** <br> These templates deploy a group of BIG-IP VEs that scale in and out based on thresholds you configure in the template. The BIG-IP VEs are all Active and are primarily used to scale out an individual L7 service on a single wildcard virtual (although you can add additional services using ports).  <br>  
  This type of deployment relies on upstream service to distribute traffic like DNS/GSLB or a platform's built-in load balancer.<br>  
  These solutions often leverage some built-in functionality (like auto-backup to cloud persistent storage) and cloud native services (such as a template's Rolling Upgrade). 