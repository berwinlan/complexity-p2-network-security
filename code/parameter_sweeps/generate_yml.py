from jinja2 import Environment, FileSystemLoader
import os
import sys
# Generates Yaml file
# running from code directory


# Global Vars
current_dir = "parameter_sweeps" 
ymlfile = "params.j2"


def params_maker(platoon, squad, spread, round):
    """Makes the yml file via a jinja template
    Args:
        name: A string of the ecu
        params: a list of string parameter names
    """
    environment = Environment()
    environment = Environment(loader=FileSystemLoader("parameter_sweeps"))
    template = environment.get_template(ymlfile)
    template.render(name="World")
    content = template.render(
        platoon=platoon, squad=squad, spread=spread, round=round)

    return content


def make_yml(platoon, squad, spread, round):
    """
    Automatically creates a yaml file and writes it to the specified location

    Args:
        platoon: number of platoons
        squad: number of 
    """

    if os.path.isfile(os.path.join(current_dir, ymlfile)):
        yml_content = params_maker(platoon, squad, spread, round)
        yml_out = "parameter_sweeps/params.yaml"
        with open(yml_out, "w+") as file:
            file.write(yml_content)
            file.close()
    else:
        raise Exception(f"{OSError}: \n No file/directory at {ymlfile}")


if __name__ == "__main__":
    ecu_list = sys.argv
    platoon_num = ecu_list[1]
    squad_num = ecu_list[2]
    spread_type = ecu_list[3]
    round_num = ecu_list[4]

    make_yml(platoon_num, squad_num, spread_type, round_num)

# How to run:
# python parameter_sweeps/generate_yml.py platoon_num, squad_num, spread_type, round_num
