def underlay_virtual_infra_vlans_mismatch_probe(label):
    expectation_query = ("node('system', system_type='switch', name='leaf',"\
                         "role='leaf').out('hosted_vn_instances')"
                         ".node('vn_instance').out('instantiates')"
                         ".node('virtual_network', name='vn')")

    actual_query = ("node('system', system_type='switch', name='leaf',"\
                    "role='leaf').out('hosted_interfaces')"
                    ".node('interface').out('link')"
                    ".node('link').in_('link')"
                    ".node('interface').in_('hosted_interfaces')"
                    ".node('system').in_('is_realized_by')"
                    ".node('hypervisor').out('has')"
                    ".node('pnic').out('carries')"
                    ".node('vnet', name='vn')")

    payload = {
        'label': label,
        'processors': [
            {'name': 'AOS configured VLANs',
             'type': 'generic_graph_collector',
             'properties' : {
                 'graph_query': expectation_query,
                 'leaf': 'leaf.label',
                 'vlan': 'vn.vn_id',
                 'value' : '1',
                 'data_type' : 'ns',},
             'inputs' : {},
             'outputs' : {'out' : 'AOS VLANs'},
             'stages' : []
            },
            {'name': 'vSphere configured VLANs',
             'type': 'generic_graph_collector',
             'properties' : {
                 'graph_query': actual_query,
                 'leaf': 'leaf.label',
                 'vlan': 'str(vn.vlan)',
                 'value' : '1',
                 'data_type' : 'ns',},
             'inputs' : {},
             'outputs' : {'out' : 'vSphere VLANs'},
             'stages' : []
            },
            {'name': 'Differences between AOS and vSphere',
             'type': 'set_comparison',
             'properties' : {
                 'significant_keys' : ['leaf', 'vlan']
             },
             'stages' : [],
             'inputs' : {'A' : 'AOS VLANs',
                         'B' : 'vSphere VLANs'},
             'outputs' : {'A - B' : 'AOS Only',
                          'B - A' : 'vSphere Only',
                          'A & B' : 'Common in AOS and vSphere'}},
            {'name': 'Count of additional VLANs on vSphere',
             'type': 'set_count',
             'properties' : {
                 'group_by' : []
             },
             'stages' : [],
             'inputs' : {'in' : 'vSphere Only'},
             'outputs' : {'out' : 'Count of additional VLANs on vSphere'}},

            {'name' : 'Is there additional VLANs on vSphere?',
             'type' : 'range_check',
             'inputs' : {'in' : 'Count of additional VLANs on vSphere'},
             'outputs' : {'out' : 'Is there additional VLANs on vSphere'},
             'stages' : [],
             'properties' : {
                 'range' : {'max' : 0},
                 'raise_anomaly': True,
             }
            },

            {'name': 'Count of additional VLANs on AOS',
             'type': 'set_count',
             'properties' : {
                 'group_by' : []
             },
             'stages' : [],
             'inputs' : {'in' : 'AOS Only'},
             'outputs' : {'out' : 'Count of additional VLANs on AOS'}},
            {'name' : 'Is there additional VLANs on AOS?',
             'type' : 'range_check',
             'inputs' : {'in' : 'Count of additional VLANs on AOS'},
             'outputs' : {'out' : 'Is there additional VLANs on AOS?'},
             'stages' : [],
             'properties' : {
                 'range' : {'max' : 0},
                 'raise_anomaly': True,
             }
            },
        ],
    }
    return payload
