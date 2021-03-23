## Auto Scale Front-End Options
Our auto scale templates have the following options for how traffic is distributed to the BIG-IP VE instances.

  - **via-dns** <br>In Auto Scale via DNS (via-dns) templates, an upstream DNS device (such as BIG-IP DNS) distributes traffic and determines which instances should receive traffic. This Solution updates DNS records on BIG-IP DNS or Cloud Service.

  - **via-lb** <br> In Auto Scale via load balancer (via-lb) templates, an upstream load balancing service distributes traffic and determines which instances should receive traffic.