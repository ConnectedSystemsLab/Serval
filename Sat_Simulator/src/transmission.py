from typing import TYPE_CHECKING
from itertools import chain
import random # type: ignore
from time import time as timeNow
import numpy as np

from src.links import Link
from src.log import Log
from src.utils import Print
import const

if TYPE_CHECKING:
    from src.satellite import Satellite
    from src.station import Station
    from src.node import Node
    from src.packet import Packet
    from typing import List, Dict, Optional

class CurrentTransmission:
    def __init__(self, sending: 'Node', receivingNodes: 'List[Node]', channel: 'int') -> None:
        self.sending = sending
        self.receivingNodes = receivingNodes
        self.receivingChannel = channel

        self.packets: 'List[Packet]' = []
        self.packetsTime: 'List[tuple(float, float)]' = [] #List of startTimes and endTimes for each packet relevative to the start of the timestep
        self.PER: 'Dict[Node, float]' = {} #the PER for each node. Should be set to 1 if the node isn't scheduled to receive the packet
        self.SNR: 'Dict[Node, float]' = {}
        
class Transmission:
    """
    This class is what sends the data between nodes
    """
    def __init__(self, links: 'Dict[Node, Dict[Node, Link]]', topology: 'Topology', satList: 'List[Satellite]', gsList: 'List[Station]', timeStep: 'int') -> None:
        self.links = links ##links should be a case of Dict[Satellite][Station] = links
        self.linkList = list( chain( *(list(d.values()) for d in self.links.values()) ))
        self.nodes = [i for i in chain(satList, gsList)]
        self.topology = topology
        self.timeStep = timeStep
        self.satList = satList
        self.gsList = gsList

        transmissions = self.get_new_transmissions()
        self.transmit(transmissions)
        
    def transmit(self, transmissions: 'List[CurrentTransmission]'):
        #so here's how this works 
        #we have each device which has been scheduled from x time to y time
        #so let's do this, for each reception device's channel, we store a list of each packet's (startTime, endTime)
        #we then find any collisions in the startTime and endTime

        #receiving is a dict[node][channel] = List[ (packet, (startTime, endTime), PER, SNR) ]
        
        receiving = {}
        #s = timeNow()
        for transmission in transmissions:
            for node in transmission.receivingNodes:
                for i in range(len(transmission.packets)):
                    lst = receiving.setdefault(node, {})
                    chanList = lst.setdefault(transmission.receivingChannel, [])
                    chanList.append((transmission.packets[i], transmission.packetsTime[i], transmission.PER[node], transmission.SNR[node], str(transmission.sending), str(transmission.packets[i])))
                    #receiving[node][transmission.receivingChannel].append((transmission.packets[i], transmission.packetsTime[i], transmission.PER[node], str(transmission.sending), str(transmission.packets[i])))
        
        #print("Time to create receiving dict", timeNow() - s)
        
        #print receiving but call the repr function for each object
        #now let's go through each receiving and find any overlapping times 
        #TODO: double check if I need to consider the -6 difference - seems kinda unimportant
        #t = timeNow()
        for receiver in receiving.keys():
            for channel, blocks in receiving[receiver].items():
                if len(blocks) == 0:
                    continue
                #now for each block, we have a list of tuples where the 0th element is the packet and the 1st element is (startTime, endTime) and 2nd is the sendingNode
                #we need to find out if any of the times overlap, and if so drop them from list
                
                times = [i[1] for i in blocks]
                collidedInds = set() #s et of indicies of collided packets
                for i in range(len(times)):
                    for j in range(len(times)):
                        if i == j:
                            continue
                        #there is overlap if the second start time is between the first start & end
                        firstTime = times[i]
                        secondTime = times[j]
                        if firstTime[0] <= secondTime[0] and secondTime[0] < firstTime[1]:
                            snrOne = blocks[i][3]
                            snrTwo = blocks[j][3]
                            #if snrOne is greater than snrTwo by 6 db, then we can drop the second packet
                            #if snrTwo is greater than snrOne by 6 db, then we can drop the first packet
                            #if they are within 6 db, then we have a collision
                            if snrOne - snrTwo > 6:
                                print("Collision between", blocks[i][0], "and", blocks[j][0], "Dropping ", blocks[j][0])
                                collidedInds.add(j)
                            elif snrTwo - snrOne > 6:
                                print("Collision between", blocks[i][0], "and", blocks[j][0], "Dropping ", blocks[i][0])
                                collidedInds.add(i)
                            else:
                                print("Collision between", blocks[i][0], "and", blocks[j][0])
                                collidedInds.add(i)
                                collidedInds.add(j)
                
                #now that we have this info, let's send
                collidedPackets = [blocks[i][0] for i in collidedInds]
                if len(collidedPackets) > 0:
                    Log("Packets in collision:", *collidedPackets, receiver)
                
                #now receive the successful packets
                successfulInds = [i for i in range(len(blocks)) if i not in collidedInds]
                succesfulBlocks = [blocks[i] for i in successfulInds]
                for block in succesfulBlocks:
                    packet = block[0]
                    PER = block[2]
                    
                    #let's check if this packet gets dropped by PER
                    
                    if random.random() <= PER:
                        #print("Packet dropped", packet, receiver)
                        pass
                        #Log("Packet dropped", packet)
                    else:
                        #print("Packet recieved", packet, receiver)
                        time = block[1][1] - block[1][0]
                        if receiver.has_power_to_recieve(time):
                            receiver.use_receive_power(time)
                            receiver.recieve_packet(packet)

    def get_new_transmissions(self) -> 'Dict[int, List[currentTransmission]]':
        devicesTransmitting = {}
        currentTransmissions = []
        
        for link in self.linkList:
            #print("Link has {} start times".format(len(link.startTimes)), *link.nodeSending)
            for idx in range(len(link.startTimes)):
                sending = link.nodeSending[idx]
                startTime = link.startTimes[idx]
                channel = link.channels[idx]
                endTime = min(link.endTimes[idx], self.timeStep)
                
                #let's do this to avoid duplicate sending - maybe think of a better way to handle this??
                if sending in devicesTransmitting:
                    #check if this is from the same  or another, if its in another - raise an exception
                    if link is devicesTransmitting[sending]:
                        pass
                    else:
                        raise Exception("{} is transmitting on two links at the same time".format(sending))
                devicesTransmitting[sending] = link
                
                receiving = []
                datarate = 0
                if sending.beamForming:
                    receiving = [link.get_other_object(sending)]
                    per = {receiving[0]: link.PER}
                    snr = {receiving[0]: link.snr}
                    datarate = link.get_relevant_datarate(sending)
                else:
                    listOfLinks = self.topology.nodeLinks[sending]
                    receiving = [i.get_other_object(sending) for i in listOfLinks]
                    per = {i.get_other_object(sending): i.PER for i in listOfLinks}
                    snr = {i.get_other_object(sending): i.snr for i in listOfLinks}
                    receiving = [i for i in receiving if i.recieveAble]
                    
                    #lst = [i.get_relevant_datarate(sending) for i in listOfLinks if i.get_other_object(sending).recieveAble]
                    #datarate = min(lst)
                    datarate = link.get_relevant_datarate(sending)
                    for i in listOfLinks:
                        if i.get_relevant_datarate(sending) < datarate or not i.is_listening():
                            per[i.get_other_object(sending)] = 1
                    #Log("Sending", sending, "receiving", *receiving, "channel", channel, "datarate", datarate, "PER", per, "SNR", snr, "totalPackets")
                
                trns = CurrentTransmission(sending, receiving, channel)
                
                #now let's assign the packets within this transmission
                currentTime = startTime
                while currentTime < endTime and len(sending.transmitPacketQueue) > 0:
                    lengthOfNextPacket = sending.transmitPacketQueue[-1].size
                    timeForNext = lengthOfNextPacket / datarate
                    if currentTime + timeForNext <= endTime and sending.has_power_to_transmit(timeForNext):
                        sending.use_transmit_power(timeForNext)
                        pck = sending.send_data()
                        trns.packets.append(pck)
                        trns.packetsTime.append((currentTime, currentTime + timeForNext))
                        currentTime = currentTime + timeForNext
                    else:
                        break  
                # Log("Sending", sending, "receiving", *receiving, "channel", channel, "datarate", datarate, "PER", per, "SNR", snr, "totalPackets", len(trns.packets))
                assert len(trns.packets) == len(trns.packetsTime)
                trns.PER = per
                trns.SNR = snr
                currentTransmissions.append(trns)
                        
        return currentTransmissions
        
        
