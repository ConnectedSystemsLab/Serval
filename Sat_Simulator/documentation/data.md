Module data
===========

Classes
-------

`Data(size: int, descriptor: str = '')`
:   Class that represents any data type, say an image
    
    Attributes:
        size (int) - size in bits
        id (int) - number to keep track of which data object is which
        descriptor (str) - string to describe what the data is
    Static:
        idCount (int) - overall id count for all data objects

    ### Class variables

    `idCount`
    :

    ### Methods

    `to_packets(self, packetSize: int) ‑> List[src.packet.Packet]`
    :   Converts the data into packets based on given packetSize. If less data than size, padding is added
        
        Arguments:
            packetSize (int) - the desired size of packet