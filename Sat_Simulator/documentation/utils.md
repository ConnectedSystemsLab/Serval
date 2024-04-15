Module utils
============

Functions
---------

    
`Print(*args, logLevel: str = 'debug') ‑> None`
:   Print files with info
    
    Args:
        message (str) : string to print
        logLevel (str) :    - debug: prints when debug flag on
                            - always: always prints
                            - error: prints in red
    Returns:
        None

Classes
-------

`Location(x: float = 0, y: float = 0, z: float = 0)`
:   Location class in ITRS Frame
    
    Attributes:
        x (float) - meters
        y (float) - meters
        z (float) - meters

    ### Static methods

    `multiple_to_lat_long(locs: List[Location]) ‑> Tuple[List[float], List[float], List[float]]`
    :   Returns lat, long, and elevation (WGS 84 output) of all of the locations. Faster than each one seperately
        Arguments:
            List[Location]
        Returns:
            Tuple (float, float, float) - lat, long, elevation in (deg, deg, m)

    ### Methods

    `calculate_altitude_angle(self, groundPoint: Location) ‑> float`
    :   Calculates the altitude angle for self at the groundPoint
        
        Arguments:
            self (Location) - location of satellite
            groundPoint (Location) - point where you want the altitude at
        Returns:
            float - angle in degrees

    `from_lat_long(self, lat: float, lon: float, elev: float = 0) ‑> utils.Location`
    :   Converts location from WGS84 lat, long, height to x, y, z in ITRF
        
        Arguments:
            lat (float) - latitude in degrees
            lon (float) - longitude in degrees
            elev (float)- elevation in meters relative to WGS84's ground.
        Returns:
            Location at point (self)

    `get_distance(self, other: Location) ‑> float`
    :   Return distance in m from this point to another
        
        Arguments:
            other (Location) - other object
        Returns:
            float - (distance in m)

    `get_radius(self) ‑> float`
    :   Gets the height above Earth's center of mass in m

    `to_alt_az(self, groundPoint: Location, time: Time) ‑> Tuple[float, float, float]`
    :   Converts this location (self) to get the alt, az, and elevation relative to this point
        
        Arguments:
            groundPoint (Location) - location of ground point
            time (Time) - time when calculation needed
        Returns:
            tuple (float, float, float) - (alt, az, distance) in (degrees, degrees, and meters)
        Raise:
            ValueError - if input location and self are the same

    `to_lat_long(self) ‑> Tuple[float, float, float]`
    :   Returns lat, long, and elevation (WGS 84 output)
        
        Returns:
            Tuple (float, float, float) - lat, long, elevation in (deg, deg, m)

    `to_str(self) ‑> str`
    :

    `to_tuple(self) ‑> Tuple[float, float, float]`
    :

`Time()`
:   Wrapper from datetime class cause python datetime can be annoying at times.
    
    Attributes:
        time (datetime) - All times here are UTC!

    ### Methods

    `add_seconds(self, second: float) ‑> None`
    :   Updates self by this number of seconds
        
        Arguments:
            second (float)

    `copy(self) ‑> utils.Time`
    :   Returns another time object with same date

    `difference_in_seconds(time1: Time, time2: Time) ‑> float`
    :   Finds the difference between two time objects. Finds time1 - time2
        
        Arguments:
            time1 (Time) - time object
            time2 (Time) - time object

    `from_datetime(self, time: datetime.datetime) ‑> utils.Time`
    :

    `from_str(self, time: str, format: str = '%Y-%m-%d %H:%M:%S') ‑> utils.Time`
    :   Gets time from specified format
        
        Arguments:
            time (str) - time in format specified by second input
            format (str) - format string, by default YYYY-MM-DD HH:MM:SS

    `to_datetime(self) ‑> datetime.datetime`
    :

    `to_str(self, format: str = '%Y-%m-%d %H:%M:%S') ‑> str`
    :   Outputs time in format YYYY-MM-DD HH:MM:SS by default
        
        Arguments:
            format (str) - optional format string to change default