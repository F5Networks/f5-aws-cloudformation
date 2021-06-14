#! /usr/local/bin/python2.7

import subprocess
import requests
import time
import argparse
import os

# usage: bigiq-config.py [-h]
#[--licensekey LICENSEKEY]
#[--masterkey MASTERKEY]
#[--personality PERSONALITY] [--hostname HOSTNAME]
#[--managementIpAddress MANAGEMENTIPADDRESS]
#[--managementRouteAddress MANAGEMENTROUTEADDRESS]
#[--discoveryAddress DISCOVERYADDRESS]
#[--timezone TIMEZONE]
#[--ntp_servers NTP_SERVERS [NTP_SERVERS ...]]
#[--dns_servers DNS_SERVERS [DNS_SERVERS ...]]
#[--user USER]
#[--password PASSWORD]
#[--utility UTILITY LICENSEKEY]

class Setup:

    BASE_URL="http://localhost:8100"
    
    def get_arguments(self):
        parser = argparse.ArgumentParser(description='Setup a BIG-IQ in one command')
        parser.add_argument("--licensekey", type=str, help="The license key")
        parser.add_argument("--masterkey", type=str, help="The masterkey passphrase", default="Thisisthemasterkey#1234")
        parser.add_argument("--personality", type=str, help="The system personality {big_iq, logging_node}", default="big_iq")
        parser.add_argument("--hostname", type=str, help="The system hostname", default="bigiq1.com")
        parser.add_argument("--managementIpAddress", type=str, help="The management IP address eg. 10.145.1.1/16", default=None)
        #parser.add_argument("--managementRouteAddress", type=str, help="The management route address eg. 10.145.1.1", default=None)
        parser.add_argument("--discoveryAddress", type=str, help="The discovery address eg. 10.145.1.1", default=None)
        parser.add_argument("--timezone", type=str, help="The system timezone", default="America/Los_Angeles")
        parser.add_argument("--user", type=str, help="The admin username", default="admin")
        parser.add_argument("--password", type=str, help="The admin password", default="admin")
        parser.add_argument(
            "--ntp_servers",
            type=str,
            nargs="+",
            help="NTP servers as a list, eg --ntp-servers time.nist.gov time.microsoft.com",
            default=["time.nist.gov"]
        )
        parser.add_argument(
            "--dns_servers",
            type=str,
            nargs="+",
            help="DNS servers as a list, eg --dns-servers 8.8.4.4 8.8.8.8 9.9.9.9",
            default=["8.8.8.8"]
        )
        parser.add_argument("--utility", type=str, help="Utility License Key")
        return parser.parse_args()

    def auth(self, user, password):
        self.session = requests.session()
        self.session.auth = (str(user), str(password))

    def wait_for_setup_mode(self):
        while True:
            print("Waiting for setup mode")
            time.sleep(5)

            result = self.session.get(Setup.BASE_URL + "/info/system")

            if result.status_code != 200:
                continue

            result_json = result.json()

            if result_json.get("available") and result_json.get("isSetupd"):
                break

    def set_license(self, license_key):
        if not license_key:
            print("No license provided, skipping licensing")
            return

        print("Setting license to " + str(license_key))

        if license_key == "skipLicense:true":
            result = self.session.post(
                Setup.BASE_URL + "/mgmt/setup/license",
                json={
                    "licenseText": "skipLicense:true"
                })
            result.raise_for_status()
            result_body = result.json()
            print(result_body)
        else:
            result = self.session.post(
                Setup.BASE_URL + "/mgmt/setup/license/activate",
                json={
                    "baseRegKey": license_key,
                    "addOnKeys":[],
                    "activationMethod":"AUTOMATIC"
                })
            result.raise_for_status()
            result_body = result.json()
            print(result_body)
            if "NEED_EULA_ACCEPT" in result_body.get("status"):
                print("Accepting EULA")

                accept_eula_body = {
                    "baseRegKey": license_key,
                    "dossier": result_body.get("dossier"),
                    "eulaText": result_body.get("eulaText")
                }
                result = self.session.post(
                    Setup.BASE_URL + "/mgmt/setup/license/accept-eula",
                    json=accept_eula_body
                )
                result.raise_for_status()

        print("Saving license to service.config.json")
        self.session.post(
            Setup.BASE_URL + "/mgmt/setup/license",
            json={
                "licenseText": result.json().get("licenseText")
            })

    def set_masterkey(self, masterkey):
        print("Setting master key to " + str(masterkey))
        result = self.session.post(
            Setup.BASE_URL + "/mgmt/setup/masterkey",
            json={
                "passphrase": masterkey
            })
        result.raise_for_status()

    def set_personality(self, personality):
        print("Setting personality to " + str(personality))
        self.session.post(
            Setup.BASE_URL + "/mgmt/setup/personality", json={ "systemPersonality": personality }
        ).raise_for_status()

    def addresses_are_valid(self, addresses):
        return (
            addresses is not None and
            addresses.get("hostname") and
            addresses.get("managementIpAddress") and
            #addresses.get("managementRouteAddress") and
            addresses.get("discoveryAddress")
        )

    def set_addresses(self, addresses):
        if not self.addresses_are_valid(addresses):
            print("Missing address arguments, skipping for now, this isn't critical to setup")
            return

        print("Setting addresses to")
        body = {
                "hostname":addresses.get("hostname"),
                "managementIpAddress":addresses.get("managementIpAddress"),
                #"managementRouteAddress":addresses.get("managementRouteAddress"),
                "discoveryAddress":addresses.get("discoveryAddress")
            }
        print(body)

        self.session.post(
            Setup.BASE_URL + "/mgmt/setup/address",
            json=body).raise_for_status()

    def set_services(self, ntp_servers, timezone, dns_servers):
        print("Setting NTP servers")
        self.session.post(Setup.BASE_URL + "/mgmt/setup/ntp", json={ "servers": ntp_servers, "timezone": timezone }).raise_for_status()
        print("Setting DNS servers")
        self.session.post(Setup.BASE_URL + "/mgmt/setup/dns", json={ "servers": dns_servers, "search": [ "localhost" ] }).raise_for_status()


    def launch_bigiq(self):
        print("Launching BIG-IQ")
        result = self.session.post(Setup.BASE_URL + "/mgmt/setup/launch")
        result.raise_for_status()
        skip = 0
        top = 100
        timestamp = result.json().get("fileTimestamp")
        while True:
            result = self.session.get(
                Setup.BASE_URL + "/mgmt/setup/launch/monitor?datetime={datetime}&top={top}&skip={skip}"
                    .format(
                        datetime=timestamp,
                        top=top,
                        skip=skip
                    )
            )

            result_json = result.json()

            if result_json.get("status") == "COMPLETE":
                print("Setup complete")
                print("Get pginit and tokuUpgrade status with")
                print("tail -f /var/log/bootstrap-" + timestamp + ".*")
                print("Get restjavad status with")
                print("restcurl /shared/system-started")
                break

            json = result.json()

            lines = result.json().get("lines")
            skip += len(lines)

            if lines:
                print("\n".join(lines))

            time.sleep(1)

    def enable_basic_auth(self):
        with open("/etc/bigstart/scripts/setupd", mode="r+") as setupd_script:
            print("Enabling basic auth")
            file_contents = setupd_script.read()
            file_contents = file_contents.replace("#export BIGIQ_BASIC_AUTH_ENABLED=True", "export BIGIQ_BASIC_AUTH_ENABLED=True")
            setupd_script.seek(0)
            setupd_script.write(file_contents)
            setupd_script.truncate()
        print("Restarting setupd")
        subprocess.check_call(["bigstart", "restart", "setupd"])

    def wait_for_initial_activation(self):
        while True:
            print("Waiting for initial_activation client")
            time.sleep(5)
            result = self.session.get(Setup.BASE_URL + "/mgmt/cm/device/licensing/pool/initial-activation")
            if result.status_code != 200:
                continue
            result_json = result.json()
            if result_json.get("selfLink") == "https://localhost/mgmt/cm/device/licensing/pool/initial-activation":
                break

    def create_utility_pool(self, utility):
        if not utility:
            print("No license provided, skipping license pool creation")
            return
        print("Adding utility license " + str(utility))
        result = self.session.post(Setup.BASE_URL + "/mgmt/cm/device/licensing/pool/initial-activation", json={"regKey": utility, "name": "production", "status":"ACTIVATING_AUTOMATIC"})
        result.raise_for_status()
        result_body = result.json()
        print(result_body)
    
    def activate_utility_pool(self, utility):
        if not utility:
            print("No license provided, skipping license pool activation")
            return
        result = self.session.get(
            Setup.BASE_URL + "/mgmt/cm/device/licensing/pool/initial-activation/" + str(utility)
            )
        result.raise_for_status()
        result_body = result.json()
        eula_text = result_body.get("eulaText") 
        if "NEED_EULA_ACCEPT" in result_body.get("status"):
            print("Accepting EULA")
            accept_eula_body = {
                "status": "ACTIVATING_AUTOMATIC_EULA_ACCEPTED",
                "eulaText": eula_text
            }
            result = self.session.patch(
                Setup.BASE_URL + "/mgmt/cm/device/licensing/pool/initial-activation/" + str(utility),
                json=accept_eula_body
            )
            result.raise_for_status()
            result_body = result.json()
            print(result_body)
        else:
            print("Eula already accepted")
            print(result_body)

    def verify_utility_activation(self, utility):
        if not utility:
            print("No license provided, skipping license pool activation verification")
            return
        result = self.session.get(
            Setup.BASE_URL + "/mgmt/cm/device/licensing/pool/initial-activation/" + str(utility)
            )
        result.raise_for_status()
        result_body = result.json()
        i = 0
        while "READY" not in result_body.get("status") and i < 120:
            i+=1
            result = self.session.get(
                Setup.BASE_URL + "/mgmt/cm/device/licensing/pool/initial-activation/" + str(utility)
                )
            result.raise_for_status()
            result_body = result.json()
            print("License not ready:" + str(result_body))
            print("Waiting for 5 seconds")
            time.sleep(5)
        if i == 120:
            print("MAX try's reached, exiting")
        else:
            print("License ready:" + str(result_body))
            self.touch("/config/cloud/config_complete")

    def touch(self, path):
        with open(path, 'a'):
            os.utime(path, None)

    def main(self):
        args = self.get_arguments()
        print("Running BIGIQ configuration with these arguments")
        print(args)

        self.enable_basic_auth()     
        self.auth(args.user,args.password)
        self.wait_for_setup_mode()
        self.set_license(args.licensekey)
        self.set_masterkey(args.masterkey)
        self.set_personality(args.personality)
        self.set_addresses({
                "hostname": args.hostname,
                "managementIpAddress": args.managementIpAddress,
                #"managementRouteAddress": args.managementRouteAddress,
                "discoveryAddress": args.discoveryAddress
            })
        self.set_services(ntp_servers=args.ntp_servers, timezone=args.timezone, dns_servers=args.dns_servers)
        self.launch_bigiq()
        time.sleep(60)
        self.enable_basic_auth()
        self.auth(args.user,args.password)
        self.wait_for_initial_activation()
        time.sleep(15)
        self.create_utility_pool(args.utility)
        time.sleep(15)
        self.activate_utility_pool(args.utility)
        self.verify_utility_activation(args.utility)

if __name__ == "__main__":
    setup = Setup()
    setup.main()