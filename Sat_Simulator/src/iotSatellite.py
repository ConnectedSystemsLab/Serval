
from src.nodeDecorator import NodeDecorator
from src.packet import Packet
import src.log as log
from src.data import Data
import const

lastSatPower = {}
class IoTSatellite (NodeDecorator):
    """
    Class for IoT Satellites that only recieve memory from an IoTDevice and transmit to a recieve-able ground station
    """
    def __init__(self, node):
        super().__init__(node)
        self.waitForAck = False
        self.sendAcks = False
        self.nChannels = 1

        self.normalPowerConsumption = 532+190
        self.currentMWs = 7030*.85 * 3600
        self.recievePowerConsumption = 133
        self.transmitPowerConsumption = 532
        self.concentrator = 266
        self.powerGeneration = 1666.67*3
        self.maxMWs = 7030*3600*.85
        self.minMWs = 4215*3600

    def generate_power(self, timeStep):
        if self in lastSatPower:
            log.Log("Consumption", self, lastSatPower[self] - self.currentMWs)
        if self.in_sunlight(log.loggingCurrentTime):
            self.maxMWs = 7030*3600*.85
            log.Log("Generating power", self.powerGeneration)
            self.currentMWs += self.powerGeneration * timeStep
        self.currentMWs = min(self.currentMWs, self.maxMWs)
        lastSatPower[self] = self.currentMWs

    def load_data(self, timeStep: float) -> None:
        """
        For Iot Satellites, no data is generated, so nothing happens
        """
        if const.ONLY_DOWNLINK:
            n = 200
            if len(self.transmitPacketQueue) < n:
                numData = n
                dataObjects = [Data(const.DATA_SIZE, relevantNode=self, generationTime=log.get_logging_time()) for i in range(numData)]
                self.dataQueue.extendleft(dataObjects)
                #log.Log("Data Generated", self, *dataObjects)
        else:
            pass

    def load_packet_buffer(self, packet:Packet = None ) -> None:
        """
        Adds a packet to the packet buffer
        """
        if const.ONLY_DOWNLINK:
            self.convert_data_objects_to_transmit_buffer()
            return
        else:
            if packet == None: ##this is run at every timestep
                while (len(self.recievePacketQueue) > 0):
                    self.transmitPacketQueue.appendleft(self.recievePacketQueue.pop()) ##move the packets from recieve to transmit
            elif len(self.recievePacketQueue) * const.PACKET_SIZE < self.packetBuffer:
                self.recievePacketQueue.appendleft(packet)
            else:
                #log("Packet not loaded", packet)
                pass
            
    def recieve_packet(self, pck: Packet) -> None:
        if const.ONLY_UPLINK:
            log.Log("Packet recieved by sat", pck, self)
            return
            
        if "ack" in pck.descriptor:
            self.recieve_ack(pck)
        else:
            self.generate_ack(pck)
            log.Log("Packet recieved by sat", pck, self)
            self.load_packet_buffer(pck) ##adds packet to recieve buffer

