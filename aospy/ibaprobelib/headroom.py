# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://apstra.com/eula


def headroom_probe(label, src_node_label, dst_node_label):
    """
    Generates Probe to Calculate Headroom
    Parameters
    ----------
    label - str
        Descriptive name for the probe
    src_node_label - str
        label of the source server/switch for the headroom calculation
    dst_node_label - str
        label of the destination server/switch for the headroom calculation

    Returns
    -------
    payload - dict
        Payload to create headroom probe
    """

    nodes_query = ('node("system", name="system", system_id=not_none()).'
                   'out("hosted_interfaces").'
                   'node("interface", name="iface", if_name=not_none())')

    payload = {
        'label': label,
        'processors': [
            {'name': 'device interface tx traffic',
             'type': 'if_counter',
             'inputs': {},
             'outputs': {'out': 'device_int_tx_traffic'},
             'properties': {
                 'system_id': 'system.system_id',
                 'interface': 'iface.if_name',
                 'counter_type': 'tx_bytes',
                 'graph_query': nodes_query,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },
            {'name': 'device interface rx traffic',
             'type': 'if_counter',
             'inputs': {},
             'outputs': {'out': 'device_int_rx_traffic'},
             'properties': {
                 'system_id': 'system.system_id',
                 'interface': 'iface.if_name',
                 'counter_type': 'rx_bytes',
                 'graph_query': nodes_query,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },
            {'name': 'headroom path data',
             'type': 'headroom',
             'inputs': {'tx_bytes': 'device_int_tx_traffic',
                        'rx_bytes': 'device_int_rx_traffic'},
             'outputs': {'min_headroom': 'min_headroom_stage',
                         'max_headroom': 'max_headroom_stage',
                         'min_headroom_path': 'min_headroom_path_stage',
                         'max_headroom_path': 'max_headroom_path_stage',
                         'link_headroom': 'link_headroom_stage'},
             'properties': {
                 'pairs': [{
                     'src_system': src_node_label,
                     'dst_system': dst_node_label}
                 ]},
             'stages': [{'name': 'min_headroom',
                         'units': 'Bps', },
                        {'name': 'max_headroom',
                         'units': 'Bps'},
                        {'name': 'link_headroom',
                         'units': 'Bps'}]
             },
        ],
    }

    return payload
