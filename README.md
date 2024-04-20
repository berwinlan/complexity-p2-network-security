# Complexity Science SP24 Project 2: Malware Spread across Agent-Based Mobile Networks

## Usage
Change the `spread` parameter in `code/params.yaml` to the movement type you want to simulate.

`cd` to the `code` folder, then run `mpirun -n 1 python main.py params.yaml` from the command line.

Output logs are written to the `code/out` directory. `code/animate.ipynb` and `code/plots.py` help
visualize the agents' movement and malware spread.