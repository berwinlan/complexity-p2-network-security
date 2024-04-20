"""
Runner for repast4py simulations.
"""

from repast4py import parameters
from mpi4py import MPI

from model import Model


def run(params: dict):
    """
    Starts the model.
    """
    model = Model(MPI.COMM_WORLD, params)
    model.start()


if __name__ == "__main__":
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(args.parameters_file, args.parameters)
    run(params)

# Usage: mpirun -n 1 python main.py params.yaml
