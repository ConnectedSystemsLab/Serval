Module iotDevice
================

Classes
-------

`IotDevice(node: Node)`
:   Decorator object for a node object, normally used on a station object.
    It will make it so that the node object can only transmit, and not recieve.
    
    Station class but transmit only.

    ### Ancestors (in MRO)

    * src.nodeDecorator.NodeDecorator
    * src.node.Node

    ### Methods

    `load_data(self, timeStep: float) ‑> None`
    :   For Iot GS, creates one byte per sec

    `load_packet_buffer(self) ‑> None`
    :   Adds a packet to the packet buffer

    `recieve_packet(self, pck: Packet) ‑> None`
    :   Code to recieve packet and add it to packet buffer
        
        Arguments:
            pck (Packet) - packet recieved