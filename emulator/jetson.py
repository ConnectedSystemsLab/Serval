from node import Node
import threading
import socket
class Jetson(Node):
    def __init__(self, datarate_trace):
        super().__init__(datarate_trace)
        self.name = "jetson"
        
        #create a socket to connect to the satellite
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #connect to the satellite
        self.s.connect(("","")) #TODO: fill in the ip address and port of the satellite
        #when the satellite sends a string, the jetson will receive it and run the models
        #then the jetson will process the image and send the results back to the satellite
        #if there is no image, the jetson will sleep for 60 seconds and then check again

    def run(self):
        #override the run method
        #first, start the threads.
        #this is a jetson, so we need to:
        #1. receive images from the satellite
        #2. process images if necessary
        #3. send images to the cloud
        
        #start the threads
        self.receiveThread = threading.Thread(target=self.receive_images)
        self.processThread = threading.Thread(target=self.process_images)
        print("starting threads")
        self.receiveThread.start()
        self.processThread.start()