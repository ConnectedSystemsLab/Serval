Module station
==============

Classes
-------

`Station(name: str, id: int, loc: src.utils.Location, transmitAble: bool = True, recieveAble: bool = True, properties: dict = None)`
:   Class for Ground stations and IoT devices
    
    Attributes:
        properties (dictionary)
        position (Location)
        transmitAble (bool)
        recieveAble (bool)
    Static attributes:
        idToStation (Dict[int, Station]) - a dictionary that maps each id to a station object
        nameToStation (Dict[str, Station]) - a dictionary that maps each name to a station object

    ### Ancestors (in MRO)

    * src.node.Node

    ### Class variables

    `idToStation: Dict[int, station.Station]`
    :

    `nameToStation: Dict[str, station.Station]`
    :

    ### Static methods

    `plot_stations(groundList: List[Station], label: str = '') ‑> None`
    :   Plot all ground stations on map
        
        Arguments:
            groundList (List[Station]) - list of stations to plot
            label (str) - what to label the objects as