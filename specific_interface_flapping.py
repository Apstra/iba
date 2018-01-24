# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://apstra.com/eula

def specific_interface_flapping_probe(label, interfaces,
                                             threshold, duration,
                                             anomaly_history_count,
                                             max_flapping_interfaces_percentage):

    """
    Generates Probe to Determine if Interfaces are Flapping
    Parameters
    ----------
    label - str
        Descriptive name for the probe
    interfaces - list[dict]
        system_label - str
            label of system node that hosts given interface
        interface_name - str
            if_name of interface node representing given interface
    threshold - int
        sum total of number of flaps in recent-history for which
        an anomaly will be raised
    duration - int
        number of seconds of recent-history in which interface flapping
        will be considered
    anomaly_history_count - int
        number of anomaly flaps that will be recorded for inspection
    max_flapping_interfaces_percentage - int
        maximum percentage of flapping interfaces on a device

    Returns
    -------
    payload - dict
        Payload to create specific interface flapping probe
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
         'where(lambda system, iface: (system.label, iface.if_name) in %s)' % \
         intf_tuple_list_string)

    payload = {
        'label': label,
        'processors': [
            {'name': 'device_int_status',
             'type': 'service_data_collector',
             'inputs' : {},
             'outputs': {'out': 'device_if_status'},
             'properties': {
                 'service_name': 'interface',
                 'system_id': 'system.system_id',
                 'key': 'iface.if_name',
                 'graph_query': nodes_query,
             },
             'stages' : [],
            },
            {'name': 'device interface status history',
             'type': 'accumulate',
             'inputs': {'in': 'device_if_status'},
             'outputs': {'out': 'device_if_status_history'},
             'properties': {
                 'total_duration': duration,
                 'max_samples': 1024,
             },
             'stages' : [],
            },
            {'name': 'device interface flapping',
             'type': 'in_range',
             'inputs': {'in': 'device_if_status_history'},
             'outputs': {'out': 'if_status_flapping'},
             'properties': {
                 'range': {'max': threshold, 'min': None},
                 'property': 'sample_count',
             },
             'stages' : [],
            },
            {'name': 'device interface flapping anomaly',
             'type': 'anomaly',
             'inputs': {'in': 'if_status_flapping'},
             'outputs': {'out': 'device_if_flap_anomaly'},
             'properties' : {},
             'stages' : [],
            },
            {'name': 'anomaly flap device history',
             'type': 'accumulate',
             'inputs': {'in': 'device_if_flap_anomaly'},
             'outputs': {'out': 'anomaly_accumulate'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': anomaly_history_count,
             },
             'stages' : [],
            },

            {'name': 'percentage flapping per device interfaces',
             'type': 'match_perc',
             'inputs': {'in' : 'if_status_flapping'},
             'outputs': {'out' : 'flapping_device_int_perc'},
             'properties' : {
                 'reference_state': 'true',
                 'group_by' : ['system_id']},
             'stages' : [],
            },
            {'name': 'system anomalous flapping',
             'type': 'in_range',
             'inputs': {'in' : 'flapping_device_int_perc'},
             'outputs': {'out' : 'system_flapping'},
             'properties': {
                 'range': {'max': max_flapping_interfaces_percentage},
             },
             'stages' : [],
            },
            {'name': 'system anomaly',
             'type': 'anomaly',
             'inputs': {'in': 'system_flapping'},
             'outputs': {'out': 'system_flapping_anomaly'},
             'properties' : {},
             'stages' : [],
            },
            {'name': 'system flapping anomaly accumulate',
             'type': 'accumulate',
             'inputs': {'in': 'system_flapping_anomaly'},
             'outputs': {'out': 'system_flapping_anomaly_accumulate'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': anomaly_history_count,
             },
             'stages' : [],
            },
        ],
    }

    return payload
