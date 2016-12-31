F5 AWS CloudFormation templates
===============================

|Slack Status|

Introduction
------------

Welcome to the GitHub repository for F5's CloudFormation templates for
F5 AWS deployments. All of the templates in this repository have been
developed by F5 Networks engineers. Across all branches in this
repository, there are two directories: *f5\_supported* and
*experimental*

    - f5\_supported\

    The f5\_supported directory contains CloudFormation templates that have been created and fully tested by F5 Networks. These templates are fully supported by F5, meaning you can get assistance if necesary from F5 Technical Support via your typical methods.

    -  experimental\

    The expermimental directory also contains CloudFormation templates that have been created by F5 Networks. However, these templates have not completed full testing and are subject to change. F5 Networks does not offer technical support for templates in the experimental diretory, so use these templates with caution.

Template information
--------------------

Descriptions for each template are contained at the top of each template in the *Description* key. For additional information, including how the templates are generated, and assistance in deploying a template, see the individual README file in the build/ directory.

List of F5 CloudFormation templates for AWS deployments
-------------------------------------------------------

The following is a list of the current F5 Supported CloudFormation templates:

- `Standalone BIG-IP VE - Single NIC <https://github.com/F5Networks/f5-aws-cloudformation/tree/master/experimental/standalone/1nic>`_

    - Hourly

        .. image:: https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png
            :target: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-1nic-bigip.template

    - BYOL

        .. image:: https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png
            :target: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-1nic-bigip.template

- `Standalone BIG-IP VE - 2 NICs <https://github.com/F5Networks/f5-aws-cloudformation/tree/master/experimental/standalone/2nic>`_

    - Hourly

        .. image:: https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png
            :target: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-2nic-bigip.template

    - BYOL

        .. image:: https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png
            :target: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-2nic-bigip.template

-  `Clustered BIG-IP VE - 2 NICs <https://github.com/F5Networks/f5-aws-cloudformation/tree/master/experimental/cluster/2nic>`_

    -  Hourly

        .. image:: https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png
            :target: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-Across-Az-Cluster-2nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-across-az-cluster-hourly-2nic-bigip.template

    - BYOL

        .. image:: https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png
            :target: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-Across-Az-Cluster-2nic-byol&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-across-az-cluster-byol-2nic-bigip.template


- `Autoscaling the BIG-IP Web Application Firewall in AWS <https://github.com/F5Networks/f5-aws-cloudformation/tree/master/experimental/solutions/autoscale>`_


.. toctree::
    :caption: F5 Supported Template Library
    :maxdepth: 1
    :glob:

    README <supported/README>
    supported/*


.. toctree::
    :caption: Experimental Template Library
    :maxdepth: 1
    :glob:

    README <deploy/README>
    experimental/solutions/autoscale/*
    experimental/standalone/1nic/*
    experimental/standalone/2nic/*
    experimental/cluster/2nic/*



Copyright
---------

Copyright 2014-2016 F5 Networks Inc.

Support
-------

See `Support <https://github.com/F5Networks/f5-aws-cloudformation/blob/master/SUPPORT>`_.

License
-------

Apache V2.0
```````````

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
except in compliance with the License. You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and
limitations under the License.

Contributor License Agreement
`````````````````````````````

Individuals or business entities who contribute to this project must
have completed and submitted the `F5 Contributor License
Agreement <http://f5-openstack-docs.readthedocs.org/en/latest/cla_landing.html>`_
to Openstack_CLA@f5.com prior to their code submission being included
in this project.

.. |Slack Status| image:: https://f5cloudsolutions.herokuapp.com/badge.svg
   :target: https://f5cloudsolutions.herokuapp.com
