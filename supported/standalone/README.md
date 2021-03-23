## Number of Network Interfaces
In many of our templates, you choose the number of network interfaces (NICs) you want your BIG-IP VE to include. Note that not all options are available for all templates. 

  - **1 NIC** <br>These templates deploy a BIG-IP VE with 1 network interface (NIC) for use in one-armed, simple network environment (the single NIC processes both management and data plane traffic).

  - **2 NIC** <br>
  These templates deploy a BIG-IP with 2 NICs for use in environments with a separate management network.

  - **3 NIC** <br>These templates deploy a BIG-IP with 3 NICs for use in environments having a traditional enterprise architecture with separate management, external, and internal networks.

  - **N NIC** <br>These templates deploy a BIG-IP with 3 or more NICs for use in environments with traditional enterprise architectures (separate management, external, and multiple internal tenant networks). <br>NOTE: In the cloud, the number of IP addresses and network interfaces an instance is allowed to have is dictated by the size of the cloud instance, so these can also be used to increase IP address capacity.

