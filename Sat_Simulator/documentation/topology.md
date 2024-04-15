Module topology
===============

Classes
-------

`Topology(time: src.utils.Time, satList: List[Satellite], groundList: List[Station])`
:   Class with availability map and link calculations that the routing class uses to schedule different paths
    
    Attributes:
        time (Time)
        satList (List[Satellite])
        groundList (List[Station])
    
    Constructor will create the availability map and all of the possible links at time.
    
    Arguments:
        time (Time)
        satList (List[Satellite])
        groundList (List[Station])

    ### Methods

    `create_available_map(self, time: src.utils.Time, satList: List[Satellite], groundList: List[Station]) ‑> Dict[src.satellite.Satellite, Dict[src.station.Station, bool]]`
    :   Method to create avaibility map which calculates which ground stations a satellite can see at a time
        
        Arguments:
            time (Time)- when to calculate
            satList (list[Satellite]) - list of satellites
            groundList (list[Station])
        Returns:
            Dict[Satellite][Station] = bool

    `create_possible_links(self, satToGround: Dict[Satellite, Dict[Station, bool]], time: src.utils.Time) ‑> Dict[src.satellite.Satellite, Dict[src.station.Station, src.links.Link]]`
    :   Method to create all of the possible links between objects.
        
        TODO: Create ISLs, current no ISLs supported via this algo, will do eventually
        
        Arguments:
            satToGround (Dict[Satellite][Station] = bool) - created from availabiltiy map which tells at time, which gs can be seen from a sat
        Returns
            Dict[Satellite][Station] = Link. If the link is not possible, Dict[Satellite][Station] should cause a KeyError