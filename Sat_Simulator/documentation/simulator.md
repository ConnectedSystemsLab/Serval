Module simulator
================

Classes
-------

`Simulator(timeStep: float, startTime: src.utils.Time, endTime: src.utils.Time, satList: List[Satellite], gsList: List[Station], recreated: bool = False)`
:   Main class that runs simulator
    
    Attributes:
        timestep (float/seconds) - timestep in seconds
        startTime (Time) - Time object to when to start
        endTime (Time) - Time object for when to end (simulation will end on this timestep. i.e if end time is 12:00 and timeStep is 10, last run will be 11:50)
        satList (List[Satellite]) - List of Satellite objects
        gsList (List[Station]) - List of Station objects
        topologys (Dict[str, Topology]) - dictionary of time strings to Topology objects
        recreated (bool) - wether or not this simulation was recreated from saved file. If true, then don't compute for t-1 timestep

    ### Static methods

    `open_stored_simulator(fileName: str, timeStepNew: Optional[float] = None, startTimeNew: Optional[Time] = None, endTimeNew: Optional[Time] = None) ‑> Simulator`
    :   Opens stored stimulator in the given file.
        
        Arguments:
            fileName (str) - file to open
            timeStepNew (float) - new time step in seconds, by default None to set to original timestep
            startTimeNew (Time) - new start time as Time object, by default None to set to original startTime
            endTimeNew (Time) - new end time as Time object, by default None to set to original endTime
        Returns:
            Simulator - returns a new simulator object with new routes based on inputed times. Call run on this object to start simulation

    ### Methods

    `run(self) ‑> None`
    :   At inital, load one time step of data into object
        then schedule based off of new data
        send info

    `save_objects(self, fileName: str) ‑> None`
    :   Will save all the variables in this class and logging to the specified file
        
        Arguments:
            fileName (str)