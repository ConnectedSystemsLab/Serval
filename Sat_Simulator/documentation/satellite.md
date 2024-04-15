Module satellite
================

Classes
-------

`Satellite(name: str, id: int, tle: str = '', beamForming: bool = False, packetBuffer: int = 2147483646, maxMemory: int = 2147483646, properties: dict = None)`
:   Satellite object which extends Node class
    
    Attributes:
        properties (dictionary)
        tle (str)
        hasTle (bool)
        position (Location)
        maxMemory (int) - total memory of satellite in bits, default max 32 bit int : 2,147,483,647
        storedPosition (Dict[str, Location])
        hasKepler (bool) - has a kepler object
        kepler (PyAstronomy.pyasl.KeplerEllipse) - kepler ellipse object. Created when create_constellation is run
        keplerReferenceTime - creates a reference time when kepler's equations are calculated with respect to
    Static attributes:
        idToSatellite (Dict[int, Satellite]) - a dictionary that maps each id to a satellite object
        nameToSatellite (Dict[str, Satellite]) - a dictionary that maps each name to a satellite object
    
    Constructor for Satellite object
    
    Arguments:
        name (str) - name of object
        id (int) - id of object, often NORAD
        tle (str) - optional argument, default is "", if tle, insert here
        beamForming (bool) - optional argument, default is False
        properties (dict) - optional argument, default is True, add any user defined properties here

    ### Ancestors (in MRO)

    * src.node.Node

    ### Class variables

    `idToSatellite: Dict[int, satellite.Satellite]`
    :

    `nameToSatellite: Dict[str, satellite.Satellite]`
    :

    ### Static methods

    `create_constellation(listOfSats: List[Satellite], numberOfPlanes: int, numberOfSatellitesPerPlane: int, inclination: float, altitude: float, referenceTime: Time) ‑> List[satellite.Satellite]`
    :   Creates a constellation of objects from a specified shell. This makes a lot of assumptions regarding a circular orbit.
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

    `plot_satellites(satList: List[Satellite]) ‑> None`
    :   Plots all the satellites and their footprints. Needs the position to already be updated
        
        Arguments:
            satList (List[Satellite]) - list of satellites

    ### Methods

    `caculate_orbit(self, time: src.utils.Time) ‑> src.utils.Location`
    :   Public method that calls the other orbit calculation methods. This will update the satellite's position and store it for later use if needed
        
        Arguments:
            time (Time) - when to calculate position at
        Returns:
            Location - the satellite's position as a utils.Location object

    `calculate_footprint(self) ‑> float`
    :   Calculates the footprint of the satellite. Needs the position to already be updated
        
        Returns:
            Footprint #radius of circle on Earth in m

    `calculate_orbit_at_multiple_times(self, startTime: src.utils.Time, endTime: src.utils.Time, timeStep: float) ‑> Dict[datetime.datetime, src.utils.Location]`
    :   Calculates the orbit of this satellite multiple times for faster processing. Be careful as this does not update self.position but updates self.storedPositions
        
        Arguments:
            startTime (Time)
            endTime (Time)
            timeStep (float) - seconds
        
        Returns:
            Dict[datetime] = Location where the key is a datetime object

    `calculate_orbit_with_tle(self, time: src.utils.Time, tle: str) ‑> src.utils.Location`
    :   Calculates the orbit of a satellite:
        
        Arguments:
            time (Time) - time when position wants to be calculated
            tle (str) - tle of satellite
        Returns:
            Location object

    `calculate_orbit_without_tle(self, time: src.utils.Time) ‑> src.utils.Location`
    :   Calculates the orbit of a satellite:
        
        Arguments:
            time (Time) - time when position wants to be calculated
        Returns:
            Location object

    `setup_skyfield(self)`
    :   Method to setup tle information