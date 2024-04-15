Module recieveGS
================

Classes
-------

`RecieveGS(node: Node)`
:   Class that models station that only recieves data and doesn't transmit anything
    
    Decorator object for a node object, normally used on a station object.
    It will make it so that the node object can only recieve, and not transmit.

    ### Ancestors (in MRO)

    * src.nodeDecorator.NodeDecorator
    * src.node.Node

    ### Methods

    `load_data(self, timeStep: float) ‑> None`
    :   It only recieves data, so don't load or do anything

    `load_packet_buffer(self) ‑> None`
    :   Doesn't have any data to transmit, so pass

    `recieve_packet(self, pck: Packet) ‑> None`
    :   Code to recieve packet and add it to packet buffer
        
        Arguments:
            pck (Packet) - packet recieved