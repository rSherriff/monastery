from __future__ import annotations

import numpy as np  # type: ignore
import tile_types

from typing import Iterable, Iterator, Optional, TYPE_CHECKING, Tuple
from tcod.console import Console
from datetime import datetime

from entity import Actor
import tcod
import queue

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from action import Action


class BaseJob:
    """Class representing a job that some actor is going to go do."""

    def __init__(self, locations, completionAction=None, cancelAction=None, startAction=None, instantAction=None, name: str = "<unnamed>"):

        if isinstance(locations[0], list):
            self.locations = locations
        else:
            self.locations = [locations]

        self.completed = False
        self.name = name
        self.in_progress = False
        self.worker = None

        self.instantAction = instantAction  # Action to be performed when this job is created
        self.completionAction = completionAction  # Actions to be performed when the job is completed
        self.cancelAction = cancelAction  # Action to be performed if the job is cancelled
        self.startAction = startAction  # Action to be performed when the job starts to be worked on

        if self.instantAction is not None:
            self.instantAction.perform()

    def update(self):
        pass

    def complete(self):
        """Mark self as completed and trigger completion event."""
        # self.worker.engine.message_log.add_message(f"Job {self.name} has been completed by {self.worker.entity.name}")
        self.completed = True

        if self.completionAction is not None:
            if isinstance(self.completionAction, list):
                for action in self.completionAction:
                    action.perform()
            else:
                self.completionAction.perform()

    def cancel(self):
        """Trigger cancel action."""
        if self.cancelAction is not None:
            if isinstance(self.cancelAction, list):
                for action in self.cancelAction:
                    action.perform()
            else:
                self.cancelAction.perform()

    def start(self):
        """Mark self as started and trigger start action."""
        if self.startAction is not None:
            if isinstance(self.startAction, list):
                for action in self.startAction:
                    action.perform()
            else:
                self.startAction.perform()

        self.in_progress = True

    def sort_locations_for_distance(self, point: Tuple[int, int]):
        """Sort the locations by distance form some point.
        This is used to get the worked doing this job to the sloest place they can do it."""
        self.locations = sorted(self.locations, key=lambda location: self.chebyshev_distance(location, point))

    def chebyshev_distance(self, pointA: Tuple[int, int], pointB: Tuple[int, int]):
        dx = pointA[0] - pointB[0]
        dy = pointA[1] - pointB[1]
        return max(abs(dx), abs(dy))  # Chebyshev distance.


class JobEffort(BaseJob):

    def __init__(self, locations, work: float, completionAction=None, cancelAction=None, startAction=None, instantAction=None, name: str = "<unnamed>"):
        super().__init__(locations, completionAction, cancelAction, startAction, instantAction, name)
        self.work = work

    def update(self, worker: Actor):
        """Do some amount of work to the job. If the job is down then complete."""
        self.worker = worker

        if not self.in_progress:
            self.start()

        self.work -= worker.get_effort()
        if self.work <= 0:
            self.complete()

class JobUntil(BaseJob):

    def __init__(self, locations, finish_time: datetime, completionAction=None, cancelAction=None, startAction=None, instantAction=None, name: str = "<unnamed>"):
        super().__init__(locations, completionAction, cancelAction, startAction, instantAction, name)
        self.finish_time = finish_time

    def update(self, worker: Actor):
        """Do some amount of work to the job. If the job is down then complete."""
        self.worker = worker

        if not self.in_progress:
            self.start()

        if self.worker.gamemap.engine.calendar.get_current_date_time() > self.finish_time:
            self.complete()


class JobActorCondition(BaseJob):
    def __init__(self, locations, finish_condition, completionAction=None, cancelAction=None, startAction=None, name: str = "<unnamed>"):
        super().__init__(locations, completionAction, cancelAction, startAction, name)
        self.condition = finish_condition

    def update(self, worker: Actor):
        self.worker = worker

        if not self.in_progress:
            self.start()

        if self.condition(self.worker):
            self.complete()


class Jobs:
    """Container of all jobs. Different queues for different types of jobs."""

    def __init__(self, engine: Engine):
        self.engine = engine
        self.queue = queue.Queue()
