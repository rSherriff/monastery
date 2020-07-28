from components.physical_property import PhysicalProperty


class Plant(PhysicalProperty):
    def __init__(self, entity):
        super().__init__(entity)
        self.grow_time = 0
        self.time_elapsed = 0

    def perform(self):
        pass
