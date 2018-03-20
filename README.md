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

Below is a collection of commonly used probes that can be used 
out of the box with AOS. They also serve as examples to help build custom probes 
yourself.

# Getting Started

You can find the setup instructions and try these out in your environment [here](docs/README.md).

To access each tutorial directly, click on the links below:

#### [East West Traffic](docs/east_west_traffic.ipynb)
    Generates Probe to Calculate Total East/West Traffic     
#### [ECMP Imbalance](docs/ecmp_imbalance.ipynb)
    Generates Probe to Calculate ECMP Imbalance on fabric ports   
#### [External ECMP Imbalance](docs/external_ecmp_imbalance.ipynb) 
    Generates Probe to Calculate ECMP Imbalance on external facing fabric ports 
#### [Headroom](docs/headroom.ipynb)  
    Generates Probe to Calculate Headroom
#### [Hot Cold Interface](docs/hot_cold_interface.ipynb)  
    Generates Probe to Determine Hot/Cold Fabric Interface Counters
#### [Interface Flapping](docs/interface_flapping.ipynb)  
    Generates Probe to Determine if Interfaces are Flapping
#### [MLAG Imbalance](docs/mlag_imbalance.ipynb)   
    Generates Probe to Calculate MLAG Imbalance
#### [Specific Hot Cold Interface](docs/specific_hot_cold_interface.ipynb) 
    Generates Probe to Determine Hot/Cold for Specific Interface Counters
#### [Specific Interface Flapping](docs/specific_interface_flapping.ipynb)  
    Generates Probe to Determine if Interfaces are Flapping
