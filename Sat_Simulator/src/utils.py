from datetime import datetime, timedelta, timezone
from queue import PriorityQueue
from typing import Deque, Iterable, Tuple, List

from astropy.coordinates import EarthLocation, ITRS, AltAz, CIRS  # type: ignore
from astropy import units as astropyUnit
from matplotlib.patches import Polygon  # type: ignore
import numpy.linalg as la  # type: ignore
import numpy as np
from collections import deque
import const


class FusedQueue(Deque):
    # All but the last queue is priority queue
    def __init__(self, queue_list: List[Deque], priority_bw_allocation=None, callback=None):
        self.queue_list = queue_list
        super().__init__()
        self.priority_bw_allocation = priority_bw_allocation if priority_bw_allocation is not None else const.MAX_PRIORITY_BANDWIDTH
        self.sent_size = 0
        self.priority_sent_size = 0
        self.callback = callback
    
    def empty(self):
        return len(self) == 0

    def pop(self):
        result = None
        for queue in self.queue_list:
            if self.priority_sent_size > 0 and self.priority_sent_size/self.sent_size > self.priority_bw_allocation and queue is not self.queue_list[-1] and len(self.queue_list[-1]) > 0:
                continue
            if len(queue) > 0:
                result = queue.pop()
                self.sent_size += result.size
                if queue is not self.queue_list[-1]:
                    self.priority_sent_size += result.size
                break
        if self.callback is not None:
            self.callback(result, 'pop')
        return result

    def appendleft(self, item):
        if self.callback is not None:
            self.callback(item, 'appendleft')
        self.queue_list[0].appendleft(item)

    def extendleft(self, __iterable: Iterable) -> None:
        if self.callback is not None:
            self.callback(__iterable, 'extendleft')
        self.queue_list[0].extendleft(__iterable)

    def append(self, item):
        if self.callback is not None:
            self.callback(item, 'append')
        self.queue_list[-1].append(item)

    def extend(self, __iterable: Iterable) -> None:
        if self.callback is not None:
            self.callback(__iterable, 'extend')
        self.queue_list[-1].extend(__iterable)

    def __len__(self) -> int:
        return sum([len(queue) for queue in self.queue_list])

    def __getitem__(self, __index: 'int'):
        i = 0
        while __index >= len(self.queue_list[i]):
            __index -= len(self.queue_list[i])
            i += 1
        return self.queue_list[i][__index]

    def __setitem__(self, __i: 'int', __x):
        i = 0
        while __i >= len(self.queue_list[i]):
            __i -= len(self.queue_list[i])
            i += 1
        self.queue_list[i][__i] = __x


class MyQueue(Deque, PriorityQueue):
    def __init__(self, callback=None):
        super(PriorityQueue, self).__init__()
        self.callback = callback

    def appendleft(self, item):
        if self.callback is not None:
            self.callback(item, 'appendleft')
        self.put(item)

    def extendleft(self, __iterable: Iterable) -> None:
        if self.callback is not None:
            self.callback(__iterable, 'extendleft')
        for item in __iterable:
            self.appendleft(item)

    def append(self, item):
        if self.callback is not None:
            self.callback(item, 'append')
        self.put(item)

    def extend(self, __iterable: Iterable) -> None:
        if self.callback is not None:
            self.callback(__iterable, 'extend')
        for item in __iterable:
            self.append(item)

    def pop(self):
        item = self.get()
        if self.callback is not None:
            self.callback(item, 'pop')
        return item

    def __len__(self) -> int:
        return super(PriorityQueue, self).qsize()

    def __str__(self) -> str:
        return super(PriorityQueue, self).__str__()

    def __getitem__(self, __index):
        raise NotImplementedError("This queue does not support random access")

    def __setitem__(self, __i, __x):
        raise NotImplementedError("This queue does not support random access")

    def __repr__(self) -> str:
        return super(PriorityQueue, self).__repr__()

    def empty(self) -> bool:
        return len(self) == 0


def Print(*args, logLevel: str = "debug") -> None:
    """
    Print files with info

    Args:
        message (str) : string to print
        logLevel (str) :    - debug: prints when debug flag on
                            - always: always prints
                            - error: prints in red
    Returns:
        None
    """
    return
    if (logLevel == "debug" and not const.DEBUG):
        return
    outStr = ""
    for arg in args:
        outStr += str(arg) + " "

    if (logLevel == "debug"):
        if (const.DEBUG):
            print(outStr)
    if (logLevel == "always"):
        print(outStr)
    if (logLevel == "error"):
        RED = '\033[31m'
        ENDC = '\033[0m'
        print(RED, outStr, ENDC)


class Time:
    """
    Wrapper from datetime class cause python datetime can be annoying at times.

    Attributes:
        time (datetime) - All times here are UTC!
    """

    def __init__(self) -> None:
        self.time = datetime(1900, 1, 1, 0, 0, 0)

    def copy(self) -> 'Time':
        """
        Returns another time object with same date
        """
        return Time().from_str(self.to_str())

    def from_str(self, time: str, format: str = "%Y-%m-%d %H:%M:%S") -> 'Time':
        """
        Gets time from specified format

        Arguments:
            time (str) - time in format specified by second input
            format (str) - format string, by default YYYY-MM-DD HH:MM:SS
        """
        self.time = datetime.strptime(time, format)
        self.time = self.time.replace(tzinfo=timezone.utc)
        return self

    def to_str(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Outputs time in format YYYY-MM-DD HH:MM:SS by default

        Arguments:
            format (str) - optional format string to change default
        """
        return self.time.strftime(format)

    def from_datetime(self, time: datetime) -> 'Time':
        self.time = time
        self.time = self.time.replace(tzinfo=timezone.utc)
        return self

    @staticmethod
    def difference_in_seconds(time1: 'Time', time2: 'Time') -> float:
        """
        Finds the difference between two time objects. Finds time1 - time2

        Arguments:
            time1 (Time) - time object
            time2 (Time) - time object
        """
        return (time1.time - time2.time).total_seconds()

    def to_datetime(self) -> datetime:
        self.time = self.time.replace(tzinfo=timezone.utc)
        return self.time

    def add_seconds(self, second: float) -> None:
        """
        Updates self by this number of seconds

        Arguments:
            second (float)
        """
        self.time = self.time + timedelta(seconds=second)

    # Operators:
    def __lt__(self, other):
        return (self.time < other.time)

    def __le__(self, other):
        return(self.time <= other.time)

    def __gt__(self, other):
        return(self.time > other.time)

    def __ge__(self, other):
        return(self.time >= other.time)

    def __eq__(self, other):
        return (self.time == other.time)

    def __ne__(self, other):
        return not(self.__eq__(self, other))

    def __str__(self) -> str:
        return self.to_str()  # + " (" + repr(self) + ")"


class Location:
    """
    Location class in ITRF Frame

    Attributes:
        x (float) - meters
        y (float) - meters
        z (float) - meters
    """

    def __init__(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        self.x = x
        self.y = y
        self.z = z

    def from_lat_long(self, lat: float, lon: float, elev: float = 0) -> 'Location':
        """
        Converts location from WGS84 lat, long, height to x, y, z in ITRF

        Arguments:
            lat (float) - latitude in degrees
            lon (float) - longitude in degrees
            elev (float)- elevation in meters relative to WGS84's ground.
        Returns:
            Location at point (self)
        """
        earthLoc = EarthLocation.from_geodetic(lon=lon, lat=lat,  height=elev, ellipsoid='WGS84').get_itrs(
        )  # Idk why they have this order, but it takes lon, lat. Also elev is distance above WGS reference, so like 0 is sea level

        self.x = float(earthLoc.x.value)
        self.y = float(earthLoc.y.value)
        self.z = float(earthLoc.z.value)
        return self

    def to_lat_long(self) -> 'Tuple[float, float, float]':
        """
        Returns lat, long, and elevation (WGS 84 output)

        Returns:
            Tuple (float, float, float) - lat, long, elevation in (deg, deg, m)

        """
        geoCentric = EarthLocation.from_geocentric(
            x=self.x, y=self.y, z=self.z, unit=astropyUnit.m)

        # round all of these to four decimal places
        lat = round(geoCentric.lat.value, 4)
        lon = round(geoCentric.lon.value, 4)
        elev = round(geoCentric.height.value, 4)
        return (lat, lon, elev)

    def to_alt_az(self, groundPoint: 'Location', time: 'Time') -> 'Tuple[float, float, float]':
        """
        Converts this location (self) to get the alt, az, and elevation relative to this point

        Arguments:
            groundPoint (Location) - location of ground point
            time (Time) - time when calculation needed
        Returns:
            tuple (float, float, float) - (alt, az, distance) in (degrees, degrees, and meters)
        Raise:
            ValueError - if input location and self are the same
        """
        if self == groundPoint:
            raise ValueError("Location of object and ground are the same")

        # based on https://docs.astropy.org/en/stable/coordinates/common_errors.html

        t = time.to_datetime()
        sat = EarthLocation.from_geocentric(
            x=self.x, y=self.y, z=self.z, unit=astropyUnit.m)
        ground = EarthLocation.from_geocentric(
            x=groundPoint.x, y=groundPoint.y, z=groundPoint.z, unit=astropyUnit.m)
        itrs_vec = sat.get_itrs().cartesian - ground.get_itrs().cartesian
        cirs_vec = ITRS(itrs_vec, obstime=t).transform_to(
            CIRS(obstime=t)).cartesian
        cirs_topo = CIRS(cirs_vec, obstime=t, location=ground)
        altAz = cirs_topo.transform_to(AltAz(obstime=t, location=ground))

        return (altAz.alt.value, altAz.az.value, altAz.distance.value)

    def calculate_altitude_angle(self, groundPoint: 'Location') -> float:
        """
        Calculates the altitude angle for self at the groundPoint

        Arguments:
            self (Location) - location of satellite
            groundPoint (Location) - point where you want the altitude at
        Returns:
            float - angle in degrees
        """
        # eqn 1 in https://arxiv.org/pdf/1611.02402.pdf
        rSat = np.array(self.to_tuple())
        rGround = np.array(groundPoint.to_tuple())
        delR = rSat - rGround
        r0Ground = rGround/np.linalg.norm(rGround, ord=2)
        val = np.dot(delR, r0Ground)/np.linalg.norm(delR, ord=2)
        return np.arcsin(val)*180/np.pi

    def get_radius(self) -> float:
        """
        Gets the height above Earth's center of mass in m
        """
        return float(la.norm(self.to_tuple(), ord=2))  # numpy norm

    def to_tuple(self) -> 'Tuple[float, float, float]':
        return (self.x, self.y, self.z)

    def to_str(self) -> str:
        return "(" + str(self.x) + "," + str(self.y) + ", " + str(self.z) + ")"

    def get_distance(self, other: 'Location') -> float:
        """
        Return distance in m from this point to another

        Arguments:
            other (Location) - other object
        Returns:
            float - (distance in m)
        """
        return float(np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2))

    @staticmethod
    def multiple_to_lat_long(locs: 'List[Location]') -> 'Tuple[List[float], List[float], List[float]]':
        """
        Returns lat, long, and elevation (WGS 84 output) of all of the locations. Faster than each one seperately
        Arguments:
            List[Location]
        Returns:
            Tuple (List[float], List[float], List[float]) - lat, long, elevation in (deg, deg, m)

        """
        xLst, yLst, zLst = zip(*[(pos.x, pos.y, pos.z) for pos in locs])
        geoCentric = EarthLocation.from_geocentric(
            x=xLst, y=yLst, z=zLst, unit=astropyUnit.m)

        lat = np.round(geoCentric.lat.value, 4).tolist()
        lon = np.round(geoCentric.lon.value, 4).tolist()
        elev = np.round(geoCentric.height.value, 4).tolist()

        return (lat, lon, elev)

    @staticmethod
    def multiple_from_lat_long(latLst: 'List[float]', lonLst: 'List[float]', elevLst: 'List[float]') -> 'List[Location]':
        """
        Returns a list of locations from lat, long, and elevation (WGS 84 input). Take a look in from_lat_long for more info

        Arguments:
            List[float] - latitudes (deg)
            List[float] - longitudes (deg)
            List[float] - elevations (m)
        Returns:
            List[Location] - locations
        """
        earthLoc = EarthLocation.from_geodetic(lon=lonLst, lat=latLst,  height=elevLst, ellipsoid='WGS84').get_itrs(
        )  # Idk why they have this order, but it takes lon, lat.Also elev is distance above WGS reference, so like 0 is sea level

        xLst = np.round(earthLoc.x.value, 4).tolist()
        yLst = np.round(earthLoc.y.value, 4).tolist()
        zLst = np.round(earthLoc.z.value, 4).tolist()

        return [Location(x, y, z) for x, y, z in zip(xLst, yLst, zLst)]
