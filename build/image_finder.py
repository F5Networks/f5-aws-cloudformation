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

        if kwargs['license'] == 'hourly' and kwargs['throughput'] is not None:
            images = [i for i in images if i['throughput'] == kwargs['throughput']]

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
        """

        BigipRegionMap = {}

        for region in kwargs['regions']:

            images = self.getImagesForRegion(region=region)

            if kwargs['license'] is not None:
                images = [i for i in images if i['license'] == kwargs['license']]

            if kwargs['license'] == 'hourly' and kwargs['throughput'] is not None:
                images = [i for i in images if i['throughput'] == kwargs['throughput']]

            if kwargs['version'] is not None:
                images = [i for i in images if i['version'] is not None and
                re.match('^({})'.format(kwargs['version']), i['version'])]

            package_dict = {}
            for image in images:
                if image['package'] == "good":
                    package_dict['Good'] = image['id']
                if image['package'] == "better":
                    package_dict['Better'] = image['id']
                if image['package'] == "best":
                    package_dict['Best'] = image['id']

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
            WebRegionMap[region] = images[0].id

        return WebRegionMap


def main():

    parser = OptionParser()
    (options, args) = parser.parse_args()

    ### BEGIN MAPPINGS
    regions = [
            'ap-northeast-1',
            'ap-southeast-1',
            'ap-southeast-2',
            'eu-west-1',
            'sa-east-1',
            'us-east-1',
            'us-west-1',
            'us-west-2',
    ]

    image_finder_obj = BigIpImageFinder()

    # Hourly Region Map ( Need to wait for v12/v13 to be released before can use Cloudinit )
    HourlyRegionMap = image_finder_obj.getBigipRegionMap(license="hourly", version="11.6.0.4.0.420", throughput="1gbps", regions=regions)
    
    with open('cached-hourly-region-map.json', 'w') as outfile:
        json.dump(HourlyRegionMap, outfile, sort_keys = True, indent = 2, ensure_ascii=False)

    # BYOL Region Map:
    ByolRegionMap = image_finder_obj.getBigipRegionMap(license="byol", version="12.0.0", throughput="1gbps", regions=regions)

    with open('cached-byol-region-map.json', 'w') as outfile:
        json.dump(ByolRegionMap, outfile, sort_keys = True, indent = 2, ensure_ascii=False)


    # Webserver Region Map:
    #bitnami-lampstack-5.5.13-0-dev-linux-ubuntu-12.04.4-x86_64-ebs-ami-a9f58699-3-ami-9dcd82ad
    #aws ec2 describe-images --region us-west-2 --filter 'Name=name,Values="bitnami-lampstack-5.5.13-0-dev-linux-ubuntu-12.04.4-x86_64-ebs*"' --query 'Images[*].[CreationDate,ImageId,Name,Description]' --output=text | awk '{print $2}'

    name_string = "bitnami-lampstack-5.5.13-0-dev-linux-ubuntu-12.04.4-x86_64-ebs*"
    image_finder_obj = WebImageFinder()
    WebserverRegionMap = image_finder_obj.getWebRegionMap(name_string=name_string, regions=regions)

    with open('cached-webserver-region-map.json', 'w') as outfile:
        json.dump(WebserverRegionMap, outfile, sort_keys = True, indent = 2, ensure_ascii=False)

if __name__ == "__main__":
    main()