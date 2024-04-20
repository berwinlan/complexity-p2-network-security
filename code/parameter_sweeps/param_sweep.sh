#!/bin/bash


#Read YAML file line by line
ROUNDS=10
PLATOON=10
SQUAD=10
SPREAD="random_walk"


for (( round=1 ; round<=$ROUNDS ; round++ )); 

do
 python parameter_sweeps/generate_yml.py $round $SQUAD $SPREAD $round
 mpirun -n 1 python main.py parameter_sweeps/params.yaml
done

