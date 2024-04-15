from datetime import datetime
from typing import Dict, List
from src.image import Image
from . import node
from .imageSatellite import ImageSatellite
from .filter_graph import FilterGraph, FilterStatus
from . import log
from .utils import FusedQueue, MyQueue, Time


class PlanetSatellite(ImageSatellite):
    def __init__(
        self,
        node: "node.Node",
        images: "List[Image]" = [],
        energy_config: Dict[str, float] = {
            "compute_energy": 0,
            "transmit_energy": 0,
            "camera_energy": 0,
            "receive_energy": 0,
        },
        computation_schedule: Dict[int, bool] = {},
        priority_bw_allocation: float = 1,
        start_time: datetime = datetime(2021, 7, 1),
        use_oec: bool = False,
    ) -> None:
        """
        Energy config:
        - compute_energy: energy to compute in a time step
        - transmit_energy: energy to transmit in a time step
        - camera_energy: energy to take a picture in a time step
        - receive_energy: energy to receive in a time step
        - TODO add other comsumption
        """
        super(ImageSatellite, self).__init__(node)
        self.images = images
        self.cache_size = 0
        self.energy_config = energy_config
        self.computation_schedule = computation_schedule
        self.computation_time_cache = 0
        (
            self.lo_priority_queue,
            self.primitive_high_priority_queue,
            self.final_high_priority_queue,
        ) = (MyQueue(), MyQueue(), MyQueue())
        self.dataQueue: "FusedQueue" = FusedQueue(
            [
                self.final_high_priority_queue,
                self.primitive_high_priority_queue,
                self.lo_priority_queue,
            ],
            priority_bw_allocation=priority_bw_allocation,
            # callback=lambda data, method: log.Log(f"Data accessed in the data queue", self, data, {"method": method})
        )
        self.priority_bw_allocation = priority_bw_allocation

        self.normalPowerConsumption = energy_config["normal_energy"]
        self.currentMWs = 25000
        self.recievePowerConsumption = 0
        self.transmitPowerConsumption = energy_config["transmit_energy"]
        self.concentrator = 0
        self.powerGeneration = energy_config["receive_energy"]
        self.maxMWs = 25000
        self.beamForming = True
        self.start_time = Time().from_datetime(start_time)
        # Pop out all images prior to start time
        while len(self.images) > 0 and self.images[0].time < self.start_time:
            self.images.pop(0)

        # Whether to use OEC and discard images with low prior
        self.use_oec = use_oec

    def populate_cache(self) -> None:
        """
        Populates the cache with images
        """
        while len(self.images) > 0 and self.images[0].time <= self.time:
            image = self.images.pop(0)
            FilterGraph.init_image(image)
            FilterGraph.compute_prior_on_image(image)
            if not image.score:  # Image has low prior
                image.compute_storage = None  # Low priority images are not computed
                log.Log("Image put in lo priority queue", image, self)
                if self.use_oec:
                    image.name+=" (OEC discarded)" # Under OEC, disturb name to indicate that image is discarded
                self.lo_priority_queue.put(image)
            else:
                # re-init image after computing prior
                FilterGraph.init_image(image)
                self.primitive_high_priority_queue.put(image)
            log.Log("Image captured by sat", image, self)
            self.currentMWs -= self.energy_config["camera_energy"]
            self.cache_size += image.size

    def get_cache_size(self) -> int:
        """
        Returns the size of the cache
        """
        return self.cache_size

    def do_computation(self) -> None:
        """
        Does the computation
        """
        while (
            len(self.primitive_high_priority_queue) > 0
            # and self.computation_time_cache > 0
        ):
            image = self.primitive_high_priority_queue.pop()
            if self.computation_time_cache < image.compute_time:
                self.primitive_high_priority_queue.put(image)
                break
            self.computation_time_cache -= image.compute_time
            log.Log(
                "Doing computation on sat", image, self, {
                    "time": image.compute_time}
            )
            status, side_results = FilterGraph.apply_on_image(image)
            if status == FilterStatus.COMPLETE_HI:
                image.score = 1
                self.final_high_priority_queue.put(image)
                log.Log("Setting image score on sat", image, self)
            elif status == FilterStatus.COMPLETE_LO:
                image.score = 0
                if self.use_oec:
                    image.name+=" (OEC discarded)" # Under OEC, disturb name to indicate that image is discarded
                self.lo_priority_queue.put(image)
                log.Log("Setting image score on sat", image, self)
            else:
                self.primitive_high_priority_queue.put(image)
            for side_result in side_results:
                self.final_high_priority_queue.put(side_result)

    def percent_of_memory_filled(self) -> float:
        return len(self.dataQueue) / 10000000

    def load_data(self, timeStep: float) -> None:
        """
        Loads data from the cache into the node
        """
        self.time = log.loggingCurrentTime
        self.populate_cache()
        # Do computation
        if self.computation_time_cache < timeStep:
            if self.currentMWs > self.energy_config["compute_energy"] * timeStep:
                self.computation_time_cache += timeStep * self.priority_bw_allocation
                self.currentMWs -= self.energy_config["compute_energy"] * timeStep
        log.Log(
            "Computation time cache", self, {
                "time_cache": self.computation_time_cache}
        )
        self.do_computation()
