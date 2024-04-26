#!/bin/bash


#parameters
ROUNDS=100
PLATOON=20
SQUAD=4
SPREAD="random_waypoint" # "random_walk" | "random_waypoint" | "heirarchical"


#starting index for for loop
for (( round=10 ; round<=$ROUNDS ; round+=10 )); 


# ORDER OF ARGS: PLATOON_NUM SQUAD_NUM SPREAD_TYPE ROUND_NUM
do
 python parameter_sweeps/generate_yml.py $round $SQUAD $SPREAD $round #Parameter sweeping platoons
 #python parameter_sweeps/generate_yml.py $PLATOON $round $SPREAD $round #Parameter sweeping squads
 mpirun -n 1 python main.py parameter_sweeps/params.yaml
 echo "Finished Running: $round"
done

