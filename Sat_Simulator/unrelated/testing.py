##TESTING
from datetime import datetime, timezone

import pandas as pd
import numpy as np
import random

from src.satellite import Satellite
from src.station import Station

from src.topology import Topology
from src.utils import Time, Location
from src.simulator import Simulator

import const

def test_satellite_tle_and_alt_az_conversion():
    tle = '1 25544U 98067A   14020.93268519  .00009878  00000-0  18200-3 0  5082\n2 25544  51.6498 109.4756 0003572  55.9686 274.8005 15.49815350868473'

    time = Time().from_str("2014-01-23 11:18:07")
    assert time.time == datetime(2014, 1, 23, 11, 18, 7, tzinfo=timezone.utc) ##testing that datetime worked

    sat = Satellite("ISS", 25544, tle, False)
    loc = sat.calculate_orbit(time)
    assert sat.position == loc ##testing that satellite object was updated

    bluffton = Location().from_lat_long(40.8939, -83.8917)
    print(bluffton.to_lat_long())
    alt, az, dist = loc.to_alt_az(bluffton, time)
    assert 16.27572*.99 < alt < 16.27572*1.01
    assert 350.25567*.99 < az < 350.25567*1.01
    assert 1168700*.99 < dist < 1168700*1.01

def test_conversion_from_lat_long():
    desiredX, desiredY = 257360.855, -4078964.716

    loc = Location().from_lat_long(50.24372, -86.38981)

    assert .99 * abs(desiredX) <= abs(loc.x) <= abs(desiredX)*1.01
    assert .99 * abs(desiredY) <= abs(loc.y) <= abs(desiredY)*1.01
    assert .99 * 6378137 <= np.linalg.norm(loc.to_tuple()) <= 1.01 * 6378137 ##Should be close to the radius of Earth
    assert .99 * 6378137 <= loc.get_radius() <= 1.01 * 6378137

    lat, long, elev = loc.to_lat_long()
    assert .99 * 50.24372 <= lat <= 50.24372*1.01
    assert 1.01 * -86.38981 <= long <= .99 * -86.38981


def test_availability_maps():
    ##to ensure that testing works:
    const.MINIMUM_VISIBLE_ANGLE = 10
    ##Confirmed contact on 2022 June 14, 11:22 pm UTC
    sat = Satellite("FossaSat2E1", 50985, "1 50985U 22002B   22164.15385852  .00017786  00000+0  86724-3 0  9993\n2 50985  97.4903 231.9015 0014617  77.7961 282.4909 15.18283897 22806")
    stat1 = Station("VK3FRV", 1, Location().from_lat_long(-37.831, 145.308, 111), True, True)
    stat2 = Station("CBRPAC", 1642725817, Location().from_lat_long(-35.245, 149.149, 576.00), True, False)

    time = Time().from_str("2022-06-14 23:22:00")
    route = Topology(time, [sat], [stat1, stat2])
    assert route.availableMap == {sat: {stat1 : True, stat2: True}}
    ##check altitude angle to tinygs posted, 29.71 and 31.21 respectively
    assert 29.71*.95 < sat.position.calculate_altitude_angle(stat1.position) < 29.71*1.05
    assert 31.21*.95 < sat.position.calculate_altitude_angle(stat2.position) < 31.21*1.05

    time = Time().from_str("2022-06-15 00:56:00")
    route = Topology(time, [sat], [stat1, stat2])
    assert route.availableMap == {sat: {stat1 : True, stat2: False}}

    time = Time().from_str("2022-06-15 00:55:00")
    route = Topology(time, [sat], [stat1, stat2])
    #print(sat.position.to_lat_long())
    assert route.availableMap == {sat: {stat1 : True, stat2: True}}

    norby = Satellite("Norby", 46494, "1 46494U 20068J   22165.62286050  .00002431  00000-0  17558-3 0  9997\n2 46494  97.7304 107.1057 0015838 297.1277  62.8336 15.04956427 93777")
    stat3 = Station("n7vvx_70cm Console", 2, Location().from_lat_long(40.934, -111.875, 1327))
    stat4 = Station("ZS6KNA", 3, Location().from_lat_long(-26.087, 28.035, 1518))

    time = Time().from_str("2022-06-14 21:31:00")
    route = Topology(time, [norby], [stat3, stat4])
    assert route.availableMap == {norby: {stat3: True, stat4: False}}

    time = Time().from_str("2022-06-14 23:48:00")
    route = Topology(time, [norby], [stat3, stat4])
    assert route.availableMap == {norby: {stat3: False, stat4: True}}

    time = Time().from_str("2022-06-14 23:00:00")
    route = Topology(time, [norby], [stat3, stat4])
    assert route.availableMap == {norby: {stat3: False, stat4: False}}

test_satellite_tle_and_alt_az_conversion()