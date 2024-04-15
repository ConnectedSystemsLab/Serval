from typing import TYPE_CHECKING
from itertools import chain
import random # type: ignore

import numpy as np

from src.links import Link
from src.log import Log
from src.utils import Print
from src.dataCenter import DataCenter
import const

if TYPE_CHECKING:
    from src.satellite import Satellite
    from src.station import Station
    from src.node import Node
    from src.packet import Packet
    from typing import List, Dict, Optional

class GroundTransmission:
    """
    This function build's off of the transmission class in the transmission.py file
    It emulates the transmission of packets from the ground to the data center
    """

    def __init__(self, gsList: 'List[Station]', timeStep: 'int') -> None:
        self.timeStep = timeStep
        self.gsList = gsList
        self.transmit_all()

    def transmit_all(self) -> None:
        ##this basically moves the packets from the ground station to the data center
        ##this assumes a wired network so no collisions
        ##this also assumes that the data center is the only reciever
        ##this uses each station's get_upload_bandwidth function
        ##assumes 1 channel for each station

        ##get the data center
        universalDataCenter = DataCenter.universalDataCenter 

        for station in self.gsList:
            if station.groundTransmitAble and station.has_data_to_transmit():
                ##get the upload bandwidth
                uploadBandwidth = station.get_upload_bandwidth()
                ##get the total number of bits to transmit
                totalBits = uploadBandwidth * self.timeStep
                while totalBits > 0:
                    ##get the packet
                    packet = station.send_data()
                    if packet is None:
                        break
                    ##get the size of the packet
                    packetSize = packet.size
                    ##send the packet
                    universalDataCenter.recieve_packet(packet)
                    totalBits -= packetSize
