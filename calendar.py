
from __future__ import annotations

import numpy as np  # type: ignore

from typing import Iterable, Iterator, Optional, TYPE_CHECKING
from tcod.console import Console
from render_functions import render_message_box
from actions import Action, CreateJobAction

from entity import Actor
import tcod
import queue
import jobs
import random

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

"""
Class for representing the passage of time.
Time is broken down in month -> day -> time
time increases by one minute every tick
"""


class Calendar:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.month = "Tempuary"
        self.day = 1
        self.hour = 1
        self.minute = 0

        self.events = list()

        self.setup_events()

    def update(self):
        self.minute += 1
        if self.minute is 60:
            self.minute = 0
            self.hour += 1
            if self.hour is 24:
                self.hour = 0
                self.day += 1

    def render(self, console: Console):
        date_string = f'{self.month} - {self.day} - {self.hour:02d}:{self.minute:02d}'
        console.print(x=3, y=1, string=date_string)

        for event in self.events:
            if self.hour is event[1][0] and event[1][1] <= self.minute <= event[1][1] + 20:
                render_message_box(console, event[0])
            if self.hour is event[1][0] and self.minute is event[1][1]:
                job = jobs.Job((29, 8), 1)
                self.engine.jobs.queue.put(job)
                job = jobs.Job((29, 9), 1)
                self.engine.jobs.queue.put(job)
                job = jobs.Job((33, 8), 1)
                self.engine.jobs.queue.put(job)
                job = jobs.Job((33, 9), 1)
                self.engine.jobs.queue.put(job)
                job = jobs.Job((33, 9), 1)
                self.engine.jobs.queue.put(job)
                job = jobs.Job((33, 9), 1)
                self.engine.jobs.queue.put(job)
            elif self.hour is event[1][0] and self.minute == event[1][1] + 30:
                for i in range(0, 6):
                    position = (int(random.random() * self.engine.map_width - 1), int(random.random() * self.engine.map_height - 1))
                    job = jobs.Job(position, 1)
                    self.engine.jobs.queue.put(job)
                    pass

    def setup_events(self):
        self.events.append(("Vigil", (2, 0), ()))
        self.events.append(("Matins", (3, 0)))
        self.events.append(("Lauds", (5, 0)))
        self.events.append(("Prime", (6, 0)))
        self.events.append(("Terce", (9, 0)))
        self.events.append(("Sext", (12, 0)))
        self.events.append(("Nones", (15, 0)))
        self.events.append(("Vespers", (18, 0)))
        self.events.append(("Compline", (19, 0)))
