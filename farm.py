from __future__ import annotations

import numpy as np  # type: ignore

from typing import Iterable, Iterator, Optional, TYPE_CHECKING, Tuple
from entity_holder import EntityHolder
from rooms import Room, RoomType
from actions import CreatePropAction, RemovePendingJobAction
from jobs import JobEffort
from components.crop import Crop, CropType

import tcod
import queue
import random
import entity_factories


class Farm(Room):
    def __init__(self, landscape: GameMap, tiles):
        super().__init__(landscape, RoomType.FARM, tiles)
        self.crop_type = CropType.NONE

        # Create a job to create the farm field that immediately spawns a "pending job entity"
        for tile in tiles:
            instant_action = CreatePropAction(self.landscape.engine.player, entity_factories.pending_job, [tile[0], tile[1]])
            completion_action = [CreatePropAction(self.landscape.engine.player, entity_factories.field, [tile[0], tile[1]]), RemovePendingJobAction(self.landscape.engine.player, [tile[0], tile[1]])]
            job = JobEffort([tile[0], tile[1]], 1, instantAction=instant_action, completionAction=completion_action, name="Create Field")
            self.landscape.engine.jobs.queue.put(job)

    def set_crop(self, crop_type: CropType):
        self.crop_type = crop_type

    def get_room_name(self):
        if self.crop_type is CropType.NONE:
            return "Empty Farm"
        return CropType.get_crop_name(self.crop_type) + " Farm"
