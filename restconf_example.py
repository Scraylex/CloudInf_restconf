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
    #_logger.setLevel(logging.DEBUG)
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


def configure_interface():
    #load config from yaml
    #config = {'is_loopback': 'True'}
    config = load_device_config()

    for k, v in config.items():
        if k == 'interfaces':
            # render and configure interfaces
            print(k)
            print(v)
            for int in v:
                env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
                template = env.get_template('interface.j2')
                print(template.render(int))

                r = requests.put(url="https://10.3.255.107/restconf/data/Cisco-IOS-XE-native:native/interface",
                                 data=template.render(int))
                if r.status_code == 200:
                    print("OK")
                else:
                    print("conf_int failed")

        elif k == 'bgp':
            env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
            template = env.get_template('route.j2')
            template.render(k)
        elif k == 'ospf':
            configure_ospf()



def configure_ospf():
    pass
def configure_bgp():
    pass


def configure_loopback():
    pass


def main():
    devices = load_devices()
    for device in devices:
        logger.info(f'Getting information for device {device}')
        print_interfaces(host=device)
    configure_interface()


if __name__ == '__main__':
    init_logger()
    main()
