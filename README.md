# NetApp C-Mode ZenPack

The ZenPack provides monitoring for NetApp data storage devices running ONTAP C-Mode. Data is collected through encrypted HTTPS requests to ONTAP REST API. You will need at least NetApp ONTAP 9.6 release installed. The ONTAP version 9.6 is the first release that provides API with highest maturity level. ZenPack is developed and tested against ONTAP 9.6P2. [Here](https://library.netapp.com/ecmdocs/ECMLP2856304/html/index.html) is the REST API documentation.

<a target="_blank" href="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-01.png"><img src="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-01.png" width="200px" height="200px" /></a><a target="_blank" href="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-02.png"><img src="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-02.png" width="200px" height="200px" /></a><a target="_blank" href="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-03.png"><img src="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-03.png" width="200px" height="200px" /></a><a target="_blank" href="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-04.png"><img src="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-04.png" width="200px" height="200px" /></a><a target="_blank" href="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-05.png"><img src="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-05.png" width="200px" height="200px" /></a><a target="_blank" href="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-06.png"><img src="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-06.png" width="200px" height="200px" /></a><a target="_blank" href="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-07.png"><img src="https://raw.githubusercontent.com/htolic/ZenPacks.CS.NetApp.CMode/master/screenshots/ss-07.png" width="200px" height="200px" /></a>

## Releases

Version 1.0.3 - [Download](https://github.com/htolic/ZenPacks.CS.NetApp.CMode/releases/download/v1.0.3/ZenPacks.CS.NetApp.CMode-1.0.3-py2.7.egg)

- Released: 2020-01-22
- Requires [PythonCollector ZenPack](https://www.zenoss.com/product/zenpacks/pythoncollector) (>=1.11.0)
- Requires [ZenPackLib ZenPack](https://www.zenoss.com/product/zenpacks/zenpacklib) (>=2.1.1)
- Compatible with Zenoss 6.2.1

## Table of contents

- [NetApp C-Mode ZenPack](#netapp-c-mode-zenpack)
  - [Releases](#releases)
  - [Table of contents](#table-of-contents)
  - [Features](#features)
    - [Device: NetApp CMode](#device-netapp-cmode)
    - [Component: Aggregates](#component-aggregates)
    - [Component: Cluster Nodes](#component-cluster-nodes)
    - [Component: Disks](#component-disks)
    - [Component: Licenses](#component-licenses)
    - [Component: Plexes](#component-plexes)
    - [Component: RAID Groups](#component-raid-groups)
    - [Component: Spare Disks](#component-spare-disks)
    - [Component: Volumes](#component-volumes)
  - [Usage](#usage)
  - [Changelog](#changelog)

## Features

### Device: NetApp CMode

- Creates Device Class /Storage/NetApp/CMode
- Adds Modeler Plugin CS.NetApp.CMode.Device
  - Models information about device (Cluster ONTAP Version)
- Adds Modeler Plugin CS.NetApp.CMode.License
  - Models information about applied licences (name, scope, state, owner, serial_number, active, evaluation, compliance)
- Adds Modeler Plugin CS.NetApp.CMode.ClusterNode
  - Models information about cluster nodes (name, serial_number, location, model, version, membership)
  - Models information about spare disks (name, disk_uid, serialnr, model, vendor, firmware, usable_size, rpm, type, spare_class, pool, bay)
- Adds Modeler Plugin CS.NetApp.CMode.Storage
  - Models information about aggregates (name, state, raid_size, disk_count, total_bytes)
  - Models information about plexes (name, online, state, pool, resync)
  - Models information about volumes (name, uuid, state, style, tiering_policy, type, is_flexclone, nas_path, nas_security_style, snapshot_policy, svm, size, space available, space used, over_provisioned, snapshot_reserve)
  - Models information about RAID groups (name, cache_tier, degraded, recomputing_parity_active, reconstruct_active)
  - Models information about disks (name, position, state, type, usable_size)
- Configuration Properties set on class /Storage/NetApp/CMode
  - zDeviceTemplates - value: []
  - zCollectorPlugins - value: [CS.NetApp.CMode.Device, CS.NetApp.CMode.License, CS.NetApp.CMode.ClusterNode, CS.NetApp.CMode.Storage]
  - zPythonClass - value: ZenPacks.CS.NetApp.CMode.NetAppDevice
  - zSnmpMonitorIgnore - value: true
- New Configuration Properties
  - zNetAppAPI - default: [empty] (if empty, https://${device.manageIp}/api is used)
  - zNetAppUser - default: root
  - zNetAppPassword - default: [empty]

### Component: Aggregates

- Monitoring Template
  - Python datasource_plugin: ZenPacks.CS.NetApp.CMode.dsplugins.Aggregates
  - Data Points collected and Graph Definitions:
    - Graph "Space Usage" - aggregate_used

### Component: Cluster Nodes

- Monitoring Template
  - Python datasource_plugin: ZenPacks.CS.NetApp.CMode.dsplugins.ClusterNodes
  - Data Points collected and Graph Definitions:
    - Graph "Node Uptime" - clusternode_uptime

### Component: Disks

- No Monitoring Template available

### Component: Licenses

- No Monitoring Template available

### Component: Plexes

- No Monitoring Template available

### Component: RAID Groups

- No Monitoring Template available

### Component: Spare Disks

- No Monitoring Template available

### Component: Volumes

- Monitoring Template
  - Python datasource_plugin: ZenPacks.CS.NetApp.CMode.dsplugins.Volumes
  - Data Points collected and Graph Definitions:
    - Graph "Latency" - latency_read, latency_write, latency_other, latency_total
    - Graph "IOPS" - iops_read, iops_write, iops_other, iops_total
    - Graph "Throughput" - throughput_read, throughput_write, throughput_other, throughput_total

## Usage

First make sure you are using supported Zenoss version and have ZenPack dependencies on right version installed. Then proceed to download and install this ZenPack using a standard procedure for your version of Zenoss.

This ZenPack monitors NetApp storage devices running at least NetApp ONTAP 9.6 CMode. It is tested against NetApp ONTAP Release 9.6P2 CMode. NetApp 7-Mode is not supported with this ZenPack and it will not work.

After installation the device class /Storage/NetApp/CMode is created. Go ahead and modify Configuration Properties for this device class. Look for properties that have name starting with zNetApp.

- zNetAppAPI: This should be URL where NetApp REST API is. Usually it https://<hostname or ip>/api where <hostname or ip> is your NetApp Conroller address. Leave this empty if IP address you enter when adding device is the same as IP address of NetApp Controller management interface. If empty ZenPack will try with https://{device.manageIp}/api
- zNetAppUser: If you have user prepared especially for Zenoss monitoring then use that user. The user must have privilege to make queries to ZAPI.
- zNetAppPassword: Enter a password related to user that you use in zNetAppUser property.

Go ahead, add your devices to /Storage/NetApp/CMode and wait for modelling to finish. If everything goes well, you should see components showing up on device details page. In a couple of minutes the graph data should start populating too.

## Changelog

Version 1.0.3

- Initial release