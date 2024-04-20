# How to run parameter sweeps


The only file you need to modify is the `param_sweep.sh` bash script. In there, you will find 4 variables you can modify, being:

- SQUAD: Total number of squads
- PLATOON: Total number of platoons
- ROUNDS: Total number of rounds
- SPREAD: Type of spread (random_walk, random_waypoint, etc)

When you run this script, it will generate parameter sweeps where you either increase the number of platoons or the number of squads through a for loop, and you can control what type of spread. It will auto-generate the csv's in a folder called "random_walk" or "random_waypoint" (depending on the type of spread chosen) in the parameter_sweeps folder. 

For example, if you decide to have $ROUNDS=10 and you choose the variable to parameter sweep to be platoons, you will generate 10 csv files, starting with 1 platoon all the way to 10 platoons. 


I use a jinja file to automatically generate the params.yml file (params.j2 is the template and generat_yml.py generates the params.yml given the arguments)

I will add comments to make it easier to read later. 
