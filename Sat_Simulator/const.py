
##Overall settings:
MICRO_TIMESTEP = .001 #seconds

DEBUG = False ##Wether or not to print debug statements
INCLUDE_POWER_CALCULATIONS = True ##wether to include power calculations in the simulation
INCLUDE_UNIVERSAL_DATA_CENTER = True ##wether to use a universal data center or not
##TRANSMISSION DETAILS:
SEND_ACKS = False ##wether to store info until ack or just send and delete the info

ONLY_UPLINK = False ##wether to only uplink or not
ONLY_DOWNLINK = False ##wether to only downlink or not
TUNE_ALPHA = True ##wether to tune alpha or not

##Packet info:
PACKET_SIZE = 2400000000 #bits ##Size of a packet excluding preamble
ACK_SIZE = 0 #bits ##Size of an ACK packet
PREAMBLE_SIZE = 0 #bits ##Size of the preamble
DATA_SIZE = 2400000000 #bits ##Size of each data object
ONLY_CONVERT_ONE_DATA_OBJECT = True ##wether to only convert one data object or not

##Availability map settings:
MINIMUM_VISIBLE_ANGLE = 15 ## minimum angle in degrees above horizon for gs to see sat

##For debugging:
FIXED_SATELLITE_POSITION = False ##wether to fix the satellite position or not

##Routing details:
from enum import Enum
class RoutingMechanism(Enum):
    assign_by_datarate_and_available_memory = 1
    transmit_with_random_delay = 2
    use_all_links = 3
    transmission_probability_function = 4
    multiple_footprints_can_only_see_one = 5
    probability_based_on_number_of_footprints = 6
    probability_with_hyperparameter = 7
    hyperparameter_and_greedy = 8
    fossa_routing = 9
    combined_weighted_and_alpha = 10
    l2d2 = 11
    single_and_l2d2 = 12
    aloha_and_l2d2 = 13
    ours = 14
    single_and_ours = 15
    aloha_and_ours = 16
    ours_and_l2d2 = 17
ROUTING_MECHANISM = RoutingMechanism.l2d2 ##Routing mechanism to use

##Details for link calculations
INCLUDE_WEATHER_CALCULATIONS = False ##wether to include weather in the link quality calculations
SNR_SCALING = 53 #The hardware offset of the ground station's antenna, in dB
FREQUENCY = 8e9 #The frequency of the Sat, in Hz
BANDWIDTH = 76.79e6 #The bandwidth of the Sat, in Hz
ALLOWED_BITS_WRONG = 2 #The number of bits that can be wrong in a packet before it is considered corrupted

class SNRMechanism(Enum):
    lora = 1
    greater_than17 = 2
    bill = 3
    none=4


# Logging details:
# wether to include uplink calculations in the log
INCLUDE_UPLINK_CALCULATIONS = True
# This will be reset at the beginning of the simulation and then continually updated
LOGGING_FILE = "log/om"

# This is the file that contains the mapping of satellite images to satellites
DEFAULT_IMAGE_FILE = "data/sat_mappping_debugging.pkl"
# This is the file that contains the ground station config
DEFAULT_GROUND_STATION_CONFIG_FILE = "data/gs_config/3G.json"
# This is the file that contains the energy config
DEFAULT_ENERGY_CONFIG_FILE = "data/energy_config/default.json"
START_TIME = "2021-07-10T00:00:00"  # This is the start time of the simulation
END_TIME = "2021-07-20T00:00:00"  # This is the end time of the simulation

# Filter configs:
# This is the file that contains the filter config
DEFAULT_FILTER_CONFIG_FILE = "data/filter_config/default_filter_config.json"
SNR_UPLINK_MECHANISM = SNRMechanism.none
SNR_DOWNLINK_MECHANISM = SNRMechanism.bill

p1 = .2
p2 = 0
ALPHA = 1

#If alpha is being tuned in our algorithm, these are the values it will be tuned between:
INITIAL_ALPHA = 1
ALPHA_HIGHER_THRESHOLD = .26
ALPHA_LOWER_THRESHOLD = .3
ALPHA_DOWN_THRESHOLD = .3
ALPHA_INCREASE = .005

#let's do 10 a day - 86400/10 = 8640
#DATA_COLLECTION_FREQUENCY = 8640
DATA_COLLECTION_FREQUENCY = 1
#DATA_COLLECTION_FREQUENCY = 60*60*3 #once every 3 hours
#DATA_COLLECTION_FREQUENCY = 8640 ##in seconds, how often a data object should be created. (This is actually random, so its when random num is less than this)
TIME_SINCE_LAST_CONTACT = 720 #actually determined by the simulation, this is just because we need to initialize it to something - (in seconds)
import math
PROBABILITY_OF_DATA = 1 - math.exp(-1/DATA_COLLECTION_FREQUENCY*TIME_SINCE_LAST_CONTACT) ##probability of data object being created

##For pruning:
MIN_DISTANCE = 3000 #meters
MINIMUM_BER = 1e-4

##Logging details:
INCLUDE_UPLINK_CALCULATIONS = True ##wether to include uplink calculations in the log
MAPS_PATH = ""

# At maximum how much bandwidth can sending priority images take up
MAX_PRIORITY_BANDWIDTH = 1

# Scale down the downlink bandwidth potentially for dgs only
DOWNLINK_BANDWIDTH_SCALING = 1

DEFAULT_CLOUD_THRESHOLD= [0.2, 0.8]

OEC = False # If true, use the OEC scheme, where unimportant data is discarded rather than sent to the cloud