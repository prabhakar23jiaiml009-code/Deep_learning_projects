import numpy as np
from pettingzoo import ParallelEnv
from gymnasium.spaces import Box, Discrete
from mision_manager import MissionManager


class DroneSwarmEnv(ParallelEnv):
    metadata = {"render_modes": ["human"], "name": "drone_swarm_v2"}

    def __init__(self, grid_size=10, num_uavs=5, max_steps=200, battery_step_cost=5.0):
        self.num_uavs = num_uavs
        self.possible_agents = [f"uav_{i}" for i in range(1, self.num_uavs + 1)]
        self.agents = self.possible_agents[:]
        self.grid_size = grid_size
        self.max_steps = max_steps
        self.battery_step_cost = battery_step_cost
        self.max_battery = 100.0
        self.initial_battery_total = self.num_uavs * self.max_battery

        self.mission_manager = MissionManager(self.grid_size, self.num_uavs)

        self.observation_spaces = {
            agent: Box(
                low=np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32),
                high=np.array([
                    float(self.grid_size - 1),
                    float(self.grid_size - 1),
                    100.0,
                    float(self.grid_size - 1),
                    float(self.grid_size - 1),
                    float(np.sqrt(2) * self.grid_size),
                    float(self.num_uavs),
                    100.0,
                    float(self.num_uavs),
                    float(self.grid_size * self.grid_size)
                ], dtype=np.float32),
                dtype=np.float32
            )
            for agent in self.possible_agents
        }

        self.action_spaces = {agent: Discrete(5) for agent in self.possible_agents}
        self.grid_matrix = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        self.state = {}
        self.targets = {}
        self.step_count = 0
        self.total_reward = 0.0
        self.collisions = 0

    def reset(self, seed=None, options=None):
        if seed is not None:
            np.random.seed(seed)

        self.agents = self.possible_agents[:]
        self.grid_matrix = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        self.state = {}
        self.targets = {}
        self.step_count = 0
        self.total_reward = 0.0
        self.collisions = 0

        occupied = []
        for agent in self.agents:
            while True:
                gx = np.random.randint(0, self.grid_size)
                gy = np.random.randint(0, self.grid_size)
                if (gx, gy) not in occupied:
                    occupied.append((gx, gy))
                    break
            self.state[agent] = np.array([float(gx), float(gy), self.max_battery], dtype=np.float32)
            self.grid_matrix[gx, gy] = 1

        self.mission_manager.reset(occupied_cells=occupied)

        agent_positions = {agent: (self.state[agent][0], self.state[agent][1]) for agent in self.agents}
        self.mission_manager.update_targets(agent_positions)
        self.targets = self.mission_manager.assigned_targets.copy()

        observations = {agent: self.get_observation(agent) for agent in self.agents}
        infos = {agent: {"episode": {}} for agent in self.agents}
        return observations, infos

    def get_observation(self, agent):
        if agent not in self.state:
            return np.zeros(10, dtype=np.float32)

        x_pos, y_pos, battery = self.state[agent]
        target = self.targets.get(agent, np.array([0.0, 0.0], dtype=np.float32))
        target_x, target_y = float(target[0]), float(target[1])

        dist_to_target = np.sqrt((x_pos - target_x) ** 2 + (y_pos - target_y) ** 2)
        coverage_percentage = self.mission_manager.get_coverage_percent()
        remaining_unvisited = float(len(self.mission_manager.get_unvisited_cells()))

        nearby_uav_count = 0
        nearest_uav_count = 0
        nearest_dist = 999.0

        for other_agent in self.agents:
            if other_agent == agent or other_agent not in self.state:
                continue
            ox, oy, _ = self.state[other_agent]
            d = np.sqrt((x_pos - ox) ** 2 + (y_pos - oy) ** 2)
            if d < nearest_dist:
                nearest_dist = d
            if d <= 2.0:
                nearby_uav_count += 1
            if d <= 1.0:
                nearest_uav_count += 1

        if nearest_dist == 999.0:
            nearest_dist = float(self.grid_size)

        battery_percent = max(0.0, min(100.0, float(battery)))

        return np.array([
            x_pos,
            y_pos,
            battery_percent,
            target_x,
            target_y,
            dist_to_target,
            float(nearest_uav_count),
            coverage_percentage,
            float(nearby_uav_count),
            remaining_unvisited
        ], dtype=np.float32)

    def calculate_reward(self, reached_target, new_cell, collision, battery_exhausted):
        reward = 0.0
        if reached_target:
            reward += 100.0
        if new_cell:
            reward += 10.0
        if collision:
            reward -= 5.0
        if battery_exhausted:
            reward -= 50.0
        return reward

    def step(self, actions):
        self.step_count += 1
        rewards = {}
        terminations = {agent: False for agent in self.agents}
        truncations = {agent: False for agent in self.agents}
        infos = {agent: {} for agent in self.agents}

        new_targets_needed = {}

        for agent in list(self.agents):
            if agent not in self.state:
                continue

            action = actions.get(agent, 0)
            x_pos, y_pos, battery = self.state[agent]

            if action == 1 and y_pos < self.grid_size - 1:
                y_pos += 1.0
            elif action == 2 and y_pos > 0:
                y_pos -= 1.0
            elif action == 3 and x_pos > 0:
                x_pos -= 1.0
            elif action == 4 and x_pos < self.grid_size - 1:
                x_pos += 1.0

            battery = max(0.0, battery - self.battery_step_cost)
            self.state[agent] = np.array([x_pos, y_pos, battery], dtype=np.float32)

            gx, gy = int(x_pos), int(y_pos)

            new_cell = False
            if self.grid_matrix[gx, gy] == 0:
                new_cell = True
                self.grid_matrix[gx, gy] = 1
                self.mission_manager.mark_covered((gx, gy))

            target = self.targets.get(agent, None)
            reached_target = False
            if target is not None:
                reached_target = (gx == int(target[0]) and gy == int(target[1]))
                if reached_target:
                    self.mission_manager.mark_covered((gx, gy))
                    new_targets_needed[agent] = (x_pos, y_pos)

            collision = False
            for other_agent in self.agents:
                if other_agent == agent or other_agent not in self.state:
                    continue
                ox, oy, _ = self.state[other_agent]
                if int(ox) == gx and int(oy) == gy:
                    collision = True
                    self.collisions += 1
                    break

            battery_exhausted = battery <= 0

            rewards[agent] = self.calculate_reward(reached_target, new_cell, collision, battery_exhausted)
            self.total_reward += rewards[agent]

            infos[agent] = {
                "reached_target": reached_target,
                "new_cell_covered": new_cell,
                "collision": collision,
                "battery_exhausted": battery_exhausted,
                "coverage_percent": self.mission_manager.get_coverage_percent(),
                "steps_taken": self.step_count
            }

            if battery_exhausted:
                terminations[agent] = True

        if new_targets_needed:
            self.mission_manager.update_targets({a: self.state[a][:2] for a in self.agents if a in self.state})
            self.targets = self.mission_manager.assigned_targets.copy()

        all_covered = len(self.mission_manager.unvisited) == 0
        all_battery_dead = all((self.state[a][2] <= 0) for a in self.agents if a in self.state)
        time_up = self.step_count >= self.max_steps
        mission_end = all_covered or all_battery_dead or time_up

        if mission_end:
            for agent in self.agents:
                terminations[agent] = all_covered or all_battery_dead
                truncations[agent] = time_up and not (all_covered or all_battery_dead)

        observations = {}
        alive_agents = []
        for agent in self.agents:
            if terminations[agent] or truncations[agent]:
                continue
            if agent in self.state:
                observations[agent] = self.get_observation(agent)
                alive_agents.append(agent)

        self.agents = alive_agents

        battery_left_total = float(sum(max(0.0, self.state[a][2]) for a in self.state))
        battery_used_percent = (
            (self.initial_battery_total - battery_left_total) / self.initial_battery_total * 100.0
            if self.initial_battery_total > 0 else 0.0
        )

        episode_info = {
            "coverage_percent": self.mission_manager.get_coverage_percent(),
            "mission_success": bool(all_covered),
            "total_reward": float(self.total_reward),
            "collisions": int(self.collisions),
            "battery_usage_percent": float(battery_used_percent),
            "battery_left_total": float(battery_left_total),
            "steps_taken": int(self.step_count)
        }

        for agent in infos:
            infos[agent]["episode"] = episode_info

        return observations, rewards, terminations, truncations, infos

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]        
