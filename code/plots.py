# Functions to plot the output files created by the models.
import pandas as pd
import matplotlib.pyplot as plt

# Number of infected squads vs. time
def num_infected(agent_log_path: str):
    """
    Args:
        agent_log_path: Path to the file created by the agent_logger.
    """
    df = pd.read_csv(agent_log_path)
        
    # Sum `infected` Trues on each tick
    # TODO: Filter based on type of spread
    grouped = df.groupby('tick').sum().reset_index()
    plt.plot(grouped['tick'], grouped['infected'])
    plt.title("Spread of Malware over Time")
    plt.xlabel("Ticks")
    plt.ylabel("# of infected squads")
    plt.show()
    

if __name__ == '__main__':
    agent_log_path = 'out/agent_log.csv'
    num_infected(agent_log_path)