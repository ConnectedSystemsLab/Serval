Module links
============

Classes
-------

`Link(sat: src.satellite.Satellite, gs: src.station.Station, time: src.utils.Time, direction: TransmitDirection = TransmitDirection.BOTH_WAYS)`
:   Class for each link between two objects
    
    Attributes:
        sat (Satellite)
        gs (Station)
        time (Time)
        snr (float) - snr of ground recieving object
        distance (float) - meters between both objects
        datarate (float) - bits p sec
        direction (TransmitDirection) - Look at TransmitDirection enum for more info
    
    Constructor for link object. Before you use this, use the create_link method instead.
    
    Arguments:
        sat (Satellite)
        gs (Station)
        time (Time)
        direction (TranmitDirection) - default BOTH_WAYS. Look at TransmitDirection enum for more info

    ### Static methods

    `create_link(satellites: Union[List[Satellite], Satellite], stations: Union[List[Station], Station], time: src.utils.Time, direction: Union[List[TransmitDirection], TranmitDirection] = TransmitDirection.BOTH_WAYS) ‑> List[Link]`
    :   This is the public method to create a link. Use this method instead of consturctor!
        This will create a link between satList[0] and groundList[0], satList[1] and groundList[1], etc.
        
        Arguments:
            satellites (List[Satellite] or Satellite) - a satellite object or a list of satellite objects. Must be the same as stations
            stations (List[Station] or Station) - a station object or a list of station objects. Must be same length as satList, each index of sat is matchd with index of groundList
            time (Time) - time of link
            direction (TransmitDirection) - default BOTH_WAYS. Look at TransmitDirection enum for more info. Can be both a list of the same size of satellites/stations or just one.
        Returns:
            List[Link] - a list of links

    `snr_to_datarate(snr: float) ‑> float`
    :   Converts given SNR to datarate using standard metrics/
        
        Currently LoRa modulation is used.
        
        Arguments:
            snr (float)
        Returns:
            float - datarate in bits/s

    ### Methods

    `get_other_object(self, nd: Node) ‑> src.node.Node`
    :   Function where if you give it one of the nodes, it'll return the other node. I added this to make the code easier to read
        
        Arguments:
            nd (Node) - the node you know
        Returns:
            Node - the other node
        Raises:
            ValueError - object does not exist in link

`TransmitDirection(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   BOTH_WAYS to simulatenously send.
    SAT_TO_GROUND if you can only send from the sat to the ground.
    GROUND_TO_SAT to only send from ground to sat

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `BOTH_WAYS`
    :

    `GROUND_TO_SAT`
    :

    `SAT_TO_GROUND`
    :