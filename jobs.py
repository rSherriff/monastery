from __future__ import annotations

import numpy as np  # type: ignore
import tile_types

from typing import Iterable, Iterator, Optional, TYPE_CHECKING, Tuple
from tcod.console import Console

from entity import Actor
import tcod
import queue

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from action import Action


class Job:
    """Class representing a job that some actor is going to go do."""

    def __init__(self, locations: list(Tuple[int, int]), work: float, completionAction: Action, cancelAction: Action, startAction: Action, name: str = "<unnamed>"):
        self.locations = locations
        self.work = work
        self.completed = False
        self.name = name
        self.in_progress = False
        self.worker = None

        self.completionAction = completionAction
        self.cancelAction = cancelAction
        self.startAction = startAction

    def work_on(self, worker: Entity, work_amount: float):
        """Do some amount of work to the job. If the job is down then complete."""
        self.worker = worker

        if not self.in_progress:
            self.start()

        self.work -= work_amount
        if self.work <= 0:
            self.complete()

    def complete(self):
        """Mark self as completed and trigger completion event."""
        # self.worker.engine.message_log.add_message(f"Job {self.name} has been completed by {self.worker.entity.name}")
        self.completed = True

        if self.completionAction is not None:
            self.completionAction.perform()

    def cancel(self):
        """Trigger cancel action."""
        if self.cancelAction is not None:
            self.cancelAction.perform()

    def start(self):
        """Mark self as started and trigger start action."""
        if self.startAction is not None:
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


class Jobs:
    """Container of all jobs. Different queues for different types of jobs."""

    def __init__(self, engine: Engine):
        self.engine = engine
        self.queue = queue.Queue()
