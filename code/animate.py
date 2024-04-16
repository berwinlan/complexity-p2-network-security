import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import clear_output
import pandas as pd
from repast4py import parameters


class Animator:
    """
    Class for animating the model. Takes a log (.csv) and uses the x,y
    coordinates of agents to chart movement over time.
    """

    def __init__(self, csv="out/agent_log.csv"):
        # Read csv file into a Pandas DataFrame
        self.df = pd.read_csv(csv)

        # Get arguments from params.yaml
        parser = parameters.create_args_parser()
        args = parser.parse_args()
        params = parameters.init_params(args.parameters_file, args.parameters)
        self.rows = params["world.height"]
        self.cols = params["world.width"]
        self.grid = np.zeros((self.rows, self.cols))
        # Set the initial state of the grid
        for _, row in self.df.iterrows():
            if (
                int(row["tick"]) < 0.2
            ):  # check if it's close to 0, but not bigger than 1
                self.grid[int(row["x"])][int(row["y"])] = 1

    def draw(self):
        """
        Draw the grid at one tick
        """
        options = dict(
            # cmap='plasma',
            extent=[0, self.rows, 0, self.cols],
            interpolation="none",
            origin="upper",
            alpha=0.7,
        )
        plt.axis([0, self.rows, 0, self.cols])
        plt.xticks([])
        plt.yticks([])
        plt.imshow(self.grid, **options)

    def animate(self, frames: int):
        """
        Animate the ACO optimization for the given number of frames

        Args:
        frames: an int, the number of frames to animate
        """
        plt.figure()
        try:
            for i in range(frames - 1):
                self.draw()
                plt.show()
                self.step()
                clear_output(wait=True)
            self.draw()
            plt.show()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    a = Animator()
    a.draw()

# Usage: python animate.py params.yaml
