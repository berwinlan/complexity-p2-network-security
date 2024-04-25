"""
Functions to plot the CSV output files created by the models.
"""
import pandas as pd
import matplotlib.pyplot as plt


# Number of infected squads vs. time
def num_infected(
    random_walk_path: str, random_waypoint_path: str, hierarchical_path: str=None
):
    """
    Args:
        agent_log_path: Path to the file created by the agent_logger.
    """
    # Plot random walk
    df = pd.read_csv(random_walk_path)

    # Sum `infected` Trues on each tick
    grouped = df.groupby("tick").sum().reset_index()
    plt.plot(
        grouped["tick"], grouped["infected"], "--", color="orange", linewidth=3
    )

    # Plot random waypoint
    df = pd.read_csv(random_waypoint_path)

    # Sum `infected` Trues on each tick
    grouped = df.groupby("tick").sum().reset_index()
    plt.plot(
        grouped["tick"], grouped["infected"], ":", color="gray", linewidth=3
    )

    if hierarchical_path:
        # Plot hierarchical
        df = pd.read_csv(hierarchical_path)

        # Sum `infected` Trues on each tick
        grouped = df.groupby("tick").sum().reset_index()
        plt.plot(
            grouped["tick"], grouped["infected"], "-", color="tab:blue", linewidth=3
        )

    # Style plots
    plt.title("Spread of Malware over Time")
    plt.xlabel("Ticks")
    plt.ylabel("# of infected squads")
    if hierarchical_path:
        plt.legend(["Random walk", "Random waypoint", "Hierarchical"])
    else:
        plt.legend(["Random walk", "Random waypoint"])
    plt.show()


if __name__ == "__main__":
    random_walk = "out/agent_log_15.csv"
    random_waypoint = "out/agent_log_16.csv"
    hierarchical = "out/agent_log_17.csv"
    num_infected(random_walk, random_waypoint, hierarchical)
