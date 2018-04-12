# /usr/bin/python env

import time
import re
import boto3
import boto
import boto.ec2
import collections
import json
from optparse import OptionParser
import os

class imageFinder(object):
    def __init__(self):
        self.imageList = {}
        pass

    def searchitem(self, keys, name):
        value = None
        for k in keys:
            match = re.search('({})'.format(k), name)
            if match:
                value = match.group(1)
                break
        return value

    def getImagesForRegion(self, region, filters=[{'Name':'name', 'Values':['F5*']}]):
        """
            Takes the name of an amazon region and retrieves a list of all
            images published for this region, with a specified image filter
            Returns a formatted object
        """

        # Use boto3 with list and filter
        ec2 = boto3.resource('ec2', region_name=region)
        images = list(ec2.images.filter(Filters=filters).all())

        # dimensions
        packages = ['good', 'better', 'best']
        throughputs = ['[0-9]+gbps', '[0-9]+mbps']
        licenses = ['byol', 'hourly']
        versions = [
            # Example matches: 13.1.0.2.0.0.6, 13.0.0.2.0.1671-hf1, 12.1.2.1.0.271, 12.1.3.3-0.0.1
            '[0-9.]{6,}[-]*[0-9.]+[-hf]*[0-9]*'
        ]

        structured = []
        for i in images:
            # Only return public images
            if i.public is not True:
                continue
            try:
                image_name = i.name.lower()
                image_id = i.id.lower()

                license = self.searchitem(licenses, image_name)
                version = self.searchitem(versions, image_name)
                throughput = self.searchitem(throughputs, image_name)
                package = self.searchitem(packages, image_name)

                structured.append({
                    'name': image_name,
                    'id': image_id,
                    'version': version,
                    'package': package,
                    'license': license,
                    'throughput': str(throughput)})

            except Exception, e:
                print 'Failed processing image "{}". Will not be added to index. Error was {}'.format(image_name, e)

        return structured

    def getBigipRegionMap(self, marketplace, bandwidth, **kwargs):
        """
            Returns region map
            Formats a return object
            BYOL:
             "ap-northeast-1": {
                "Best": "ami-0659ab67",
                "Better": "ami-ed5eac8c",
                "Good": "ami-1859ab79"
              },
            Hourly:
              "us-east-1": {
                "Good-25Mbps": "ami-xxxxxxxx",
                "Better-25Mbps": "ami-xxxxxxxx",
                "Best-25Mbps": "ami-3aab2c2d",
                "Good-200Mbps": "ami-xxxxxxxx",
                "Better-200Mbps": "ami-xxxxxxxx",
                "Best-200Mbps": "ami-93ac2b84",
                "Good-1000Mbps": "ami-xxxxxxxx",
                "Better-1000Mbps": "ami-xxxxxxxx",
                "Best-1000Mbps": "ami-c9ac2bde"
              },
        """
        BigipRegionMap = {}
        for region in kwargs['regions']:
            # only get image list for specific region once
            if region not in self.imageList:
                images = self.getImagesForRegion(region=region)
                self.imageList[region] = images
            else:
                images = self.imageList[region]

            if kwargs['license'] is not None:
                images = [i for i in images if i['license'] == kwargs['license']]
            if kwargs['version'] is not None:
                images = [i for i in images if i['version'] is not None and
                          re.match('^({})'.format(kwargs['version']), i['version'])]
            package_dict = {}
            mg25 = {}
            mg200 = {}
            mg1000 = {}
            mg5000 = {}
            mbr25 = {}
            mbr200 = {}
            mbr1000 = {}
            mbr5000 = {}
            mbt25 = {}
            mbt200 = {}
            mbt1000 = {}
            mbt5000 = {}

            for image in images:
                if image['license'] == "byol":
                    if image['package'] == "good":
                        package_dict['Good'] = image['id']
                    elif image['package'] == "better":
                        package_dict['Better'] = image['id']
                    elif image['package'] == "best":
                        package_dict['Best'] = image['id']
                elif image['license'] == "hourly":
                    if image['package'] == "good":
                        if image['throughput'] == "25mbps":
                            package_dict['Good25Mbps'] = image['id']
                            mg25['Good25Mbps'] = image['id']
                        if image['throughput'] == "200mbps":
                            package_dict['Good200Mbps'] = image['id']
                            mg200['Good200Mbps'] = image['id']
                        if image['throughput'] == "1gbps":
                            package_dict['Good1000Mbps'] = image['id']
                            mg1000['Good1000Mbps'] = image['id']
                        if image['throughput'] == "5gbps":
                            package_dict['Good5000Mbps'] = image['id']
                            mg5000['Good5000Mbps'] = image['id']
                    elif image['package'] == "better":
                        if image['throughput'] == "25mbps":
                            package_dict['Better25Mbps'] = image['id']
                            mbr25['Better25Mbps'] = image['id']
                        if image['throughput'] == "200mbps":
                            package_dict['Better200Mbps'] = image['id']
                            mbr200['Better200Mbps'] = image['id']
                        if image['throughput'] == "1gbps":
                            package_dict['Better1000Mbps'] = image['id']
                            mbr1000['Better1000Mbps'] = image['id']
                        if image['throughput'] == "5gbps":
                            package_dict['Better5000Mbps'] = image['id']
                            mbr5000['Better5000Mbps'] = image['id']
                    elif image['package'] == "best":
                        if image['throughput'] == "25mbps":
                            package_dict['Best25Mbps'] = image['id']
                            mbt25['Best25Mbps'] = image['id']
                        if image['throughput'] == "200mbps":
                            package_dict['Best200Mbps'] = image['id']
                            mbt200['Best200Mbps'] = image['id']
                        if image['throughput'] == "1gbps":
                            package_dict['Best1000Mbps'] = image['id']
                            mbt1000['Best1000Mbps'] = image['id']
                        if image['throughput'] == "5gbps":
                            package_dict['Best5000Mbps'] = image['id']
                            mbt5000['Best5000Mbps'] = image['id']
            if marketplace == "good" and bandwidth == "25":
                BigipRegionMap[region] = mg25
            if marketplace == "good" and bandwidth == "200":
                BigipRegionMap[region] = mg200
            if marketplace == "good" and bandwidth == "1000":
                BigipRegionMap[region] = mg1000
            if marketplace == "good" and bandwidth == "5000":
                BigipRegionMap[region] = mg5000
            if marketplace == "better" and bandwidth == "25":
                BigipRegionMap[region] = mbr25
            if marketplace == "better" and bandwidth == "200":
                BigipRegionMap[region] = mbr200
            if marketplace == "better" and bandwidth == "1000":
                BigipRegionMap[region] = mbr1000
            if marketplace == "better" and bandwidth == "5000":
                BigipRegionMap[region] = mbr5000
            if marketplace == "best" and bandwidth == "25":
                BigipRegionMap[region] = mbt25
            if marketplace == "best" and bandwidth == "200":
                BigipRegionMap[region] = mbt200
            if marketplace == "best" and bandwidth == "1000":
                BigipRegionMap[region] = mbt1000
            if marketplace == "best" and bandwidth == "5000":
                BigipRegionMap[region] = mbt5000
            if marketplace == "no" and bandwidth == "all":
                BigipRegionMap[region] = package_dict
        return BigipRegionMap

    def getWebRegionMap(self, **kwargs):
        """
            Returns formatted region map
        """
        WebRegionMap = {}

        for region in kwargs['regions']:
            images = self.getImagesForRegion(region=region, filters=[{'Name':'name', 'Values':[kwargs['name_string']]}])
            WebRegionMap[region] = {'AMI': images[0]['id']}
        return WebRegionMap

def main():
    print "Script started "  + time.strftime("%H:%M:%S")

    ### BEGIN MAPPINGS
    regions = [
        'ap-south-1',
        'ap-southeast-1',
        'ap-southeast-2',
        'ap-northeast-1',
        'ap-northeast-2',
        'ca-central-1',
        'eu-west-1',
        'eu-west-2',
        'eu-central-1',
        'sa-east-1',
        'us-west-1',
        'us-west-2',
        'us-east-1',
        'us-east-2'
    ]
    version = "13.1.0.2.0.0.6"
    marketplace_version = version
    marketplace_run = True
    image_finder_obj = imageFinder()
    # Manually import gov region ami map for now
    gov_region = 'us-gov-west-1'
    gov_path_version = "13.1.0.2-0.0.6"
    with open('../AMI Maps/{}/cached-hourly-region-map-us-gov-west-1.json'.format(gov_path_version)) as json_file:
        gov_cloud_amis_hourly = json.load(json_file)[gov_region]
    with open('../AMI Maps/{}/cached-byol-region-map-us-gov-west-1.json'.format(gov_path_version)) as json_file:
        gov_cloud_amis_byol = json.load(json_file)[gov_region]

    ## Hourly Region Map Marketplace ##
    if marketplace_run:
        mp = {}
        mp["Good25Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="good", bandwidth="25", license="hourly", version=marketplace_version, regions=regions)
        mp["Good200Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="good", bandwidth="200", license="hourly", version=marketplace_version, regions=regions)
        mp["Good1000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="good", bandwidth="1000", license="hourly", version=marketplace_version, regions=regions)
        mp["Good5000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="good", bandwidth="5000", license="hourly", version=marketplace_version, regions=regions)
        mp["Better25Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="better", bandwidth="25", license="hourly", version=marketplace_version, regions=regions)
        mp["Better200Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="better", bandwidth="200", license="hourly", version=marketplace_version, regions=regions)
        mp["Better1000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="better", bandwidth="1000", license="hourly", version=marketplace_version, regions=regions)
        mp["Better5000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="better", bandwidth="5000", license="hourly", version=marketplace_version, regions=regions)
        mp["Best25Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="best", bandwidth="25", license="hourly", version=marketplace_version, regions=regions)
        mp["Best200Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="best", bandwidth="200", license="hourly", version=marketplace_version, regions=regions)
        mp["Best1000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="best", bandwidth="1000", license="hourly", version=marketplace_version, regions=regions)
        mp["Best5000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="best", bandwidth="5000", license="hourly", version=marketplace_version, regions=regions)

        # Add gov region to each mp key
        for key, value in mp.items():
            value[gov_region] = {key:gov_cloud_amis_hourly[key]}

        m_dict = {
            '../build/marketplace/cached-good25Mbps-region-map.json': mp["Good25Mbps"],
            '../build//marketplace/cached-good200Mbps-region-map.json': mp["Good200Mbps"],
            '../build//marketplace/cached-Good1000Mbps-region-map.json': mp["Good1000Mbps"],
            '../build//marketplace/cached-Good5000Mbps-region-map.json': mp["Good5000Mbps"],
            '../build//marketplace/cached-Better25Mbps-region-map.json': mp["Better25Mbps"],
            '../build//marketplace/cached-Better200Mbps-region-map.json': mp["Better200Mbps"],
            '../build//marketplace/cached-Better1000Mbps-region-map.json': mp["Better1000Mbps"],
            '../build//marketplace/cached-Better5000Mbps-region-map.json': mp["Better5000Mbps"],
            '../build//marketplace/cached-Best25Mbps-region-map.json': mp["Best25Mbps"],
            '../build//marketplace/cached-Best200Mbps-region-map.json': mp["Best200Mbps"],
            '../build//marketplace/cached-Best1000Mbps-region-map.json': mp["Best1000Mbps"],
            '../build//marketplace/cached-Best5000Mbps-region-map.json': mp["Best5000Mbps"]
        }
        # Dump marketplace maps to files
        for k in m_dict:
            with open(k, 'wb') as outfile:
                json.dump(m_dict[k], outfile, sort_keys=True, indent=2, ensure_ascii=False)

    ## Non-Marketplace Maps ##
    # Hourly Region Map:
    HourlyRegionMap = image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", license="hourly", version=version, regions=regions)
    HourlyRegionMap[gov_region] = gov_cloud_amis_hourly
    # BYOL Region Map:
    ByolRegionMap = image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", license="byol", version=version, regions=regions)
    ByolRegionMap[gov_region] = gov_cloud_amis_byol
    # BIG-IQ Region Map:
    BigiqRegionMap = image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", license="byol", version="5.1.0.0.0.631", regions=regions)

    m_dict = {
        'cached-hourly-region-map.json': HourlyRegionMap,
        'cached-byol-region-map.json': ByolRegionMap,
        'cached-bigiq-region-map.json': BigiqRegionMap
    }
    # Dump maps to files
    for k in m_dict:
        with open(k, 'wb') as outfile:
            json.dump(m_dict[k], outfile, sort_keys=True, indent=2, ensure_ascii=False)

    # Webserver Region Map:
    # bitnami-lampstack-5.5.13-0-dev-linux-ubuntu-12.04.4-x86_64-ebs-ami-a9f58699-3-ami-9dcd82ad
    webserver_version = "F5 Demo App v0.0.1"
    WebserverRegionMap = image_finder_obj.getWebRegionMap(name_string=webserver_version, regions=regions)

    with open('cached-webserver-region-map.json', 'wb') as outfile:
        json.dump(WebserverRegionMap, outfile, sort_keys=True, indent=2, ensure_ascii=False)

    print "Script ended "  + time.strftime("%H:%M:%S")

if __name__ == "__main__":
    main()