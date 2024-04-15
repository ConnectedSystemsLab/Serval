from datetime import datetime
from typing import List, Dict, Optional
import math
from matplotlib.offsetbox import OffsetImage

from skyfield.api import load, wgs84, EarthSatellite  # type: ignore
from skyfield.toposlib import ITRSPosition # type: ignore
import matplotlib.pyplot as plt # type: ignore
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import numpy as np # type: ignore
import pandas as pd # type: ignore
import cartopy # type: ignore
import cartopy.crs as ccrs # type: ignore
from cartopy.geodesic import Geodesic # type: ignore
import shapely # type: ignore
from PyAstronomy import pyasl # type: ignore

from src.node import Node
from src.utils import Location, Print, Time
from src.data import Data
from src.packet import Packet
import const

class Satellite (Node):
    """
    Satellite object which extends Node class

    Attributes:
        tle (str)
        hasTle (bool)
        storedPosition (Dict[str, Location])
        hasKepler (bool) - has a kepler object
        kepler (PyAstronomy.pyasl.KeplerEllipse) - kepler ellipse object. Created when create_constellation is run
        keplerReferenceTime - creates a reference time when kepler's equations are calculated with respect to
    Static attributes:
        idToSatellite (Dict[int, Satellite]) - a dictionary that maps each id to a satellite object
        nameToSatellite (Dict[str, Satellite]) - a dictionary that maps each name to a satellite object
    """

    EarthPos = None
    SunPos = None

    idToSatellite: 'Dict[int, Satellite]' = {}
    nameToSatellite: 'Dict[str, Satellite]' = {}

    def __init__(self, name: str, id: int, tle: str = "", beamForming = False, packetBuffer: int = 2147483646, maxMemory: int = 2147483646) -> None:
        """
        Constructor for Satellite object

        Arguments:
            name (str) - name of object
            id (int) - id of object, often NORAD
            tle (str) - optional argument, default is "", if tle, insert here
            *rest is from node*
        """
        super().__init__(name, id, Location(0,0,0), beamForming, packetBuffer, maxMemory)

        if id in Satellite.idToSatellite.keys():
            raise ValueError("All satellite ids must be unique")

        Satellite.idToSatellite[self.id] = self
        Satellite.nameToSatellite[self.name] = self
        self.storedPositions: 'Dict[datetime, Location]' = {}

        self.beamForming = beamForming

        ##Position stuff:
        self.tle = tle
        self.hasTle = True
        self.hasKepler = False
        self.kepler: 'Optional[pyasl.KeplerEllipse]' = None
        self.keplerReferenceTime: 'Optional[Time]' = None
        self.setup_skyfield()

    def setup_skyfield(self):
        """
        This method sets up all of the necessary skyfield variables based on what's passed in the constructor. 
        """
        if self.tle != "":
            self.hasTle = True

            ##skyfield stuff:
            self.ts = load.timescale() ##skyfield stuff
            tleLines = self.tle.rstrip('\n').split("\n")

            if len(tleLines) == 2:
                self.earthSatellite = EarthSatellite(tleLines[0], tleLines[1]);
            elif len(tleLines) == 3:
                self.earthSatellite = EarthSatellite(tleLines[1], tleLines[2])
            else:
                raise ValueError("Invalid TLE")

        else:
            ##false for now till create constellations method is run
            self.hasTle = False
            self.tle = ""
            self.hasKepler = False

        if const.INCLUDE_POWER_CALCULATIONS and Satellite.SunPos is None and Satellite.EarthPos is None:
            ##This should only be run once!
            data = load('dependencies/de440s.bsp')
            Satellite.SunPos = data['sun']
            Satellite.EarthPos = data['earth']

    def delete_skyfield(self):
        """
        This method will delete all the information created in setup_skyfield. It's useful for pickling objects. 
        """
        self.earthSatellite = None
        self.ts = None
        self.kepler = None
        self.keplerReferenceTime = None

    def calculate_orbit(self, time: Time) -> Location:
        """
        Public method that calls the other orbit calculation methods. This will update the satellite's position and store it for later use if needed

        Arguments:
            time (Time) - when to calculate position at
        Returns:
            Location - the satellite's position as a utils.Location object
        """
        if const.FIXED_SATELLITE_POSITION:
            return self.position
        
        if time.to_datetime() in self.storedPositions.keys():
            pos = self.storedPositions[time.to_datetime()]
            self.position = pos
            return pos

        elif self.hasTle:
            loc =  self.calculate_orbit_with_tle(time, self.tle)
            self.storedPositions[time.to_datetime()] = loc
            self.position = loc
            return loc

        elif self.hasKepler:
            loc = self.calculate_orbit_without_tle(time)
            self.storedPositions[time.to_datetime()] = loc
            self.position = loc
            return loc
        else:
            raise ValueError("No position based information given. Either give constellation info using create_constellation or insert TLE")
            pass

    def calculate_orbit_at_multiple_times(self, startTime: Time, endTime: Time, timeStep: float) -> "Dict[datetime, Location]":
        """
        Calculates the orbit of this satellite multiple times for faster processing. Be careful as this does not update self.position but updates self.storedPositions

        Arguments:
            startTime (Time)
            endTime (Time)
            timeStep (float) - seconds

        Returns:
            Dict[datetime] = Location where the key is a datetime object
        """
        ##based on https://stackoverflow.com/questions/49494082/skyfield-achieve-sgp4-results-with-1-second-periodicity-for-given-time-interval

        Print("Calculating positions for " , self, " between these times: ", startTime.to_str(), " and ", endTime.to_str())

        times = []
        timeDifferenceInSeconds = []
        tme = startTime.copy()

        while tme < endTime:
            times.append(tme.to_datetime())
            tme.add_seconds(timeStep)

            if self.hasKepler and isinstance(self.keplerReferenceTime, Time):
                timeDifferenceInSeconds.append( tme.difference_in_seconds(self.keplerReferenceTime) )

        out = {}
        if self.hasTle:

            t = self.ts.utc(times)
            gcrsLocation = self.earthSatellite.at(t)

            for idx in range(len(times)):
                itrs = gcrsLocation[idx].itrf_xyz().m
                out[times[idx]] = Location(itrs[0], itrs[1], itrs[2])

        elif self.hasKepler and isinstance(self.kepler, pyasl.KeplerEllipse):
            loc = self.kepler.xyzPos(np.array(timeDifferenceInSeconds))

            for i in range(len(times)):
                out[times[i]] = Location(loc[i][0], loc[i][1], loc[i][2])

        self.storedPositions = out
        return out

    def calculate_orbit_with_tle(self, time: Time, tle: str) -> Location:
        """
        Calculates the orbit of a satellite:

        Arguments:
            time (Time) - time when position wants to be calculated
            tle (str) - tle of satellite
        Returns:
            Location object
        """
        #code based off of https://rhodesmill.org/skyfield/earth-satellites.html
        t = self.ts.utc(time.to_datetime())
        if abs(t - self.earthSatellite.epoch) > 21:
            Print("Warning: TLE is more than 21 days old", logLevel="error")
            Print("TLE: ", self.tle, logLevel="error")
            Print("Time: ", time.to_str(), logLevel="error")
            Print("Epoch: ", self.earthSatellite.epoch.utc_strftime(), logLevel="error")
            Print("Time Difference (Days): ", (t - self.earthSatellite.epoch), logLevel="error")

        gcrsLocation = self.earthSatellite.at(t)
        itrs = gcrsLocation.itrf_xyz().m
        loc = Location(itrs[0], itrs[1], itrs[2])
        return loc

    def calculate_orbit_without_tle(self, time: Time) -> Location:
        """
        Calculates the orbit of a satellite:

        Arguments:
            time (Time) - time when position wants to be calculated
        Returns:
            Location object
        """
        #code based off of https://pyastronomy.readthedocs.io/en/latest/pyaslDoc/aslDoc/keplerOrbitAPI.html#PyAstronomy.pyasl.KeplerEllipse

        if self.hasKepler and isinstance(self.kepler, pyasl.KeplerEllipse) and isinstance(self.keplerReferenceTime, Time):
            loc = self.kepler.xyzPos(time.difference_in_seconds(self.keplerReferenceTime))
            return Location(loc[0], loc[1], loc[2])
        else:
            raise ValueError("No kepler object found. Run create_constellation")

    def in_sunlight(self, time: Time) -> bool:
        """
        Checks if the satellite is in sunlight at a given time. Needs the position to be updated

        Arguments:
            time (Time) - time to check
        Returns:
            bool - True if in sunlight, False if not
        """
        ##code stolen from: https://space.stackexchange.com/questions/37713/how-can-i-calculate-if-a-satellite-is-currently-in-sunlight-or-eclipse-using-pye
        if Satellite.SunPos is None or Satellite.EarthPos is None:
            raise ValueError("Sunlight calculations not initialized")
        if not self.hasTle:
            raise ValueError("Currently this feature only works with TLEs")

        tme = self.ts.utc(time.to_datetime())
        sat = Satellite.EarthPos + self.earthSatellite

        sunpos, earthpos, satpos = [thing.at(tme).position.km for thing in (Satellite.SunPos, Satellite.EarthPos , sat)]
        sunearth, sunsat = earthpos-sunpos, satpos-sunpos
        sunearthnorm, sunsatnorm = [vec/np.sqrt((vec**2).sum(axis=0)) for vec in (sunearth, sunsat)]
        angle = np.arccos((sunearthnorm * sunsatnorm).sum(axis=0))
        sunearthdistance = np.sqrt((sunearth**2).sum(axis=0))
        sunsatdistance = np.sqrt((sunsat**2).sum(axis=0))
        limbangle        = np.arctan2(6378.137, sunearthdistance)
        return (angle > limbangle) or (sunsatdistance < sunearthdistance)

    def calculate_footprint(self) -> float:
        """
        Calculates the footprint of the satellite. Needs the position to already be updated

        Returns:
            float - Footprint #radius of circle on Earth in m
        """        
        ##This uses geometry to find the footprint of the satellite
        ##There is a triangle with one side being the length from the center of the earth to the satellite (h), another side is the length from the center of the earth to the farthest point that a station can see a satellite (r), and the third side is from that station to the satellite (d).
        ##The angle above the horizon from the station is the const.MINIMUM_VISIBLE_ANGLE, so the angle between r & d is 90 + const.MINIMUM_VISIBLE_ANGLE
        ##We need to find theta the angle between h & r - so use the law of sines to find the values of all the angles

        EARTH_RADIUS = 6371000.0 #Meters
        elev = self.position.to_lat_long()[2] #Height above earth in m

        h = elev + EARTH_RADIUS
        r = EARTH_RADIUS
        phi = const.MINIMUM_VISIBLE_ANGLE + 90 #Angle between r & d
        phi = np.radians(phi)

        ##find angle opposite of r using law of sines
        ##sin(phi)/h = sin(gamma)/r
        gamma = np.arcsin(r*np.sin(phi)/h) #angle between d & h
        gamma = np.degrees(gamma)

        phi = np.degrees(phi)
        theta = 180 - phi - gamma

        distance = theta/360 * 2 * np.pi * EARTH_RADIUS #arc length of the circle of the Earth
        return distance

    @staticmethod
    def plot_satellites(satList: 'List[Satellite]', threeDimensions: bool = True, outPath = "") -> None:
        """
        Plots all the satellites and their footprints. Needs the position to already be updated.

        Arguments:
            satList (List[Satellite]) - list of satellites
            threeDimensions (bool) - default is true, plot in 3d, if not, plot in 2d. It only plots the footprints if in 3d (it's kind of ugly in 2d)
            outPath (str) - default is "", if not, you can specify the outfile & path it'll save to
        """
        Print("Plotting satellites:", len(satList))
        
        gd = Geodesic()
        
        if threeDimensions:
            map = ccrs.Orthographic(-10, 45)
        else:
            map = ccrs.PlateCarree()
        transform = ccrs.PlateCarree()

        fig = plt.figure(figsize=(3, 3))
        ax = fig.add_subplot(projection=map)
        ax.coastlines()
        ax.set_global()
        ax.gridlines()
        geoms = []

        latList, longList, elevList = Location.multiple_to_lat_long([sat.position for sat in satList])
        if min(elevList) <= 0:
            Print("Ensure that your satellites positions are updated before plotting", logLevel="error")
        
        ##Now we assign each type of satellite to its own color
        label = [type(sat).__name__ for sat in satList]
        labelDict: 'Dict[str, List[int]]' = {lb: [] for lb in label} #dict of ind to list of indexes
        for i in range(len(satList)):
            labelDict[label[i]].append(i)

        for lb in labelDict:
            lngList = [longList[i] for i in labelDict[lb]]
            ltList = [latList[i] for i in labelDict[lb]]
            distances = [satList[i].calculate_footprint() for i in labelDict[lb]]
            
            if threeDimensions:
                plt.scatter(x = lngList, y = ltList, transform=transform, label=lb, color='orange')
                for ind in labelDict[lb]:
                    cp = gd.circle(lon=longList[ind], lat=latList[ind], radius=satList[ind].calculate_footprint())
                    geoms.append(shapely.geometry.Polygon(cp))
            else:
                plt.scatter(x = lngList, y = ltList, transform=transform, label=lb)

        if threeDimensions:
            ax.add_geometries(geoms, crs=transform, edgecolor='r', alpha=.5)

        plt.legend()
        plt.tight_layout()
        plt.title("Satellites Current Position")
        if outPath == "":
            plt.show()
        else:
            plt.savefig(outPath, bbox_inches='tight')

    @staticmethod
    def create_constellation(listOfSats: 'List[Satellite]', numberOfPlanes: int, numberOfSatellitesPerPlane: int, inclination: float, altitude: float, referenceTime: 'Time') -> 'List[Satellite]':
        """
        Creates a constellation of objects from a specified shell. This makes a lot of assumptions regarding a circular orbit.
        Probably will have to change for other orbital models such as sun-synchronous satellites.

        This does not affect satellite.position, but using compute_at_multiple_times will be very useful for this system

        Arguments:
            listOfSats (List[Satellite]) - a list of Satellites which have already been constructed. This will replace the position and tle of the satellites
            numberOfPlanes (int) - the number of orbital planes
            numberOfSatellitesPerPlane (int) - the number of satellites per orbital plane
            inclination (float) - the inclination of the orbital plane in degrees
            altitude (float) - the altitude of the orbital plane in meters
            referenceTime (Time) - start time that the constellation is modeled off of
        Returns:
            List[Satellite] - list of satellites
        """
        #code based off of https://pyastronomy.readthedocs.io/en/latest/pyaslDoc/aslDoc/keplerOrbitAPI.html#PyAstronomy.pyasl.KeplerEllipse

        ##this uses a keplarian orbit to create a constellation
        ##so you need 6 things: eccentricity, semi major axis, inclination, argument of periapsis, right ascension of ascending node, true anomaly

        ##Constants:
        EARTH_RADIUS = 6371000.0 #Meters
        EARTH_MASS = 5.972 * 10**24 #kg
        GRAVITATIONAL_CONSTANT = 6.67408 * 10**-11 #N*m^2/kg^2

        ##Assuming a circle, decently accurate for LEO and GEO
        semiMajorAxis = altitude + EARTH_RADIUS
        eccentricity = 0
        period = 2 * math.pi * math.sqrt(semiMajorAxis**3 / (GRAVITATIONAL_CONSTANT * EARTH_MASS)) # seconds

        angleOfAssending = 360 ##The angle between the ascending nodes and the orbital planes that the satellites are in
        ##assume that it's 360 degrees, might have to change for constelattions such as Iridium that has a 180 degree angle
        longitudeOffsetsAtEquator = [(angleOfAssending / numberOfPlanes) * i for i in range(numberOfPlanes)]
        timeOffsets = [(period/numberOfSatellitesPerPlane) * i for i in range(numberOfSatellitesPerPlane)]

        ##change the satellites object
        for planeNumber in range(numberOfPlanes):
            for numberInPlane in range(numberOfSatellitesPerPlane):
                sat = listOfSats[planeNumber*numberOfSatellitesPerPlane + numberInPlane]
                sat.hasKepler = True
                sat.kepler = pyasl.KeplerEllipse(a = semiMajorAxis, per = period, e = eccentricity, tau = timeOffsets[numberInPlane], Omega = longitudeOffsetsAtEquator[planeNumber], i = inclination)
                sat.keplerReferenceTime = referenceTime.copy()
        return listOfSats

    @staticmethod
    def load_from_tle(tleFile: str, **kwargs) -> 'List[Satellite]':
        """
        Loads a file of three-line TLEs and returns a list of all of the objects. These will be satellite objects which a decorator will need to be applied to
        
        Arguments:
            tleFile (str) - a path to a 3 line tle file - you can get this from celestrak or another source
            kwargs (keywords) - specify any additional arguments which will be passed to the constructor of satellite
        Returns:
            List[Satellite] - list of satellites
        Raises:
            ValueError - if the number of lines in the tle file is not divisible by 3
        """

        file = open(tleFile, 'r')
        lines = file.readlines()
        
        if (len(lines) % 3 != 0):
            raise ValueError("Number of lines in tle file is not divisible by 3")
        
        satList = []
        for i in range(0, len(lines), 3):
            name = lines[i]
            line1 = lines[i+1]
            line2 = lines[i+2]

            id = int(line2.split()[1])
            s = Satellite(name, id, line1 + line2, **kwargs)
            satList.append(s)
        return satList
