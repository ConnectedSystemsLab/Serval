from typing import TYPE_CHECKING, Union
from matplotlib import pyplot as plt  # type: ignore
import random

import cartopy  # type: ignore
import cartopy.crs as ccrs  # type: ignore
from cartopy.geodesic import Geodesic  # type: ignore
from matplotlib.patches import Polygon  # type: ignore

from src.utils import Location, Print
from src.node import Node
from src.packet import Packet
import const

if TYPE_CHECKING:
    from typing import List, Dict


class Station (Node):
    """
    Class for Groud stations and IoT devices

    Attributes:
        position (Location)
        groundTransmitAble (bool) - if the station can transmit to another ground station
        groundRecieveAble (bool) - if the station can recieve from another ground station
    Static attributes:
        idToStation (Dict[int, Station]) - a dictionary that maps each id to a station object
        nameToStation (Dict[str, Station]) - a dictionary that maps each name to a station object
    """
    idToStation: 'Dict[int, Station]' = {}
    nameToStation: 'Dict[str, Station]' = {}

    def __init__(self, name: str, id: int, loc: Location, beamForming: bool = False, packetBuffer: int = 2147483646, maxMemory: int = 2147483646, uploadBandwidthTrace:'Union[int,List[int]]'=None) -> None:
        super().__init__(name, id, loc, beamForming, packetBuffer, maxMemory)

        if id in Station.idToStation.keys():
            raise ValueError("All station ids must be unique")

        Station.idToStation[self.id] = self
        Station.nameToStation[self.name] = self

        self.groundTransmitAble = False
        self.groundRecieveAble = False

        # this is for including the percipitation in the simulation. It's only used when const.INCLUDE_WEATHER_CALCULATIONS is True,
        self.percip = random.random()*25
        # look at https://github.com/inigodelportillo/ITU-Rpy/blob/ab8e82dd46b018c7312ae8c5ced682664c9d594d/itur/__init__.py#L109 for more info

        # This is for the upload bandwidth trace, it's either a list of ints (variable bandwidth) or an int (constant bandwidth)
        self.uploadBandwithTrace=uploadBandwidthTrace
        
    @staticmethod
    def plot_stations(gsList: 'List[Station]', threeDimensions: bool = True, outPath="") -> None:
        """
        Plots all the stations. Needs the position to already be updated.

        Arguments:
            gsList (List[Station]) - list of stations
            threeDimensions (bool) - default is true, plot in 3d, if not, plot in 2d. 
            outPath (str) - default is "", if not, you can specify the outfile & path it'll save to
        """
        Print("Plotting stations:", len(gsList))

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

        latList, longList, elevList = Location.multiple_to_lat_long(
            [gs.position for gs in gsList])
        if elevList[0] < -6000000:
            Print("Ensure that your  positions are updated before plotting",
                  logLevel="error")

        # Now we assign each type of satellite to its own color
        label = [type(gs).__name__ for gs in gsList]
        labelDict: 'Dict[str, List[int]]' = {
            lb: [] for lb in label}  # dict of ind to list of indexes
        for i in range(len(gsList)):
            labelDict[label[i]].append(i)

        for lb in labelDict:
            lngList = [longList[i] for i in labelDict[lb]]
            ltList = [latList[i] for i in labelDict[lb]]
            plt.scatter(x=lngList, y=ltList, transform=transform, label=lb)

        plt.legend()
        plt.tight_layout()
        plt.title("Ground Stations Current Position")
        if outPath == "":
            plt.show()
        else:
            plt.savefig(outPath, bbox_inches='tight')

    def get_upload_bandwidth(self) -> int:
        """
        Returns the upload bandwidth of the station (in bps)
        """
        raise NotImplementedError(
            "This method must be implemented by the child class")
