## Stack Type
For each of the standalone templates, you must choose the type of stack into which you want to deploy the BIG-IP VE. See the individual README files for exact requirements.  Note that not all options are available for all templates. 


  - **Existing Stack** <br> These templates deploy into an existing cloud network.  This means that all of the cloud networking infrastructure must be available prior to launching the template.

  - **Production Stack** <br>Production stack templates also require the cloud networking infrastructure to be in place, however these templates do not create or attach a public IP address/NAT (there is never a public IP address assigned to the Management IP address). As BIG-IP VEs need access to the internet to access Cloud API services and download files for onboarding, these deployments assume Internet access is provided via another Public NAT service, Firewall, etc.  In most cases, there is no public IP assigned to the IP addresses on the external interfaces (Virtual Servers, Self IP addresses, etc).