import itertools
from typing import List, Dict # type: ignore
from enum import Enum # type: ignore
import random
import math
import matplotlib.pyplot as plt # type: ignore
from time import time as time_now # type: ignore
import scipy

import numpy as np # type: ignore
import networkx as nx # type: ignore

from src.satellite import Satellite
from src.station import Station
from src.links import Link
from src.topology import Topology
from src.log import Log
from src.Coloring_MWIS_heuristics import greedy_MWIS

import const
from const import RoutingMechanism

distanceBetweenGS = {}
lastTransmitted = {}
class Routing:
    """
    Class that creates the scheduling of the different satellites

    Attributes:
        topology (Topology) - Instance of Topology class created at this time
        bestLinks (Dict[Satellite][Station] = Link) - the links that were scheduled
    """
    def __init__(self, top: 'Topology', timeStep:float) -> None:
        self.timeStep = timeStep
        self.topology = top
        self.bestLinks = self.schedule_best_links()
    
    def plot_bipartite_graph(self):
        """
        Plots the bipartite graph of the links
        """
        print("plotting bipartite graph")
        print(len(self.topology.satList))
        print(len(self.topology.groundList))
        G = nx.Graph()
        print("adding nodes")
        for sat in self.topology.satList:
            G.add_node(sat, bipartite=0)
        print("adding edges")
        for station in self.topology.groundList:
            if station.recieveAble:
                G.add_node(station, bipartite=1)
        print("adding edges")
        for sat in self.topology.satList:
            for station in self.topology.possibleLinks[sat]:
                G.add_edge(sat, station)
        print("drawing graph")

        pos = nx.bipartite_layout(G, self.topology.satList)

        #make labels the nodeId
        labels = {}
        for node in G.nodes:
            labels[node] = node.id
        nx.draw(G, pos = pos, with_labels = True, labels = labels, node_size = 20)
        #plt.savefig("bipartite.png")
        plt.show()
        print("bipartite graph saved to bipartite.png")

    def schedule_best_links(self) -> 'Dict[Satellite, Dict[Station, Link]]':
        """
        Public method to schedule best links. If you want to change the routing mechanism, you can change the ROUTING_MECHANISM variable in const.py
        If you want to add a method, add a new RoutingMechanism enum value and add it to the statement in the function below and create a method

        Returns:
            Dict[Satellite][Station] = Link - the links that were scheduled. If you try to schedule a link that is not possible, it should return a keyerror
        """
        if const.ROUTING_MECHANISM == RoutingMechanism.assign_by_datarate_and_available_memory:
            return self.assign_by_datarate_and_available_memory(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.transmit_with_random_delay:
            return self.transmit_with_random_delays(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.use_all_links:
            return self.use_all_links(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.transmission_probability_function:
            return self.transmission_probability_function(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.multiple_footprints_can_only_see_one:
            return self.multiple_footprints_can_only_see_one(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.probability_based_on_number_of_footprints:
            return self.probability_based_on_number_of_footprints(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.probability_with_hyperparameter:
            return self.probability_with_hyperparameter(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.hyperparameter_and_greedy:
            return self.hyperparameter_and_greedy(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.fossa_routing:
            return self.fossa_routing(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.combined_weighted_and_alpha:
            return self.combined_weighted_and_alpha(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.l2d2:
            return self.l2d2(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.single_and_l2d2:
            return self.single_and_l2d2(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.aloha_and_l2d2:
            return self.aloha_and_l2d2(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.ours:
            return self.ours(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.single_and_ours:
            return self.single_and_ours(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.aloha_and_ours:
            return self.aloha_and_ours(self.topology.possibleLinks)
        elif const.ROUTING_MECHANISM == RoutingMechanism.ours_and_l2d2:
            return self.ours_and_l2d2(self.topology.possibleLinks)
        else:
            raise Exception("Routing mechanism not implemented")


    def assign_by_datarate_and_available_memory(self, possibleLinks: 'Dict[Satellite, Dict[Station, Link]]') -> 'Dict[Satellite, Dict[Station, Link]]':
        """
        This method will assign the links to the satellites based on the datarate and the available memory of the satellite/ground stations.

        Arguments:
            possibleLinks: Dict[Satellite][Station] = Link
        Returns:
            Dict[Satellite][Station] = Link, which is where info should be transmitted
        """
        outList: 'Dict[Satellite, Dict[Station, Link]]' = {}
        for sat in self.topology.satList:
            outList[sat] = {}
        self.linkList = sorted(self.topology.linkList, key= lambda d : d.downlinkDatarate * d.sat.percent_of_memory_filled() + d.uplinkDatarate * d.gs.percent_of_memory_filled(), reverse=True)

        ground_station_available = {gs: True for gs in self.topology.groundList}
        satellite_available = {sat: True for sat in self.topology.satList}

        for link in self.linkList:
            sat = link.sat
            ground = link.gs
            if satellite_available[sat] and ground_station_available[ground]:
                if ground.recieveAble and ground.transmitAble:
                    link.assign_transmission(0, self.timeStep, 0, sat)
                    link.assign_transmission(0, self.timeStep, 0, ground)
                    satellite_available[sat] = False
                    ground_station_available[ground] = False
                elif ground.recieveAble:
                    link.assign_transmission(0, self.timeStep, 0, sat)
                    satellite_available[sat] = False
                    if sat.beamForming == False:
                        for gs in possibleLinks[sat].keys():
                            ground_station_available[gs] = False
                    else:
                        ground_station_available[ground] = False

                elif ground.transmitAble:
                    ground_station_available[ground] = False
                    satellite_available[sat] = False

        return possibleLinks

    def transmit_with_random_delays(self, possibleLinks: 'Dict[Satellite, Dict[Station, Link]]') -> 'Dict[Satellite, Dict[Station, Link]]':
        """
        In this method every device will randomly pick a start time from lets say 1 to 60. Once they start, they will transmit exactly one packet.
        If at any point in time, there is a collision, the datarate of that device changes based on the updated SINR, and they will continue to transmit based on that for the rest of the packet.
        And once they transmitted the whole packet, they will randomly pick a delay and then transmit remaining packets. However, no partial packets will be sent, such as if the startingDelay is close to the end of the timestep.
        """

        gsUsed: 'Dict[Station, bool]' = {}

        satLst = list(possibleLinks.keys())
        random.shuffle(satLst) ##let's randomly move around the list so one sat isn't always transmitted to

        for sat in satLst:
            satTransmitting = False
            ##make sure gs can only transmit to one sat
            gsAble = {}
            if sat.has_power_to_recieve(self.timeStep):
                #TODO: add concentrator overall
                #sat.currentMWs -= sat.concentrator * self.timeStep
                for gs, lnk in possibleLinks[sat].items():
                    if gs not in gsUsed.keys() and gs.transmitAble and gs.has_data_to_transmit():
                        gsAble[gs] = lnk
                        gsUsed[gs] = True
                    elif gs.recieveAble and gs not in gsUsed.keys() and not satTransmitting and sat.has_data_to_transmit():
                        satTransmitting = True
                        lnk.assign_transmission(0, self.timeStep, 0, sat) #this will send data to ground
                        lnk.assign_transmission(0, self.timeStep, 0, gs) ##this should let the acks come back
                        for gs in possibleLinks[sat]:
                            if gs.recieveAble:
                                gsUsed[gs] = True
            ##then randomly have every gs randomly pick a starting second
            for gs, link in gsAble.items():
                timeToTransmit = math.ceil(gs.transmitPacketQueue[-1].size/link.uplinkDatarate)
                #this is set to 0 currently because nothing has been scheduled yet, but the variable is set to the time when the last packet stopped transmitting
                endTransmitTime = 0

                currPacketCounter = -1
                numPackets = gs.get_number_of_packets_to_transmit()

                ##while the last packet's transmission time still leaves enough time to transmit the next packet and there are more packets to transmit
                while endTransmitTime < (self.timeStep - timeToTransmit) and abs(currPacketCounter) <= numPackets:
                    startTime = random.randrange(endTransmitTime, int(self.timeStep - timeToTransmit), 1)
                    channel = random.randrange(0, sat.nChannels, 1)
                    endTransmitTime = startTime + timeToTransmit

                    currPacket = gs.transmitPacketQueue[currPacketCounter]
                    link.assign_transmission(startTime, currPacket.size/link.uplinkDatarate, channel, gs)

                    currPacketCounter -= 1

        return possibleLinks
    
    def transmission_probability_function(self, possibleLinks: 'Dict[Satellite, Dict[Station, Link]]') -> 'Dict[Satellite, Dict[Station, Link]]':        
        gsUsed: 'Dict[Station, bool]' = {}

        satLst = list(possibleLinks.keys())
        random.shuffle(satLst) ##let's randomly move around the list so one sat isn't always transmitted to

        for sat in satLst:
            satTransmitting = False
            ##make sure gs can only transmit to one sat
            gsAble = {}
            if sat.has_power_to_recieve(self.timeStep):
                #TODO: fix concentrator power model
                #sat.currentMWs -= sat.concentrator * self.timeStep
                for gs, lnk in possibleLinks[sat].items():
                    if gs not in gsUsed.keys() and gs.transmitAble:
                        gsAble[gs] = lnk
                        gsUsed[gs] = True
            ##then randomly have every gs randomly pick a starting second
            for gs, link in gsAble.items():
                lengthOfSlot = (const.PACKET_SIZE + const.PREAMBLE_SIZE)/link.uplinkDatarate
                numSlots = int(self.timeStep // lengthOfSlot)
                #this is set to 0 currently because nothing has been scheduled yet, but the variable is set to the time when the last packet stopped transmitting
                probabilityOfTransmission = min(1, 1/len(gsAble.keys())) 
                for i in range(0, numSlots):
                    if random.random() < probabilityOfTransmission:
                        #print("Transmitting and able to see:", len(self.topology.nodeLinks[gs]))
                        link.assign_transmission(lengthOfSlot*i, lengthOfSlot, random.randrange(0, sat.nChannels), gs)

        return possibleLinks
    
    def aloha(self, possibleLinks):
        for gs in self.topology.groundList:
            if not gs.transmitAble:
                continue
            if len(self.topology.nodeLinks[gs]) == 0:
                continue
            if not gs.has_data_to_transmit():
                continue
            
            link = self.topology.nodeLinks[gs][0]
            timeToTransmit = gs.transmitPacketQueue[-1].size/link.uplinkDatarate
            #this is set to 0 currently because nothing has been scheduled yet, but the variable is set to the time when the last packet stopped transmitting
            endTransmitTime = 0
            startTime = random.randrange(endTransmitTime, int(self.timeStep - timeToTransmit), 1)
            link.assign_transmission(startTime, timeToTransmit, 0, gs)
        return possibleLinks

    def single_sat(self, possibleLinks):
        for gs in self.topology.groundList:
            if not gs.transmitAble:
                continue
            if len(self.topology.nodeLinks[gs]) == 0:
                continue
            if not gs.has_data_to_transmit():
                continue
            lengthOfSlot = (const.PACKET_SIZE + const.PREAMBLE_SIZE)/self.topology.nodeLinks[gs][0].uplinkDatarate
            numSlots = int(self.timeStep // lengthOfSlot)
            #this is set to 0 currently because nothing has been scheduled yet, but the variable is set to the time when the last packet stopped transmitting
            #nDevicesColliding = 0
            sat = self.topology.nodeLinks[gs][0].sat
            nDevicesColliding = self.topology.nFootprints[sat]
            probabilityOfTransmission = min(1, 1/nDevicesColliding)
            random = np.random.rand(numSlots)
            slots = np.argwhere(random < probabilityOfTransmission)
            slots = slots[:len(gs.transmitPacketQueue)]
            slots = slots.flatten()
            #print("Device has", len(gs.transmitPacketQueue), "packets to transmit", "and", len(slots), "slots to transmit them in")
            for slot in slots:
                #print(slot)
                #print("Assigning transmission", lengthOfSlot*slot, lengthOfSlot*slot + lengthOfSlot, 0, gs, sat, "nDevicesColliding", nDevicesColliding)
                self.topology.nodeLinks[gs][0].assign_transmission(lengthOfSlot*slot, lengthOfSlot, 0, gs)
        return possibleLinks

    def l2d2(self, possibleLinks: 'Dict[Satellite, Dict[Station, Link]]') -> 'Dict[Satellite, Dict[Station, Link]]':
        cost_matrix = np.zeros((len(self.topology.satList), len(self.topology.groundList)))
        cost_matrix.fill(1000000000)
        total_downlink_rate=0
        satToId = {sat: i for i, sat in enumerate(self.topology.satList)}
        idToSat = {i: sat for i, sat in enumerate(self.topology.satList)}
        gsToId = {gs: i for i, gs in enumerate(self.topology.groundList) if gs.recieveAble}
        idToGs = {i: gs for i, gs in enumerate(self.topology.groundList) if gs.recieveAble}

        for sat in self.topology.satList:
            totalNum = len(sat.dataQueue) + len(sat.transmitPacketQueue)
            totalNum *= const.DATA_SIZE
            for gs, lnk in self.topology.possibleLinks[sat].items():
                if gs.recieveAble and totalNum > 0:
                    cost_matrix[satToId[sat]][gsToId[lnk.gs]] = -1 * (lnk.downlinkDatarate * self.timeStep/totalNum)
                else:
                    cost_matrix[satToId[sat]][gsToId[lnk.gs]] = 1000000000

        ideal_links = scipy.optimize.linear_sum_assignment(cost_matrix)
        row, col = ideal_links
        for row, col in zip(row, col):
            gs = idToGs[col]
            sat = idToSat[row]
            if gs not in possibleLinks[sat].keys():
                continue
            #if cost_matrix[row][col] == 0:
            #    continue
            lnk = possibleLinks[idToSat[row]][idToGs[col]]
            # Log("Assigning transmission", 0, self.timeStep, 0, idToGs[col], idToSat[row], "snr", -1 * cost_matrix[row][col], lnk.downlinkDatarate)
            lnk.assign_transmission(0, self.timeStep, 0, idToSat[row])
            total_downlink_rate += lnk.downlinkDatarate
            lnk.mark_gs_listening()
        Log("Total downlink rate", total_downlink_rate)
        return possibleLinks
    
    def our_uplink(self, possibleLinks):
        print("Scheduling uplink j")        
        iotDevices = [gs for gs in self.topology.groundList if gs.transmitAble]
        lengthOfSlot = (const.PACKET_SIZE + const.PREAMBLE_SIZE)/262 #self.topology.nodeLinks[gs][0].uplinkDatarate
        numSlots = int(self.timeStep // lengthOfSlot)
        satsToSlots: 'Dict[Satellite, Dict[numSlots, int]]' = {sat: {i: 0 for i in range(0, numSlots)} for sat in possibleLinks.keys()}
        
        random = np.random.rand(len(iotDevices), numSlots)
        for i in range(len(iotDevices)):
            gs = iotDevices[i]
            if gs.has_data_to_transmit() and len(self.topology.nodeLinks[gs]) > 0:
                sats = set()
                nDevicesColliding = 0
                
                for link in self.topology.nodeLinks[gs]:
                    if link.sat not in sats:
                        sats.add(link.sat)
                        nDevicesColliding += self.topology.nFootprints[link.sat]
                
                if nDevicesColliding == 0:
                    p = 1
                else:
                    p = gs.alpha / nDevicesColliding
                              
                slots = np.argwhere(random[i] < p)        
                slots = slots[:len(gs.transmitPacketQueue)]
                slots = slots.flatten()

                for slot in slots:
                    for sat in sats:
                        satsToSlots[sat][slot] += 1
                    self.topology.nodeLinks[gs][0].assign_transmission(lengthOfSlot*slot, lengthOfSlot, 0, gs)
                    print("Assigning transmission", lengthOfSlot*slot, lengthOfSlot*slot + lengthOfSlot, 0, gs, sat, "nDevicesColliding", nDevicesColliding)
                  
        if True:
            #now let's tune the alphas
            #print()
            for sat in satsToSlots.keys():
                if len(self.topology.nodeLinks[sat]) == 0:
                    continue
                numCollisions = sum([1 for i in satsToSlots[sat].keys() if satsToSlots[sat][i] > 1])
                numZeros = sum([1 for i in satsToSlots[sat].keys() if satsToSlots[sat][i] == 0])
                
                #print("Collisions", sat, numCollisions, numSlots)
                percentages = numCollisions / numSlots
                
                #print("Percentages", percentages)
                #N = number of devices transmitting, n = number of devices that can transmit
                #P(N >= 2) = 1 - P(N = 0) - P(N = 1)
                #p = 1/n
                #P(N = 0) = (1 - p)^n = (1 - 1/n)^n 
                #P(N = 1) = n * p * (1 - p)^(n-1) = n * 1/n * (1 - 1/n)^(n-1) = (1 - 1/n)^(n-1)
                #prob = 1 - [(1-1/n)^(n-1) + (1-1/n)^n]
                #idealProb = 1 - ((1 - 1/nDevicesTransmitting)**(nDevicesTransmitting - 1) + (1 - 1/nDevicesTransmitting)**nDevicesTransmitting)
                #print("idealProb:", idealProb, "current probability", sum(self.historicalCollisions[sat]) / 3, "nDevicesTransmitting:", nDevicesTransmitting)
                #idealColsProb = .26
                #upperBound = 1.25 * idealColsProb
                
                devices = set()
                if percentages > const.ALPHA_HIGHER_THRESHOLD:
                    for link in self.topology.nodeLinks[sat]:
                        if link.gs.transmitAble and link.gs not in devices:
                            link.gs.decrease_alpha()
                            devices.add(link.gs)
                
                #let's find ideal probability of no slots being used
                #P(N = 0) = (1 - p)^n = (1 - 1/n)^n
                
                #print("numZeros", numZeros, "numSlots", numSlots)
                if numZeros / numSlots > const.ALPHA_DOWN_THRESHOLD:
                    for link in self.topology.nodeLinks[sat]:
                        #print("Increasing alpha", link.gs.alpha)
                        if link.gs.transmitAble and link.gs not in devices:
                            link.gs.increase_alpha()
                            devices.add(link.gs)
        
        return possibleLinks
    

    def our_downlink(self, possibleLinks):
        global distanceBetweenGS, lastTransmitted

        if len(distanceBetweenGS) == 0:
            distanceBetweenGS = {gs1: {gs2: gs1.position.get_distance(gs2.position) for gs2 in self.topology.groundList if gs1.recieveAble} for gs1 in self.topology.groundList if gs1.recieveAble}
        if len(lastTransmitted) == 0:
            lastTransmitted = {sat: 1 for sat in self.topology.satList}
        print("Scheduling Downlink Ours")
        #Now lets schedule the downlink
        
        #create a graph of the links
        grph = nx.Graph()
        satLinks = {sat: [] for sat in self.topology.satList}
        validGs = {gs: [] for gs in self.topology.groundList if gs.recieveAble}
        for sat in self.topology.satList:
            for gs, link in possibleLinks[sat].items():
                if gs.recieveAble:
                    grph.add_node(link, weight=(link.snr + 10000))
                    satLinks[sat].append(link)
                    validGs[gs].append(link)

        for sat in satLinks.keys():
            for link1 in satLinks[sat]:
                for link2 in satLinks[sat]:
                    if link1 != link2 and link1.gs.recieveAble and link2.gs.recieveAble and distanceBetweenGS[link1.gs][link2.gs] < 0:
                        grph.add_edge(link1, link2)
                
        for gs in self.topology.groundList:
            if gs.recieveAble:
                for link in self.topology.nodeLinks[gs]:
                    for link2 in self.topology.nodeLinks[gs]:
                        if link != link2 and link.gs.recieveAble and link2.gs.recieveAble and link.sat != link2.sat:
                            grph.add_edge(link, link2)
                        for link3 in self.topology.nodeLinks[link2.sat]:
                            if link != link3 and link.gs.recieveAble and link3.gs.recieveAble and link.sat != link3.sat:
                                grph.add_edge(link, link3)    

        #plot the graph spread out so we can see it better
    
        if len(grph.edges)  != 0:
            #links = nx.maximal_independent_set(grph)
            #this algo is taken from https://stackoverflow.com/questions/30921996/heuristic-to-find-the-maximum-weight-independent-set-in-an-arbritary-graph
            #this solves for minimum weight independent set so we negate the weights
            
            adj_0 = nx.adjacency_matrix(grph).todense()
            a = -np.array([-grph.nodes[u]['weight'] for u in grph.nodes])
            IS = -np.ones(adj_0.shape[0])
            while np.any(IS==-1):
                rem_vector = IS == -1
                adj = adj_0.copy()
                adj = adj[rem_vector, :]
                adj = adj[:, rem_vector]

                u = np.argmin(a[rem_vector].dot(adj!=0)/a[rem_vector])
                n_IS = -np.ones(adj.shape[0])
                n_IS[u] = 1
                neighbors = np.argwhere(adj[u,:]!=0)
                if neighbors.shape[0]:
                    n_IS[neighbors] = 0
                IS[rem_vector] = n_IS
            
            goodInds = np.argwhere(IS == 1)
            indepdentLinks = [list(grph.nodes)[int(i)] for i in goodInds]
            print(len(indepdentLinks), "independent links")
            scheduled = {}
            scheduledLinks = {}
            for link in indepdentLinks:
                sat = link.sat
                if sat in scheduledLinks:
                    scheduledLinks[sat].append(link)
                else:
                    scheduledLinks[sat] = [link]
                #print("Scheduling", sat, "to", link.gs, "with snr", link.snr)
                link.mark_gs_listening()
                if sat in scheduled:
                    #let's use the link with the highest snr
                    if scheduled[sat].snr < link.snr:
                        scheduled[sat] = link
                else:
                    scheduled[sat] = link
                    
            for sat in scheduled.keys():
                print("Sat has", len(scheduledLinks[sat]), "links")
                Link.update_link_datarates(scheduledLinks[sat])
                scheduled[sat].assign_transmission(0, self.timeStep, 0, sat)
        
        print("Done Scheduling")
        lastTransmitted = {sat: lastTransmitted[sat] + 1 for sat in self.topology.satList}
        return possibleLinks
    
    def single_and_l2d2(self, possibleLinks):
        if not const.ONLY_DOWNLINK:
            possibleLinks = self.single_sat(possibleLinks)
        if not const.ONLY_UPLINK:
            possibleLinks = self.l2d2(possibleLinks)
        return self.l2d2(possibleLinks)
    
    def aloha_and_l2d2(self, possibleLinks):
        if not const.ONLY_DOWNLINK:
            possibleLinks = self.aloha(possibleLinks)
        if not const.ONLY_UPLINK:
            possibleLinks = self.l2d2(possibleLinks)
        return possibleLinks
    
    def ours(self, possibleLinks):
        if not const.ONLY_DOWNLINK:
            possibleLinks = self.our_uplink(possibleLinks)
        if not const.ONLY_UPLINK:
            possibleLinks = self.our_downlink(possibleLinks)
        return possibleLinks
    
    def single_and_ours(self, possibleLinks):
        if not const.ONLY_DOWNLINK:
            possibleLinks = self.single_sat(possibleLinks)
        if not const.ONLY_UPLINK:
            possibleLinks = self.our_downlink(possibleLinks)
        return possibleLinks
    
    def aloha_and_ours(self, possibleLinks):
        possibleLinks = self.aloha(possibleLinks)
        return self.our_downlink(possibleLinks)
    
    def ours_and_l2d2(self, possibleLinks):
        possibleLinks = self.our_uplink(possibleLinks)
        return self.l2d2(possibleLinks)
