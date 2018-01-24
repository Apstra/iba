# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://apstra.com/eula


def ecmp_imbalance_probe(label, average_period, duration, threshold_duration,
                         std_max, anomaly_history_count, max_systems_imbalanced,
                         system_imbalance_history_count):
    """

    Parameters
    ----------
    label - str
        Descriptive name for the probe
    average_period - int
        period over which to average input Bps counter samples
    duration - int
        number of seconds of recent-history in which we
        will consider ECMP imbalance
    threshold_duration - int
        sum total of number of seconds of recent-history for which
        set of ECMP links must be unbalanced
        for anomaly to be raised
    std_max - int
        maxiumum standard deviation in Bps across a set of ECMP paths on
        a given system.  If this std deviation is exceeded, we consider
        that system to be imbalanced'
    anomaly_history_count - int
        number of anomaly flaps that will be recorded for inspection
    max_systems_imbalanced - int
        if this number of total imbalanced systems is exceeded, an
        anomaly is raised
    system_imbalance_history_count - int
        the number of samples of recent-history for which we maintain
        data about the number of systems that are imbalanced

    Returns
    -------
        payload - dict
        Payload to create ecmp imbalance probe
    """

    nodes_query = \
        ('node("system", name="system", deploy_mode="deploy", role="leaf").'
         'out("hosted_interfaces").'
         'node("interface", name="iface", if_name=not_none()).'
         'out("link").'
         'node("link", link_type="ethernet").'
         'in_("link").'
         'node("interface").'
         'in_("hosted_interfaces").'
         'node("system", role="spine", deploy_mode="deploy")')

    payload = {
        'label': label,
        'processors': [
            {'name': 'leaf fabric interface traffic',
             'type': 'if_counter',
             'inputs': {},
             'outputs': {'out': 'leaf_fabric_int_traffic'},
             'properties': {
                 'label': 'system.label',
                 'system_id': 'system.system_id',
                 'interface': 'iface.if_name',
                 'counter_type': 'tx_bytes',
                 'graph_query': nodes_query,
             },
             'stages': [{'name': 'out', 'units': 'Bps'}],
             },
            {'name': 'leaf fabric interface traffic average',
             'type': 'periodic_average',
             'inputs': {'in': 'leaf_fabric_int_traffic'},
             'outputs': {'out': 'leaf_fab_int_tx_avg'},
             'properties': {
                 'period': average_period,
             },
             'stages': [{'name': 'out',
                         'units': 'Bps'}],
             },
            {'name': 'leaf fabric interface history',
             'type': 'accumulate',
             'inputs': {'in': 'leaf_fabric_int_traffic'},
             'outputs': {'out': 'leaf_fab_int_time_series'},
             'properties': {
                 'total_duration': duration,
                 'max_samples': 1024,
             },
             'stages': [{'name': 'out', 'units': 'Bps'}],
             },
            {'name': 'leaf fabric interface std-dev',
             'type': 'std_dev',
             'inputs': {'in': 'leaf_fab_int_tx_avg'},
             'outputs': {'out': 'leaf_fab_int_std_dev'},
             'properties': {
                 'group_by': ['system_id', 'label'],
             },
             'stages': [{'name': 'out', 'units': 'Bps'}],
             },
            {'name': 'live ecmp imbalance',
             'type': 'in_range',
             'inputs': {'in': 'leaf_fab_int_std_dev'},
             'outputs': {'out': 'live_ecmp_imbalance'},
             'properties': {
                 'range': {'max': std_max},
             },
             'stages': [{'name': 'out', 'units': 'Bps'}],
             },
            {'name': 'sustained ecmp imbalance',
             'type': 'time_in_state',
             'inputs': {'in': 'live_ecmp_imbalance'},
             'outputs': {'out': 'system_tx_imbalance'},
             'properties': {
                 'time_window': duration,
                 'state_range': {'true': [{'max': threshold_duration}]},
             },
             'stages': [{'name': 'out', 'units': 'Bps'}],
             },
            {'name': 'ecmp imbalance anomaly',
             'type': 'anomaly',
             'inputs': {'in': 'system_tx_imbalance'},
             'outputs': {'out': 'ecmp_imbalance_anomaly'},
             'properties': {},
             'stages': [],
             },
            {'name': 'anomaly accumulate',
             'type': 'accumulate',
             'inputs': {'in': 'ecmp_imbalance_anomaly'},
             'outputs': {'out': 'anomaly_accumulate'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': anomaly_history_count,
             },
             'stages': [],
             },

            {'name': 'systems imbalanced count',
             'type': 'match_count',
             'inputs': {'in': 'system_tx_imbalance'},
             'outputs': {'out': 'system_imbalance_count'},
             'properties': {
                 'reference_state': 'true',
                 'group_by': []},
             'stages': [],
             },
            {'name': 'imbalanced system count out of range',
             'type': 'in_range',
             'inputs': {'in': 'system_imbalance_count'},
             'outputs': {'out': 'imbalanced_system_count_out_of_range'},
             'properties': {
                 'range': {'max': max_systems_imbalanced},
             },
             'stages': [],
             },
            {'name': 'imbalanced systems count out of range anomaly',
             'type': 'anomaly',
             'inputs': {'in': 'imbalanced_system_count_out_of_range'},
             'outputs': {'out': 'system_tx_imbalance_count_anomaly'},
             'properties': {},
             'stages': [],
             },

            {'name': 'imbalanced system count anomaly history',
             'type': 'accumulate',
             'inputs': {'in': 'system_imbalance_count'},
             'outputs': {'out': 'imbalanced_system_count_history'},
             'properties': {
                 'total_duration': 0,
                 'max_samples': system_imbalance_history_count,
             },
             'stages': [],
             },
        ],
    }

    return payload
