# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://apstra.com/eula

def specific_hotcold_ifcounter_probe(label, interfaces, if_counter, min, max,
                                            max_hot_interface_percentage,
                                            max_cold_interface_percentage,
                                            average_period, duration,
                                            threshold_duration,
                                            anomaly_history_count):

    """
    Generates Probe to Determine Hot/Cold for Specific Interface Counters
    Parameters
    ----------
    label - str
        Descriptive name for the probe
    interfaces - list[dict]
        system_label - str
            label of system node that hosts given interface
        interface_name - str
            if_name of interface node representing given interface
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
        Payload to create specific interface hot cold probe
    """

    def generate_intf_tuple_list_string(interfaces):
        rval = '['
        for intf in interfaces:
            rval = rval + "('" + \
                   intf['system_label'] + "','" + \
                   intf['interface_name'] + "'),"
        rval = rval + ']'
        return rval

    intf_tuple_list_string = generate_intf_tuple_list_string(interfaces)

    nodes_query = \
        ('node("system", name="system", system_id=not_none()).'
         'out("hosted_interfaces").'
         'node("interface", name="iface", if_name=not_none()).'
         'out("link").'
         'node("link", name="link", link_type="ethernet").'
         'where(lambda system, iface: (system.label, iface.if_name) in %s)' % \
         intf_tuple_list_string)

    payload = {
        'label': label,
        'processors': [
            {'name': 'device interface traffic',
             'type': 'if_counter',
             'inputs' : {},
             'outputs': {'out': 'int_traffic'},
             'properties': {
                 'link_role': 'link.role',
                 'system_id': 'system.system_id',
                 'interface': 'iface.if_name',
                 'counter_type': if_counter,
                 'graph_query': nodes_query,
             },
             'stages' : [],
            },

            {'name': 'device interface tx avg',
             'type': 'periodic_average',
             'inputs': {'in': 'int_traffic'},
             'outputs': {'out': 'device_int_tx_avg'},
             'properties': {
                 'period': average_period,
             },
             'stages' : [{'name' : 'out',
                          'units':'Bps'}],
            },

            {'name': 'device int traffic accumulate',
             'type': 'accumulate',
             'inputs': {'in': 'int_traffic'},
             'outputs': {'out': 'int_traffic_accumulate'},
             'properties': {
                 'total_duration': duration,
                 'max_samples': 1024,
             },
             'stages' : [],
            },
            {'name': 'live device interface hot',
             'type': 'in_range',
             'inputs': {'in': 'device_int_tx_avg'},
             'outputs': {'out': 'live_device_int_hot'},
             'properties': {
                 'range': {'max': max},
             },
             'stages' : [],
            },

            {'name': 'live device interface cold',
             'type': 'in_range',
             'inputs': {'in': 'device_int_tx_avg'},
             'outputs': {'out': 'live_device_int_cold'},
             'properties': {
                 'range': {'min': min},
             },
             'stages' : [],
            },

            {'name': 'sustained hot interfaces',
             'type': 'time_in_state',
             'inputs': {'in': 'live_device_int_hot'},
             'outputs': {'out': 'if_counter_anomalous_hot'},
             'properties': {
                 'time_window': duration,
                 'state_range': {'true': [{'max': threshold_duration}]},
             },
             'stages' : [],
            },
            {'name': 'sustained cold interfaces',
             'type': 'time_in_state',
             'inputs': {'in': 'live_device_int_cold'},
             'outputs': {'out': 'if_counter_anomalous_cold'},
             'properties': {
                 'time_window': duration,
                 'state_range': {'true': [{'max': threshold_duration}]},
             },
             'stages' : [],
            },


            {'name': 'anomaly hot leaf int traffic',
             'type': 'anomaly',
             'inputs': {'in': 'if_counter_anomalous_hot'},
             'outputs': {'out': 'anomaly_hot_int_traffic'},
             'properties' : {},
             'stages' : [],
            },
            {'name': 'anomaly cold leaf int traffic',
             'type': 'anomaly',
             'inputs': {'in': 'if_counter_anomalous_cold'},
             'outputs': {'out': 'anomaly_cold_int_traffic'},
             'properties' : {},
             'stages' : [],
            },

            {'name': 'int hot anomaly history',
             'type': 'accumulate',
             'inputs': {'in': 'anomaly_hot_int_traffic'},
             'outputs': {'out': 'int_hot_accumulate_anomaly'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': anomaly_history_count,
             },
             'stages' : [],
            },
            {'name': 'int cold anomaly history',
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
             'inputs': {'in': 'device_int_tx_avg'},
             'outputs': {'out': 'if_counter_sum_per_device'},
             'properties': {
                 'group_by': ['system_id']
             },
             'stages' : [],
            },
            {'name': 'interface sum per device per link role',
             'type': 'sum',
             'inputs': {'in': 'device_int_tx_avg'},
             'outputs': {'out': 'if_counter_sum_per_device_per_role'},
             'properties': {
                 'group_by': ['system_id', 'link_role']
             },
             'stages' : [],
            },

            {'name': 'system percent hot',
             'type': 'match_perc',
             'inputs': {'in' : 'if_counter_anomalous_hot'},
             'outputs': {'out' : 'system_perc_hot'},
             'properties' : {
                 'reference_state': 'true',
                 'group_by' : ['system_id']},
             'stages' : [],
            },
            {'name': 'system perc cold',
             'type': 'match_perc',
             'inputs': {'in' : 'if_counter_anomalous_cold'},
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
