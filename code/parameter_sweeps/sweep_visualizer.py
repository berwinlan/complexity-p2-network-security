import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Parameter Sweeps variables


def ticks(path: str):
    """
    Args:
        agent_log_path: Path to the file created by the agent_logger.
    """
    # Plot random walk
    df = pd.read_csv(path)

    # Sum `infected` Trues on each tick
    grouped = df.groupby("tick").sum().reset_index()
    return grouped


def total_agents(path):
    """
    Calculate total number of agents/squads given a csv log

    path: string of csv file path"""
    df = pd.read_csv(path)
    return len(df.groupby("agent_id").sum().reset_index())


def over_percentage(percentage):
    """
    finds the first time step where the number of infected squads is over the given percentage

    Args:
        percentage: An integer which is the number of infected squads threshold
    """
    for i in range(len(infect_array["infected"])):
        if infect_array["infected"][i] > percentage:
            return i


if __name__ == "__main__":
    graphing_options = ["Individual Graphs",
                        "Random Walk", "Random Waypoint", "Random Walk Defenses"]

    option = graphing_options[3]

    match option:
        case "Individual Graphs":
            for i in [x * 10 for x in range(1, 11)]:
                path_url = f"parameter_sweeps/random_walk/agent_log_random_walk_{i}.csv"
                infect_array = ticks(path_url)
                total_squads = total_agents(path_url)
                plt.plot(infect_array["tick"], infect_array["infected"],
                         "-", linewidth=3, label=f"Random Walk with {i} Platoons")
                plt.title("Spread of Malware over Time")
                plt.xlabel("Ticks")
                plt.ylabel("# of infected squads")
                plt.legend()
                plt.savefig(f"images/random_walk_sweep_{i}.png")
                plt.close()

        case "Random Walk":
            for i in [x * 10 for x in range(1, 11)]:
                path_url = f"parameter_sweeps/random_walk/agent_log_random_walk_{i}.csv"
                infect_array = ticks(path_url)
                total_squads = total_agents(path_url)
                plt.plot(infect_array["tick"], infect_array["infected"]/total_squads,
                         "-", linewidth=3, label=f"Random Walk with {i} Platoons")
                # Plot a dot to show when % of agents cross the threshold (at 50%)
                threshold = over_percentage(total_squads/2)
                plt.plot(infect_array["tick"][threshold],
                         infect_array["infected"][threshold]/total_squads, 'ro')
            plt.title("Spread of Malware over Time")
            plt.xlabel("Ticks")
            plt.ylabel("Percentage of infected squads")
            plt.legend()
            plt.savefig(f"images/random_walk_sweep.png")
            plt.close()
        case "Random Waypoint":
            for i in [x * 10 for x in range(1, 4)]:
                path_url = f"parameter_sweeps/random_waypoint/agent_log_random_waypoint_{i}.csv"
                infect_array = ticks(path_url)
                total_squads = total_agents(path_url)
                plt.plot(infect_array["tick"][0:100], infect_array["infected"][0:100]/total_squads,
                         "-", linewidth=3, label=f"Random Walk with {i} Platoons")
                # Plot a dot to show when % of agents cross the threshold (at 50%)
                threshold = over_percentage(total_squads/2)
                plt.plot(infect_array["tick"][threshold],
                         infect_array["infected"][threshold]/total_squads, 'ro')
            plt.title("Spread of Malware over Time")
            plt.xlabel("Ticks")
            plt.ylabel("Percentage of infected squads")
            plt.legend()
            plt.savefig(f"images/random_waypoint_sweep.png")
            plt.close()
        case "Random Walk Defenses":
            for i in [x for x in range(0, 2)]:
                path_url = f"code/out/agent_log_{i}.csv"
                infect_array = ticks(path_url)
                total_squads = total_agents(path_url)
                plt.plot(infect_array["tick"], infect_array["infected"]/total_squads,
                         "-", linewidth=3, label=f"Random Walk with defenses at {100 - i *10 - 10}%")
                # Plot a dot to show when % of agents cross the threshold (at 50%)
                threshold = over_percentage(total_squads/2)
                

            plt.title("Spread of Malware over Time")
            plt.xlabel("Ticks")
            plt.ylabel("Percentage of infected squads")
            plt.legend()
            plt.savefig(f"code/images/random_walk_defenses_sweep.png")
            plt.close()
        case "Random Waypoint Defenses":
            for i in [x for x in range(0, 9)]:
                path_url = f"code/out/agent_log_{i}.csv"
                infect_array = ticks(path_url)
                total_squads = total_agents(path_url)
                plt.plot(infect_array["tick"].iloc[:90], infect_array["infected"].iloc[:90]/total_squads,
                         "-", linewidth=3, label=f"Random Waypoint with defenses at {100 - i *10 - 10}%")
                # Plot a dot to show when % of agents cross the threshold (at 50%)
                threshold = over_percentage(total_squads/2)
                plt.plot(infect_array["tick"][threshold],
                         infect_array["infected"][threshold]/total_squads, 'ro')
            plt.title("Spread of Malware over Time")
            plt.xlabel("Ticks")
            plt.ylabel("Percentage of infected squads")
            plt.legend()
            plt.savefig(f"code/images/random_waypoint_defenses_sweep.png")
            plt.close()
