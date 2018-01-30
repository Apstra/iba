# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://apstra.com/eula


def eastwest_traffic_probe(label, average_period, history_sample_count):
    """
    Generates probe to calculate total East/West Traffic
    Parameters
    ----------
    label - str
        Descriptive name for the probe
    average_period - int
        period over which to average input counter samples
    history_sample_count - int
        number of samples of history to maintain

    Returns
    -------
    payload - dict
        Payload to create east west traffic probe
    """

    server_facing_interface_query = \
        ('node("system", name="system", system_id=not_none(), role="leaf").'
         'out("hosted_interfaces").'
         'node("interface", name="iface", if_name=not_none()).'
         'out("link").'
         'node("link", link_type="ethernet").'
         'in_("link").'
         'node("interface").'
         'in_("hosted_interfaces").'
         'node("system", system_type="server")')

    external_router_facing_interface_query = \
        ('node("system", name="system", system_id=not_none()).'
         'out("hosted_interfaces").'
         'node("interface", name="iface", if_name=not_none()).'
         'out("link").'
         'node("link", link_type="ethernet", role="to_external_router")')

    payload = {
        'label': label,
        'processors': [
            {'name': 'leaf server traffic counters',
             'type': 'if_counter',
             'inputs': {},
             'outputs': {'out': 'server_traffic_counters'},
             'properties': {
                 'system_id': 'system.system_id',
                 'interface': 'iface.if_name',
                 'counter_type': 'rx_bytes',
                 'graph_query': server_facing_interface_query,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },

            {'name': 'server traffic average',
             'type': 'periodic_average',
             'inputs': {'in': 'server_traffic_counters'},
             'outputs': {'out': 'server_traffic_avg'},
             'properties': {
                 'period': average_period,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },

            {'name': 'external router south-north link traffic',
             'type': 'if_counter',
             'inputs': {},
             'outputs': {'out': 'ext_router_interface_traffic'},
             'properties': {
                 'system_id': 'system.system_id',
                 'interface': 'iface.if_name',
                 'counter_type': 'tx_bytes',
                 'graph_query': external_router_facing_interface_query,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },
            {'name': 'external router south-north links traffic average',
             'type': 'periodic_average',
             'inputs': {'in': 'ext_router_interface_traffic'},
             'outputs': {'out': 'ext_router_interface_traffic_avg'},
             'properties': {
                 'period': average_period,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },

            {'name': 'total server traffic',
             'type': 'sum',
             'inputs': {'in': 'server_traffic_avg'},
             'outputs': {'out': 'total_server_traffic'},
             'properties': {
                 'group_by': []
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },
            {'name': 'server generated traffic average',
             'type': 'periodic_average',
             'inputs': {'in': 'total_server_traffic'},
             'outputs': {'out': 'total_server_generated_traffic_average'},
             'properties': {
                 'period': average_period,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },
            {'name': 'total server traffic history',
             'type': 'accumulate',
             'inputs': {'in': 'total_server_generated_traffic_average'},
             'outputs': {'out': 'total_server_traffic_history'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': history_sample_count,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },

            {'name': 'south-north traffic',
             'type': 'sum',
             'inputs': {'in': 'ext_router_interface_traffic_avg'},
             'outputs': {'out': 'total_outgoing_traffic'},
             'properties': {
                 'group_by': []
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },
            {'name': 'outgoing_traffic_average',
             'type': 'periodic_average',
             'inputs': {'in': 'total_outgoing_traffic'},
             'outputs': {'out': 'total_outgoing_traffic_average'},
             'properties': {
                 'period': average_period,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },
            {'name': 'south-north traffic history',
             'type': 'accumulate',
             'inputs': {'in': 'total_outgoing_traffic_average'},
             'outputs': {'out': 'total_outgoing_traffic_timeseries'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': history_sample_count,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],

             },

            {'name': 'east-west traffic',
             'type': 'subtract',
             'inputs': {'minuend': 'total_server_generated_traffic_average',
                        'subtrahend': 'total_outgoing_traffic_average'},
             'outputs': {'out': 'eastwest_traffic'},
             'properties': {},
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },
            {'name': 'east-west traffic history',
             'type': 'accumulate',
             'inputs': {'in': 'eastwest_traffic'},
             'outputs': {'out': 'eastwest_traffic_history'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': history_sample_count,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],

             },
        ],
    }

    return payload
