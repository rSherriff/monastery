from components.plant import Plant

from enum import Enum, auto


class CropType(Enum):
    NONE = auto()
    WHEAT = auto()

    @classmethod
    def get_crop_name(cls):
        if cls is cls.NONE:
            return ""
        if cls is cls.WHEAT:
            return "Wheat"

    @classmethod
    def get_grow_time(cls):
        if cls is cls.NONE:
            return 0
        if cls is cls.WHEAT:
            return 100


class Crop(Plant):
    def __init__(self, entity):
        super().__init__(entity)
        self.crop_type = CropType.NONE

    def perform(self):
        pass
