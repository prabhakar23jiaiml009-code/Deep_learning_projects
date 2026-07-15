"""import numpy as np

class MissionManager:
    def __init__(self, grid_size, num_uavs):
        self.grid_size = grid_size
        self.num_uavs = num_uavs
        self.unvisited = set()
        self.covered = set()
        self.assigned_targets = {}

    def reset(self, occupied_cells=None):
        self.unvisited = {(x, y) for x in range(self.grid_size) for y in range(self.grid_size)}
        self.covered = set()
        self.assigned_targets = {}
        if occupied_cells:
            for cell in occupied_cells:
                self.unvisited.discard(tuple(cell))

    def get_unvisited_cells(self):
        return list(self.unvisited)

    def get_coverage_percent(self):
        total = self.grid_size * self.grid_size
        return (len(self.covered) / total) * 100.0 if total > 0 else 0.0

    def mark_covered(self, cell):
        cell = tuple(cell)
        self.covered.add(cell)
        self.unvisited.discard(cell)
        for agent, target in list(self.assigned_targets.items()):
            if tuple(target.astype(int)) == cell:
                del self.assigned_targets[agent]

    def _nearest_cell(self, pos, exclude=None):
        if not self.unvisited:
            return None
        exclude = set() if exclude is None else set(map(tuple, exclude))
        candidates = [c for c in self.unvisited if c not in exclude]
        if not candidates:
            candidates = list(self.unvisited)
        px, py = int(pos[0]), int(pos[1])
        return min(candidates, key=lambda c: abs(c[0] - px) + abs(c[1] - py))

    def assign_target(self, agent, position, avoid_taken=True):
        taken = set(tuple(v.astype(int)) for v in self.assigned_targets.values()) if avoid_taken else set()
        target = self._nearest_cell(position, exclude=taken)
        if target is None:
            target = self._nearest_cell(position)
        if target is not None:
            self.assigned_targets[agent] = np.array(target, dtype=np.float32)
        return self.assigned_targets.get(agent, None)

    def update_targets(self, agent_positions):
        for agent, pos in agent_positions.items():
            current = self.assigned_targets.get(agent)
            if current is None or tuple(current.astype(int)) not in self.unvisited:
                self.assign_target(agent, pos)
        return self.assigned_targets """


import numpy as np

class MissionManager:
    def __init__(self, grid_size, num_uavs):
        self.grid_size = grid_size
        self.num_uavs = num_uavs
        self.unvisited = set()
        self.covered = set()
        self.assigned_targets = {}

    def reset(self, occupied_cells=None):
        self.unvisited = {(x, y) for x in range(self.grid_size) for y in range(self.grid_size)}
        self.covered = set()
        self.assigned_targets = {}
        if occupied_cells:
            for cell in occupied_cells:
                self.unvisited.discard(tuple(cell))

    def get_unvisited_cells(self):
        return list(self.unvisited)

    def get_coverage_percent(self):
        total = self.grid_size * self.grid_size
        return (len(self.covered) / total) * 100.0 if total > 0 else 0.0

    def mark_covered(self, cell):
        cell = tuple(cell)
        self.covered.add(cell)
        self.unvisited.discard(cell)
        for agent, target in list(self.assigned_targets.items()):
            if tuple(target.astype(int)) == cell:
                del self.assigned_targets[agent]

    def _nearest_cell(self, pos, exclude=None):
        if not self.unvisited:
            return None
        exclude = set() if exclude is None else set(map(tuple, exclude))
        candidates = [c for c in self.unvisited if c not in exclude]
        if not candidates:
            candidates = list(self.unvisited)
        px, py = int(pos[0]), int(pos[1])
        return min(candidates, key=lambda c: abs(c[0] - px) + abs(c[1] - py))

    def assign_target(self, agent, position, avoid_taken=True):
        taken = set(tuple(v.astype(int)) for v in self.assigned_targets.values()) if avoid_taken else set()
        target = self._nearest_cell(position, exclude=taken)
        if target is None:
            target = self._nearest_cell(position)
        if target is not None:
            self.assigned_targets[agent] = np.array(target, dtype=np.float32)
        return self.assigned_targets.get(agent, None)

    def update_targets(self, agent_positions):
        for agent, pos in agent_positions.items():
            current = self.assigned_targets.get(agent)
            if current is None or tuple(current.astype(int)) not in self.unvisited:
                self.assign_target(agent, pos)
        return self.assigned_targets
    
print("hello")

list = [1, 2, 3, 4]
list.append([5, 6, 7, 8])
print(list)

a = [1, 2, 3, 4, 5]
b = a
b[0] = 0
print(a)

a = [1998, 2002]
b = [2014, 2016]
print((a+b)*2)
a = ['Apple', 'Banana', 'Mango', 'Orange']
print(a[2][0])

a = [1, 2, 3, None]
