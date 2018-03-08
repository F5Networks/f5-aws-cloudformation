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

class BigIpImageFinder(object):
    def __init__(self):
        pass

    def searchitem(self, keys, name):
        value = None
        for k in keys:
            match = re.search('({})'.format(k), name)
            if match:
                value = match.group(1)
                break
        return value

    def getImagesForRegion(self, region):
        """
            Takes the name of an amazon region and retrieves a list of all
            images published by F5 for this region.
            Formats a return object
        """

        # get all the images
        # Following 3 lines commented out on 12/23/2017, old Chris stuff
        #arg_s = ['aws', 'ec2', 'describe-images',
                 #'--region', region, '--filter',
                 #'Name=name,Values=\'F5*\'', '--output=json']

        # When using boto
        #conn = boto.ec2.connect_to_region(region)
        #images = conn.get_all_images(filters={'name': 'F5*'})

        # When using boto3 with describe_images
        #client = boto3.client('ec2', region_name='eu-west-3')
        #images = client.describe_images(Filters=[{'Name':'name','Values':['F5*']}])
        #print images

        # When using boto3 with list
        ec2 = boto3.resource('ec2', region_name=region)
        images = list(ec2.images.filter(Filters=[{'Name':'name', 'Values':['F5*']}]).all())

        #print images
        #f5_init_images = {}
        #for i in images:
        #    start_position = i.name.find("ami-")
        #    if start_position > 0:
        #        #print (i.name[start_position:])[0:12]
        #        f5_init_images[(i.name[start_position:])[0:12]]=True
        #        #print f5_init_images

        # dimensions
        packages = ['good', 'better', 'best']
        throughputs = ['[0-9]+gbps', '[0-9]+mbps']
        licenses = ['byol', 'hourly']
        versions = [
            # 11.6.0.1.0.403-hf1
            '[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+[.][0-9]+[.][0-9]+[-hf]*[0-9]*',
            # 11.4.1-649.0-hf5
            '[0-9]+[.][0-9]+[.][0-9]+[-][0-9]+[.][0-9]+[-hf]*[0-9]*'
        ]

        structured = []
        c = 0
        for i in images:
            c = c + 1
            #print "%d %s %s %s" (c, region, i.name , i.id)
            print str(c) + " " + region + " " + i.name + " " + i.id
            if region == "us-east-1":
                if re.search(r'BIGIP', i.name):
                    if (i.name.lower())[-1] != "4":
                        print "Skipping invalid BIG-IP AMI......"
                        continue
            #if f5_init_images.get(i.id.lower(),None):
            #    continue
            try:
                image_name = i.name.lower()
                #image_name = i['Images'][0]['Name'].lower()
                #print image_name
                image_id = i.id.lower()
                #image_id = i['Images'][0]['ImageId'].lower()
                #print image_id

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

    def find(self, **kwargs):
        images = self.getImagesForRegion(region=kwargs['region'])
        if kwargs['package'] is not None:
            images = [i for i in images if i['package'] == kwargs['package']]

        if kwargs['license'] is not None:
            images = [i for i in images if i['license'] == kwargs['license']]

        # if kwargs['license'] == 'hourly' and kwargs['throughput'] is not None:
        #     images = [i for i in images if i['throughput'] == kwargs['throughput']]

        if kwargs['version'] is not None:
            images = [i for i in images if i['version'] is not None and
                      re.match('^({})'.format(kwargs['version']), i['version'])]

        def byName_version(image):
            return image['version']

        try:
            return sorted(images, key=byName_version, reverse=kwargs['take_newest'])
        except KeyError:
            return sorted(images, key=byName_version, reverse=True)

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
            images = self.getImagesForRegion(region=region)
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

class WebImageFinder(object):
    def __init__(self):
        pass

    def getWebRegionMap(self, **kwargs):
        """
            Returns region map
            Formats a return object
        """

        WebRegionMap = {}

        for region in kwargs['regions']:
            conn = boto.ec2.connect_to_region(region)
            images = conn.get_all_images(filters={'name': kwargs['name_string']})
            WebRegionMap[region] = {'AMI': images[0].id}

        return WebRegionMap


def main():
    print "Script started "  + time.strftime("%H:%M:%S")
    parser = OptionParser()
    (options, args) = parser.parse_args()

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

    image_finder_obj = BigIpImageFinder()
    marketplace_version = "13.1.0.2.0.0.6"

    # Hourly Region Map Marketplace ( Need to wait for v12/v13 to be released before can use Cloudinit )
    mp = {} # Marketplace Dict
    mp["Good25Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="good", bandwidth="25", license="hourly", version=marketplace_version, regions=regions,)
    mp["Good200Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="good", bandwidth="200", license="hourly", version=marketplace_version, regions=regions, )
    mp["Good1000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="good", bandwidth="1000", license="hourly", version=marketplace_version, regions=regions, )
    mp["Good5000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="good", bandwidth="5000", license="hourly", version=marketplace_version, regions=regions, )
    mp["Better25Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="better", bandwidth="25", license="hourly", version=marketplace_version, regions=regions,)
    mp["Better200Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="better", bandwidth="200", license="hourly", version=marketplace_version, regions=regions, )
    mp["Better1000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="better", bandwidth="1000", license="hourly", version=marketplace_version, regions=regions, )
    mp["Better5000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="better", bandwidth="5000", license="hourly", version=marketplace_version, regions=regions, )
    mp["Best25Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="best", bandwidth="25", license="hourly", version=marketplace_version, regions=regions,)
    mp["Best200Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="best", bandwidth="200", license="hourly", version=marketplace_version, regions=regions, )
    mp["Best1000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="best", bandwidth="1000", license="hourly", version=marketplace_version, regions=regions, )
    mp["Best5000Mbps"] = image_finder_obj.getBigipRegionMap(marketplace="best", bandwidth="5000", license="hourly", version=marketplace_version, regions=regions, )
    
    # For marketplace templates only, add two regions for CAR support in the Gov Cloud and CDG regions (us-gov-west-1 and eu-west-3), old request from AWS Michelle
    #for key, value in mp.items(): # returns the dictionary as a list of value pairs
    #    car_regions = ['us-gov-west-1', 'eu-west-3']
    #    for car_region in car_regions:
    #        value[car_region] = {value['us-east-1'].keys()[0]:""}

    gov_region = 'us-gov-west-1'
    with open('../AMI Maps/13.1.0.2-0.0.6/cached-hourly-region-map-us-gov-west-1.json') as json_file:
        data = json.load(json_file)
        gov_cloud_amis = data[gov_region]
        #for k,v in gov_cloud_amis.items():
             #print k + " = " + v

    for key, value in mp.items(): # returns the dictionary as a list of value pairs
        value[gov_region] = {key:gov_cloud_amis[key]}

    # Dump to files
    with open('../build/marketplace/cached-good25Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Good25Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build//marketplace/cached-good200Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Good200Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build/marketplace/cached-good1000Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Good1000Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build/marketplace/cached-good5000Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Good5000Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build/marketplace/cached-better25Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Better25Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build//marketplace/cached-better200Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Better200Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build/marketplace/cached-better1000Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Better1000Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build/marketplace/cached-better5000Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Better5000Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build/marketplace/cached-best25Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Best25Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build//marketplace/cached-best200Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Best200Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build/marketplace/cached-best1000Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Best1000Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open('../build/marketplace/cached-best5000Mbps-region-map.json', 'w') as outfile:
        json.dump(mp["Best5000Mbps"], outfile, sort_keys=True, indent=2, ensure_ascii=False)

    # Hourly Region Map Non-Marketplace
    HourlyRegionMap = image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", license="hourly", version="13.1.0.2.0.0.6", regions=regions, )
    with open('cached-hourly-region-map.json', 'w') as outfile:
        json.dump(HourlyRegionMap, outfile, sort_keys=True, indent=2, ensure_ascii=False)
    # BYOL Region Map:
    ByolRegionMap = image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", license="byol", version="13.1.0.2.0.0.6", regions=regions, )
    with open('cached-byol-region-map.json', 'w') as outfile:
        json.dump(ByolRegionMap, outfile, sort_keys=True, indent=2, ensure_ascii=False)
    # BIG-IQ Region Map:
    BigiqRegionMap = image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", license="byol", version="5.1.0.0.0.631", regions=regions, )
    with open('cached-bigiq-region-map.json', 'w') as outfile:
        json.dump(BigiqRegionMap, outfile, sort_keys=True, indent=2, ensure_ascii=False)

        # Webserver Region Map:
    # bitnami-lampstack-5.5.13-0-dev-linux-ubuntu-12.04.4-x86_64-ebs-ami-a9f58699-3-ami-9dcd82ad
    # aws ec2 describe-images --region us-west-2 --filter 'Name=name,Values="bitnami-lampstack-5.5.13-0-dev-linux-ubuntu-12.04.4-x86_64-ebs*"' --query 'Images[*].[CreationDate,ImageId,Name,Description]' --output=text | awk '{print $2}'
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
    name_string = "F5 Demo App v0.0.1"
    image_finder_obj = WebImageFinder()
    WebserverRegionMap = image_finder_obj.getWebRegionMap(name_string=name_string, regions=regions)

    with open('cached-webserver-region-map.json', 'w') as outfile:
        json.dump(WebserverRegionMap, outfile, sort_keys=True, indent=2, ensure_ascii=False)

    print "Script ended "  + time.strftime("%H:%M:%S")

if __name__ == "__main__":
    main()