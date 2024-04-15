from node import Node
import threading

##overall idea is this:
##this will represent ALL of the gs
##it will have a connection to the satellite
##it will connect to the satellite on start
##when the satellite sends a string, it will receive it and put it in the queue


class Gs(Node):
    models_to_run = [
        ["california", "forest", "cloud", "fire"],
        ["port", "cloud", "vessel"],
    ]  # GS should always run all images

    def __init__(self, datarate_trace):
        # set up the connection
        super().__init__(datarate_trace)
        self.name = "gs"
    def run(self):
        # override the run method
        # first, start the threads.
        # this is a ground station, so we need to:
        # 1. receive images from the satellite
        # 2. process images if necessary
        # 3. send images to the cloud

        # start the threads
        self.setup_connection()
        self.receiveThread = threading.Thread(target=self.receive_images)
        self.processThread = threading.Thread(target=self.process_images)
        print("starting threads")
        self.receiveThread.start()
        self.processThread.start()
if __name__ == "__main__":
    ratetrace = "fullTrace.pkl"
    gs = Gs(ratetrace)
    gs.run()
    