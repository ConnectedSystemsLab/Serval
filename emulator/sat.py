from node import Node, Image
import threading
import os
import queue
import time
import pickle5 as pickle
from argparse import ArgumentParser
from datetime import datetime

from skyfield.api import load


##overall idea is this:
##this is the satellite so just take images and send them
MAX_POWER = 25000
NORMAL_POWER_CONSUMPTION = 2.13
CAMERA_POWER_CONSUMPTION = 6 #Watt
POWER_GENERATION = 14
TRANSMIT_POWER = 10
path_to_data_pickle = './data/1048_whole_day_allimages.pkl'


class Sat(Node):
    models_to_run = None # To be initialized by main function
    def __init__(self, datarate_trace):
        #set up the connection 
        super().__init__(datarate_trace)
        self.currentPower = MAX_POWER
        self.transmitPower = TRANSMIT_POWER
        self.name = "SAT"
        #let's overwrite the transmitQueue to a priority queue
        #it's either going to be high priority or low priority
        self.transmitQueue = queue.PriorityQueue()
        self.earthSat = load.tle("tle")
        self.earthSat = list(self.earthSat.values())[0]
        print(self.earthSat)
        self.ts = load.timescale()

        self.jetsonSocket = None #socket to the jetson to send images for processing
        # load sat images
        
    def run(self):
        #override the run method
        #first, start the threads. 
        #this is a sat, so we need to:
        #1. process images if necessary
        #2. send images to the gs
        
        #start the threads
        
        #no need to receive on sat
        #self.receiveThread = threading.Thread(target=self.receive_images)
        self.processThread = threading.Thread(target=self.process_images)
        self.sendThread = threading.Thread(target=self.send_images)
        self.createThread = threading.Thread(target=self.create_image)
        self.powerHandlerThread = threading.Thread(target=self.power_handler)
        print("starting threads")
        #self.receiveThread.start()
        self.processThread.start()
        self.sendThread.start()
        self.createThread.start()
        self.powerHandlerThread.start()

    def create_image(self):
        #create an image and put it in the queue
        #load the file with path to all images
        idx = 0
        image_dict = pickle.load(open(path_to_data_pickle, 'rb'))
        # sort dict by CaptureTime
        img_file_list = list(image_dict.keys())
        img_data_list = list(image_dict.values())
        img_list = list(zip(img_file_list, img_data_list))
        img_list.sort(key=lambda x: x[1]['captureTime'])
        #print(img_list[0][1]['captureTime'])
        while True:
            # capture image 
            for img in img_list[idx:]:
                image_id = img[0]
                img_cap_time = datetime.strptime(img[1]['captureTime'], '%Y%m%d%H%M%S')#get image time
                if img_cap_time<self.get_time():
                    #print("Image {} created".format(image_id))
                    #load image on the compute queue
                    newImg = Image()
                    newImg.imgPath = img[0]
                    newImg.coordinates = img[1]['coordinates']
                    newImg.captureTime = img[1]['captureTime']
                    newImg.imageId = image_id
                    self.computeQueue.put(newImg)
                    self.logger.info("SAT:Image {} added to compute queue".format(newImg.imgPath))
                    #burn power
                    self.add_power(-CAMERA_POWER_CONSUMPTION)
                    idx+=1
                else:
                    break
    
    def power_handler(self):
        eph = load('/projects/vasishtgroup/omWork/Sat_Simulator/dependencies/de440s.bsp')
        currTime = self.get_time()
        lastTime = currTime
        while True:
            #check if we should add power
            currTime = self.get_time() 
            seconds = (currTime - lastTime).total_seconds()
            tme = self.ts.utc(currTime.year, currTime.month, currTime.day, currTime.hour, currTime.minute, currTime.second)
            in_sunlight = self.earthSat.at(tme).is_sunlit(eph)
            if in_sunlight:
                self.add_power(POWER_GENERATION*seconds)
            self.add_power(-NORMAL_POWER_CONSUMPTION*seconds)
            self.logger.info("SAT: Power: " + str(self.currentPower) + " at " + str(currTime))
            lastTime = currTime
            
    def add_power(self, power):
        self.currentPower += power
        self.currentPower = min(self.currentPower, MAX_POWER)
        self.currentPower = max(self.currentPower, 0)
        if self.currentPower == 0:
            self.logger.info("SAT: Out of power" + str(self.get_time()))
            print("SAT: Out of power")
    
    def send_image_to_jetson(self, image):
        #send the image to the jetson
        self.logger.info("SAT: Jetson processing image" + str(image.imageId) + " at " + str(self.get_time()))
        self.jetsonSocket.send(image.send())
        data = self.jetsonSocket.recv(1024)
        #data should be a pickle of a tuple of (priority, list of images)
        self.logger.info("SAT: Jetson processed image")
        data = pickle.loads(data)
        return data

def main():
    parser=ArgumentParser()
    #parser.add_argument("-i", "--ip", dest="ip", help="IP address of the ground station", default="127.0.0.1")
    #parser.add_argument("-p", "--port", dest="port", help="Port of the ground station", default=5000)
    parser.add_argument("-m","--mode", dest="mode", help="Mode of the experiment", default="in_order_delivery")
    parser.add_argument("-d", "--ratetrace", dest="ratetrace", help="Path to the ratetrace file", default="fullTrace.pkl")
    args = parser.parse_args()
    #ip = args.ip # TODO(@omchabra) use these variables
    #port = args.port
    mode = args.mode
    sat = Sat(args.ratetrace)
    if mode == "in_order_delivery": 
        Sat.models_to_run=[] # regardless of what we run the ground station should always run everything
    elif mode == "prior_only":
        Sat.models_to_run=[["california","forest"],["port"]]
    elif mode == "no_prior":
        Sat.models_to_run=[["california","cloud","fire"],["port","vessel"]]
    
    sat.setup_connection(False)
    sat.run()

if __name__ == "__main__":
    main()