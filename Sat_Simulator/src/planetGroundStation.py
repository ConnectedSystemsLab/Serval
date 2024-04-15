from ctypes import Union
from typing import List
from src.log import Log
from src.node import Node
from .recieveGS import RecieveGS
from src.utils import FusedQueue, MyQueue
from src.filter_graph import FilterGraph, FilterStatus


class PlanetGS(RecieveGS):
    """
    Class that models a planet ground station
    """

    def __init__(self, node: 'Node', uploadBandwidthTrace: 'Union(List[int], int)', num_channels: 'int' = 1, use_oec: 'bool' = False) -> None:
        """
        Decorator object for a node object, normally used on a station object.
        It will make it so that the node object can only recieve, and not transmit.
        """
        super().__init__(node)
        self.uploadBandwithTrace = uploadBandwidthTrace
        self.received_data_queue, self.processed_data_queue = MyQueue(), MyQueue()
        self.dataQueue = FusedQueue([self.received_data_queue, self.processed_data_queue])
        self.use_oec = use_oec

    def get_upload_bandwidth(self) -> int:
        """
        Returns the upload bandwidth
        """
        if isinstance(self.uploadBandwithTrace, int):
            return self.uploadBandwithTrace
        if isinstance(self.uploadBandwithTrace, list):
            return self.uploadBandwithTrace[self.time]
        raise ValueError("Upload bandwidth trace is not provided")

    def load_packet_buffer(self) -> None:
        return

    def has_data_to_transmit(self) -> bool:
        return super().has_data_to_transmit() or not self.dataQueue.empty()

    def load_data(self, timeStep: float) -> None:
        super().load_data(timeStep)
        # Process data objects
        image_computation_queue = []
        while not self.received_data_queue.empty():
            data = self.received_data_queue.pop()
            Log("Processing data object: ", self, data)
            image_computation_queue.append(data)
        for image in image_computation_queue:
            if image.compute_storage is not None:
                Log("Running the rest of the filter graph", self, image)
                status = FilterStatus.RUNNING
                while status == FilterStatus.RUNNING:
                    status, side_results = FilterGraph.apply_on_image(image)
                    for side_result in side_results:
                        if self.use_oec:
                            side_result.score = 0
                            Log("Setting image score to 0 under OEC", self, side_result)
                        self.processed_data_queue.put(side_result)
                if status == FilterStatus.COMPLETE_HI:
                    image.score = 1
                elif status == FilterStatus.COMPLETE_LO:
                    image.score = 0
                Log("Setting image score on ground station", self, image)
                if self.use_oec: # Under OEC, the compute should be done on cloud. We simulate this by doing compute on GS but setting the score to 0
                    image.score = 0
                    Log("Setting image score to 0 under OEC", self, image)
            else:
                Log("Image is already processed", self, image)
            self.processed_data_queue.put(image)