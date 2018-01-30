# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://apstra.com/eula

def hotcold_ifcounter_probe(label, if_counter, min, max, max_hot_interface_percentage,
                                   max_cold_interface_percentage, average_period, duration,
                                   threshold_duration, anomaly_history_count):

    """
    Generates Probe to Determine Hot/Cold Fabric Interface Counters
    Parameters
    ----------
    label - str
        Descriptive name for the probe
    if_counter - int
        Type of interface counter
    min - int
        minimum level of counter
    max - int
        maximum level of counter
    max_hot_interface_percentage - int
        maximum percentage of hot interfaces on a device
    max_cold_interface_percentage - int
        maximum percentage of cold interfaces on a device
    average_period - int
        period over which to average input counter samples
    duration - int
        number of seconds of recent-history over which interface counter
        hot/cold status will be considered
    threshold_duration - int
        sum total of number of seconds of recent-history for which
        interface must be hot/cold for anomaly to be raised
    anomaly_history_count - int
        number of anomaly flaps that will be recorded for inspection

    Returns
    -------
        payload - dict
        Payload to create hot cold interface probe
    """

    nodes_query = \
        ('node("system", name="system", deploy_mode="deploy", role="leaf").'
         'out("hosted_interfaces").'
         'node("interface", name="iface", if_name=not_none()).'
         'out("link").'
         'node("link", name="link", link_type="ethernet").'
         'in_("link").'
         'node("interface").'
         'in_("hosted_interfaces").'
         'node("system", name="dst_system", deploy_mode="deploy", role="spine")')

    payload = {
        'label': label,
        'processors': [
            {'name': 'leaf interface traffic',
             'type': 'if_counter',
             'inputs' : {},
             'outputs': {'out': 'leaf_int_traffic'},
             'properties': {
                 'link_role': 'link.role',
                 'system_id': 'system.system_id',
                 'interface': 'iface.if_name',
                 'counter_type': if_counter,
                 'graph_query': nodes_query,
             },
             'stages' : [],
            },

            {'name': 'leaf interface tx avg',
             'type': 'periodic_average',
             'inputs': {'in': 'leaf_int_traffic'},
             'outputs': {'out': 'leaf_int_tx_avg'},
             'properties': {
                 'period': average_period,
             },
             'stages' : [{'name' : 'out',
                          'units':'Bps'}],
            },

            {'name': 'leaf int traffic accumulate',
             'type': 'accumulate',
             'inputs': {'in': 'leaf_int_traffic'},
             'outputs': {'out': 'leaf_int_traffic_accumulate'},
             'properties': {
                 'total_duration': duration,
                 'max_samples': 1024,
             },
             'stages' : [],
            },
            {'name': 'live leaf interface hot',
             'type': 'in_range',
             'inputs': {'in': 'leaf_int_tx_avg'},
             'outputs': {'out': 'live_leaf_int_hot'},
             'properties': {
                 'range': {'max': max},
             },
             'stages' : [],
            },

            {'name': 'live leaf interface cold',
             'type': 'in_range',
             'inputs': {'in': 'leaf_int_tx_avg'},
             'outputs': {'out': 'live_leaf_int_cold'},
             'properties': {
                 'range': {'min': min},
             },
             'stages' : [],
            },

            {'name': 'sustained hot leaf interfaces',
             'type': 'time_in_state',
             'inputs': {'in': 'live_leaf_int_hot'},
             'outputs': {'out': 'hot_leaf_int'},
             'properties': {
                 'time_window': duration,
                 'state_range': {'true': [{'max': threshold_duration}]},
             },
             'stages' : [],
            },
            {'name': 'sustained cold leaf interface',
             'type': 'time_in_state',
             'inputs': {'in': 'live_leaf_int_cold'},
             'outputs': {'out': 'cold_leaf_int'},
             'properties': {
                 'time_window': duration,
                 'state_range': {'true': [{'max': threshold_duration}]},
             },
             'stages' : [],
            },


            {'name': 'anomaly hot leaf int traffic',
             'type': 'anomaly',
             'inputs': {'in': 'hot_leaf_int'},
             'outputs': {'out': 'anomaly_hot_int_traffic'},
             'properties' : {},
             'stages' : [],
            },
            {'name': 'anomaly cold leaf int traffic',
             'type': 'anomaly',
             'inputs': {'in': 'cold_leaf_int'},
             'outputs': {'out': 'anomaly_cold_int_traffic'},
             'properties' : {},
             'stages' : [],
            },

            {'name': 'leaf int hot anomaly history',
             'type': 'accumulate',
             'inputs': {'in': 'anomaly_hot_int_traffic'},
             'outputs': {'out': 'int_hot_accumulate_anomaly'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': anomaly_history_count,
             },
             'stages' : [],
            },
            {'name': 'leaf int cold anomaly history',
             'type': 'accumulate',
             'inputs': {'in': 'anomaly_cold_int_traffic'},
             'outputs': {'out': 'anomaly_cold_int_accumulate'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': anomaly_history_count,
             },
             'stages' : [],
            },

            {'name': 'interface sum per device',
             'type': 'sum',
             'inputs': {'in': 'leaf_int_tx_avg'},
             'outputs': {'out': 'if_counter_sum_per_device'},
             'properties': {
                 'group_by': ['system_id']
             },
             'stages' : [],
            },
            {'name': 'interface sum per device per link role',
             'type': 'sum',
             'inputs': {'in': 'leaf_int_tx_avg'},
             'outputs': {'out': 'if_counter_sum_per_device_per_role'},
             'properties': {
                 'group_by': ['system_id', 'link_role']
             },
             'stages' : [],
            },

            {'name': 'system percent hot',
             'type': 'match_perc',
             'inputs': {'in' : 'hot_leaf_int'},
             'outputs': {'out' : 'system_perc_hot'},
             'properties' : {
                 'reference_state': 'true',
                 'group_by' : ['system_id']},
             'stages' : [],
            },
            {'name': 'system percent cold',
             'type': 'match_perc',
             'inputs': {'in' : 'cold_leaf_int'},
             'outputs': {'out' : 'system_perc_cold'},
             'properties' : {
                 'reference_state': 'true',
                 'group_by' : ['system_id']},
             'stages' : [],
            },

            {'name': 'device hot',
             'type': 'in_range',
             'inputs': {'in': 'system_perc_hot'},
             'outputs': {'out': 'device_hot_anomalous'},
             'properties': {
                 'range': {'max': max_hot_interface_percentage},
             },
             'stages' : [],
            },
            {'name': 'device cold',
             'type': 'in_range',
             'inputs': {'in': 'system_perc_cold'},
             'outputs': {'out': 'device_cold_anomalous'},
             'properties': {
                 'range': {'max': max_cold_interface_percentage},
             },
             'stages' : [],
            },

            {'name': 'anomaly device hot',
             'type': 'anomaly',
             'inputs': {'in': 'device_hot_anomalous'},
             'outputs': {'out': 'device_hot_anomaly'},
             'properties' : {},
             'stages' : [],
            },
            {'name': 'anomaly device cold',
             'type': 'anomaly',
             'inputs': {'in': 'device_cold_anomalous'},
             'outputs': {'out': 'device_cold_anomaly'},
             'properties' : {},
             'stages' : [],
            },

            {'name': 'anomaly device hot history',
             'type': 'accumulate',
             'inputs': {'in': 'device_hot_anomaly'},
             'outputs': {'out': 'device_hot_anomaly_timeseries'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': anomaly_history_count,
             },
             'stages' : [],
            },
            {'name': 'anomaly device cold history',
             'type': 'accumulate',
             'inputs': {'in': 'device_cold_anomaly'},
             'outputs': {'out': 'device_cold_anomaly_timeseries'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': anomaly_history_count,
             },
             'stages' : [],
            },
        ],
    }

    return payload
