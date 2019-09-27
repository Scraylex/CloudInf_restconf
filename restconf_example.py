import logging
from typing import List

import requests
import yaml
from jinja2 import Environment, FileSystemLoader

import restconf_helpers

requests.packages.urllib3.disable_warnings()

logger = logging.getLogger('restconf.example')


def load_devices() -> List[dict]:
    with open('device_infos.yaml', 'r') as host_file:
        hosts = yaml.load(host_file.read(), Loader=yaml.FullLoader)
        return hosts


def load_device_config():
    with open('config.yaml', 'r') as config_file:
        config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
        return config


def init_logger():
    _logger = logging.getLogger('restconf')
    # _logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    _logger.addHandler(ch)


def get_interfaces(host: dict) -> str:
    response = restconf_helpers.RestconfRequestHelper().get(
        url=f'https://{host["connection_address"]}/restconf/data/Cisco-IOS-XE-native:native/interface/',
        username=host['username'],
        password=host['password'])
    return response


def print_interfaces(host: dict) -> None:
    print(get_interfaces(host=host))


def configure(host: dict) -> None:
    config = load_device_config()

    send_data('Cisco-IOS-XE-native:native', config, host, 'reworked.j2')
    # for section, values in config.items():
    #     if section == 'interfaces':
    #         for interface in values:
    #             send_data('Cisco-IOS-XE-native:native/interface', interface, host, 'templates/interface.j2')
    #
    #     # elif section == 'bgp':
    #     #     send_data('Cisco-IOS-XE-native:native/router/bgp', values, host, 'templates/bgp.j2')
    #     #
    #     elif section == 'ospf':
    #         send_data('Cisco-IOS-XE-native:native/router/ospf/', values, host, 'templates/ospf.j2')


def render_template(data, template_file: str):
    env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(template_file)
    return template.render(data)


def send_data(restconf_path: str, data, host: dict, template_file: str):
    print(render_template(data, template_file))

    head = {'Content-Type': 'application/yang-data+xml',
            'Accept': 'application/yang-data+xml'}
    # Uncomment to actually send the configuration to the device
    try:
        response = requests.put(url=f"https://{host['connection_address']}/restconf/data/{restconf_path}",
                                  data=render_template(data, template_file),
                                  auth=(host['username'], host['password']),
                                  headers=head,
                                  verify=False
                                  )
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        print("Session Timeout")
    except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        print("Too many redirects")
    except requests.exceptions.RequestException as e:
        print(e)

    # if response.status_code == 200:
    #     print("Configuration successful")
    # else:
    #     print("Configuration failed")
    #     print(response)


def main():
    devices = load_devices()
    for device in devices:
        logger.info(f'Getting information for device {device}')
        # print_interfaces(host=device)
    configure(host=device)


if __name__ == '__main__':
    init_logger()
    main()
