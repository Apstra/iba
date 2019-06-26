# IBA Probes

The devices managed by Apstra AOS generate large amounts of data over time. On its own, 
this data is voluminous and unhelpful. Through Intent-Based Analytics (IBA), AOS 
allows the operator to combine intent from the AOS graph database with current 
and historic data from devices to reason about the network at-large.

For a detailed explaination of AOS IBA, please watch our recent webinar ["Intent-Based Analytics: Prevent Network Outages and Gray Failures"](http://www.apstra.com/resources/webinars/)! 

Probes are the basic unit of abstraction in IBA. Operators can configure, create, 
and delete probes. Generally, a given probe consumes some set of data from the 
network, does various successive aggregations and calculations on it, and 
optionally specifies some conditions of said aggregations and calculations on 
which anomalies are raised.

![IBA workflow](docs/media/iba1.png?raw=true "IBA Workflow")

Below is a collection of readily available probes organized by rough categories.
They also serve as examples to help build custom probes yourself.


## Layer1

| Probe | Description
| ---------- | -----------
| fabric_interface_flapping | Detect interface that are flapping |
| sfp | Detect high and/or low warning thresholds in SFP RX Power, TX Power, Temperature, Voltage, or Current |


## Layer2

| Probe | Description
| ---------- | -----------
| mlag_domain_config_sanity_anomalies | Detect MLAG (a.k.a MCLAG or VPC) domains with inconsistent configuration between member devices |
| stp_state | Detect STP blocked interfaces in all VLANs |
| stp_state_change | Detect any southbound interface STP state change seen in the last specified number of days |
| mlag_domain_state_anomalies | Detects MLAG domain state anomalies |


## Layer3

| Probe | Description
| ---------- | -----------
| border_leaf_default_gateway_anomalies | Verify routing intent on border leafs by ensuring default gateway nexthop count is as expected in all VRFs|
| non_border_leaf_default_gateway_anomalies | Verify routing intent on non-border leafs by ensuring default gateway nexthop count is as expected in all VRFs |


## Data plane

| Probe | Description
| ---------- | -----------
| fabric_ecmp_imbalance | Detect imbalance between interfaces within the Fabric |
| ecmp_imbalance_external_interfaces | Detect imbalance between interfaces exiting the Fabric |
| mlag_imbalance | Detect imbalance between member links of an aggregate MLAG link |
| drain_node_traffic_anomaly | Verify no application traffic on devices under maintenance |
| counters_error_anomalies | Detect Fabric interface showing alignment errors, FCS errors, runts, giants, or error packets |
| pkt_discard_anomalies | Detect Fabric interface having packet drops |
| interface_queue_drops_anomalies | Detect interfaces with overflowing buffers resulting in dropped packets |
| monitor_packet_loss | Detect high packet loss observed from pinging specified destination(s) |
| server_rtt | Detect high roundtrip time observed from pinging specified destination(s) |
| fabric_bgp_anomalies | Detects BGP anomalies in the fabric |
| interface_status_anomalies | Detects physical interface status |
| leaf_bgp_vrf_anomalies | Detects leaf vrf-aware BGP session anomalies |


## Traffic patterns

| Probe | Description
| ---------- | -----------
| fabric_hotcold_ifcounter | Detect hot and cold interfaces in the Fabric and flag systems with excessive cold or hot interfaces |
| eastwest_traffic | Show the distribution of north-south vs. east-west traffic in the Fabric |
| bandwidth_utilization_history | History of traffic patterns with varying degrees of aggregation |


## Troubleshooting

| Probe | Description
| ---------- | -----------
| Headroom | Calculate headroom between two servers along all available paths |


## Virtual Infrastructure

| Probe | Description
| ---------- | -----------
| virtual_infra_vlan_match | Detect inconsistencies between physical underlay and virtual networking |
| missing_vlan_vms | Detect Virtual Machines that have connectivity issues due to configuration inconsistencies between physical underlay and virtual networking |
| virtual_infra_lag_match | Detect inconsistencies between physical underlay and hypervisor LAG configuration|
| virtual_infra_missing_lldp_config | Detect virtual infra hosts that are not configured for LLDP|


## Capacity Planning

| Probe | Description
| ---------- | -----------
| arp_usage_anomalies | Detect devices with ARP table usage exceeding specified threshold |
| unicast_route_usage_anomalies | Detect devices with Unicast route table usage exceeding specified threshold |
| multicast_route_usage_anomalies | Detect devices with Multicast route table usage exceeding specified threshold |
| interface_bandwidth_anomalies | Detect interfaces with bandwidth exceeding specified threshold |


## Multicast

| Probe | Description
| ---------- | -----------
| anycast_rp_anomalies | Verify rendezvous point intent by ensuring all systems designated as rendezvous points have the expected peers present |
| anycast_rp_peer_count_anomalies | Ensure high-availability of rendezvous points by ensuring all rendezvous points have min number of anycast peers configured |
| mroute_count_anomalies | Detect abnormal changes in number of multicast sources, groups or routes |
| pim_neighbor_anomalies | Verify Multicast intent by ensuring all SVI interfaces, leaf-spine and leaf-leaf links in every VRF have an expected PIM neighbor |
| pim_rp_anomalies | Verify every VRF in every switch in Fabric has expected rendezvous point IP configured
| vrfs_missing_rp | Ensure any device acting as RP on any VRF is an RP for all other multicast enabled VRFs on that device |
| multicast_group_info | Detects Multicast Group Info from RPs |


## Device health

| Probe | Description
| ---------- | -----------
| memory_usage_threshold_anomalies | Detect memory leaks in specified process on all switches in the Fabric |
| power_supply_anomalies | Detect faults in power supply status, power supply fan status and power supply temperature status |
| system_memory_usage_threshold_anomalies | Detect switches having potential memory leaks in the Fabric |


## Compliance

| Probe | Description
| ---------- | -----------
| os_version_anomalies | Detect devices not running expected Operating System version |


## Overlay

| Probe | Description
| ---------- | -----------
| bum_to_total_traffic_anomalies | Detect % of BUM traffic to overall traffic exceeding specified threshold |
| bum_traffic_on_unlearnt_vteps_anomaly | Detect when decap traffic is seen from an unlearnt remote VTEP |
| hardware_vtep_counters_enabled | Detect devices where hardware telemetry to capture VXLAN counters is not enabled |
| vxlan_status | Detect devices with VXLAN interface that is not up |
| static_vxlan_vtep_anomalies | Verify VXLAN intent by ensuring all L2 segments have expected VTEP flood list |

## Security

| Probe | Description
| ---------- | -----------
| acl_stat_anomalies | Report on acl rule matches that exceed user defined thresholds |

## EVPN

| Probe | Description
| ---------- | -----------
| evpn | Monitors EVPN Telemetry including expected remote VTEP count |
| evpn_type3 | Monitors EVPN remote VTEPs Type 3 telemetry |

# Getting Started
All the probes listed above are available as part of AOS server predefined probe list or aos-cli predefined probe list. For the former, use AOS web UI to instantiate a predefined probe - you can find more details in AOS documentation. For the latter, see the probe templates section below.

## Probe Templates

You can find working probes in the `templates` subfolder.

The files in this folder are IBA probe json payloads that are represented as
[JINJA templates](http://jinja.pocoo.org/docs/2.10/templates/). You need to use
aos-cli to load these probes on to AOS server. The command to use in aos-cli is
`probe create --blueprint <id> --file </path/to/template/file> [<additional_args>]`
