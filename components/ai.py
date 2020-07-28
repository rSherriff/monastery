from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod
from jobs import JobEffort
import random

from actions import Action, MovementAction, WaitAction
from components.base_component import BaseComponent
from rooms import RoomType, Room

if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action, BaseComponent):
    entity: Actor

    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        pathfinder = tcod.path.Pathfinder(self.entity.gamemap.graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


class MoveToPlayer(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()


class MoveAlongRoute(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []
        self.route_index = 0

    @property
    def route(self) -> List[Tuple[int, int]]:
        return self.route

    @route.setter
    def route(self, route: List[Tuple[int, int]]) -> None:
        self._route = route

    def perform(self) -> None:
        if len(self._route) <= 0:
            return

        dx = self._route[self.route_index][0] - self.entity.x
        dy = self._route[self.route_index][1] - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        if distance is 0:
            self.route_index += 1
            if self.route_index is len(self._route):
                self.route_index = 0
            return

        self.path = self.get_path_to(self._route[self.route_index][0], self._route[self.route_index][1])

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()


class Brother(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

        self.passive_job = None
        self.active_job = None
        self.current_job = None

        self.selected_job_location = 0

    def perform(self) -> None:
        """
        Brother AI!
        Pseudo:
        if very important job waiting:
            job = very important job

        if job is not null:
            if desires compel me to stop job:
                job = null
            else:
                if i am not at job:
                    move towards job
                else
                    perform job
        else:
            job = first available job

        if job is still null:
            idle

        """
        if self.passive_job_waiting():
            self.get_next_job()

        # If we have a job then try and go do it
        if self.current_job is not None:

                # print(f"{self.entity.name} has a job at {self.job.location}")

                # if desires tell me to stop the job
                # job = None

            if(self.selected_job_location >= len(self.current_job.locations)):
                print(f"Error: Trying to go to location {self.selected_job_location} for job {self.current_job.name} but it only has {len(current_job.locations)} locations.")
                return

            dx = self.current_job.locations[self.selected_job_location][0] - self.entity.x
            dy = self.current_job.locations[self.selected_job_location][1] - self.entity.y
            distance = max(abs(dx), abs(dy))  # Chebyshev distance.

            if distance is 0:
                # If we are at the job location perform the job
                # print(f"{self.entity.name} is working on a job at {self.job.location}")

                self.current_job.update(self.entity)
                if self.current_job.completed:
                    print(f"Completed job + {self.current_job.name}")
                    if self.is_assigned_passive_job():
                        self.passive_job = None
                    elif self.is_assigned_active_job():
                        self.active_job = None

                    self.current_job = None
                    return
            else:                # else move towards the job location
                self.path = self.get_path_to(self.current_job.locations[self.selected_job_location][0], self.current_job.locations[self.selected_job_location][1])

                if self.path:
                    dest_x, dest_y = self.path.pop(0)
                    return MovementAction(
                        self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
                    ).perform()
                else:
                    # If we can't reach where we need to be to perform this job, pick another of its work locations (not worrying about distance)
                    self.selected_job_location += 1
                    if self.selected_job_location >= len(self.current_job.locations):
                        # print(f"{self.entity.name} cannot find a route to job {self.job.name}")
                        self.selected_job_location = 0
        else:
            # Try to get a new job! (been there fella!!!!!!!)
            self.get_next_job()

        if self.current_job is None:
            if random.random() < 1.2:
                cloister = self.engine.game_map.room_holder.get_room(RoomType.CLOISTER)
                if cloister is not None:
                    position = cloister.get_random_point_in_room()
                    job = JobEffort([position], 1, name="Idle")
                    self.engine.jobs.queue.put(job)
                else:
                    print("No Cloister!")
            else:
                job = JobEffort([[self.entity.x, self.entity.y]], 60, name="Idle")
                self.selected_job_location = 0
                self.job = job

    def is_assigned_passive_job(self):
        return self.current_job is self.passive_job

    def is_assigned_active_job(self):
        return self.current_job is self.active_job

    def get_next_job(self):
        if self.passive_job_waiting():
            self.passive_job = self.entity.schedule.jobs.popleft()

        if not self.engine.jobs.queue.empty() and self.active_job is None:
            self.active_job = self.engine.jobs.queue.get()

        if self.passive_job is not None:
            self.current_job = self.passive_job
        elif self.active_job is not None:
            self.current_job = self.active_job

        if self.current_job is not None:
            # Sort the job locations by distance relative to me
            self.current_job.sort_locations_for_distance([self.entity.x, self.entity.y])
            self.selected_job_location = 0

    def passive_job_waiting(self):
        return len(self.entity.schedule.jobs) > 0 and self.passive_job is None
