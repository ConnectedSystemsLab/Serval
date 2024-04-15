from datetime import datetime
import json
import pickle
from typing import Any, Dict, List
from src.dataCenter import DataCenter
from src.image import Image
from shapely.geometry import Polygon

import numpy as np
from src.planetGroundStation import PlanetGS
from src.planetSatellite import PlanetSatellite
from src.satellite import Satellite
from src.simulator import Simulator
from src.station import Station
from src.filter_graph import FilterGraph, build_filter

from src.utils import Location, Time


def build_filters(filter_config: "Dict[str, Any]"):
    for filter_name in filter_config:
        _ = build_filter(filter_name, **filter_config[filter_name])


def fractional_day(date: "datetime") -> "float":
    """
    Returns the fractional day of a date
    """
    return (
        date.timetuple().tm_yday
        - 1
        + date.hour / 24.0
        + date.minute / 1440.0
        + date.second / 86400.0
    )


def get_planet_sat_tle(id: "str", current_date: "datetime") -> "str":
    """
    Returns the tle of a planet satellite
    """
    id = id.lower()

    filename = "data/names.txt"
    translations = {}
    with open(filename) as f:
        lines = f.readlines()
    for each in lines:
        line = each.split()
        if line[0] == "0505" or line[0] == "0711":
            translations[line[0]] = line[6]
        elif line[0] != "#" and "SKYSAT" not in line and "OBJECT" not in line:
            translations[line[0]] = line[7]
    norad = translations[id]
    f = open("data/HistoricalTLEs/sat" + norad + ".txt", "r")
    tles = [line for line in f.readlines() if line.strip()]
    days = np.array([np.float_(line[16:32]) for line in tles[0:-1:2]])
    f_date = str(fractional_day(current_date))
    whole = f_date.split(".")[0]
    if len(whole) == 2:
        f_date = "0" + f_date
    elif len(whole) == 1:
        f_date = "00" + f_date
    f_date = str(current_date.year)[-2:] + f_date
    f_date = float(f_date)
    tle_idx = [np.where(days < f_date)[0][-1]]
    v = np.unique(tle_idx)
    tles_ret = []
    for idx in range(len(v)):
        tle1 = tles[v[idx] * 2]
        tle2 = tles[v[idx] * 2 + 1]
        tles_ret.append(tle1)
        tles_ret.append(tle2)
    if len(tles_ret) == 2:
        return tles_ret[0].strip("\n") + "\n" + tles_ret[1].strip("\n")
    raise IndexError(
        "No TLE found for "
        + id
        + " on "
        + str(current_date)
        + ", possibly date out of range"
    )


def generate_satellite_image_mapping_dict(image_info, image_size, datetime_cutoff=None):
    satellite_mapping = {}
    for id in image_info:
        sat_id = image_info[id]["properties"]["satellite_id"]
        image_time = image_info[id]["properties"]["acquired"]
        try:
            image_time = Time().from_str(image_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            image_time = Time().from_str(image_time, "%Y-%m-%dT%H:%M:%SZ")
        if datetime_cutoff is not None and image_time.to_datetime() > datetime_cutoff:
            continue
        coordinates = image_info[id]["geometry"]["coordinates"][0]
        if len(coordinates) == 1:
            coordinates = coordinates[0]
        image_region = Polygon(coordinates)
        if sat_id not in satellite_mapping:
            satellite_mapping[sat_id] = []
        img = Image(
            int(image_size),
            image_region,
            image_time,
            filter_result=image_info[id]["filter_result"],
            name=id,
            side_channel_info=image_info[id]["side_channel"],
        )
        satellite_mapping[sat_id].append(img)
    for sat_id in satellite_mapping:
        satellite_mapping[sat_id].sort(key=lambda x: x.time)
    return satellite_mapping


def create_simulator(args):
    gs_config = json.load(open(args.ground_station_config_file))
    sat_energy_config = json.load(open(args.energy_config_file))
    groundStations: "List[Station]" = []
    gs_id = 0
    for name in gs_config:
        station = Station(
            name,
            gs_id,
            Location().from_lat_long(*gs_config[name]["position"]),
            packetBuffer=9999999999999999999999,
            maxMemory=9999999999999999999999,
        )
        station = PlanetGS(station, int(gs_config[name]["bandwidth"]),use_oec=args.oec)
        groundStations.append(station)  # type: ignore
        gs_id += 1
    print("number of ground stations:", len(groundStations))
    sat_id = 0
    satellites: "List[Satellite]" = []
    satellite_image_mapping, current_image_id = pickle.load(
        open(args.satellite_image_mapping_file, "rb")
    )
    Image.set_id(current_image_id)

    for name in satellite_image_mapping:
        satellite = Satellite(
            name,
            sat_id,
            get_planet_sat_tle(name, args.start_datetime),
            packetBuffer=9999999999999999999999,
            maxMemory=9999999999999999999999,
        )
        satellite = PlanetSatellite(
            satellite,
            satellite_image_mapping[name],
            energy_config=sat_energy_config,
            priority_bw_allocation=args.priority_bw_allocation,
            start_time=args.start_datetime,
            use_oec=args.oec,
        )
        satellites.append(satellite)  # type: ignore
        sat_id += 1

    print("number of satellites:", len(satellites))
    startTime = Time().from_datetime(args.start_datetime)
    endTime = Time().from_datetime(args.end_datetime)

    dataCenter = Station("Data Center", -1, Location().from_lat_long(0, 0))
    dataCenter = DataCenter(dataCenter)

    sim = Simulator(60, startTime, endTime, satellites, groundStations)
    return sim
