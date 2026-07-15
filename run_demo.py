"""from drons_swarm_env import DroneSwarmEnv
#old file 
if __name__ == "__main__":
    print("5 DRONES ABSOLUTE GRID COVERAGE ENVIRONMENT STARTED")
    env = DroneSwarmEnv(grid_size=10, num_uavs=5, max_steps=50)
    observations, infos = env.reset(seed=42)

    print("Initial agents:", env.agents)
    for agent, obs in observations.items():
        print(f"{agent} initial obs:", obs)

    for step in range(1, env.max_steps + 1):
        if not env.agents:
            print("All agents finished.")
            break

        print(f"\n--- STEP {step} ---")
        actions = {agent: env.action_space(agent).sample() for agent in env.agents}
        observations, rewards, terminations, truncations, infos = env.step(actions)

        print("Alive agents:", list(observations.keys()))
        print("Rewards:", rewards)
        print("Terminations:", terminations)
        print("Truncations:", truncations)

        for agent, obs in observations.items():
            battery_left = float(obs[2])
            battery_used = 100.0 - battery_left

            print(
                f"{agent} obs -> pos=({int(obs[0])},{int(obs[1])}), "
                f"battery_left={battery_left:.1f}%, "
                f"battery_used={battery_used:.1f}%, "
                f"target=({int(obs[3])},{int(obs[4])}), "
                f"dist={obs[5]:.2f}, nearest={obs[6]:.0f}, "
                f"coverage={obs[7]:.1f}%, nearby={obs[8]:.0f}, remaining={obs[9]:.0f}"
            )

    print("\nFinal episode info:")
    if infos:
        first_agent = next(iter(infos))
        print(infos[first_agent].get("episode", {}))"""
# update file      
from drons_swarm_env import DroneSwarmEnv

if __name__ == "__main__":
    print("5 DRONES ABSOLUTE GRID COVERAGE ENVIRONMENT STARTED")
    env = DroneSwarmEnv(grid_size=10, num_uavs=5, max_steps=50)
    observations, infos = env.reset(seed=42)

    print("Initial agents:", env.agents)
    for agent, obs in observations.items():
        print(f"{agent} initial obs:", obs)

    for step in range(1, env.max_steps + 1):
        if not env.agents:
            print("All agents finished.")
            break

        print(f"\n--- STEP {step} ---")
        actions = {agent: env.action_space(agent).sample() for agent in env.agents}
        observations, rewards, terminations, truncations, infos = env.step(actions)

        print("Alive agents:", list(observations.keys()))
        print("Rewards:", rewards)
        print("Terminations:", terminations)
        print("Truncations:", truncations)

        for agent, obs in observations.items():
            battery_left = float(obs[2])
            battery_used = 100.0 - battery_left

            print(
                f"{agent} obs -> pos=({int(obs[0])},{int(obs[1])}), "
                f"battery_left={battery_left:.1f},% "
                f"battery_used={battery_used:.1f}%, "
                f"target=({int(obs[3])},{int(obs[4])}), "
                f"dist={obs[5]:.2f}, nearest={obs[6]:.0f}, "
                f"coverage={obs[7]:.1f}%, nearby={obs[8]:.0f}, remaining={obs[9]:.0f}"
            )
# ab hoga change 
    print("\nFinal episode info:")
    if infos:
        first_agent = next(iter(infos))
        ep = infos[first_agent].get("episode", {})
        print(
            {
                **ep,
                "battery_usage_percent": f"{ep.get('battery_usage_percent', 0.0):.1f}%",
                "coverage_percent": f"{ep.get('coverage_percent', 0.0):.1f}%"
            }
        )