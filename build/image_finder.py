# /usr/bin/python env

import time
import re
import boto3
import boto
import boto.ec2
import collections
import json
import argparse
import os
import sys

# Parse any commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--bigip-version', help='Optionally provide BIG-IP Version to generate AMI Map for')
parser.add_argument('-q', '--bigiq-version', help='Optionally provide BIG-IQ Version to generate AMI Map for')
parser.add_argument('-u', '--profile', help='Optionally provide cli profile to use when querying images in US aws')
parser.add_argument('-c', '--china_profile', help='Optionally provide cli profile to use when querying images in china aws')
parser.add_argument('-g', '--gov_profile', help='Optionally provide cli login profile to use when querying images in us gov aws')
args = parser.parse_args()

# Constants 
# Versions to update, update whenever AMIs or BIGIP/IQ versions are updated
BIGIP_MARKETPLACE_VERSION = args.bigip_version or "15.1.2.1-0.0.10"
BIGIQ_MARKETPLACE_VERSION = args.bigiq_version or "6.1.0.0.0.1224"
# Profiles to use, profiles specified must be present in ~/.aws/credentials and ~/.aws/config: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html
AWS_PROFILE = args.profile or "default"
CHINA_AWS_PROFILE = args.china_profile or "china"
GOV_AWS_PROFILE = args.gov_profile or "gov"

PACKAGE_THROUGHPUT_MAP = {
                        "good": {
                            "25mbps": "Good25Mbps",
                            "200mbps": "Good200Mbps",
                            "1gbps": "Good1000Mbps",
                            "5gbps": "Good5000Mbps",
                            "10gbps": "Good10000Mbps"
                        },
                        "better": {
                            "25mbps": "Better25Mbps",
                            "200mbps": "Better200Mbps",
                            "1gbps": "Better1000Mbps",
                            "5gbps": "Better5000Mbps",
                            "10gbps": "Better10000Mbps"
                        },
                        "best": {
                            "25mbps": "Best25Mbps",
                            "200mbps": "Best200Mbps",
                            "1gbps": "Best1000Mbps",
                            "5gbps": "Best5000Mbps",
                            "10gbps": "Best10000Mbps"
                        },
                        "payg - waf": {
                            "25mbps": "AdvancedWaf25Mbps",
                            "200mbps": "AdvancedWaf200Mbps",
                            "1gbps": "AdvancedWaf1000Mbps",
                            "5gbps": None,
                            "10gbps": None
                        },
                        "payg-adv waf": {
                            "25mbps": "AdvancedWaf25Mbps",
                            "200mbps": "AdvancedWaf200Mbps",
                            "1gbps": "AdvancedWaf1000Mbps",
                            "5gbps": None,
                            "10gbps": None
                        },
                        "payg-advwaf": {
                            "25mbps": "AdvancedWaf25Mbps",
                            "200mbps": "AdvancedWaf200Mbps",
                            "1gbps": "AdvancedWaf1000Mbps",
                            "5gbps": None,
                            "10gbps": None
                        },
                        "per app ve - advanced waf": {
                            "25mbps": "PerAppVeAwaf25Mbps",
                            "200mbps": "PerAppVeAwaf200Mbps",
                            "1gbps": None,
                            "5gbps": None,
                            "10gbps": None
                        },
                        "pve adv waf": {
                            "25mbps": "PerAppVeAwaf25Mbps",
                            "200mbps": "PerAppVeAwaf200Mbps",
                            "1gbps": None,
                            "5gbps": None,
                            "10gbps": None
                        },
                        "pveadvwaf": {
                            "25mbps": "PerAppVeAwaf25Mbps",
                            "200mbps": "PerAppVeAwaf200Mbps",
                            "1gbps": None,
                            "5gbps": None,
                            "10gbps": None
                        },
                        "per app ve - ltm": {
                            "25mbps": "PerAppVeLtm25Mbps",
                            "200mbps": "PerAppVeLtm200Mbps",
                            "1gbps": None,
                            "5gbps": None,
                            "10gbps": None
                        },
                        "pve ltm": {
                            "25mbps": "PerAppVeLtm25Mbps",
                            "200mbps": "PerAppVeLtm200Mbps",
                            "1gbps": None,
                            "5gbps": None,
                            "10gbps": None
                        },
                        "pveltm": {
                            "25mbps": "PerAppVeLtm25Mbps",
                            "200mbps": "PerAppVeLtm200Mbps",
                            "1gbps": None,
                            "5gbps": None,
                            "10gbps": None
                        }
}

PACKAGE_CPU_MAP = {
                        "payg-hp ltm": {
                            "8vcpu": None,
                            "16vcpu": "Good16vCPU"
                        },
                        "payg-hpltm": {
                            "8vcpu": None,
                            "16vcpu": "Good16vCPU"
                        },
                        "payg-hp adv waf": {
                            "8vcpu": "AdvancedWaf8vCPU",
                            "16vcpu": "AdvancedWaf16vCPU"
                        },
                        "payg-hpadvwaf": {
                            "8vcpu": "AdvancedWaf8vCPU",
                            "16vcpu": "AdvancedWaf16vCPU"
                        }
}

BYOL_BOOT_LOCATION_MAP = {
    "ltm 1boot loc": "LTMOneBootLocation",
    "ltm 2boot loc": "LTMTwoBootLocations",
    "all modules 1boot loc": "AllOneBootLocation",
    "all modules 2boot loc": "AllTwoBootLocations",
    "ltm1bootloc": "LTMOneBootLocation",
    "ltm2bootloc": "LTMTwoBootLocations",
    "allmodules1bootloc": "AllOneBootLocation",
    "allmodules2bootloc": "AllTwoBootLocations"
}

GIGA_TO_MEGA_BPS_MAP = {
    "25mbps": "25Mbps",
    "200mbps": "200Mbps",
    "1gbps": "1000Mbps",
    "5gbps": "5000Mbps",
    "10gbps": "10000Mbps"
}


class BigIpImageFinder(object):
    def __init__(self):
        self.region_ami = {}
        # Criteria to search for
        self.packages = ['(good)', '(better)', '(best)', '(payg - waf)', '(payg-adv waf)', '(payg-advwaf)', '(per app ve - ltm)', '(pve ltm)', '(pveltm)', '(per app ve - advanced waf)', '(pve adv waf)', '(pveadvwaf)', '(payg-hp adv waf)', '(payg-hpadvwaf)', '(payg-hp ltm)', '(payg-hpltm)']
        self.throughputs = ['([0-9]+gbps)', '([0-9]+mbps)']
        self.licenses = ['(byol)', '(payg)']
        self.bigip_version_regex = [
            # 13.1.1-0.0.4
            'bigip-(\\d{1,2}.[0-9].[0-9]-[0-9].[0-9].\\d{1,2})',
            # 15.1.0.4-0.0.3
            'bigip-(\\d{1,2}.[0-9].[0-9].[0-9]-[0-9].[0-9].\\d{1,2})'
        ]
        self.bigiq_version_regex = [
            # 6.0.0.0.0.x
            'big-iq-(\\d{1,2}.\\d{1,2}.[0-9].[0-9].[0-9].\\d{1,4})'
        ]
        self.boot_locations = ['(%s)' % (i) for i in BYOL_BOOT_LOCATION_MAP.keys()]
        self.cpus = ['([0-9]+vcpu)']

    def searchitem(self, keys, name):
        value = None
        for k in keys:
            match = re.search('{}'.format(k), name)
            if match:
                value = match.group(1)
                break
        return value

    def getImagesForRegion(self, region, profile):
        """
            Takes the name of an amazon region and retrieves a list of all
            images published by F5 for this region.
            Formats a return object
        """
        
        # When using boto3 with list
        session = boto3.Session(profile_name=profile)
        ec2 = session.resource('ec2', region_name=region)
        images = list(ec2.images.filter(Filters=[{'Name': 'description', 'Values': ['F5*']}]).all())

        structured = []
        c = 0
        for i in images:
            c = c + 1
            # print str(c) + " " + region + " " + i.description + " " + i.id
            if region == "us-east-1":
                if re.search(r'BIGIP', i.name):
                    if (i.name.lower())[-1] != "4":
                        continue
            try:
                image_name = i.description.lower()
                image_id = i.image_id.lower()

                license = self.searchitem(self.licenses, image_name)
                bigip_version = self.searchitem(self.bigip_version_regex, image_name)
                bigiq_version = self.searchitem(self.bigiq_version_regex, image_name)
                throughput = self.searchitem(self.throughputs, image_name)
                package = self.searchitem(self.packages, image_name)
                byol_boot_location = self.searchitem(self.boot_locations, image_name)
                cpu = self.searchitem(self.cpus, image_name)

                structured.append({
                    'name': image_name,
                    'id': image_id,
                    'bigip_version': bigip_version,
                    'bigiq_version': bigiq_version,
                    'package': package,
                    'license': license,
                    'throughput': str(throughput),
                    'cpu': str(cpu),
                    'byol_boot_location': byol_boot_location})
            except Exception as e:
                print('Failed processing image "{}". Will not be added to index. Error was {}'.format(image_name, e))
        return structured

    def getBigipRegionMap(self, marketplace, bandwidth, profile, **kwargs):
        """
            Returns region map
            Formats a return object
            BYOL:
             "ap-northeast-1": {
                "Best": "ami-0659ab67",
                "Better": "ami-ed5eac8c",
                "Good": "ami-1859ab79"
              },
            payg:
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
        print("marketplace = {}, bandwidth = {}".format(marketplace, bandwidth))
        BigipRegionMap = {}
        for region in kwargs['regions']:
            images = None
            if region not in self.region_ami:
                self.region_ami[region] = self.getImagesForRegion(region=region, profile=profile)
            if kwargs['license'] is not None:
                images = [i for i in self.region_ami[region] if i['license'] == kwargs['license']]
            if kwargs['version'] is not None:
                # Look for BIG IP
                images = [i for i in images if ((i['bigip_version'] is not None and re.match('^({})'.format(kwargs['version']), i['bigip_version'])) or (i['bigiq_version'] is not None and re.match('^({})'.format(kwargs['version']), i['bigiq_version'])))]
            package_dict = {}
            for image in images:
                if image['license'] == "byol":
                    # AMIs for BYOL BIGIP
                    if (image['byol_boot_location'] in BYOL_BOOT_LOCATION_MAP and BYOL_BOOT_LOCATION_MAP[image['byol_boot_location']] not in package_dict):
                        package_dict[BYOL_BOOT_LOCATION_MAP[image['byol_boot_location']]] = image['id']
                    # AMIs for BIG IQ
                    elif (image['bigiq_version'] is not None and image['package'] in PACKAGE_THROUGHPUT_MAP and image['package'] not in package_dict):
                        package_dict[image['package']] = image['id']
                # AMIs for PAYG BIGIP
                elif image['license'] == "payg":
                    if (image['package'] in PACKAGE_THROUGHPUT_MAP and image['throughput'] in PACKAGE_THROUGHPUT_MAP["good"] and PACKAGE_THROUGHPUT_MAP[image['package']][image['throughput']] not in package_dict):
                        package_dict[PACKAGE_THROUGHPUT_MAP[image['package']][image['throughput']]] = image['id']
                    # High Performance VEs
                    if (image['package'] in PACKAGE_CPU_MAP and (image['cpu'] in PACKAGE_CPU_MAP['payg-hp ltm'] or image['cpu'] in PACKAGE_CPU_MAP['payg-hpltm']) and PACKAGE_CPU_MAP[image['package']][image['cpu']] not in package_dict):
                            package_dict[PACKAGE_CPU_MAP[image['package']][image['cpu']]] = image['id']
            # Region may not contain a specific BIG-IP version. Check package_dict
            if not package_dict:
                print("No {} Images found in {}".format(kwargs['version'], region))
            else:
                if marketplace == "no" and bandwidth == "all":
                    BigipRegionMap[region] = package_dict
                else:
                    try:
                        BigipRegionMap[region] = {PACKAGE_THROUGHPUT_MAP[marketplace][bandwidth] : package_dict[PACKAGE_THROUGHPUT_MAP[marketplace][bandwidth]]}
                    except:
                        print("Cannot find {} offering for {} in {} in package_dict.".format(marketplace, bandwidth, region))
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


def region_finder(profile):
    session = boto3.Session(profile_name=profile)
    ec2_client = session.client('ec2')
    try:
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
        print(regions)
    except Exception as e:
        print('Unable to execute EC2.Client.describe_regions()')
        print(e)
        sys.exit(1)
    return regions


def main():
    print("Script started " + time.strftime("%H:%M:%S"))

    # BEGIN MAPPINGS
    image_finder_obj = BigIpImageFinder()

    # payg Region Map Non-Marketplace
    HourlyRegionMap = image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", profile=AWS_PROFILE, license="payg", version=BIGIP_MARKETPLACE_VERSION, regions=(region_finder(AWS_PROFILE)), )
    HourlyRegionMap.update(image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", profile=GOV_AWS_PROFILE, license="payg", version=BIGIP_MARKETPLACE_VERSION, regions=(region_finder(GOV_AWS_PROFILE)), ))
    HourlyRegionMap.update(image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", profile=CHINA_AWS_PROFILE, license="payg", version=BIGIP_MARKETPLACE_VERSION, regions=(region_finder(CHINA_AWS_PROFILE)), ))
    print('Dump PAYG maps: cached-payg-region-map.json')
    with open('cached-payg-region-map.json', 'w') as outfile:
        json.dump(HourlyRegionMap, outfile, sort_keys=True, indent=2, ensure_ascii=False)
    # BYOL Region Map:
    ByolRegionMap = image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", profile=AWS_PROFILE, license="byol", version=BIGIP_MARKETPLACE_VERSION, regions=(region_finder(AWS_PROFILE)), )
    ByolRegionMap.update(image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", profile=GOV_AWS_PROFILE, license="byol", version=BIGIP_MARKETPLACE_VERSION, regions=(region_finder(GOV_AWS_PROFILE)), ))
    ByolRegionMap.update(image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", profile=CHINA_AWS_PROFILE, license="byol", version=BIGIP_MARKETPLACE_VERSION, regions=(region_finder(CHINA_AWS_PROFILE)), ))
    print('Dump BYOL maps: cached-byol-region-map.json')
    with open('cached-byol-region-map.json', 'w') as outfile:
        json.dump(ByolRegionMap, outfile, sort_keys=True, indent=2, ensure_ascii=False)
    # BIG-IQ Region Map:
    BigiqRegionMap = image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", profile=AWS_PROFILE, license="byol", version=BIGIQ_MARKETPLACE_VERSION, regions=(region_finder(AWS_PROFILE)), )
    BigiqRegionMap.update(image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", profile=GOV_AWS_PROFILE, license="byol", version=BIGIQ_MARKETPLACE_VERSION, regions=(region_finder(GOV_AWS_PROFILE)), ))
    BigiqRegionMap.update(image_finder_obj.getBigipRegionMap(marketplace="no", bandwidth="all", profile=CHINA_AWS_PROFILE, license="byol", version=BIGIQ_MARKETPLACE_VERSION, regions=(region_finder(CHINA_AWS_PROFILE)), ))
    print('Dump BIGIQ maps: cached-bigiq-region-map.json')
    with open('cached-bigiq-region-map.json', 'w') as outfile:
        json.dump(BigiqRegionMap, outfile, sort_keys=True, indent=2, ensure_ascii=False)

    # Webserver Region Map:
    regions = [
        'me-south-1',
        'ap-south-1',
        'ap-southeast-1',
        'ap-southeast-2',
        'ap-northeast-1',
        'ap-northeast-2',
        'ca-central-1',
        'eu-west-1',
        'eu-west-2',
        'eu-west-3',
        'eu-central-1',
        'sa-east-1',
        'us-west-1',
        'us-west-2',
        'us-east-1',
        'us-east-2'
    ]

    print("Script ended " + time.strftime("%H:%M:%S"))

if __name__ == "__main__":
    main()
