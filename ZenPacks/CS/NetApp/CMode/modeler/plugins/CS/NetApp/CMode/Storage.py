"""Models NetApp CMode device using ONTAP REST API"""

# stdlib Imports
import json
import urllib
import base64

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap


class Storage(PythonPlugin):
    """NetApp CMode modeler plugin."""

    relname = 'aggregates'
    modname = 'ZenPacks.CS.NetApp.CMode.Aggregate'

    requiredProperties = (
        'zNetAppAPI',
        'zNetAppUser',
        'zNetAppPassword',
        )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        log.info('%s: collecting data', device.id)

        baseUrl = getattr(device, 'zNetAppAPI', None)
        if not baseUrl:
            manageIp = getattr(device, 'manageIp', None)
            if not manageIp:
                log.error("Please fill in zNetAppAPI property")
                returnValue(None)
            baseUrl = 'https://{ip}/api'.format(ip=manageIp)
        
        un = getattr(device, 'zNetAppUser', None)
        pw = getattr(device, 'zNetAppPassword', None)
	if un and pw:
            basic = base64.encodestring('{un}:{pw}'.format(un=un, pw=pw))
            auth = {'Authorization': 'Basic {b}'.format(b=basic.strip())}
        else:
            auth = {}
            log.info('Please consider using zNetAppUser and zNetAppPassword for authorization')

        try:
            response = yield getPage('{url}/storage/aggregates?fields=name,state,block_storage.primary.raid_size,block_storage.primary.disk_count,plexes,space.block_storage.size&return_timeout=15'.format(url=baseUrl), headers=auth)
            response = json.loads(response)
        except Exception, e:
            log.error('%s: %s', device.id, e)
            returnValue(None)

        rm = self.relMap()
        for record in response['records']:
            om = self.objectMap()
            om.id = self.prepId(record['name'])
            om.aggr_name = record['name']
            om.aggr_state = record['state']
            om.raid_size = record['block_storage']['primary']['raid_size']
            om.disk_count = record['block_storage']['primary']['disk_count']
            om.total_bytes = record['space']['block_storage']['size']
            rm.append(om)

            compname = 'aggregates/{0}'.format(om.id)
            (plexrm, raidgrouprm, diskrm) = yield self.plexes(device, record['uuid'], baseUrl, auth, compname, log)
            volumerm = yield self.volumes(device, record['uuid'], baseUrl, auth, compname, log)

        returnValue([rm] + [plexrm] + [raidgrouprm] + [diskrm]  + [volumerm])

    def process(self, device, results, log):
        """Process results. Return iterable of datamaps or None."""
        return results

    @inlineCallbacks
    def plexes(self, device, uuid, baseUrl, auth, compname, log):
        try:
            response = yield getPage('{url}/storage/aggregates/{oid}/plexes?fields=online,state,pool,resync,raid_groups&return_records=true&return_timeout=15'.format(url=baseUrl,oid=uuid), headers=auth)
            response = json.loads(response)
        except Exception, e:
            log.error('%s: %s', device.id, e)
            returnValue(None)

        rm = RelationshipMap()
        rm.compname = compname
        rm.relname = 'plexs'
        rm.modname = 'ZenPacks.CS.NetApp.CMode.Plex'
        rm.classname = 'Plex'

        for record in response['records']:
            om = ObjectMap()
            om.modname = 'ZenPacks.CS.NetApp.CMode.Plex'
            om.id = self.prepId(record['name'])
            om.plex_name = record['name']
            om.online = record['online']
            om.plex_state = record['state']
            om.pool = record['pool']
            om.resync = record['resync']['active']
            rm.append(om)

            compname = '{parent}/plexs/{id}'.format(parent=compname, id=om.id)
            raidgrouprm, diskrm = self.raidgroups(record['raid_groups'], compname, log)
        
        returnValue((rm, raidgrouprm, diskrm))

    @inlineCallbacks
    def volumes(self, device, uuid, baseUrl, auth, compname, log):
        try:
            response = yield getPage('{url}/storage/volumes?fields=aggregates,name,uuid,space.size,state,style,tiering,type,svm.name,snapshot_policy.name,nas.path,clone,space.available,space.used,space.over_provisioned,space.snapshot.reserve_percent,nas.security_style&return_records=true&return_timeout=15'.format(url=baseUrl,oid=uuid), headers=auth)
            response = json.loads(response)
        except Exception, e:
            log.error('%s: %s', device.id, e)
            returnValue(None)

        rm = RelationshipMap()
        rm.compname = compname
        rm.relname = 'volumes'
        rm.modname = 'ZenPacks.CS.NetApp.CMode.Volume'
        rm.classname = 'Volume'

        for record in response['records']:
            if uuid != record['aggregates'][0]['uuid']: continue
            om = ObjectMap()
            om.modname = 'ZenPacks.CS.NetApp.CMode.Volume'
            om.id = self.prepId(record['uuid'])
            om.volume_name = record['name']
            om.volume_uuid = record['uuid']
            om.state = record['state']
            om.style = record['style']
            om.tiering_policy = record['tiering']['policy']
            om.type = record['type']
            om.is_flexclone = record['clone']['is_flexclone']
            om.nas_path = record['nas']['path']
            om.nas_security_style = record['nas']['security_style']
            om.snapshot_policy = record['snapshot_policy']['name']
            om.svm = record['svm']['name']
            om.size = record['space']['size']
            om.available = record['space']['available']
            om.used = record['space']['used']
            om.over_provisioned = record['space']['over_provisioned']
            om.snapshot_reserve = record['space']['snapshot']['reserve_percent']
            rm.append(om)

        returnValue(rm)

    def raidgroups(self, raidgroups, compname, log):
        rm = RelationshipMap()
        rm.compname = compname
        rm.relname = 'raidGroups'
        rm.modname = 'ZenPacks.CS.NetApp.CMode.RaidGroup'
        rm.classname = 'RaidGroup'

        for raid in raidgroups:
            om = ObjectMap()
            om.modname = 'ZenPacks.CS.NetApp.CMode.RaidGroup'
            om.id = self.prepId(raid['name'])
            om.rg_name = raid['name']
            om.cache_tier = raid['cache_tier']
            om.degraded = raid['degraded']
            om.recomputing_parity_active = raid['recomputing_parity']['active']
            om.reconstruct_active = raid['reconstruct']['active']
            rm.append(om)

            compname = '{parent}/raidGroups/{id}'.format(parent=compname, id=om.id)
            diskrm = self.disks(raid['disks'], compname, log)

        return (rm, diskrm)

    def disks(self, disks, compname, log):
        rm = RelationshipMap()
        rm.compname = compname
        rm.relname = 'disks'
        rm.modname = 'ZenPacks.CS.NetApp.CMode.Disk'
        rm.classname = 'Disk'

        for disk in disks:
            om = ObjectMap()
            om.modname = 'ZenPacks.CS.NetApp.CMode.Disk'
            om.id = self.prepId(disk['disk']['name'])
            om.disk_name = disk['disk']['name']
            om.position = disk['position']
            om.state = disk['state']
            om.type = disk['type']
            om.usable_size = disk['usable_size']
            rm.append(om)

        return rm

