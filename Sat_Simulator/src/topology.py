import _pickle as pickle
import gc
from typing import List, Dict, Tuple # type: ignore
import typing
from time import time as timeNow

import numpy as np # type: ignore
import itertools

from src.satellite import Satellite
from src.station import Station
from src.links import Link
from src.utils import Time, Print
from src.log import Log
import const
import json

class Topology:
    """
    Class with availability map and link calculations that the routing class uses to schedule different paths

    Attributes:
        time (Time)
        satList (List[Satellite])
        groundList (List[Station])
        availableMap (Dict[sat][ground] = bool) - wether or not these two devices can see each other
        possibleLinks (Dict[sat][ground] = link) - the link object between these two devices
        nodeLinks (Dict[Node] = List[Links]) - a dict to a list of all potential links that it can have
    """
    #@profile
    def __init__(self, time: Time, satList: 'List[Satellite]', groundList: 'List[Station]') -> None:
        """
        Constructor will create the availability map and all of the possible links at time.

        Arguments:
            time (Time)
            satList (List[Satellite])
            groundList (List[Station])
        """
        self.satList = satList
        self.groundList = groundList
        self.time = time.copy()

        self.availableMap = self.create_available_map(time, satList, groundList)
        self.possibleLinks, self.nodeLinks = self.create_possible_links(self.availableMap, self.time)
        self.nFootprints = {sat: sum([1 for link in self.nodeLinks[sat] if link.gs.transmitAble]) for sat in self.satList}
    #@profile
    def create_available_map(self, time: Time, satList: 'List[Satellite]', groundList: 'List[Station]') -> 'Dict[Satellite, Dict[Station, bool]]':
        """
        Method to create avaibility map which calculates which ground stations a satellite can see at a time

        Arguments:
            time (Time)- when to calculate
            satList (list[Satellite]) - list of satellites
            groundList (list[Station])
        Returns:
            Dict[Satellite][Station] = bool
        """
        satToGround: 'Dict[Satellite, Dict[Station, bool]]' = {sat: {ground : False for ground in groundList} for sat in satList}
        ## this is based on eqn 1 in https://arxiv.org/pdf/1611.02402.pdf
        ## let n be number of sat, m be number of ground

        satPos = np.zeros((len(satList), 3))
        groundPos = np.zeros((len(groundList), 3))


        ## satPos : n x 3 where each row is a satellite's position vector
        for idx in range(len(satList)):
            sat = satList[idx]
            sat.calculate_orbit(time)
            satPos[idx] = sat.position.to_tuple()

        ## groundPos : m x 3 where each row is a gs's position vector
        for idx in range(len(groundList)):
            groundPos[idx] = groundList[idx].position.to_tuple()

        ## rNorms is a column vector of size m with the norms of the gs's position vectors
        rNorms = np.linalg.norm(groundPos, axis=1)

        # r0Site is a m x 3 mat where it is the gs's position vector normalized by its magnitude
        r0Site = np.divide(groundPos.T, rNorms).T

        ## update that matrix by duplicating it by the number of satellites.
        ## For example, [1,2,3] becomes [1,2,3]
        ##                              [1,2,3]
        ##                              etc
        ## This will be of size (m*n) x 3, where it goes
        ## [gs0]
        ## [gs1]
        ## [gsN]
        ## [gs0]
        r0Site = np.vstack([r0Site] * len(satList))

        ## delR is a (m*n) x 3 matrix where each row is the vector of the subtraction between the satellite positon and the ground position
        ## It is in the order of:
        ## [sat0 - gs0]
        ## [sat0 - gs1]
        ## [sat0 - gs2]
        ## etc.
        ## [sat1 - gs0]
        ## etc.
        delR = (satPos[:, np.newaxis] - groundPos).reshape(-1, groundPos.shape[1])

        delRNorms = np.linalg.norm(delR, axis=1)

        # delRDividedByMag is each row of delR normalized where delRNorms is the norm of each row
        delRDividedByMag = np.divide(delR.T, delRNorms).T

        ## Find the dot product of each row between delRDividedByMag and r0Site, and then convert to degrees
        ## the index of angles = the index of the satellite * len(groundList) + the index of each groundList
        ## 1d vector of size (m*n)
        angles =  np.arcsin( np.einsum('ij, ij->i', delRDividedByMag, r0Site) ) * 180/np.pi
        
        ## 1d vector of size (m*n) of booleans if they are greater than the required angle
        #greater = np.greater(angles, const.MINIMUM_VISIBLE_ANGLE)
        
        indicies = np.where(angles > const.MINIMUM_VISIBLE_ANGLE)
        ln = len(groundList)

        for idx in indicies[0]:
            sat = satList[ idx // ln]
            ground = groundList[idx % ln]

            #uncomment this line to check if your calculations are right
            #print(angles[idx], sat.position.calculate_altitude_angle(ground.position), sat.position.to_alt_az(ground.position, time)[0])
            #print(greater[idx], sat.position.calculate_altitude_angle(ground.position) > const.MINIMUM_VISIBLE_ANGLE)
            #if greater[idx]:
            satToGround[sat][ground] = True

        #satToGround = {satList[ idx // len(groundList)]: {ground : angles[idx] > const.MINIMUM_VISIBLE_ANGLE for ground in groundList} for idx in range(angles)}
        return satToGround

    def create_possible_links(self, satToGround: 'Dict[Satellite, Dict[Station, bool]]', time: Time) -> 'Tuple[Dict[Satellite, Dict[Station, Link]], Dict[Node, List[Link]]]':
        """
        Method to create all of the possible links between objects.

        Arguments:
            satToGround (Dict[Satellite][Station] = bool) - created from availabiltiy map which tells at time, which gs can be seen from a sat
        Returns
            A tuple of the following
            Dict[Satellite][Station] = Link. If the link is not possible, Dict[Satellite][Station] should cause a KeyError
        """
        ##TODO: speed this u
        linksDict: 'Dict[Satellite, Dict[Station, Link]]' = {}
        nodeLinks: 'Dict[Node, List[Link]]' = {i: [] for i in itertools.chain(self.satList, self.groundList)}

        ## create a list of all of the satellites and links as needed by the create_link method
        tmpSatList = []
        tmpGroundList = []
        for sat in satToGround.keys():
            linksDict[sat] = {}
            for gs in satToGround[sat].keys():
                if satToGround[sat][gs]:
                    tmpSatList.append(sat)
                    tmpGroundList.append(gs)
        
        self.linkList = Link.create_link(tmpSatList, tmpGroundList, self.time)

        ##put back into dictionary form:
        idx = 0
                
        for sat in satToGround.keys():
            for gs in satToGround[sat].keys():
                if satToGround[sat][gs]:
                    link = self.linkList[idx]
                    idx += 1
                    linksDict[sat][gs] = link

                    nodeLinks[sat].append(link)
                    nodeLinks[gs].append(link)

        return linksDict, nodeLinks

    @typing.no_type_check
    def save(self, outFile) -> str:
        """
        Method to save a topology object to a string so it can be reloaded

        Returns:
            str - string representation of the topology. It is formatted as:
        """
        #All we save is the SNR & distance - rest we recalculate
        
        #snr (float) - snr of ground recieving object
        """
        #let's make a json object instead
        outDict = {}
        outDict["time"] = self.time.to_str()
        #let's make it for self.possibleLinks
        outDict["possibleLinks"] = {}
        for sat, dict in self.possibleLinks.items():
            outDict["possibleLinks"][sat.id] = {}
            for gs, val in dict.items():
                outDict["possibleLinks"][sat.id][gs.id] = {}
                outDict["possibleLinks"][sat.id][gs.id]["snr"] = val.snr
                outDict['possibleLinks'][sat.id][gs.id]["distance"] = val.distance
        
        outStr = json.dumps(outDict)
        """
        #We're going to save the maps as a pickle file
                
        #we really only need the linkList
        #we need to switch the keys to be the id's
        
        for link in self.linkList:
            link.sat = link.sat.id
            link.gs = link.gs.id
            
        #for sat in self.possibleLinks.keys():
        #    newLinks[sat.id] = {gs.id: item for gs, item in self.possibleLinks[sat].items()}
        
        pickle.dump(self.linkList, outFile)
        
    @typing.no_type_check
    @staticmethod
    def load(filePath: 'str', satList: 'List[Satellite]', gsList: 'List[Station]') -> 'Topology':
        """
        Method to load a topology object from a string

        Arguments:
            str (str) - string to load from
        Returns:
            Topology - topology object loaded from string
        """
        idToSat = {sat.id: sat for sat in satList}
        idToGs = {gs.id: gs for gs in gsList}
        
        #let's try loading the pickle file
        print(filePath)
        t = timeNow()
        with open(filePath, 'rb') as file:
            gc.disable()
            loadedList = pickle.load(file) #this is a list of links
            print(len(loadedList))
        print("Time to load pickle: ", timeNow() - t)
        t = timeNow()
        possibleLinks = {sat: {} for sat in satList}
        #create the nodeLinks with preallocated space - let's guess 100 links per node
        nodeLinks = {node: [] for node in itertools.chain(satList, gsList)}
        nFootprints = {sat: 0 for sat in satList}
        
        #change the sat and gs to be the actual objects
        def changeLink(link):
            link.sat = idToSat[link.sat] #link.sat is the id
            link.gs = idToGs[link.gs] #link.gs is the id
            nodeLinks[link.sat].append(link)
            nodeLinks[link.gs].append(link)
            
            if link.gs.transmitAble:
                nFootprints[link.sat] += 1
        
        for link in loadedList:
            changeLink(link)
        
        print(len(loadedList))
        print("Time to load links: ", timeNow() - t)
        
        top = Topology.__new__(Topology)
        #top.time = time
        top.availableMap = {}
        top.possibleLinks = possibleLinks
        top.nodeLinks = nodeLinks
        top.satList = satList
        top.groundList = gsList
        top.nFootprints = nFootprints
        gc.enable()
       
        return top
