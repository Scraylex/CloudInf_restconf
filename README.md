# CloudInf Restconf Device Configurator
This python script can be used to configure Cisco devices. It supports configuring the hostname, interfaces,
ospf and bgp routing. The script uses `pyang`, `jinja2` templates and `yaml` config which will be rendered to xml and pushed
to the device via restconf.

## Table of content
1. [Prerequirements & installation](#prerequirements-&-installation)
2. [Usage](#usage)
3. [Configuration](#configuration)
4. [Idea](#idea)


## Prerequirements & installation
- Python > 3.6
- pip
- we recommend to use virtual environments [Documentation](https://docs.python.org/3/library/venv.html)
- Install the required libraries by running the command `pip install -r requirements.txt`

## Usage
The programm can be used to configure the device by running the following command. It will configure all sections of the
device silenty and just return a good `0` or bad `1` exitcode. While `0` means the configuration was applied
successfully and a html return code of `204` was returned and `1` means that there may was an error and a
return code of not `204` was returned by the device.
```bash
$ python restconf_device_configurator.py
```

If you would like to only configure one section of the device you can use the `-s` or the `--section`
parameter with a value of `full`, `interfaces`, `ospf` or `bgp`. This will only configure the defined section.
For Example to configure only the bgp section.
```bash
$ python restconf_device_configurator.py --section 'bgp'
```

If you encounter errors while configuring the device it may be usefull to invoke the script with the additional
argument `-v` or `--verbose`. This will print you the whole rendered `xml` configuration like it will be sent 
to the device.
```xml
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"  xmlns:ios="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname>RT-7</hostname>
    <interface>
        <GigabitEthernet>
            <name>1</name>
            <description>RESTful API Interface</description>
            <ip>
                <address>
...
```

It also prints the reason why the request failed and the exact error like shown below:
```
2019-09-28 12:28:29,952 - restconf.device_configurator - INFO - Configuration failed
2019-09-28 12:28:29,952 - restconf.device_configurator - INFO - Bad Request
2019-09-28 12:28:29,952 - restconf.device_configurator - INFO - b'<errors xmlns="urn:ietf:params:xml:ns:yang:ietf-restconf">\n  <error>\n    <error-message>inconsistent value: Device refused one or more commands</error-message>\n    <error-path>/Cisco-IOS-XE-native:native</error-path>\n    <error-tag>invalid-value</error-tag>\n    <error-type>application</error-type>\n  </error>\n</errors>\n'
```

Also see the help of the script with `--help`.
```bash
$ python restconf_device_configurator.py --help
usage: restconf_device_configurator.py [-h] [-v]
                                       [-s {full,interfaces,ospf,bgp}]

Restconf device configurator

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Additionally print the config passed to the device
  -s {full,interfaces,ospf,bgp}, --section {full,interfaces,ospf,bgp}
                        Set what section should be configured, default: full
```

## Configuration
The whole configuration is done in the file `config.yaml`. It will be loaded and rendered into the `config.j2`
template. To specify what you'd like to configure on the device you can simply adjust the `config.yaml` file.
Every section is optional and can be ommited as a whole set, f.e. if you don't want to configure a bgp peering
just omit the whole `bgp:` section.

### General
In general it is possible to configure the hostname of the device by setting the `hostname` parameter.

```yaml
hostname: RT-7
```

### Interfaces
You can add additional interfaces by adding a an interface block to the `interfaces` hash. While rendering the template
will loop through the `interfaces` hash. Parameters to add an interface are the following:
* `name`: *required* - The number of the interface.
* `description`: *optional* - Add a meaningful interface description for easier identification.
* `ip`: *required* - The ip address to assign.
* `mask`: *required* - The network mask of the ip.
* `is_loopback`: *optional* - Will configure the interface as a loopback interface if `true`.
* `auto_negotiation`: *optional* - Set auto negotiation to true or false.

Example:
```yaml
interfaces:
  - name: 1
    description: RESTful API Interface
    ip: 10.3.255.107
    mask: 255.255.255.0
    is_loopback: false
    auto_negotiation: 'true'
```

### OSPF
Configure the ospf routing protocol by adding a section `ospf` to the `config.yaml`. Parameters are the following:
* `process`: *required* - The ospf process number.
* `router_id`: *required* - The router id, usually the ip address of the loopback interface.
* `passive_interfaces`: *optional* - Add interfaces which should not receive ospf hello packets. This parameter is a
list and can contain multiple interfaces.
* `networks`: *required* - A hash of networks to configure for ospf. Add more `network` sections to configure more
networks taking part in ospf.
  * `network`: *required* - The ip address of the network.
  * `mask`: *required* - The netmask of the network.
  * `area`: *required* - The ospf area number where the network should belong to.

Example:
```yaml
ospf:
  process: 1
  router_id: 7.7.7.7
  passive_interfaces:
    - Loopback1
  networks:
    - network: 10.3.255.0
      mask: 0.0.0.255
      area: 0
```

### BGP
Configure the bgp routing protocol by adding a section `bgp` to the `config.yaml`. Parameters are the following:
* `as_number`: *required* - The AS number the local network should have.
* `network_ip`: *required* - The ip address of the local network.
* `mask`: *required* - The netmask of the network.
* `neighbors`: *required* - A hash of neighbors which should get configured for bgp. Add more `id` sections to
add more neigbhorships.
  * `id`: *required* - The id of the bpg router. Usually the ip address of a loopback interface.
  * `remote-asn`: *required* - The AS number of the neighbor.
  * `max-hops`: *optional* - Define the number of max-hops, use 2 to also reach loopback interfaces.
  * `update_source`: *optional* - Define where to send bgp updates from.

Example:
```yaml
bgp:
  as_number: 7
  network_ip: 192.168.7.0
  mask: 255.255.255.0
  neighbors:
    - id: 20.20.20.20
      remote_asn: 20
      max_hops: 2
      update_source: '0'
```


## Idea
Our idea for this script was to make it as dynamic as possible. That's why we included the possibility
to be able to configure the whole device at once and also only one section. It is possible to also omit
whole sections in the `config.yaml` file which will not break the execution of the script by checking
in the template which sections are available. We also included basic error handling to check if a section
is available in the `config.yaml` file if you only want to configure a specifiy section with `-s` or `--section`.

The given network architecture required the configuration of several things. The interfaces had to be correctly
addressed and masked, with two of them being loopback interfaces thus requiring a `is_loopback` attribute for
the templating engine. An ospf process is required on the physical and on one loopback interface, both belong
to area 0, thus providing backbone connectivity. We chose ospfv2, because of the extendability of simply having
a list of added networks. A Bgp process is necessary so that the loopback interface outside of the ospf process
has full connectivity into the adjacent networks of our router.


