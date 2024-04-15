from .node import Node
import threading
##overall idea is this:
##this is cloud so just receive images and process them

class Cloud(Node):
    def __init__():
        #set up the connection 
        super().__init__()
            
    def run(self):
        #override the run method
        #first, start the threads. 
        #this is a ground station, so we need to:
        #1. receive images from the satellite
        #2. process images if necessary
        #3. send images to the cloud
        
        #start the threads
        self.receiveThread = threading.Thread(target=self.receive_images)
        self.processThread = threading.Thread(target=self.process_images)
        
        #no need to send images in the cloud
        #self.sendThread = threading.Thread(target=self.send_images)
        
            