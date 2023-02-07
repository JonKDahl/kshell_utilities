import os, warnings
from .parameters import GS_FREE_PROTON, GS_FREE_NEUTRON

def _ask_for_time_input(unit: str, lower_lim: int, upper_lim: int) -> int:
    """
    Input prompting generalized for seconds, minutes, hours, and days.

    Parameters
    ----------
    unit : str
        'seconds', 'minutes', 'hours', or 'days'.
    
    lower_lim : int
        Lower allowed limit for the unit input.

    upper_lim : int
        Upper allowed limit for the unit input.

    Returns
    -------
    ans : int
        User input for the unit within the limits.
    """
    while True:
        try:
            ans = int(input(f"Number of {unit}: "))
        except ValueError:
            print("Only integers are allowed!")
            continue
        
        if lower_lim <= ans <= upper_lim:
            return ans
        else:
            print(f"The number of {unit} must be in the interval [{lower_lim}, {upper_lim}]")
            continue

def edit_and_queue_executables():
    """
    Loop over .sh files generated by 'kshell_ui' and adjust queue system
    parameters and if possible, queue the .sh file.

    Currently hard-coded to the slurm system.
    """
    available_parameters = {
        "nodes": False,
        "seconds": False,
        "minutes": False,
        "hours": False,
        "days": False,
        "job_name": False,
        "quench": False,
        "queue": False
    }

    print("Please choose what parameters you want to alter (y/n) (default n):")
    for parameter in available_parameters:
        """
        Decide what to do with all parameters.
        """
        while True:
            ans = input(f"{parameter}: ").lower()
            if ans == "y":
                available_parameters[parameter] = True
                break
            elif ans == "n":
                break
            elif ans == "":
                break
            else:
                continue

    content = [i for i in os.listdir() if i.endswith(".sh")]
    content.sort()

    for elem in content:
        """
        Loop over all .sh files in directory.
        """
        edit_ans = input(f"\nEdit {elem}? (y/n) (default y): ").lower()
        if edit_ans == "n":
            print(f"Skipping {elem}")
            continue

        print(f"Loading {elem}")
        time_parameter = ""
        nodes_parameter = ""
        job_name_parameter = ""
        gs_parameter = ""
        content = ""

        with open(elem, "r") as infile:
            """
            Extract all file content and other specific lines.
            """
            for line in infile:
                content += line
                if "#SBATCH --time=" in line:
                    time_parameter += line
                elif "#SBATCH --nodes=" in line:
                    nodes_parameter += line
                elif "#SBATCH --job-name=" in line:
                    job_name_parameter += line
                elif "gs =" in line:
                    gs_parameter += line

        if (not content) or ((not time_parameter) and (not nodes_parameter) and (not job_name_parameter)):
            print(f"Could not extract info from {elem}. Skipping ...")
            continue

        if available_parameters["job_name"]:
            available_parameters["job_name"] = input("Job name: ")

        if available_parameters["nodes"]:
            while True:
                """
                Ask for new number of nodes.
                """
                try:
                    available_parameters["nodes"] = int(input("Number of nodes: "))
                    break
                except ValueError:
                    print("Only integers are allowed!")
                    continue
        
        time_parameter_new = time_parameter.split("=")[-1].strip()    # '0-00:00:00' d-hh:mm:ss

        if available_parameters["seconds"]:
            available_parameters["seconds"] = _ask_for_time_input(
                unit = "seconds",
                lower_lim = 0,
                upper_lim = 59
            )
            tmp = time_parameter_new.split(":")
            time_parameter_new = f"{tmp[0]}:{tmp[1]}:{available_parameters['seconds']:02d}"

        if available_parameters["minutes"]:
            available_parameters["minutes"] = _ask_for_time_input(
                unit = "minutes",
                lower_lim = 0,
                upper_lim = 59
            )
            tmp = time_parameter_new.split(":")
            time_parameter_new = f"{tmp[0]}:{available_parameters['minutes']:02d}:{tmp[2]}"

        if available_parameters["hours"]:
            available_parameters["hours"] = _ask_for_time_input(
                unit = "hours",
                lower_lim = 0,
                upper_lim = 23
            )
            tmp = time_parameter_new.split(":")
            tmp_days, _ = tmp[0].split("-")
            time_parameter_new = f"{tmp_days}-{available_parameters['hours']:02d}:{tmp[1]}:{tmp[2]}"

        if available_parameters["days"]:
            available_parameters["days"] = _ask_for_time_input(
                unit = "days",
                lower_lim = 0,
                upper_lim = 4
            )
            tmp = time_parameter_new.split(":")
            _, tmp_hours = tmp[0].split("-")
            time_parameter_new = f"{available_parameters['days']}-{tmp_hours}:{tmp[1]}:{tmp[2]}"

        if available_parameters["quench"]:
            while True:
                try:
                    available_parameters["quench"] = float(input("quench: "))
                    break
                except ValueError:
                    print("Only integers and floats are allowed!")
                    continue
  
        if time_parameter:
            """
            Insert new time parameter.
            """
            content_tmp = content.replace(time_parameter, f"#SBATCH --time={time_parameter_new}\n")

            if (content_tmp == content) and (available_parameters['seconds'] or available_parameters['minutes'] or available_parameters['hours'] or available_parameters['days']):
                msg = "Time parameter is unchanged. Either str.replace could"
                msg += " not find a match or new time parameter is identical"
                msg += " to old time parameter."
                warnings.warn(msg, RuntimeWarning)
            else:
                content = content_tmp

        if job_name_parameter and available_parameters['job_name']:
            """
            Insert new job name parameter.
            """
            content_tmp = content.replace(job_name_parameter, f"#SBATCH --job-name={available_parameters['job_name']}\n")

            if content_tmp == content:
                msg = "Job name parameter is unchanged. Either str.replace"
                msg += " could not find a match or new job name parameter is"
                msg += " identical to old job name parameter."
                warnings.warn(msg, RuntimeWarning)
            else:
                content = content_tmp

        if nodes_parameter and available_parameters["nodes"]:
            """
            Insert new nodes parameter.
            """
            nodes_parameter_new = nodes_parameter.split("=")[0]
            nodes_parameter_new += f"={available_parameters['nodes']}\n"
            content_tmp = content.replace(nodes_parameter, nodes_parameter_new)
            
            if content_tmp == content:
                msg = "Nodes parameter is unchanged. Either str.replace could"
                msg += " not find a match or new nodes parameter is identical"
                msg += " to old nodes parameter."
                warnings.warn(msg, RuntimeWarning)
            else:
                content = content_tmp

        if available_parameters["quench"]:
            quenching_factor = available_parameters["quench"]
            gs_parameter_new = gs_parameter.split("=")[0]
            gsp = round(quenching_factor*GS_FREE_PROTON, 2)
            gsn = round(quenching_factor*GS_FREE_NEUTRON, 2)
            gs_parameter_new += f"= {gsp}, {gsn}\n"
            content_tmp = content.replace(gs_parameter, gs_parameter_new)

            if content_tmp == content:
                msg = "gs parameter is unchanged. Either str.replace could"
                msg += " not find a match or new nodes parameter is identical"
                msg += " to old nodes parameter."
                warnings.warn(msg, RuntimeWarning)
            else:
                content = content_tmp

        with open(elem, "w") as outfile:
            outfile.write(content)

        if available_parameters["queue"]:
            os.system(f"sbatch {elem}")