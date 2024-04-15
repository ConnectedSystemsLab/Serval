from typing import TYPE_CHECKING, List
from src.log import Log

if TYPE_CHECKING:
    from typing import Tuple
    from src.data import Data

import const

class Packet:
    """
    Packet type

    Attributes:
        size (int) - total size in bits
        infoSize (int) - size of the information in bits
        preambleSize (int) - size of the preamble in bits
        id (int) - number to keep track of which packet object is which
        descriptor (str) - string to describe what the data is
    Static Attributes:
        idCount (int) - keeps track of how many packets have been created
        packetIdToData (dict[Packet] = List[Data]]) - dictionary to keep track of which packet object is which
    """

    idCount = 0
    #@profile
    def __init__(self, relevantData: 'Union[List[Data], Data]', infoSize: int = const.PACKET_SIZE, preambleSize: int = const.PREAMBLE_SIZE, descriptor: str = "", relevantNode = None, generationTime = None) -> None:
        self.size = infoSize + preambleSize
        self.infoSize = infoSize
        self.preambleSize = preambleSize
        self.descriptor = descriptor

        self.id = Packet.idCount
        Packet.idCount += 1

        if not isinstance(relevantData, List):
            relevantData = [relevantData]

        self.relevantData = relevantData
        self.generationTime = generationTime #already a string
        self.relevantNode = relevantNode
        
    def __str__(self) -> str:
        return "{{packetId: {}, packetSize: {}, packetDescriptor: {}, relevantNode: {}, generationTime: {}, relevantData: {}}}".format(self.id, self.size, self.descriptor, self.relevantNode, self.generationTime, str(self.relevantData[0].id))

    @staticmethod
    def from_data(dataList: 'List[Data]') -> 'Tuple[List[Packet], List[Data]]':
        """
        Packs the list of data objects into packet objects. Normally used when a packet contains more than one data object.
        This will not return anything till there is enough data to make a packet. This is used when the data size is less than the packet size.

        Will create packets based on const.PACKET_SIZE & const.PREAMBLE_SIZE
        
        Arguments:
            dataList (List[Data]) - the list of data objects the packet will create
        Returns:
            Tuple(List[Packet], List[Data]) - a tuple of a list of packets that were created and a list of data objects which were converted to a packet
        """
        raise NotImplementedError("Currently the packet size must be less than or equal to the data size-use data.to_packets() instead")
        cnt = 0 # counter for the current bits in the packet
        
        outPacket: 'List[Packet]' = []
        outData: 'List[Data]' = []

        dataCurrentlyBeingConverted: 'List[Data]' = []
        infoSize = const.PACKET_SIZE
        
        for data in dataList:
            cnt += data.size
            dataCurrentlyBeingConverted.append(data)

            if cnt >= infoSize:
                ##if more than enough was added, move the extra data to the next packet
                if cnt > infoSize:
                    ##don't store the last data object and instead save for next packet
                    dataCurrentlyBeingConverted = dataCurrentlyBeingConverted[:-1]

                pck = Packet(dataCurrentlyBeingConverted)
                
                outData.extend(dataCurrentlyBeingConverted)
                outPacket.append(pck)

                if cnt > infoSize:
                    dataCurrentlyBeingConverted = [data]
                    cnt = data.size
                else:
                    dataCurrentlyBeingConverted = []
                    cnt = 0
        
        return (outPacket, outData)