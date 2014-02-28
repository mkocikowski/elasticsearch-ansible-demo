#!/usr/bin/env python

# server.manager.set_meta(server, {'group': 'basic,search'})

import os
import json
import pprint

import novaclient.auth_plugin
import novaclient.client



def get_servers(env):

    client = novaclient.client.Client(
        version = '2',
        username = env['OS_USERNAME'],
        api_key = env['OS_PASSWORD'],
        auth_url = env['OS_AUTH_URL'],
        region_name = env['OS_REGION_NAME'],
        project_id = env['OS_PROJECT_ID'],
        auth_system = env['OS_AUTH_SYSTEM'],
        auth_plugin = novaclient.auth_plugin.load_plugin(env['OS_AUTH_SYSTEM']),
    )
    servers = client.servers.list()
    # don't return servers which are either spinnning up or down
    servers = [s for s in servers if s.status == 'ACTIVE']
    return servers

inventory = dict()
for server in get_servers(os.environ):
    # when cloud instances are spun up, metadata is attached to them, which
    # defines their roles / the groups to which they belong. That metadata is
    # accessed through server.metadata['groups'], the value of which is a
    # string, in which group names are separated by comma. Servers which don't
    # have 'group' metadata key are skipped here.
    if 'groups' not in server.metadata:
        continue
    groups = server.metadata['groups'].split(",")
    groups = [s.strip().lower() for s in groups]
    for group in groups:
        # a node may belong to multiple groups. Add its IP address to each of
        # the ansible inventory groups to which it belongs.
        if group not in inventory:
            inventory[group] = {'hosts': [], 'children': {}, 'vars': {},}
        address = server.accessIPv4
        if address and address not in inventory[group]['hosts']:
            inventory[group]['hosts'].append(str(address))

print(json.dumps(inventory))

