#/usr/bin/python env

import re
import boto
import boto.ec2
import collections
import json
from optparse import OptionParser


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

        #get all the images
        arg_s = ['aws', 'ec2', 'describe-images',
          '--region', region, '--filter',
          'Name=name,Values=\'F5*\'', '--output=json']
     
        conn = boto.ec2.connect_to_region(region)
        images = conn.get_all_images(filters={'name':'F5*'})

        #dimensions
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
        for i in images:
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


    def getBigipRegionMap(self, **kwargs):
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
                        if image['throughput'] == "200mbps":
                            package_dict['Good200Mbps'] = image['id']
                        if image['throughput'] == "1gbps":
                            package_dict['Good1000Mbps'] = image['id']    
                    elif image['package'] == "better":
                        if image['throughput'] == "25mbps":
                            package_dict['Better25Mbps'] = image['id']
                        if image['throughput'] == "200mbps":
                            package_dict['Better200Mbps'] = image['id']
                        if image['throughput'] == "1gbps":
                            package_dict['Better1000Mbps'] = image['id']  
                    elif image['package'] == "best":
                        if image['throughput'] == "25mbps":
                            package_dict['Best25Mbps'] = image['id']
                        if image['throughput'] == "200mbps":
                            package_dict['Best200Mbps'] = image['id']
                        if image['throughput'] == "1gbps":
                            package_dict['Best1000Mbps'] = image['id']  

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
            images = conn.get_all_images(filters={'name': kwargs['name_string'] })
            WebRegionMap[region] = { 'AMI': images[0].id }

        return WebRegionMap


def main():

    parser = OptionParser()
    (options, args) = parser.parse_args()

    ### BEGIN MAPPINGS
    regions = [
                'us-east-1',
                'us-west-2',
                'us-west-1',
                'eu-west-1',
                'eu-central-1',
                'ap-southeast-1',
                'ap-northeast-1',
                'ap-southeast-2',
                'sa-east-1',
    ]

    image_finder_obj = BigIpImageFinder()

    # Hourly Region Map ( Need to wait for v12/v13 to be released before can use Cloudinit )
    HourlyRegionMap = image_finder_obj.getBigipRegionMap(license="hourly", version="12.1.0.1.1.1447", regions=regions)
    
    with open('cached-hourly-region-map.json', 'w') as outfile:
        json.dump(HourlyRegionMap, outfile, sort_keys = True, indent = 2, ensure_ascii=False)

    # BYOL Region Map:
    ByolRegionMap = image_finder_obj.getBigipRegionMap(license="byol", version="12.1.0.1.1.1447", regions=regions)

    with open('cached-byol-region-map.json', 'w') as outfile:
        json.dump(ByolRegionMap, outfile, sort_keys = True, indent = 2, ensure_ascii=False)

    #Webserver Region Map:
    #bitnami-lampstack-5.5.13-0-dev-linux-ubuntu-12.04.4-x86_64-ebs-ami-a9f58699-3-ami-9dcd82ad
    #aws ec2 describe-images --region us-west-2 --filter 'Name=name,Values="bitnami-lampstack-5.5.13-0-dev-linux-ubuntu-12.04.4-x86_64-ebs*"' --query 'Images[*].[CreationDate,ImageId,Name,Description]' --output=text | awk '{print $2}'

    name_string = "F5 Demo App v0.0.1"
    image_finder_obj = WebImageFinder()
    WebserverRegionMap = image_finder_obj.getWebRegionMap(name_string=name_string, regions=regions)

    with open('cached-webserver-region-map.json', 'w') as outfile:
        json.dump(WebserverRegionMap, outfile, sort_keys = True, indent = 2, ensure_ascii=False)

if __name__ == "__main__":
    main()
