# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://apstra.com/eula


def interface_status():
    """
    Generates Probe that raises anomalies when interface status is down on any
    leaf-spine interface in the fabric. The goal for this probe is to mimic builtin
    interface status anomalies so people can understand the probe creation process
    with simple examples.

    Returns
    -------
    payload - dict
        Payload to create interface flapping probe
    """
    nodes_query = ('node("system", name="system", system_id=not_none()).'
                   'out("hosted_interfaces").'
                   'node("interface", name="iface", if_name=not_none()).'
                   'out("link").'
                   'node("link", role="spine_leaf")')

    return {
        'label': 'interface status anomalies',
        'processors': [
            {
                'name': 'collect leaf-spine interface status',
                'type': 'generic_data_collector',
                'outputs': {'out': 'leaf_spine_if_status'},
                'properties': {
                    'service_name': 'interface_iba',
                    'data_type': 'ns',
                    'system_id': 'system.system_id',
                    'key': 'iface.if_name',
                    'graph_query': nodes_query,
                },
            },
            {
                'name': 'leaf-spine down interfaces',
                'type': 'in_range',
                'inputs': {'in': 'leaf_spine_if_status'},
                'outputs': {'out': 'leaf_spine_if_down'},
                'properties': {
                    'range': {
                        'min': 1,
                        'max': 1
                    }
                },
            },
            {
                'name': 'leaf-spine interface down anomaly',
                'type': 'anomaly',
                'inputs': {'in': 'leaf_spine_if_down'},
                'outputs': {'out': 'leaf_spine_if_down_anomaly'},
            },
        ]
    }
