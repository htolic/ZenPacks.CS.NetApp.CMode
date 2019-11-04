"""Metrics monitor using NetApp CMode 9.6 API."""

# Logging
import logging
log = logging.getLogger('zen.NetApp.CMode')

# stdlib Imports
import json
import time
import urllib
import base64

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue, succeed
from twisted.web.client import getPage

# Zenoss Imports
from Products.ZenUtils.Utils import prepId

# PythonCollector Imports
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import (
    PythonDataSourcePlugin,
    )


class Aggregates(PythonDataSourcePlugin):

    """Aggregates data source plugin."""


    @classmethod
    def config_key(cls, datasource, context):
        return (
            context.device().id,
            datasource.getCycleTime(context),
            'netapp-aggregates',
            )

    @classmethod
    def params(cls, datasource, context):
        return {
            'ip': context.device().manageIp,
            'api': context.zNetAppAPI,
            'un': context.zNetAppUser,
            'pw': context.zNetAppPassword,
            }

    @inlineCallbacks
    def collect(self, config):
        data = self.new_data()

        params = config.datasources[0].params
        baseUrl = params['api']
        if not baseUrl:
            if not params['ip']:
                log.error("Please fill in zNetAppAPI property")
                returnValue(None)
            baseUrl = 'https://{ip}/api'.format(ip=params['ip'])

        un = params['un']
        pw = params['pw']
        if un and pw:
            basic = base64.encodestring('{un}:{pw}'.format(un=un, pw=pw))
            auth = {'Authorization': 'Basic {b}'.format(b=basic.strip())}
        else:
            auth = {}
            log.info('Please consider using zNetAppUser and zNetAppPassword for authorization')

        try:
            response = yield getPage('{url}/storage/aggregates?fields=uuid,space.block_storage.used&return_records=true&return_timeout=15'.format(url=baseUrl), headers=auth)
            response = json.loads(response)
        except Exception, e:
            log.error(e)
            returnValue(None)

        for datasource in config.datasources:
            for record in response['records']:
                if datasource.component == prepId(record['name']):
                    for datapoint_id in (x.id for x in datasource.points):
                        if datapoint_id == 'used':
                            value = int(record['space']['block_storage']['used'])
                            dpname = '_'.join((datasource.datasource, datapoint_id))
                            data['values'][datasource.component][dpname] = (value, 'N')

        returnValue(data)

