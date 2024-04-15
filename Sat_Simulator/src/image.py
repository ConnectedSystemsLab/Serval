from typing import Dict, List
from shapely.geometry import Polygon

from src.data import Data
from src.utils import Time


class Image(Data):
    id = 0

    def __init__(self, size: int, region: 'Polygon', time: 'Time', 
                 filter_result: Dict[str, List[float]] = {}, 
                 side_channel_info: Dict[str, float] = {},
                 name=""):
        """
        Arguments:
                size (float) - size of image in m
                region (Polygon) - region of image
                time (datetime) - time of image
                mask (np.ndarray) - mask of image
                filter_result  - filter result of image, {name:[score, computation_time]}
                name: name of the image
        """
        super().__init__(size)
        self.time = time
        self.region = region
        self.size = size
        self.filter_result = filter_result
        self.id = Image.id
        self.compute_storage = None
        self.score = None
        Image.id += 1
        self.name = name
        self.side_channel_info = side_channel_info

    def set_score(self, value):
        self.score = value

    @classmethod
    def set_id(cls, value):
        cls.id = value

    @staticmethod
    def from_dict(data):
        min_x, min_y, max_x, max_y = data['region']
        region = Polygon([(min_x, min_y), (max_x, min_y),
                         (max_x, max_y), (min_x, max_y)])
        return Image(
            **data,
            region=region
        )

    # To implement custom comparator (on the score) for the priority queue in the detector
    def __lt__(self, obj):
        """self < obj."""
        # Priority queue is a min heap while we want to put the highest score first
        # So we reverse the comparison
        return self.score > obj.score if not self.score == obj.score else self.time < obj.time

    def __le__(self, obj):
        """self <= obj."""
        return self < obj or self == obj

    def __eq__(self, obj):
        """self == obj."""
        return self.score == obj.score and self.time == obj.time

    def __ne__(self, obj):
        """self != obj."""
        return not self == obj

    def __gt__(self, obj):
        """self > obj."""
        return not self <= obj

    def __ge__(self, obj):
        """self >= obj."""
        return not self < obj

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return "{{imageId: {}, imageSize: {}, imageScore: {}, imageName: {}}}".format(self.id, self.size, self.score, self.name)
