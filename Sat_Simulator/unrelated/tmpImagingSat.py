
from src.nodeDecorator import NodeDecorator
from src.packet import Packet
import src.log as log
from src.data import Data
import const

class IoTSatellite (NodeDecorator):
    """
    Class for IoT Satellites that only recieve memory from an IoTDevice and transmit to a recieve-able ground station
    """
    def __init__(self, node):
        super().__init__(node)
        self.waitForAck = True
        self.sendAcks = False
        self.nChannels = 1

        self.normalPowerConsumption =  1.13 * 1000
        self.currentMWs = 7030*.85 * 3600
        self.recievePowerConsumption = 0
        self.transmitPowerConsumption = 0
        self.concentrator = 0
        self.powerGeneration = 0

    def generate_power(self, timeStep):
        if self.in_sunlight(log.loggingCurrentTime):
            self.maxMWs = 7030*3600*.85
            self.currentMWs += self.powerGeneration * timeStep
        else:
            self.maxMWs = 4218*3600*.85
        self.currentMWs = min(self.currentMWs, self.maxMWs)

    def load_data(self, timeStep: float) -> None:
        """
        For Iot Satellites, no data is generated, so nothing happens
        """
        return
        n = 500
        if (len(self.dataQueue) < n and len(self.transmitPacketQueue) < n):
            numData = n
            dataObjects = [Data(const.DATA_SIZE) for i in range(numData)]
            self.dataQueue.extendleft(dataObjects)

    def load_packet_buffer(self, packet:Packet = None ) -> None:
        """
        Adds a packet to the packet buffer
        """
        #self.convert_data_objects_to_transmit_buffer()
        #return
        if packet == None: ##this is run at every timestep
            while (len(self.recievePacketQueue) > 0):
                self.transmitPacketQueue.appendleft(self.recievePacketQueue.pop()) ##move the packets from recieve to transmit
        elif len(self.recievePacketQueue) * const.PACKET_SIZE < self.packetBuffer:
            self.recievePacketQueue.appendleft(packet)
        else:
            #log("Packet not loaded", packet)
            pass
            
    def recieve_packet(self, pck: Packet) -> None:
        if "ack" in pck.descriptor:
            self.recieve_ack(pck)
        else:
            self.generate_ack(pck)
            log.Log("Packet recieved by sat", pck)
            self.load_packet_buffer(pck) ##adds packet to recieve buffer

