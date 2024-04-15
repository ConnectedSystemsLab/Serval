
##this is the generic class to handle some of the combined stuff:
import socket
import queue
import logging
import time
import threading
import datetime
import pickle 
import os
from model_config import load_models
import tiffile as tiff

class TimeHandler:
    date = datetime.datetime(2021, 7, 15, 0, 6, 30)
    
    def __init__(self):    
        self.baseTime = datetime.datetime.now() #this is 0:00:00 on the first day of the simulation
    
    def update_time(self):
        self.baseTime = datetime.datetime.now()

    def get_time(self):
        #return the current time relative to the base time as a datetime object
        newDate = self.date + (datetime.datetime.now() - self.baseTime)
        return newDate
    
class Image:
    models=load_models()
    # Set this variable in main function for different baselines
    def __init__(self, imgPath):
        if imgPath != "":
           self.name = imgPath.split("/")[-1].replace("3B_AnalyticMS.tif", "")
        else:
            self.name = ""
        self.imgPath = ""
        self.imageId = 0
        self.captureTime = None
        self.modelsToRun = [] #TODO: override all of this to handle when the models should be run
        self.modelResults = {}
        self.shouldRun = True
        self.size=2.4e9
        self.data = None #set this to the data of the image 
        self.coordinates = None #set this to the coordinates of the image

    def run_models(self, models_to_run, device) -> int:
        #return the importance of the image 
        ##run the models
        #check if the models should be run
        
        all_side_results=[]
        high_priority=0
        for application_chain in models_to_run:
            for application in application_chain:
                if not self.shouldRun:
                    return high_priority, all_side_results # TODO should we always return 0 here?

                if device != "sat":
                    result, side_results=self.models[application](self)
                else:
                    if application != "forest" and application != "california" and application != "port":
                        result, side_results = device.send_image_to_jetson(self)
                        
                all_side_results.extend(side_results)
                if not result:
                    break
            else:
                high_priority=1
        return high_priority, all_side_results

    def stop_running_models(self):
        self.shouldRun = False
        #TODO: wait for the current model to finish
        pass
    
    def send(self):
        #send all the metadata but not the data itself. this should return a string
        self.data = None
        return str(self.__dict__)
    
    def receive(string):
        #create an image from the string 
        img = Image("")
        img.data = None 
        img.__dict__ = eval(string)
        return img
    
    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __lt__(self, other):
        return self.captureTime < other.captureTime
    def __gt__(self, other):
        return self.captureTime > other.captureTime
    def __eq__(self, other):
        if other == None:
            return False
        return self.captureTime == other.captureTime
    def __le__(self, other):
        return self.captureTime <= other.captureTime
    def __ge__(self, other):
        return self.captureTime >= other.captureTime
    def __ne__(self, other):
        return self.captureTime != other.captureTime
    
class Node:
    id = 0
    def __init__(self, datarate_trace):
        self.currentPower = 0 
        self.transmitPower = 0
        self.name = ""
        # data_rate_trace should be a pickle file of a list [(datetime,datarate)]

        ##setup 3 threads:
        ##1. to send images
        ##2. to receive images
        ##3, to run the models
        self.s = None
        
        self.computeQueue = queue.Queue()
        self.transmitQueue = queue.PriorityQueue()
        self.datarate_trace = pickle.load(open(datarate_trace, "rb"))
        self.datarate_trace_index = 0
        
        #self.setup_connection()

        self.time = TimeHandler()

        #create a logger for the node - go to its own file. 
        self.logger = logging.getLogger("node"+str(Node.id))
        Node.id+=1
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('node'+str(Node.id)+'.log')
        fh.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)
        self.logger.info("Node created" + str(Node.id))
        
    def get_time(self):
        return self.time.get_time()

    def get_datarate(self):
        current_time=self.get_time()
        
        while self.datarate_trace_index < len(self.datarate_trace) and current_time > self.datarate_trace[self.datarate_trace_index][0]:
            self.datarate_trace_index+=1
        if self.datarate_trace_index == len(self.datarate_trace):
            raise ValueError("Datarate trace is too short")
        return self.datarate_trace[self.datarate_trace_index][1]

    def run(self):
        ##run the simulation
        ##this will be overridden
        pass


    def check_comp(self):
        #check if we should stop the computation and send instead
        pass

    def send_images(self):
        currImage = None
        while True:
            #get the current datarate
            datarate = self.get_datarate()
            #print(datarate, self.get_time())
            if datarate == 0:
                time.sleep(.05)
                continue
            #get the current image
            currImage = self.transmitQueue.get()
            timeToTransmit = currImage.size/datarate
            if self.currentPower - self.transmitPower * timeToTransmit  > 0:
                self.currentPower -= self.transmitPower * timeToTransmit 
            else:
                time.sleep(.05)
                continue
            if currImage == None:
                if self.check_comp():
                    #stop the computation and send instead
                    continue #TODO: handle
                else:
                    time.sleep(1)
            #send the image to the server
            self.send_image(currImage)
            #log the image
            self.logger.info(self.name + ":Image sent:"+ currImage.imgPath + "\tTime" + str(self.get_time()))
            #sleep for the amount of time it takes to send the image
            time.sleep(timeToTransmit)

    def process_images(self):
        currImage = None
        while True:
            #get the current image
            currImage = self.computeQueue.get()
            if currImage == None:
                time.sleep(1)
            #run the models on the image
            importance, side_products = currImage.run_models(self.models_to_run, self) #should internally process and hold/store the results
            #put the image in the queue
            self.transmitQueue.put(currImage, importance)
            for side_product in side_products:
                self.transmitQueue.put(side_product, 1) # Side products are always sent with importance 1
    
    def receive_images(self):
        currImage = None
        while True:
            #get the current datarate
            datarate = self.get_datarate()
            
            #get the current image
            currImage = self.receive_image()
             
            #no need to sleep here since we are receiving the image
            #sleep for the amount of time it takes to receive the image since we aren't actually sending it
            #time.sleep(currImage.size/datarate)

            if currImage == None:
                if self.name == "jetson":
                    os.system("sudo rtcwake -m mem -s 60")
                else:
                    time.sleep(1)
                continue
            #log the image
            self.logger.info(self.name + ":Image received: "+currImage.name + "\ttime:" + str(self.get_time()))
            #put the image in the queue
            if self.name == "jetson":
                currImage.data = tiff.imread(currImage.imgPath)
            self.computeQueue.put(currImage)
    
    def setup_connection(self, out=True):
        ##using the python socket library, set up a connection to the server
        #ipPort = input("Enter the ip address and port of the device u want to connect to: ")
        #ip = ipPort.split(":")[0]
        #port = int(ipPort.split(":")[1])
        
        #setup a tcp connection - prompt for ip address and port
        #create a socket object
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #if it's an outgoing connection, bind to a port
        if out:
            self.s.bind(('', 0))
            #get the ip address and port of the socket
            ip, port = self.s.getsockname()
            #print the ip address and port
            print("ip address: ", ip, " port: ", port)
            #listen for incoming connections
            self.s.listen(5)
            #wait for a connection
            self.s, addr = self.s.accept()
            self.time.update_time()
            logging.info("connected to other device", addr)
        else:
            ip = input("Enter the ip address of the device you want to connect to: ")
            port = int(input("Enter the port of the device you want to connect to: "))

            #connection to hostname on the port
            self.s.connect((ip, port))
            logging.info("connected to other device", ip, port)
            self.time.update_time()
            
    def send_string(self, string):
        logging.info("sending string")
        ##send a string to the server
        self.s.send(string.encode('ascii'))
    
    def receive_string(self):
        ##check for a string from the server
        logging.info("receiving string")
        if self.s.recv(1024) == b'':
            return None
        return self.s.recv(1024).decode('ascii')

    def close_connection(self):
        ##close the connection
        self.s.close()
    
    def send_image(self, image):
        ##send an image to the server
        logging.info(self.name + ":sending image: " + image.name + ":at time:" + str(self.get_time()))
        self.send_string(image.send())
    
    def receive_image(self):
        ##receive an image from the server
        string = self.receive_string()
        if string == None:
            return None
        image = Image.receive(string)
        return image
    