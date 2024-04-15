Module routing
==============

Classes
-------

`Routing(top: Topology)`
:   Class that creates the scheduling of the different satellites
    
    Attributes:
        topology (Topology) - Instance of Topology class created at this time
        bestLinks (Dict[Satellite][Station] = Link) - the links that were scheduled

    ### Methods

    `assign_by_datarate_and_available_memory(self, possibleLinks: Dict[Satellite, Dict[Station, Link]]) ‑> Dict[src.satellite.Satellite, Dict[src.station.Station, src.links.Link]]`
    :   This method will assign the links to the satellites based on the datarate and the available memory of the satellite/ground stations.
        
        Arguments:
            possibleLinks: Dict[Satellite][Station] = Link
        Returns:
            Dict[Satellite][Station] = Link, which is where info should be transmitted

    `compute_uplink_collisions(self)`
    :

    `schedule_best_links(self) ‑> Dict[src.satellite.Satellite, Dict[src.station.Station, src.links.Link]]`
    :   Public method to schedule best links. If you want to change the routing mechanism, you can change the ROUTING_MECHANISM variable in const.py
        If you want to add a method, add a new RoutingMechanism enum value and add it to the statement in the function below and create a method
        
        Returns:
            Dict[Satellite][Station] = Link - the links that were scheduled. If you try to schedule a link that is not possible, it should return a keyerror

    `transmit_from_ground_to_sat_with_slots(self, possibleLinks: Dict[Satellite, Dict[Station, Link]]) ‑> Dict[src.satellite.Satellite, Dict[src.station.Station, src.links.Link]]`
    :   This will randomly assign each gs that is visible to a gs to a satellite.

    `use_all_links(self, possibleLinks: Dict[Satellite, Dict[Station, Link]]) ‑> Dict[src.satellite.Satellite, Dict[src.station.Station, src.links.Link]]`
    :