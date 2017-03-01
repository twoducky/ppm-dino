class EntityManager:
    def __init__(self):
        self.entities = []
        self.componentsByClass = {}
        self.lowestUnassignedEid = 0

    def generate_new_eid(self):
        self.lowestUnassignedEid += 1
        return self.lowestUnassignedEid

    def create_new_entity(self):
        eid = self.generate_new_eid()
        self.entities.append(eid)
        return eid

    # Takes an initialized component and the entity it will be assigned to
    def add_component(self, component_init, eid):
        if not component_init.__class__.__name__ in self.componentsByClass:
            components = {}
            self.componentsByClass[component_init.__class__.__name__] = components
        else:
            components = self.componentsByClass[component_init.__class__.__name__]
        components[eid] = component_init

    # Takes a component class and the entity that owns this type of component
    def remove_component(self, component, eid):
        if not component.__name__ in self.componentsByClass:
            return
        else:
            components = self.componentsByClass[component.__name__]
        if eid in components:
            del components[eid]

    # Returns all entity IDs with a particular component class as a list
    def get_all_entities_possessing_component(self, component):
        retval = []
        if component.__name__ in self.componentsByClass:
            component = self.componentsByClass[component.__name__]
            for key in component:
                retval.append(key)
        return retval

    # Returns the specific component owned by an entity given the component class and the entity ID
    def get_component_of_class(self, component, eid):
        if not component.__name__ in self.componentsByClass:
            return
        elif not eid in self.componentsByClass[component.__name__]:
            return
        else:
            return self.componentsByClass[component.__name__][eid]

    def remove_entity(self, eid):
        v = list(self.componentsByClass.values())
        if v:
            for i in range(len(v)):
                if eid in v[i]:
                    del v[i][eid]
        self.entities.remove(eid)


class World:
    position = [0, 300]
    render = {
        'Path': 'trexrunner.png',
        'States': {'Idle': 1, 'Scroll': 1},
        'Idle': ((0, 104, 2402, 26), 0),
        'Scroll': ((0, 104, 2402, 26), 0)
    }
    states = {'Gravity': 15, 'Ground': 300}
    scroll = -35


class Dino:
    render = {
        'Path': 'trexrunner.png',
        'States': {'Idle': 1, 'Dead': 4, 'Run': 2, 'Jump': 2},
        'Idle': ((76, 2, 88, 96), 0),
        'Dead': ((1338, 0, 88, 96), (1426, 0, 88, 96), (1690, 0, 88, 96), (1778, 0, 88, 96)),
        'Jump': ((1338, 0, 88, 96), (1426, 0, 88, 96)),
        'Run': ((1514, 0, 88, 96), (1602, 0, 88, 96))
    }
    jump = -80
    position = [5, 300]


class Cactus:
    position = (1202, 300)
    render = {
        'Path': 'trexrunner.png',
        'States': {'Small-1.0': 1, 'Small-2.0': 1, 'Small-3.0': 1,
                   'Small-1.1': 1, 'Small-2.1': 1, 'Small-3.1': 1,
                   'Large-1.0': 1, 'Large-2.0': 1,
                   'Large-1.1': 1, 'Large-2.1': 1,
                   'Combo': 1},
        'Small-1.0': ((446, 0, 34, 72), 0),
        'Small-2.0': ((446, 0, 68, 72), 0),
        'Small-3.0': ((446, 0, 102, 72), 0),
        'Small-1.1': ((548, 0, 34, 72), 0),
        'Small-2.1': ((548, 0, 68, 72), 0),
        'Small-3.1': ((548, 0, 102, 72), 0),
        'Large-1.0': ((652, 0, 50, 102), 0),
        'Large-2.0': ((652, 0, 100, 102), 0),
        'Large-1.1': ((752, 0, 50, 102), 0),
        'Large-2.1': ((752, 0, 98, 102), 0),
        'Combo': ((802, 0, 152, 102), 0)
    }
    movement = -35
