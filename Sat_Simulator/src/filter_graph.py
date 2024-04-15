from enum import Enum

from src.image import Image
from .log import Log, loggingCurrentTime
from .data import Data
import networkx as nx


class FilterStatus(Enum):
    RUNNING = 0
    COMPLETE_LO = 1
    COMPLETE_HI = 2


class Filter:
    name_to_filter = {}

    def __init__(
        self,
        name,
        preemptive=False,
        apply_method=lambda image: image,
        runtime=0,
        side_channel_threshold=[
            0.2,
            0.8,
        ],  # side_channel_threshold is a tuple of (min, max) values, where if the side channel value is outside of this range, the filter is bypassed
    ):
        if name in Filter.name_to_filter:
            raise Exception("Filter name already exists")
        self.name = name
        self.preemptive = preemptive
        Filter.name_to_filter[name] = self
        self.apply = apply_method
        self.runtime = runtime
        self.side_channel_threshold = side_channel_threshold
        Log("Created filter", self.__dict__)

    def do_filter(self, image, mode="default"):
        Log(f"Filtering data with filter in mode {mode}", self, image)
        # It is safe to run preemptive filters in non-preemptive mode and have their runtime set to 0
        image_score, side_results = self.apply(image)
        if self.name in image.side_channel_info:
            if self.side_channel_threshold[0] > image.side_channel_info[self.name]:
                Log("Bypassing filter", self, image, {"score": 0})
                return 0, side_results
            if self.side_channel_threshold[1] < image.side_channel_info[self.name]:
                Log("Bypassing filter", self, image, {"score": 1})
                return 1, side_results
            Log(
                "Side channel info not bypassing filter",
                self,
                image,
                {"side_channel": image.side_channel_info[self.name]},
            )
        if mode == "preemptive" and not self.preemptive:
            image_score = 1  # assume all non-preemptive filters pass per our discussion
        return image_score, side_results

    def estimate_time(self, image):
        if self.preemptive:
            return 0
        if self.name in image.completed_filters:
            return 0
        if self.name in image.side_channel_info and (
            self.side_channel_threshold[0] > image.side_channel_info[self.name]
            or self.side_channel_threshold[1] < image.side_channel_info[self.name]
        ):
            return 0
        return self.runtime

    def __str__(self) -> str:
        return "{{filterId: {}}}".format(self.name)


def build_filter(
    name, score_threshold=0.5, output_size=None, preemptive=False, runtime=0, **kwargs
):
    def filter(image):
        image_score = image.filter_result[name][0]
        side_results = []
        Log("Filter result for image", image, {"score": image_score}, {"name": name})
        if output_size is not None:
            data_digest = Image(
                size=output_size,
                region=image.region,
                time=image.time,
                name=f"{image.name}_{name}_digest",
            )  # data digest is e.g. number of ships in image
            data_digest.score = 1  # Digests are always high priority
            side_results.append(data_digest)
            Log("Insight generated for image on filter", image.size, data_digest)
        return image_score >= score_threshold, side_results

    return Filter(name, preemptive=preemptive, apply_method=filter, runtime=runtime, **kwargs)


class FilterGraph:
    global_filter = None

    def __init__(self, application_list=[]):
        """
        arguments:
            application_list: list of lists of filters to be applied in order
        """
        if FilterGraph.global_filter is not None:
            raise Exception("FilterGraph is a singleton")
        FilterGraph.global_filter = self
        self.graph = nx.DiGraph()
        self.application_list = application_list
        Log("Filter graph initialized", self.application_list)

    @staticmethod
    def init_image(image):
        """
        Initiate the compute status of an image. An image will undergo 2 passes of computation: during computing prior and during final computation.
        When an image is under computation, it will have a compute_storage attribute that stores the application index and filter index of the next filter to be applied.
        When an image has never been computed or has completed computation, its compute_storage attribute will be None.
        """
        if FilterGraph.global_filter is None:
            raise Exception("Global filter graph not initialized")
        image.compute_storage = (0, 0)  # (application_index, filter_index)
        image.compute_time = 0  # time to compute next filter
        image.completed_filters = []  # list of filters that have been computed

    @classmethod
    def apply_on_image(cls, image, mode="default"):
        """
        arguments:
            image: Image object
            mode: 'default' for normal computation or 'preemptive' for computing prior
        """
        if cls.global_filter is None:
            raise Exception("Global filter graph not initialized")
        application_index, filter_index = image.compute_storage
        image_score, side_results = Filter.name_to_filter[
            cls.global_filter.application_list[application_index][filter_index]
        ].do_filter(image, mode=mode)
        image.completed_filters.append(
            cls.global_filter.application_list[application_index][filter_index]
        )
        if image_score:  # filter passed
            filter_index += 1
            if filter_index == len(
                cls.global_filter.application_list[application_index]
            ):
                image.compute_storage = None
                return FilterStatus.COMPLETE_HI, side_results
            image.compute_storage = (application_index, filter_index)
        else:  # filter didn't pass
            application_index += (
                1  # move to next application directly since this one didn't pass
            )
            filter_index = 0
            if application_index == len(cls.global_filter.application_list):
                image.compute_storage = None
                return FilterStatus.COMPLETE_LO, side_results
            image.compute_storage = (application_index, filter_index)
        next_filter_name = cls.global_filter.application_list[application_index][
            filter_index
        ]
        next_filter = Filter.name_to_filter[next_filter_name]
        # filter has already been computed or is preemptive
        image.compute_time = next_filter.estimate_time(image)
        return FilterStatus.RUNNING, side_results

    @classmethod
    def compute_prior_on_image(cls, image):
        if cls.global_filter is None:
            raise Exception("Global filter graph not initialized")
        if (
            getattr(image, "score", None) is None
        ):  # Image has not completed computation yet
            status = FilterStatus.RUNNING
            cls.init_image(image)
            while status == FilterStatus.RUNNING:
                status, _ = cls.apply_on_image(image, mode="preemptive")
            if status == FilterStatus.COMPLETE_HI:
                image.score = 1
            else:
                image.score = 0
        Log("Image priority computed", image, {"score": image.score})
        image.compute_storage = None
