import logging
from typing import List

import requests
import yaml
from jinja2 import Environment, FileSystemLoader

import argparse
import sys

parser = argparse.ArgumentParser(description='Restconf device configurator')
parser.add_argument('-v', '--verbose',
                    help='Additionally print the config passed to the device',
                    action="store_true")
parser.add_argument('-s', '--section',
                    help='Set what section should be configured, default: full',
                    choices=['full', 'interfaces', 'ospf', 'bgp'],
                    default='full')
args = parser.parse_args()
VERBOSE = args.verbose
SECTION = args.section
HEADERS = {'Content-Type': 'application/yang-data+xml',
           'Accept': 'application/yang-data+xml'}

requests.packages.urllib3.disable_warnings()
logger = logging.getLogger('restconf.device_configurator')


def init_logger():
    _logger = logging.getLogger('restconf')
    _logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    _logger.addHandler(ch)


def load_devices() -> List[dict]:
    with open('device_infos.yaml', 'r') as host_file:
        hosts = yaml.load(host_file.read(), Loader=yaml.FullLoader)
        return hosts


def load_device_config():
    with open('config.yaml', 'r') as config_file:
        config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
        return config


def configure(host: dict) -> None:
    config = load_device_config()

    print(SECTION)
    if SECTION == 'full':
        verbose_print("Configure all sections")
        send_configuration('Cisco-IOS-XE-native:native', config, host, 'templates/config.j2')
    elif SECTION == 'interfaces':
        verbose_print("Configure section interfaces")
        if SECTION in config:
            send_configuration('Cisco-IOS-XE-native:native/interface', config, host, 'templates/interface.j2')
        else:
            verbose_print(f"No {SECTION} config in config.yaml available")
            sys.exit(1)
    elif SECTION == 'ospf':
        verbose_print("Configure section ospf")
        if SECTION in config:
            send_configuration('Cisco-IOS-XE-native:native/router/ospf/', config, host, 'templates/ospf.j2')
        else:
            verbose_print(f"No {SECTION} config in config.yaml available")
            sys.exit(1)
    elif SECTION == 'bgp':
        verbose_print("Configure section bgp")
        if SECTION in config:
            send_configuration('Cisco-IOS-XE-native:native/router/bgp/', config, host, 'templates/bgp.j2')
        else:
            verbose_print(f"No {SECTION} config in config.yaml available")
            sys.exit(1)


def render_template(data, template_file: str):
    env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(template_file)
    return template.render(data)


def send_configuration(restconf_path: str, data, host: dict, template_file: str):
    payload = render_template(data, template_file)
    verbose_print(payload)

    response = requests.patch(url=f"https://{host['connection_address']}/restconf/data/{restconf_path}",
                              auth=(host['username'], host['password']),
                              data=payload,
                              headers=HEADERS,
                              verify=False
                              )

    if response.status_code == 204:
        verbose_print("Configuration successful")
    else:
        verbose_print("Configuration failed")
        verbose_print(response.reason)
        verbose_print(response.content)
        sys.exit(1)


def verbose_print(message):
    if VERBOSE:
        logger.info(message)


def main():
    devices = load_devices()
    for device in devices:
        if VERBOSE: logger.info(f'Getting information for device {device}')
        configure(host=device)


if __name__ == '__main__':
    init_logger()
    main()
