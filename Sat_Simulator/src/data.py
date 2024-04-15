import math
import const
# from numba import types
# from numba.experimental import jitclass

from typing import List


from src.packet import Packet
from src.log import Log

class Data(object):
    """
    Class that represents any data type, say an image

    Attributes:
        size (int) - size in bits
        id (int) - number to keep track of which data object is which
        descriptor (str) - string to describe what the data is
    Static:
        idCount (int) - overall id count for all data objects
    """    
    idCount = 0
    #__slots__ = ['size', 'percentLeft', 'descriptor', 'id']
    def __init__(self, size: int = const.DATA_SIZE, descriptor: str = "", relevantNode = None, generationTime = None) -> None:
        self.size = size
        self.percentLeft = 0.0
        self.descriptor = descriptor
        self.id = Data.idCount
        Data.idCount += 1
        
        self.relevantNode = relevantNode
        if generationTime is not None:
            self.generationTime = generationTime.to_str()
        else:
            self.generationTime = None
    def to_packets(self, packetSize: int=const.PACKET_SIZE) -> 'List[Packet]':
        """
        Converts the data into packets based on the const.PACKET_SIZE & const.PREAMBLE_SIZE. 
        If less data than the packet size, padding is added. This is used when the data size is greater than the packet size.
        """
        if self.size != const.DATA_SIZE:
            packetSize = self.size
        if self.size < packetSize:
            raise Exception("Data size is less than packet size")
        numPacket = math.ceil(self.size / packetSize)
        out: 'List[Packet]' = [Packet(self, infoSize = packetSize, relevantNode=self.relevantNode, generationTime=self.generationTime) for i in range(numPacket)]
        Log("Packet Created by ", self, *out)
        return out

    def __str__(self) -> str:
        return "{{dataId: {}, dataSize: {}, dataDescriptor: {}, relevantNode: {}, generationTime: {} }}".format(self.id, self.size, self.descriptor, self.relevantNode, self.generationTime)
