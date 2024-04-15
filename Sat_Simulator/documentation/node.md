Module node
===========

Classes
-------

`Node(name: str, id: int, pos: src.utils.Location, packetBuffer: int = 2147483647, maxMemory: int = 2147483646)`
:   Main level Node which objects should extend from
    
    Attributes:
        name (str) - name of object
        id (int) - id of object
        position (Location) - location of object
        packetBuffer (int) - size of packet buffer in bits, default max 32 bit int : 2,147,483,647
        maxMemory (int) - total memory size in bits, default max 32 bit int : 2,147,483,647
        occupiedPacketBuffer (int) - how many bits of packet buffer is occupied
        memoryFilled (int) - memory currently occupied in bits
        packetQueue (deque(Pakcet)) - queue which stores the packet buffer
        dataQueue (deque(Data)) - queue which has the data

    ### Methods

    `load_data(self, timeStep: float) ‑> None`
    :   Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should determine how to generate data and add it to the dataQueue.
        Note: when you create a data object, it is treated as an integer, so if a timestep is lower than the time to generate a data, you will either need to keep track of how much is created in each timestep
        or find some way to split the data generation. An example of these can be found in both iotSatellite.py and iotDevices.py.
        Make sure you determine how the occupiedPacketBuffer variable, the memoryFilled variable, the packetQueue, and dataQueue should be changed.

    `load_packet_buffer(self) ‑> None`
    :   Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should convert the loaded data in dataQueue and add them to the packetQueue.
        Make sure you determine how the occupiedPacketBuffer variable, the memoryFilled variable, the packetQueue, and dataQueue should be changed.

    `recieve_packet(self, pck: src.packet.Packet) ‑> None`
    :   Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should determine what to do when a packet is added recieved by the device
        Make sure you determine how the occupiedPacketBuffer variable, the memoryFilled variable, the packetQueue, and dataQueue should be changed.

    `send_data(self, lnk: Link, timeStep: float)`
    :   Method to send data in each of the packet buffers from sat to ground.