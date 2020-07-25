
from __future__ import annotations

import numpy as np  # type: ignore

from typing import Iterable, Iterator, Optional, TYPE_CHECKING
from tcod.console import Console
from render_functions import render_message_box
from actions import Action, CreateJobAction
from rooms import RoomType, Rooms
from datetime import datetime, timedelta

from entity import Actor
import tcod
import queue
import jobs
import random

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Calendar:
    """
    Class for representing the passage of time.

    Time is broken down in month -> day -> time
    """

    def __init__(self, engine: Engine):
        self.engine = engine
        self.date_time = datetime(year=600, month=1, day=1, hour=12)
        self.date_time_tick = timedelta(minutes=1)

    def update(self):
        self.date_time += self.date_time_tick

    def render(self, console: Console):
        console.print(x=3, y=1, string=self.date_time.strftime("%A, %d. %B %Y %I:%M%p"))

    def get_current_date_time(self):
        return self.date_time

        """
        for event in self.events:
            if self.hour is event[2][0] and event[2][1] <= self.minute <= event[2][1] + 20:
                render_message_box(console, event[0])
            if self.hour is event[2][0] and self.minute is event[2][1]:
                for i in range(0, 6):
                    room = self.engine.game_map.room_holder.get_room(event[1])
                    if room is not None:
                        position = room.get_random_point_in_room()
                        job = jobs.Job([position], 30, None, None, None, event[0])
                        self.engine.jobs.queue.put(job)
        """
