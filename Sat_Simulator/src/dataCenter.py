from typing import TYPE_CHECKING, List
from src.data import Data
from src.image import Image
from src.packet import Packet
from src.log import Log,loggingCurrentTime
from typing import TYPE_CHECKING
from src.station import Station
from src.utils import Location
from src.nodeDecorator import NodeDecorator

if TYPE_CHECKING:
    from src.node import Node

class DataCenter(NodeDecorator):
    """
    Class that models a universal data center that receives data from all stations
    Calls each station's 
    """
    universalDataCenter: 'Union[DataCenter, None]' = None

    def __init__(self, node: 'Node') -> None:
        """
        Decorator object for a node object, normally used on a station object.
        It will make it so that the node object can only recieve, and not transmit. Calls each station's get_upload_bandwidth() function
        """
        if DataCenter.universalDataCenter is not None:
            raise Exception("There can only be one data center")
        super().__init__(node)
        ##self._node is a station object, so set transmit
        self.transmitAble = False
        self.recieveAble = True
        self.waitForAck = False
        self.sendAcks = False
        self.groundTransmitAble = True
        self.groundReceiveAble = True
        self.receive_queue: 'List[Data]' = []

        DataCenter.universalDataCenter = self

    #@profile
    def recieve_packet(self, pck: 'Packet') -> None:
        """
        Code to receive packet and add it to packet buffer

        Arguments:
            pck (Packet) - packet received
        """
        Log("Data Center Received data:", pck.relevantData[0], self)
        #self.recievePacketQueue.appendleft(pck)
        #Log("Data Center Received packet:", pck, self)
    def load_data(self, timeStep: float) -> None:
        """
        It only recieves data, so don't load or do anything
        """
        return
        self.convert_receive_buffer_to_data_objects()
        while len(self.dataQueue) > 0:
            data = self.dataQueue.pop()
            Log("Data Center Received data:", data, self)
            # data.received_time=loggingCurrentTime #type: ignore
            # self.receive_queue.append(data) #type: ignore
            # print("Data Center Received data:", data, self)
            
        ##Process data objects

    def load_packet_buffer(self) -> None:
        """
        Doesn't have any data to transmit, so pass
        """
        pass
