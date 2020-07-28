from __future__ import annotations

from typing import TYPE_CHECKING
from components.base_component import BaseComponent
from actions import Action

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class PhysicalProperty(Action, BaseComponent):
    entity: Entity  # Owning entity instance.

    def perform(self):
        raise NotImplementedError()

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine
