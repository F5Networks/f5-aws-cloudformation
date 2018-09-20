## Traffic Distribution Type
For failover templates, you choose the way you want traffic distribution and failover to occur. Note that not all options are available for all templates. 


  - **via-api** <br> In Failover via API (via-api) templates, failover is implemented by making API calls (vs. Gratuitous ARP) to read and update resources such as IP mappings (EIPs/NATs), LB/Forwarding Rules, and so on. 

  - **via-lb** <br> In failover via load balancer (via-lb) templates, an upstream load balancing service distributes traffic and determines which instances should receive traffic.

  - **via-nlb** <br> In failover via network load balancer (via-nlb) templates, an upstream network load balancer distributes traffic and determines which instances should receive traffic = Type L4.

  - **via-alb** <br> In Failover via application load balancer (via-alb) templates, an upstream application load balancer distributes traffic and determines which instances should receive traffic = Type L7.