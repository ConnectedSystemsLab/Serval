from enum import Enum
from typing import List, Union
import math

import itur # type: ignore
import numpy as np # type: ignore

from src.node import Node
from src.utils import Time, Location
from src.satellite import Satellite
from src.station import Station

import const
from const import SNRMechanism

class Link:
    """
    Class for each link between two objects

    Attributes:
        sat (Satellite)
        gs (Station)
        time (Time)
        snr (float) - snr of ground recieving object
        distance (float) - meters between both objects
        uplinkDatarate (float) - bits p sec of ground transmitting to sat
        downlinkDatarate (float) - bits p sec of sat transmitting to ground
    """

    @staticmethod
    def create_link(satellites: 'Union[List[Satellite], Satellite]', stations: 'Union[List[Station], Station]', time: Time) -> 'List[Link]':
        """
        This is the public method to create a link. Use this method instead of consturctor!
        This will create a link between satList[0] and groundList[0], satList[1] and groundList[1], etc.

        Arguments:
            satellites (List[Satellite] or Satellite) - a satellite object or a list of satellite objects. Must be the same as stations
            stations (List[Station] or Station) - a station object or a list of station objects. Must be same length as satList, each index of sat is matchd with index of groundList
            time (Time) - time of link
        Returns:
            List[Link] - a list of links
        """
        ##Convert everything to lists and double check lengths
        if not isinstance(satellites, List):
            satellites = [satellites]
        if not isinstance(stations, List):
            stations = [stations]
        if len(satellites) != len(stations):
            raise ValueError("Length of satellites and stations must be the same")

        n = len(satellites)

        ##This is the SNR model for TinyGS Satellites. Take a look and change this if u want to use something else.
        #based off of https://www.kymetacorp.com/wp-content/uploads/2020/09/Link-Budget-Calculations-2.pdf

        distance = np.array([stations[i].position.get_distance(satellites[i].position) for i in range(n)])

        fsl = 20 * np.log10(distance) + 20 * np.log10(const.FREQUENCY) + 20 * np.log10(4 * np.pi / 3e8)

        if const.INCLUDE_WEATHER_CALCULATIONS:
            alt = np.array([satellites[i].position.calculate_altitude_angle(stations[i].position) for i in range(n)])
            groundPos = [ground.position for ground in stations]
            lat, long, elev = Location.multiple_to_lat_long(groundPos)
            latNp = np.array(lat)
            longNp = np.array(long)

            A = itur.atmospheric_attenuation_slant_path(lat=latNp, lon=longNp, f= const.FREQUENCY/1e9, el=alt, p=0.01, D=1, R001=0, return_contributions=False)

            A = A.value
        else:
            A = np.zeros(n)

        ##Model for tinygs
        EIRP = -8
        BOTZMAN = 228.6 # in dB
        GR_T = -15.1 #Place holder for now
        LOG_BANDWIDTH = 10 * np.log10(const.BANDWIDTH)
        CONST = EIRP + BOTZMAN + GR_T - LOG_BANDWIDTH
        snrs = CONST - (fsl + A) + const.SNR_SCALING
        ##END of SNR model

        ##Create link objects
        outLinks = [Link(sat, ground, time, snr=snr, distance=dist) for sat, ground, snr, dist in zip(satellites, stations, snrs, distance)]

        return outLinks
    

    @staticmethod
    def vectorized_load(satellites: 'List[Satellite]', gsList: 'List[Station]', snrs: 'List[float]', distances: 'List[float]', time: 'Time'):
        """
        This is the public method to create a link. Use this method instead of consturctor!
        
        Arguments:
            satellites (List[Satellite]) - a list of satellite objects
            gsList (List[Station]) - a list of station objects
            snrs (List[float]) - a list of snrs
            distances (List[float]) - a list of distances
            time (Time) - time of link
        Returns:
            List[Link] - a list of links
        """
        #let's use numpy vectorization to make this faster. Link.constructor is a vectorized function so we can just call it
        time = np.array([time for i in range(len(satellites))])
        snrs = np.array(snrs)
        outList = Link.constructor(satellites, gsList, time, {})
        print(outList[:5])
        return outList
        

    def __init__(self, sat: Satellite, gs: Station, time: Time, **kwargs) -> None:
        """
        Constructor for link object. Before you use this, use the create_link method instead.
        Also: if you change this, double check the load method in topology.py
        TODO: move the link method to & from str to here
        Arguments:
            sat (Satellite)
            gs (Station)
            time (Time)
            **kwargs (dict) - optional arguments. If you pass this, it will override the default values
                snr (float)
                distance (float)
                uplinkDatarate (float)
                downlinkDatarate (float)
                BER (float)
                PER (float)
        """

        self.sat = sat
        self.gs = gs
        self.time = time.copy()

        self.percip = gs.percip
        self.freq = const.FREQUENCY

        ##these are calculated in the create_link method
        if 'snr' in kwargs:
            self.snr = kwargs['snr']
        else:
            self.snr = 0.0
        if 'distance' in kwargs:
            self.distance = kwargs['distance']
        else:
            self.distance = 0.0
        
        if 'uplinkDatarate' in kwargs:
            self.uplinkDatarate = kwargs['uplinkDatarate']
        else:
            self.uplinkDatarate = self.snr_to_datarate(self.snr, const.SNR_UPLINK_MECHANISM)
        if 'downlinkDatarate' in kwargs:
            self.downlinkDatarate = kwargs['downlinkDatarate']
        else:
            self.downlinkDatarate = self.snr_to_datarate(self.snr, const.SNR_DOWNLINK_MECHANISM)
        if 'BER' in kwargs:
            self.BER = kwargs['BER']
        else:
            self.BER = 0 # TODO fix this: self.ber_from_snr(self.snr)
        if 'PER' in kwargs:
            self.PER = kwargs['PER']
        else:
            ##NOTE: PER IS ONLY CORRECT WHEN USING CONST.PACKET_SIZE
            self.PER = 0 #self.per_from_ber(self.BER)
        
        ##these will be updated by the assign_transmission method
        self.startTimes: 'List[float]' = []
        self.endTimes: 'List[float]' = []
        self.channels: 'List[int]' = []
        self.nodeSending: 'List[Node]' = []

        self.gsListening = False
    
    #let's create a vectorized version of the constructor
    constructor = np.vectorize(__init__, excluded=['self'])
    
    def per_from_ber(self, ber):
        #We will use the const.ALLOWED_BITS_WRONG to calculate the PER
        if ber == 0:
            return 0
        #now let's use the binomial formula to calculate the PER for this BER
        packet_size = const.PACKET_SIZE + const.PREAMBLE_SIZE
        comb = np.math.comb
        per = 1 
        for i in range(0, const.ALLOWED_BITS_WRONG + 1):
            #n choose i * p^i * (1-p)^(n-i)
            #n = packet_size
            per -= comb(packet_size, i) * (ber**i) * ((1-ber)**(packet_size - i))
        return per

    def ber_from_snr(self, snr):
        if snr > -7.5:
            return .1 * 10**(-4)
        elif snr > -10:
            return .1 * 10**(-3)
        elif snr > -12.5:
            return .1 * 10**(-4)
        elif snr > -15:
            return .1 * 10**(-5)
        elif snr > -17.5:
            return .1 * 10 ** (-3)
        elif snr > -20:
            return .7 * 10**(-4)
        else:
            return 0
    
    def assign_transmission(self, startTime: 'float', duration: 'float', channel: int, node: 'Node'):
        """
        This method will add the scheduled transmission time to this link object

        Arguments:
            startTime (float) - start time relative to the beginning of the timeStep in seconds.
            duration (float) - duration of transmission in seconds
            channel (int) - channel of transmission
            node (Node) - node that is sending the transmission
        """
        if len(self.nodeSending) > 0 and self.nodeSending[0] != node:
            raise ValueError("Support for multiple nodes sending on the same link is not implemented yet. (This includes acks). Let Om know if u need these features back in.")
        self.shouldBeScheduled = True
        self.startTimes.append(startTime)
        self.endTimes.append(startTime + duration)
        self.channels.append(channel)
        self.nodeSending.append(node)

    def get_relevant_datarate(self, nd: 'Node') -> float:
        """
        Function where if you give it one of the nodes, it'll return the datarate if that node would transmit to the other. I added this to make the code easier to read

        Arguments:
            nd (Node) - the node you have
        Returns:
            float - the datarate from nd to the other node
        Raises:
            ValueError - object does not exist in link
        """
        if nd == self.sat:
            return self.downlinkDatarate
        if nd == self.gs:
            return self.uplinkDatarate
        else:
            raise ValueError("Not in this link")

    def get_other_object(self, nd: 'Node') -> Node:
        """
        Function where if you give it one of the nodes, it'll return the other node. I added this to make the code easier to read

        Arguments:
            nd (Node) - the node you know
        Returns:
            Node - the other node
        Raises:
            ValueError - object does not exist in link
        """
        if nd == self.sat:
            return self.gs
        if nd == self.gs:
            return self.sat
        else:
            raise ValueError("Not in this link")

    def mark_gs_listening(self):
        self.gsListening = True
    
    def is_listening(self):
        if len(self.nodeSending) > 0 and self.nodeSending[0] == self.gs:
            return True
        return self.gsListening
    
    @staticmethod
    def snr_to_datarate(snr: float, snrMechanism: 'SNRMechanism') -> float:
        """
        Converts the SNR to datarate.
        """
        if snrMechanism == SNRMechanism.lora:
            return Link.lora(snr)
        elif snrMechanism == SNRMechanism.greater_than17:
            return Link.greater_than17(snr)
        elif snrMechanism == SNRMechanism.bill:
            return Link.bill_model(snr)
        elif snrMechanism == SNRMechanism.none:
            return 0
        else:
            raise ValueError("SNR mechanism not recognized")

    @staticmethod
    def greater_than17(snr: float) -> float:
        if snr > -17.5:
            return 262
        else:
            return 0

    @staticmethod
    def lora(snr: float) -> float:
        if snr > -10:
            return 1855
        if snr > -12.5:
            return 1020
        if snr > -15:
            return 583
        if snr > -17.5:
            return 262
        if snr > -20:
            return 146
    
    @staticmethod
    def sf_to_rate(sf: int) -> float:
        #rlly the same as lora but i'm too lazy to change it
        if sf == 12:
            return 146
        elif sf == 11:
            return 262
        elif sf == 10:
            return 583
        elif sf == 9:
            return 1020
        elif sf == 8:
            return 1855
        
    
    @staticmethod
    def bill_model(snr: float) -> float:
        rate = 0
        rate_vals = [2 * 1 / 4, 2 * 1 / 3, 2 * 2 / 5, 2 * 1 / 2, 2 * 3 / 5, 2 * 2 / 3, 2 * 3 / 4, 2 * 4 / 5, 2 * 5 / 6,
                    2 * 8 / 9, 2 * 9 / 10, 3 * 3 / 5, 3 * 2 / 3, 3 * 3 / 4, 3 * 5 / 6, 3 * 8 / 9, 3 * 9 / 10, 4 * 2 / 3,
                    4 * 3 / 4, 4 * 4 / 5, 4 * 5 / 6, 4 * 8 / 9, 4 * 9 / 10, 5 * 3 / 4, 5 * 4 / 5, 5 * 5 / 6, 5 * 8 / 9,
                    5 * 9 / 10]
        snr_vals = [-2.35, -1.24, -0.30, 1.00, 2.23, 3.10, 4.03, 4.68, 5.18, 6.20, 6.42, 5.50, 6.62, 7.91, 9.35, 10.69,
                    10.98, 8.97, 10.21, 11.03, 11.61, 12.89, 13.13, 12, 73, 13.64, 14.28, 15.69, 16.05]
        for idx in range(len(rate_vals)):
            if snr > snr_vals[idx]:
                cur_rate = rate_vals[idx]
                if cur_rate > rate:
                    rate = cur_rate
        return 76.8 * 1e6 * rate * 6 * const.DOWNLINK_BANDWIDTH_SCALING

    @staticmethod
    def get_data_rate_with_collisions(lnkList: 'List[Link]', recievingNode: 'Node') -> 'List[float]':
        """
        Given a list of link objects, return new datarates based on the SINR of the collisions. This will not change anything about the link objects

        Arguments:
            lnkList (List[Link]) - list of links colliding
            recievingNode (Node) - node that is receiving the collisions
        Returns:
            List[float] - list of datarates
        """
        raise Exception("This method is deprecated - newer ways to do this!")

    #this table is from the paper "Analysis of BER and Coverage Performance of LoRa Modulation under Same Spreading Factor Interference"
    #it's fig 1 converted from a graph to a table
    sf_and_snr_to_ber = {
        7: {
            -24: .5,
            -18: .4, 
            -16: .3,
            -14: .2,
            -12: .1,
            -10: 1.1e-2,
            -8: .8e-3,
            -7: .8e-4,
            -6.5: .1e-4
        },
        8: {
            -24: .5,
            -18: .3,
            -16: .1,
            -14: .7e-1,
            -12: .8e-2,
            -10: 1.1e-4,
            -9: .2e-4,
            -8: .8e-5
        },
        9: {
            -24: .5,
            -22: .4,
            -20: .3,
            -18: .1,
            -16: .3e-1,
            -15: 1e-2,
            -14: 1.1e-3,
            -13: 1.1e-4,
            -12: 1e-5,
        },
        10: {
            -24: .3,
            -22: .2,
            -20: .1,
            -18: .1e-1,
            -17: 1.3e-3,
            -16: 1.3e-4,
            -15: 1e-4
        }, 
        11: {
            -24: .1,
            -22: .8e-1,
            -21: 1.1e-2,
            -20: 1.4e-3,
            -19: 1.4e-4,
            -18: 1.2e-5,
        },
        12: {
            -24: 1.2e-2,
            -22: .9e-3,
            -21: 1.4e-5,
        }
    }
    @staticmethod
    def update_link_datarates(lnkList: 'List[link]'):
        """
        This method updates the datarates of the links in the list. 
        Use this to adapt the datarates to there respective SNRs when transmitting to multiple gs
        
        Arguments:
            lnkList (List[Link]) - list of links to update. All sending from the same satellite
        Returns:
            None
        """
        
        assert len(lnkList) > 0, "List of links is empty"
        #make sure all the links are sending from the same satellite
        sat = lnkList[0].sat
        assert all([lnk.sat == sat for lnk in lnkList]), "Not all links are sending from the same satellite"
        if len(lnkList) == 1:
            return
        
        sfs = [8, 9, 10, 11, 12]
        for sf in sfs:
            #let's get the overall ber for this sf
            #each link has a different snr, so we need to get the ber for each snr
            #ber is indepdent for each link, so we can just multiply them together
            ber = 1
            bers = {}
            for lnk in lnkList:
                #get the value in the dictionary that is the closest but less than the snr
                #ber = ber * Link.sf_and_snr_to_ber[sf][max([x for x in Link.sf_and_snr_to_ber[sf].keys() if x <= snr])]
                bers[lnk] = Link.sf_and_snr_to_ber[sf][max([x for x in Link.sf_and_snr_to_ber[sf].keys() if x <= lnk.snr])]
                ber = ber * bers[lnk]
            print("sf: {}, ber: {}".format(sf, ber))
            if ber < const.MINIMUM_BER:
                #we found the sf that works for all the links
                for lnk in lnkList:
                    original = lnk.downlinkDatarate
                    lnk.downlinkDatarate = Link.sf_to_rate(sf)
                    print("Changing datarate from {} to {} for link {}".format(original, lnk.downlinkDatarate, lnk))
                    lnk.BER = ber
                    per = lnk.PER
                    lnk.PER = lnk.per_from_ber(ber)
                    print("Changing PER from {} to {} for link {}".format(per, lnk.PER, lnk))
                return
            
        #if we get here, then we couldn't find a sf that works for all the links
        #so just use the values that are already there
        
