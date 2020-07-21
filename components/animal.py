from components.base_component import BaseComponent


class Animal (BaseComponent):
    def __init__(self, hp: int):
        self.max_hp = hp
        self._hp = hp

        self.max_want_level = 100
        self._hunger = self.max_want_level
        self._thirst = self.max_want_level
        self._energy = self.max_want_level

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))

    @property
    def hunger(self):
        return self._hunger

    @hunger.setter
    def hunger(self, value: int) -> None:
        self._hunger = max(0, min(value, self.max_want_level))

    @property
    def thirst(self):
        return self._thirst

    @thirst.setter
    def thirst(self, value: int) -> None:
        self._hunger = max(0, min(value, self.max_want_level))

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value: int) -> None:
        self._energy = max(0, min(value, self.max_want_level))
