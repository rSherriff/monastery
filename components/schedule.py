
from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING
from datetime import datetime, timedelta, time
from components.base_component import BaseComponent
from actions import Action, GoToServiceAction, GoToMealAction, GoToBedAction
from calendar import Calendar
from rooms import RoomType, Room
from room_holder import Rooms


import random
import collections

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from entity import Actor
    from game_map import Gamemap


class ScheduleEvent:
    def __init__(self, name: str, action: Action, time: time):
        self.name = name
        self.action = action
        self.time = time
        self.passed = False


class BaseSchedule(BaseComponent):
    def __init__(self, actor: Actor):
        self.events = []
        self.actor = actor
        self.waiting_event = -1
        self.event_window = timedelta(minutes=5)
        self.jobs = collections.deque()

    def update(self):
        for event in self.events:
            if not event.passed and self.is_time_between((event.time - self.event_window).time(), (event.time + self.event_window).time(), self.actor.gamemap.engine.calendar.date_time.time()):
                event.passed = True
                if event.action is not None:
                    event.action.perform()

    def reset(self):
        for event in self.events:
            event.completed = False

    def setup_schedule(self):
        pass

    def add_event(self, name: str, job: Job, time: time):
        self.events.append(ScheduleEvent(name, job, time))

    def get_waiting_event(self):
        if self.waiting_event is not -1:
            return self.events[self.waiting_event]
            self.waiting_event = -1
        else:
            return None

    def is_time_between(self, begin_time, end_time, check_time):
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else:  # crosses midnight
            return check_time >= begin_time or check_time <= end_time


class BrotherSchedule(BaseSchedule):
    def __init__(self, actor: Actor):
        super().__init__(actor)

        self.add_event("Vigil", GoToServiceAction(actor, timedelta(minutes=30)), datetime(1, 1, 1, hour=2))
        self.add_event("Lauds", GoToServiceAction(actor, timedelta(minutes=30)), datetime(1, 1, 1, hour=3))
        self.add_event("Lauds", GoToServiceAction(actor, timedelta(minutes=30)), datetime(1, 1, 1, hour=5))
        self.add_event("Prime", GoToServiceAction(actor, timedelta(minutes=30)), datetime(1, 1, 1, hour=6))
        self.add_event("Terce", GoToServiceAction(actor, timedelta(minutes=30)), datetime(1, 1, 1, hour=9))
        self.add_event("Sext", GoToServiceAction(actor, timedelta(minutes=30)), datetime(1, 1, 1, hour=12))
        self.add_event("Lunch", GoToMealAction(actor), datetime(1, 1, 1, hour=13))
        self.add_event("Nones", GoToServiceAction(actor, timedelta(minutes=30)), datetime(1, 1, 1, hour=15))
        self.add_event("Vespers", GoToServiceAction(actor, timedelta(minutes=30)), datetime(1, 1, 1, hour=18))
        self.add_event("Compline", GoToServiceAction(actor, timedelta(minutes=30)), datetime(1, 1, 1, hour=19))
        self.add_event("Bedtime", GoToBedAction(actor), datetime(1, 1, 1, hour=20))
