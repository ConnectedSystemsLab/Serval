from collections import deque
import math
from typing import TYPE_CHECKING, Deque, Optional

from src.packet import Packet
from src.utils import Location, Print
from src.log import Log

import const
import random

if TYPE_CHECKING:
    from src.links import Link
    from src.data import Data
    from src.packet import Packet

class Node:
    """
    Main level Node which objects should extend from. Every node object has two packet buffers of size packetBuffer.
    The maxMemory variable does not include the packet buffers.

    Attributes:
        name (str) - name of object
        id (int) - id of object
        position (Location) - location of object
        beamForming (bool) - wether the device sends to all objects in view or just one, default is False
        packetBuffer (int) - size of packet buffer in bits, default max 32 bit int : 2,147,483,647 (note: python ints don't overflow)
        maxMemory (int) - total memory size in bits, default max 32 bit int : 2,147,483,647
        transmitPacketQueue (deque(Packet)) - queue which stores the transmit packet buffer
        recievePacketQueue (deque(Packet)) - queue which stores the recieve packet buffer
        dataQueue (deque(Data)) - queue which has the data
        nChannels (int) - number of channels the node has. Default is 1, please set the variable in the decorator if you want to change this.
        sendAcks (bool) - whether or not this node should send acks. Default is false, please set the variable in the decorator if you want to change this.
        waitForAck (bool) - whether or not this node should wait for acks before deleting the data. Default is false, please set the variable in the decorator if you want to change this.
    """
    def __init__(self, name: str, id: int, pos: Location, beamForming: (bool) = False, packetBuffer: int = 2147483647, maxMemory: int = 2147483646, transmitAble: bool = True, recieveAble: bool = True) -> None:
        self.name = name.strip()
        self.id = id
        self.position = pos
        
        self.beamForming = beamForming
        self.packetBuffer = packetBuffer
        self.maxMemory = maxMemory
        self.transmitAble = True
        self.recieveAble = True

        ##for these dequeues, the -1 element is the first element in the queue
        ##TODO: find better way of doing these
        self.transmitPacketQueue: 'Deque[Packet]' =  deque(maxlen=math.floor(self.packetBuffer/const.PACKET_SIZE))
        self.recievePacketQueue: 'Deque[Packet]' =  deque(maxlen=math.floor(self.packetBuffer/const.PACKET_SIZE))
        self.dataQueue: 'Deque[Data]' = deque(maxlen=math.floor(self.maxMemory/const.PACKET_SIZE)) ##
        
        ##Communication variables for each type of object
        self.nChannels: int = 1 #number of recieving channels
        self.sendAcks: bool = False #whether this device will send an ack that it recieved a packet
        self.waitForAck: bool = False #whether this device will wait for an ack before it deletes a packet

        ##Power variables for each type of satellite - set in decorator
        self.maxMWs: 'float' = 0 ##max battery capacity in milliwatt seconds
        self.currentMWs: 'float' = 0 ##current battery capacity in milliwatt seconds
        self.normalPowerConsumption: 'float' = 0 ##normal power consumption in milliwatts. This is stuff like heaters, gps, normal compute, etc.
        self.transmitPowerConsumption: 'float' = 0 ##power consumption in milliwatts when transmitting
        self.recievePowerConsumption: 'float' = 0 ##power consumption in milliwatts when receiving
        self.powerGeneration: 'float' = 0 ##power generation in milliwatt seconds
        self.minMWs: 'float' = 0 ##minimum battery capacity in milliwatt seconds

        #Log("Node Created", self, *self.position.to_lat_long())

    def __str__(self):
        return "{{nodeName: {}, nodeId: {}}}".format(self.name, self.id)

    ##Should be overloaded by decorator classes
    ##These are the communication methods to setup packet transmission
    def load_packet_buffer(self) -> None:
        """
        Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should convert the loaded data in dataQueue and add them to the packetQueue.
        Make sure you determine how the packetQueues and dataQueue should be changed.
        """
        Print("This is running the original node.load_packet_buffer(). If not intended, please override this method in your subclass.", logLevel="error")
        pass

    def recieve_packet(self, pck: Packet) -> None:
        """
        Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should determine what to do when a packet is added recieved by the device
        Make sure you determine how the packetQueues, and dataQueue should be changed.
        """
        Print("This is running the original node.recieve_packet(). If not intended, please override this method in your subclass.", logLevel="error")
        pass

    def load_data(self, timeStep: float) -> None:
        """
        Normally implemented by subclass, original will simply pass and do nothing.
        If implemented, this method should determine how to generate data and add it to the dataQueue.
        Note: when you create a data object, it is treated as an integer, so if a timestep is lower than the time to generate a data, you will either need to keep track of how much is created in each timestep
        or find some way to split the data generation. An example of these can be found in both iotSatellite.py and iotDevices.py.
        Make sure you determine how the packetQueue, and dataQueue should be changed.
        """
        Print("This is running the original node.load_data(). If not intended, please override this method in your subclass.", logLevel="error")
        pass

    def generate_power(self, timeStep: 'float') -> None:
        """
        This method will add the power generation to the currentMWs porportional to the passed in timestep

        Arguments:
            timeStep (seconds) - timeStep of simulation
        """
        self.currentMWs += self.powerGeneration * timeStep
        Log("Generated power", self)
        if self.currentMWs > self.maxMWs:
            self.currentMWs = self.maxMWs

    def use_regular_power(self, timeStep: 'float') -> bool:
        """
        This method will subtract the power consumption of the node from the battery.

        Returns:
            bool - whether or not the node has enough power to perform necessary features
        """
        powerNeeded = self.normalPowerConsumption * timeStep
        if self.currentMWs >= powerNeeded + self.minMWs:
            self.currentMWs -= powerNeeded
            Log("Used regular power",powerNeeded, self)
            return True
        else:
            Log("Not enough power to perform necessary features", self)
            return False

    def has_power_to_recieve(self, timeStep: 'float') -> bool:
        """
        This method will subtract the power consumption of the node from the battery.

        Returns:
            bool - whether or not the node has enough power to recieve for the MACRO_TIMESTEP
        """
        powerNeeded = self.recievePowerConsumption * timeStep
        if self.currentMWs >= powerNeeded + self.minMWs:
            return True
        else:
            Log("Not enough power to recieve", self)
            return False

    def has_power_to_transmit(self, timeStep: 'float') -> bool:
        """
        This method will subtract the power consumption of the node from the battery.

        Returns:
            bool - whether or not the node has enough power to recieve for the MACRO_TIMESTEP
        """
        powerNeeded = self.transmitPowerConsumption * timeStep
        if self.currentMWs >= powerNeeded + self.minMWs:
            return True
        else:
            Log("Not enough power to recieve", self)
            return False

    def use_receive_power(self, timeStep: 'float') -> bool:
        powerNeeded = self.recievePowerConsumption * timeStep
        if self.currentMWs >= powerNeeded + self.minMWs:
            self.currentMWs -= powerNeeded
            Log("Used receive power",powerNeeded, self)
            return True
        else:
            Log("Not enough power to recieve", self)
            return False

    def use_transmit_power(self, timeStep: 'float') -> bool:
        """
        This method will subtract the power consumption of the node from the battery.

        Returns:
            bool - whether or not the node has enough power to transmit for the MICRO_TIMESTEP
        """
        powerNeeded = self.transmitPowerConsumption * timeStep
        if self.currentMWs >= powerNeeded + self.minMWs:
            self.currentMWs -= powerNeeded
            Log("Used transmit power",powerNeeded, self)
            return True
        else:
            Log("Not enough power to transmit", self)
            return False

    def has_data_to_transmit(self) -> bool:
        """
        Returns whether or not the node has data to transmit

        Returns:
            bool - whether or not the node has data to transmit
        """
        return len(self.transmitPacketQueue) > 0

    def percent_of_memory_filled(self) -> float:
        """
        Returns how much of the total memory capacity of the node is full. Accounts for packet buffers and data queue

        Returns:
            float - percent of memory filled
        """
        size = 0
        for data in self.dataQueue:
            size += data.size
        for packet in self.transmitPacketQueue:
            size += packet.size
        for packet in self.recievePacketQueue:
            size += packet.size
        return (size) / (self.maxMemory + self.packetBuffer * 2)

    def get_number_of_packets_to_transmit(self) -> int:
        """
        Returns how many packets are in the transmit packet buffer
        """
        return len(self.transmitPacketQueue)
    
    def convert_data_objects_to_transmit_buffer(self):
        """
        This method will convert all of the current data objects in the data queue into packets and then load them into the packet buffer. 
        This method gets called in the iotDevice decorator. 
        """        
        if const.DATA_SIZE >= const.PACKET_SIZE:
            ##while you can still add more packets to the buffer
            while len(self.transmitPacketQueue) < self.transmitPacketQueue.maxlen:
                if len(self.dataQueue) > 0:
                    data = self.dataQueue.pop()
                    if data.size < self.packetBuffer - len(self.transmitPacketQueue) * (const.PACKET_SIZE + const.PREAMBLE_SIZE):
                        packets = data.to_packets()
                        self.transmitPacketQueue.extendleft(packets)
                    else:
                        self.dataQueue.extendleft(data)
                        break
                else:
                    break
        ##if you want multiple data objects to be converted into one packet
        else:
            ##data size is less than packets so convert over
            ##if there's not enough data to create a packet, do nothing
            raise NotImplementedError("The simulator currently does not support packets being larger than data objects currently. Reach out to Om")

    def convert_receive_buffer_to_data_objects(self):
        """
        This method will convert all of the current received packets into the data queue. 
        """
        packetsToBeRemoved = [] ##store them in this list and remove them at end cause u don't want to be removing during loop
        if const.DATA_SIZE < const.PACKET_SIZE:
            raise NotImplementedError("The simulator currently does not support packets being larger than data objects currently. Reach out to Om")

        else:
            ##if the data size is greater than the packet size, then you need to make sure that all of the packets for a data object are received before adding it to the data queue
            ##this is because the data object is split into multiple packets
            ##this is a bit more complicated
            outData = {} #store a dictionary of data objects and the size that has been received
            outDataToPacket = {} #store a dictionary of data objects and the packets that have been received
            for packet in self.recievePacketQueue:
                # Log("Processing packet", self, packet)
                if packet.relevantData[0] in outData:
                    outData[packet.relevantData[0]] += packet.infoSize
                    outDataToPacket[packet.relevantData[0]].append(packet)
                else:
                    outData[packet.relevantData[0]] = packet.infoSize
                    outDataToPacket[packet.relevantData[0]] = [packet]
            for data in outData:
                #print("out data", data, outData[data], data.size)
                if outData[data] >= data.size:
                    self.dataQueue.appendleft(data)
                    for pck in outDataToPacket[data]:
                        packetsToBeRemoved.append(pck)
        for pck in packetsToBeRemoved:
            self.recievePacketQueue.remove(pck)

    def generate_ack(self, pck: 'Packet') -> None:
        """
        This will load an ack packet into the transmit packet buffer, for sending at a later time.

        Arguments:
            pck (Packet) - the packet that is recieved
            lnk (Link) - the link that is used to send the ack
        """
        ##TODO: deal with multiple acks beeing created
        return 

    def recieve_ack(self, ack: 'Packet') -> None:
        """
        Receives an ack from the other device

        Arguments:
            ack (Packet) - the packet that is recieved
        """
        return 

    def send_data(self) -> 'Optional[Packet]':
        """
        This will return the packet that should be sent next from the transmit packet buffer. This will also remove the packet from the buffer.


        Returns:
            Packet - the packet that should be sent next
        """
        outPacket = None
        if const.ONLY_CONVERT_ONE_DATA_OBJECT:
            if len(self.transmitPacketQueue) == 0:
                if len(self.dataQueue) > 0:
                    dataObj = self.dataQueue.pop()
                    packets = dataObj.to_packets()
                    self.transmitPacketQueue.extendleft(packets)
        
        if len(self.transmitPacketQueue) > 0:
            outPacket = self.transmitPacketQueue.pop()
            Print("Sending", outPacket, "from", self)
            # Log("Sending packet from", self, outPacket)

            if self.waitForAck:
                self.transmitPacketQueue.appendleft(outPacket)
            
        if const.ONLY_CONVERT_ONE_DATA_OBJECT:
            if len(self.transmitPacketQueue) == 0:
                if len(self.dataQueue) > 0:
                    dataObj = self.dataQueue.pop()
                    packets = dataObj.to_packets()
                    self.transmitPacketQueue.extendleft(packets)
                    
        return outPacket