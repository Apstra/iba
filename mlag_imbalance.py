# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://apstra.com/eula

def mlag_imbalance_probe(label, duration, std_max):

    """

    Parameters
    ----------
    label - str
        Descriptive name for the probe
    duration - int
        number of seconds of recent-history in which we
        will consider mlag imbalance
    std_max - int
        maxiumum standard deviation used for imbalance detection
    Returns
    -------
    payload - dict
        Payload to create mlag imbalance probe
    """

    interface_query = (
        'match(node("system", name="leaf", role="leaf").'
        'in_("composed_of_systems").'
        'node("redundancy_group", name="rack").'
        'out("hosted_interfaces").'
        'node("interface", name="mlag_interface", if_type="port_channel").'
        'out("composed_of").'
        'node("interface", name="leaf_port_channel", if_type="port_channel").'
        'out("composed_of").'
        'node("interface", name="leaf_interface").'
        'out("link").'
        'node("link").'
        'in_("link").'
        'node("interface", name="server_interface").'
        'in_("hosted_interfaces").'
        'node("system", name="server", role="l2_server"),'
        'node("system", name="leaf").'
        'out("hosted_interfaces").'
        'node("interface", name="leaf_interface"))')


    payload = {
        'label': label,
        'processors': [
            # 0
            {'name': 'mlag interface traffic',
             'type': 'if_counter',
             'inputs' : {},
             'outputs': {'out': 'mlag_int_traffic'},
             'properties': {
                 'mlag_id': 'mlag_interface.mlag_id',
                 'server': 'server.label',
                 'leaf' : 'leaf.label',
                 'rack' : 'rack.label',
                 'system_id': 'leaf.system_id',
                 'interface': 'leaf_interface.if_name',
                 'counter_type': 'tx_bytes',
                 'graph_query': interface_query,
             },
             'stages' : [{'name' : 'out',
                          'units':'Bps'}],
            },
            #1
            {'name': 'mlag interface traffic history',
             'type': 'accumulate',
             'inputs' : {'in' : 'mlag_int_traffic'},
             'outputs': {'out': 'mlag_int_traffic_history'},
             'properties': {
                 'total_duration' : duration,
                 'max_samples' : 100,
             },
             'stages' : [{'name' : 'out',
                          'units':'Bps'}],
            },
            #2
            {'name': 'mlag interface traffic average',
             'type': 'periodic_average',
             'inputs': {'in': 'mlag_int_traffic'},
             'outputs': {'out': 'mlag_int_traffic_avg'},
             'properties': {
                 'period': duration,
             },
             'stages' : [{'name' : 'out',
                          'units':'Bps'}],
            },

            #3
            {'name': 'mlag interface traffic imbalance',
             'type': 'std_dev',
             'inputs': {'in': 'mlag_int_traffic_avg'},
             'outputs': {'out': 'mlag_int_traffic_imbalance'},
             'properties': {
                 'group_by': ['rack', 'mlag_id']
             },
             'stages' : [{'name' : 'out',
                          'units':'Bps'}],
            },
            #4
            {'name': 'live mlag imbalance',
             'type': 'in_range',
             'inputs': {'in': 'mlag_int_traffic_imbalance'},
             'outputs': {'out': 'live_mlag_imbalance'},
             'properties': {
                 'range': {'max': std_max, 'min': None},
             },
             'stages' : [],
            },
            #5
            {'name': 'mlag interface imbalance anomaly',
             'type': 'anomaly',
             'inputs': {'in': 'live_mlag_imbalance'},
             'outputs': {'out': 'mlag_int_imbalance_anomaly'},
             'properties' : {},
             'stages' : [],
            },
            #6
            {'name': 'mlag imbalance per rack percent',
             'type': 'match_perc',
             'inputs' : {
                 'in' : 'live_mlag_imbalance'},
             'outputs' : {
                 'out' : 'mlag_imbalance_rack_perc'},
             'properties' : {
                 'reference_state': 'true',
                 'group_by' : ['rack']},
             'stages' : [],
            },

            #7
            {'name': 'port-channel interface std-dev',
             'type': 'std_dev',
             'inputs': {'in': 'mlag_int_traffic_avg'},
             'outputs': {'out': 'port_channel_int_std_dev'},
             'properties': {
                 'group_by': ['rack', 'mlag_id', 'leaf']
             },
             'stages' : [{'name' : 'out',
                          'units':'Bps'}],
            },
            #8
            {'name': 'live port-channel imbalance',
             'type': 'in_range',
             'inputs': {'in': 'port_channel_int_std_dev'},
             'outputs': {'out': 'live_port_channel_imbalance'},
             'properties': {
                 'range': {'max': std_max, 'min': None},
             },
             'stages' : [],
            },
            #9
            {'name': 'port-channel imbalance anomaly',
             'type': 'anomaly',
             'inputs': {'in': 'live_port_channel_imbalance'},
             'outputs': {'out': 'port_channel_links_anomaly'},
             'properties' : {},
             'stages' : [],
            },
            #10
            {'name': 'port-channel imbalance per rack',
             'type': 'match_perc',
             'inputs' : {
                 'in' : 'live_port_channel_imbalance'},
             'outputs' : {
                 'out' : 'port_channel_imbalance_per_rack'},
             'properties' : {
                 'reference_state': 'true',
                 'group_by' : ['rack']},
             'stages' : [],
            },

            #11
            {'name': 'port-channel total traffic',
             'type': 'sum',
             'inputs' : {
                 'in' : 'mlag_int_traffic_avg'},
             'outputs' : {
                 'out' : 'mlag_port_channel_total'},
             'properties' : {
                 'group_by' : ['rack', 'mlag_id', 'leaf']},
             'stages' : [{'name' : 'out',
                          'units':'Bps'}],
            },
            #12
            {'name': 'mlag port-channel traffic std-dev',
             'type': 'std_dev',
             'inputs': {'in': 'mlag_port_channel_total'},
             'outputs': {'out': 'mlag_port_channel_imbalance'},
             'properties': {
                 'group_by': ['rack', 'mlag_id']
             },
             'stages' : [{'name' : 'out',
                          'units':'Bps'}],
            },
            #13
            {'name': 'live mlag port-channel imbalance',
             'type': 'in_range',
             'inputs': {'in': 'mlag_port_channel_imbalance'},
             'outputs': {'out': 'mlag_port_channel_imbalance_out_of_range'},
             'properties': {
                 'range': {'max': std_max, 'min': None},
             },
             'stages' : [],
            },
            #14
            {'name': 'mlag_port-channel imbalance anomaly',
             'type': 'anomaly',
             'inputs': {'in': 'mlag_port_channel_imbalance_out_of_range'},
             'outputs': {'out': 'mlag_port_channel_imbalance_anomaly'},
             'properties' : {},
             'stages' : [],
            },
            #15
            {'name': 'mlag port-channel imbalance per rack',
             'type': 'match_perc',
             'inputs' : {
                 'in' : 'mlag_port_channel_imbalance_anomaly'},
             'outputs' : {
                 'out' : 'mlag_port_channel_imbalance_anomaly_per_rack'},
             'properties' : {
                 'reference_state': 'true',
                 'group_by' : ['rack']},
             'stages' : [],
            },
        ],
    }

    return payload