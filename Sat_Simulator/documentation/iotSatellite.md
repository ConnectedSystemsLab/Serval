Module iotSatellite
===================

Classes
-------

`IoTSatellite(node: src.node.Node)`
:   Class for IoT Satellites that only recieve memory and transmit to ground station

    ### Ancestors (in MRO)

    * src.nodeDecorator.NodeDecorator
    * src.node.Node

    ### Methods

    `load_data(self, timeStep: float) ‑> None`
    :   For Iot Satellites, no data is generated, so nothing happens

    `load_packet_buffer(self, packet: src.packet.Packet = None) ‑> None`
    :   Adds a packet to the packet buffer

    `recieve_packet(self, pck: src.packet.Packet) ‑> None`
    :   Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should determine what to do when a packet is added recieved by the device
        Make sure you determine how the occupiedPacketBuffer variable, the memoryFilled variable, the packetQueue, and dataQueue should be changed.