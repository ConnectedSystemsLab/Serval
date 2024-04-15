Module nodeDecorator
====================

Classes
-------

`NodeDecorator(node: src.node.Node)`
:   This class functions as a decorator object for the satellite class.
    Please use this object to add new functionality to a an already existing satellite object.

    ### Ancestors (in MRO)

    * src.node.Node

    ### Methods

    `load_data(self, timeStep: float) ‑> None`
    :   Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should determine how to generate data and add it to the dataQueue.
        Note: when you create a data object, it is treated as an integer, so if a timestep is lower than the time to generate a data, you will either need to keep track of how much is created in each timestep
        or find some way to split the data generation. An example of these can be found in both iotSatellite.py and iotDevices.py.
        Make sure you determine how the occupiedPacketBuffer variable, the memoryFilled variable, the packetQueue, and dataQueue should be changed.

    `load_packet_buffer(self, packet: Packet = None)`
    :   Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should convert the loaded data in dataQueue and add them to the packetQueue.
        Make sure you determine how the occupiedPacketBuffer variable, the memoryFilled variable, the packetQueue, and dataQueue should be changed.

    `recieve_packet(self, pck: Packet)`
    :   Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should determine what to do when a packet is added recieved by the device
        Make sure you determine how the occupiedPacketBuffer variable, the memoryFilled variable, the packetQueue, and dataQueue should be changed.