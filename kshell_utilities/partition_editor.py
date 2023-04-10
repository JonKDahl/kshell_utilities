import time, os, curses
from typing import Callable
from .data_structures import OrbitalParameters, ConfigurationParameters
from .parameters import spectroscopic_conversion, shell_model_order
from .vum import Vum
from .count_dim import count_dim
from .kshell_exceptions import KshellDataStructureError

def calculate_configuration_parity(
    configuration: list[int],
    model_space: list[OrbitalParameters]
) -> int:
    parity = 1
    for i in range(len(configuration)):
        if not configuration[i]: continue   # Empty orbitals do not count towards the total parity.
        parity *= model_space[i].parity**configuration[i]

    return parity

def analyse_existing_configuration(
    vum: Vum,
    proton_configurations_formatted: list[ConfigurationParameters],
    neutron_configurations_formatted: list[ConfigurationParameters],
    input_wrapper: Callable,
    model_space: list[OrbitalParameters],
    y_offset: int,
) -> None:
    """
    Prompt the user for an index of an existing configuration and show
    an analysis of the configuration in question. This function is only
    used once and exists simply to make the amount of code lines in
    `_partition_editor` smaller.
    """
    pn_configuration_dict: dict[str, list[ConfigurationParameters]] = {
        "p": proton_configurations_formatted,
        "n": neutron_configurations_formatted,
    }
    while True:
        if input_wrapper("Analyse existing configuration? (y/n)") == "y":
            while True:
                p_or_n = input_wrapper("Proton or neutron configuration? (p/n)")
                if (p_or_n == "p"):
                    is_proton = True
                    is_neutron = False
                    break
                if (p_or_n == "n"):
                    is_proton = False
                    is_neutron = True
                    break
            
            draw_shell_map(vum=vum, model_space=model_space, is_proton=is_proton, is_neutron=is_neutron)
            
            while True:
                configuration_idx = input_wrapper(f"Choose a {p_or_n} orbital index in 1, 2, ..., {len(pn_configuration_dict[p_or_n])} (q to quit)")
                if configuration_idx == "q": break
                
                try:
                    configuration_idx = int(configuration_idx)
                except ValueError:
                    continue
                
                configuration_idx -= 1    # List indices are from 0 while indices in .ptn are from 1.
                if configuration_idx in range(len(pn_configuration_dict[p_or_n])):

                    current_configuration = pn_configuration_dict[p_or_n][configuration_idx].configuration
                    configuration_parity = 1
                    for i in range(len(current_configuration)):
                        orbital_parity = (-1)**model_space[i].l
                        configuration_parity *= orbital_parity**current_configuration[i] if current_configuration[i] else 1  # Avoid multiplication by 0.
                        draw_shell_map(
                            vum = vum,
                            model_space = model_space,
                            is_proton = is_proton,
                            is_neutron = is_neutron,
                            occupation = (i, current_configuration[i]),
                        )

                    vum.addstr(y_offset + 6, 0, f"parity current configuration = {configuration_parity}")

        else: break # If answer from user is not 'y'.

    vum.addstr(y_offset + 6, 0, "parity current configuration = None")

def draw_shell_map(
    vum: Vum,
    model_space: list[OrbitalParameters],
    is_proton: bool,
    is_neutron: bool,
    occupation: tuple[int, int] | None = None,
) -> None:
    """
    Draw a simple map of the model space orbitals of the current
    interaction file. Sort the orbitals based on the shell_model_order
    dict.

    Parameters
    ----------
    vum : Vum
        The Vum object to draw the map with.

    model_space : list[OrbitalParameters]
        The model space orbitals to draw.

    is_proton : bool
        Whether to draw the proton map.

    is_neutron : bool
        Whether to draw the neutron map.

    occupation : tuple[int, int] | None, optional
        The occupation of the model space orbitals. The tuple contains
        (orbital index, occupation). If None, draw the entire map with
        no occupation, by default None.

    Returns
    -------
    None
    """
    y_offset: int = 9
    model_space_copy = sorted(  # Sort the orbitals based on the shell_model_order dict.
        model_space,
        key = lambda orbital: shell_model_order[f"{orbital.n}{spectroscopic_conversion[orbital.l]}{orbital.j}"],
        reverse = True
    )
    model_space_proton = [orbital for orbital in model_space_copy if orbital.tz == -1]
    model_space_neutron = [orbital for orbital in model_space_copy if orbital.tz == 1]

    max_neutron_j: int = max([orbital.j for orbital in model_space_neutron], default=0)
    max_proton_j: int = max([orbital.j for orbital in model_space_proton], default=0)  # Use the max j value to center the drawn orbitals.

    if is_proton:
        proton_offset: int = 17 + (max_proton_j + 1)*2  # The offset for the neutron map.
        is_blank_line: bool = False
        if occupation is None:
            """
            Draw the entire map with no occupation.
            """
            for i in range(len(model_space_proton)):
                string = (
                    f"{model_space_proton[i].idx + 1:2d}"
                    f" {model_space_proton[i].name}"
                    f" {(-1)**model_space_proton[i].l:2d} " +
                    " "*(max_proton_j - model_space_proton[i].j) + "-" + " -"*(model_space_proton[i].j + 1)
                )
                vum.addstr(i + y_offset, 0, string)
        else:
            """
            Re-draw a single orbital with the user inputted occupation.
            """
            location: int = 0
            for orbital in model_space_proton:
                if orbital.idx == occupation[0]: break
                location += 1
            else:
                msg = (
                    f"Orbital index {occupation[0]} not found in the"
                    " current model space!"
                )
                raise RuntimeError(msg)
            
            string = (
                f"{orbital.idx + 1:2d}"
                f" {orbital.name}"
                f" {(-1)**orbital.l:2d} " +
                " "*(max_proton_j - orbital.j) + "-"
            )
            string += "o-"*occupation[1] + " -"*(orbital.j + 1 - occupation[1])
            vum.addstr(location + y_offset, 0, string)

    else:
        proton_offset: int = 0
        is_blank_line: bool = True

    if is_neutron:
        if occupation is None:
            for i in range(len(model_space_neutron)):        
                string = (
                    f"{model_space_neutron[i].idx + 1:2d}"
                    f" {model_space_neutron[i].name}"
                    f" {(-1)**model_space_proton[i].l:2d} " +
                    " "*(max_neutron_j - model_space_neutron[i].j) + "-" + " -"*(model_space_neutron[i].j + 1)
                )
                vum.addstr(i + y_offset, proton_offset, string, is_blank_line=is_blank_line)
        
        else:
            """
            Re-draw a single orbital with the user inputted occupation.
            """
            location: int = 0
            for orbital in model_space_neutron:
                if orbital.idx == occupation[0]: break
                location += 1
            else:
                msg = (
                    f"Orbital index {occupation[0]} not found in the"
                    " current model space!"
                )
                raise RuntimeError(msg)
            
            string = (
                f"{orbital.idx + 1:2d}"
                f" {orbital.name}"
                f" {(-1)**orbital.l:2d} " +
                " "*(max_neutron_j - orbital.j) + "-"
            )
            string += "o-"*occupation[1] + " -"*(orbital.j + 1 - occupation[1])
            vum.addstr(location + y_offset, proton_offset, string)

def _generate_total_configurations(
    proton_configurations: list[ConfigurationParameters],
    neutron_configurations: list[ConfigurationParameters],
    total_configurations: list[list[int]],
    partition_file_parity: int,
) -> None:
    """
    Generate all the possible combinations of proton and neutron
    configurations. The parities of the proton and neutron
    configurations must combine multiplicatively to the parity of
    the partition file. The `total_configurations` list will be
    cleared before the new configurations are added.

    Parameters
    ----------
    proton_configurations : list[ConfigurationParameters]
        The list of proton configurations.
    
    neutron_configurations : list[ConfigurationParameters]
        The list of neutron configurations.

    total_configurations : list[list[int]]
        The list to store all possible combinations of proton and
        neutron configurations.

    partition_file_parity : int
        The parity of the partition file.

    Returns
    -------
    None

    Raises
    ------
    KshellDataStructureError
        If any proton or neutron configuration is unused. This happens
        if the parity of the configuration does not multiplicatively
        combine with any of the configurations of the opposite nucleon
        to the parity of the partition file.
    """
    total_configurations.clear()
    n_proton_configurations = len(proton_configurations)
    n_neutron_configurations = len(neutron_configurations)
    neutron_configurations_count: list[int] = [0]*n_neutron_configurations
    proton_configurations_count: list[int] = [0]*n_proton_configurations
    
    for p_idx in range(n_proton_configurations):
        for n_idx in range(n_neutron_configurations):
            if proton_configurations[p_idx].parity*neutron_configurations[n_idx].parity == partition_file_parity:
                """
                Only combinations of proton and neutron orbitals with
                the same parity as the parity of the partition file are
                accepted.
                """
                total_configurations.append([p_idx, n_idx])
                neutron_configurations_count[n_idx] += 1
                proton_configurations_count[p_idx] += 1

    for p_idx in range(n_proton_configurations):
        if proton_configurations_count[p_idx] == 0:
            msg = (
                f"Proton configuration {p_idx + 1} ({proton_configurations[p_idx].configuration}) has not been paired with"
                " any neutron configuration due to parity mismatch."
                f" Unable to produce partition file parity ({partition_file_parity})"
                f" with the parity of this configuration ({proton_configurations[p_idx].parity})."
            )
            raise KshellDataStructureError(msg)

    for n_idx in range(n_neutron_configurations):
        if neutron_configurations_count[n_idx] == 0:
            msg = (
                f"Neutron configuration {n_idx + 1} ({neutron_configurations[n_idx].configuration}) has not been paired with"
                " any proton configuration due to parity mismatch."
                f" Unable to produce partition file parity ({partition_file_parity})"
                f" with the parity of this configuration ({neutron_configurations[n_idx].parity})."
            )
            raise KshellDataStructureError(msg)

def partition_editor(
    filename_interaction: str | None = None,
    filename_partition: str | None = None,
    filename_partition_edited: str | None = None,
    input_wrapper: Callable | None = None,
    is_interactive: bool = True,
):  
    """
    Wrapper for error handling.
    """
    try:
        msg = _partition_editor(
            filename_interaction = filename_interaction,
            filename_partition = filename_partition,
            filename_partition_edited = filename_partition_edited,
            input_wrapper = input_wrapper,
            is_interactive = is_interactive
        )
    except KeyboardInterrupt:
        curses.endwin()

    except curses.error as e:
        curses.endwin()
        raise(e)
    
    except Exception as e:
        curses.endwin()
        raise(e)

    else:
        curses.endwin()
        print(msg)

def _partition_editor(
    filename_interaction: str | None = None,
    filename_partition: str | None = None,
    filename_partition_edited: str | None = None,
    input_wrapper: Callable | None = None,
    is_interactive: bool = True,
):
    """
    Extract the model space orbitals from an interaction file. Extract
    proton and neutron partitions from an accompanying partition file.
    Prompt the user for new proton and neutron configurations and 
    regenerate the proton-neutron partition based on the existing and
    new proton and neutron configurations.

    Here, 'configuration' refers to a specific occupation of protons or
    neutrons in the model space orbitals while 'partition' refers to the
    set of all the configurations. Hence, a 'proton configuration' is
    one specific configuration, like
    ```
    1     6  4  2  0  2  4  2  0  0  0  0  0
    ```
    while the 'proton partition' is the set of all the proton
    configurations, like
    ```
    1     6  4  2  0  2  4  2  0  0  0  0  0
    2     6  4  2  0  3  3  2  0  0  0  0  0
    3     6  4  2  0  3  4  1  0  0  0  0  0
    ...
    ```

    Parameters
    ----------
    filename_interaction : str | None
        The name of the interaction file. If None, the user will be
        prompted to select a file from the current directory. If only
        one interaction file is present in the current directory, it
        will be automatically selected.

    filename_partition : str | None
        The name of the partition file. If None, the user will be
        prompted to select a file from the current directory. If only
        one partition file is present in the current directory, it
        will be automatically selected.

    filename_partition_edited : str | None
        The name of the edited partition file. If None, a name will be
        generated automatically.

    input_wrapper : Callable
        NOTE: CURRENTLY NOT FUNCTIONING FOR TESTS. Defaults to `input`
        which asks the user for input. This wrapper exists so that unit
        tests can be performed in which case
        `input_wrapper = input_wrapper_test`.

    is_interactive : bool
        If True, the user will be prompted to select an interaction
        file and partition file if they are not provided. If False,
        the user will not be prompted and the program will exit if
        the interaction file or partition file are not provided.
    """
    y_offset: int = 0
    vum = Vum()
    screen = vum.screen
    if input_wrapper is None:
        input_wrapper = vum.input

    if is_interactive:
        filenames_interaction = sorted([i for i in os.listdir() if i.endswith(".snt")])
        filenames_partition = sorted([i for i in os.listdir() if i.endswith(".ptn")])
        
        if not filenames_interaction:
            return f"No interaction file present in {os.getcwd()}. Exiting..."
        if not filenames_partition:
            return f"No partition file present in {os.getcwd()}. Exiting..."

        if len(filenames_interaction) == 1:
            filename_interaction = filenames_interaction[0]
            screen.addstr(0, 0, f"{filename_interaction} chosen")
            screen.refresh()

        elif len(filenames_interaction) > 1:
            interaction_choices: str = ""
            for i in range(len(filenames_interaction)):
                interaction_choices += f"{filenames_interaction[i]} ({i}), "
            
            screen.addstr(vum.n_rows - 1 - vum.command_log_length - 1, 0, "Several interaction files detected.")
            screen.addstr(vum.n_rows - 1 - vum.command_log_length, 0, interaction_choices)
            screen.refresh()
            
            while True:
                ans = vum.input("Several interaction files detected. Please make a choice")
                try:
                    ans = int(ans)
                except ValueError:
                    continue
                
                try:
                    filename_interaction = filenames_interaction[ans]
                except IndexError:
                    continue

                break

        screen.addstr(0, 0, vum.blank_line)
        screen.addstr(1, 0, vum.blank_line)
        screen.refresh()
        
        if len(filenames_partition) == 1:
            filename_partition = filenames_partition[0]
            screen.addstr(0, 0, f"{filename_partition} chosen")
            screen.refresh()

        elif len(filenames_partition) > 1:
            partition_choices: str = ""
            for i in range(len(filenames_partition)):
                partition_choices += f"{filenames_partition[i]} ({i}), "
            
            screen.addstr(vum.n_rows - 1 - vum.command_log_length - 1, 0, "Several partition files detected.")
            screen.addstr(vum.n_rows - 1 - vum.command_log_length, 0, partition_choices)
            screen.refresh()
            
            while True:
                ans = vum.input("Several partition files detected. Please make a choice")
                try:
                    ans = int(ans)
                except ValueError:
                    continue
                
                try:
                    filename_partition = filenames_partition[ans]
                except IndexError:
                    continue

                break
        
        screen.addstr(vum.n_rows - 1 - vum.command_log_length - 1, 0, vum.blank_line)
        screen.addstr(vum.n_rows - 1 - vum.command_log_length, 0, vum.blank_line)
        screen.refresh()

    elif not is_interactive:
        if filename_interaction is None:
            return "No interaction file provided. Exiting..."
        if filename_partition is None:
            return "No partition file provided. Exiting..."

    header: str = ""
    proton_configurations: list[str] = []
    neutron_configurations: list[str] = []
    proton_configurations_formatted: list[ConfigurationParameters] = [] # For calculating the dim without writing the data to file.
    neutron_configurations_formatted: list[ConfigurationParameters] = []
    total_configurations_formatted: list[list[int]] = []
    model_space: list[OrbitalParameters] = []

    if filename_partition_edited is None:
        filename_partition_edited = f"{filename_partition.split('.')[0]}_edited.ptn"

    with open(filename_interaction, "r") as infile:
        """
        Extract information from the interaction file about the orbitals
        in the model space.
        """
        for line in infile:
            """
            Example:
            ! 2015/07/13
            ! from GCLSTsdpfsdgix5pn.snt 
            !  8 0g9/2  -0.8MeV
            !  9 0g7/2  -3.2MeV
            ! 10 1d5/2  -2.5MeV
            ! 11 1d3/2  -5.7MeV
            ! 12 2s1/2  -4.0MeV
            !
            ! sdpfsdg_64.sps
            ! sdpfsdg-shell
            ! index,    n,  l,  j, tz
            12  12   8   8
            ...
            """
            if line[0] != "!":
                tmp = line.split()
                n_proton_orbitals = int(tmp[0])
                n_neutron_orbitals = int(tmp[1])
                n_core_protons = int(tmp[2])
                n_core_neutrons = int(tmp[3])
                break

        for line in infile:
            if line[0] == "!": break
            idx, n, l, j, tz = [int(i) for i in line.split("!")[0].split()]
            idx -= 1
            nucleon = "p" if tz == -1 else "n"
            model_space.append(OrbitalParameters(
                idx = idx,
                n = n,
                l = l,
                j = j,
                tz = tz,
                nucleon = nucleon,
                name = f"{nucleon} {n}{spectroscopic_conversion[l]}{j}/2",
                parity = (-1)**l,
            ))

    if not all(orb.idx == i for i, orb in enumerate(model_space)):
        """
        Make sure that the list indices are the same as the orbit
        indices.
        """
        msg = (
            "The orbitals in the model space are not indexed correctly!"
        )
        raise KshellDataStructureError(msg)

    model_space_proton = [orbital for orbital in model_space if orbital.tz == -1]   # These are practical to have in separate lists.
    model_space_neutron = [orbital for orbital in model_space if orbital.tz == 1]
    
    draw_shell_map(vum=vum, model_space=model_space, is_proton=True, is_neutron=True)

    with open(filename_partition, "r") as infile:
        for line in infile:
            """
            Extract the information from the header before partitions
            are specified. Example:

            # hw trucnation,  min hw = 0 ,   max hw = 1
            # partition file of gs8.snt  Z=20  N=31  parity=-1
            20 31 -1
            # num. of  proton partition, neutron partition
            86 4
            # proton partition
            ...
            """
            if "#" not in line:
                tmp = [int(i) for i in line.split()]

                try:
                    """
                    For example:
                    20 31 -1
                    """
                    n_valence_protons, n_valence_neutrons, parity = tmp
                except ValueError:
                    """
                    For example:
                    86 4
                    """
                    n_proton_configurations, n_neutron_configurations = tmp
                    infile.readline()   # Skip header.
                    break

            header += line

        for line in infile:
            """
            Extract proton partitions.
            """
            if "# neutron partition" in line: break

            proton_configurations.append(line)
            configuration = [int(i) for i in line.split()[1:]]

            proton_configurations_formatted.append(
                ConfigurationParameters(
                    configuration = configuration,
                    idx = int(line.split()[0]) - 1,
                    parity = calculate_configuration_parity(
                        configuration = configuration,
                        model_space = model_space_proton
                    ),
                )
            )

        for line in infile:
            """
            Extract neutron partitions.
            """
            if "# partition of proton and neutron" in line: break

            neutron_configurations.append(line)
            configuration = [int(i) for i in line.split()[1:]]
            
            neutron_configurations_formatted.append(
                ConfigurationParameters(
                    configuration = configuration,
                    idx = int(line.split()[0]) - 1,
                    parity = calculate_configuration_parity(
                        configuration = configuration,
                        model_space = model_space_neutron
                    ),
                )
            )

    _generate_total_configurations(
        proton_configurations = proton_configurations_formatted,
        neutron_configurations = neutron_configurations_formatted,
        total_configurations = total_configurations_formatted,
        partition_file_parity = parity
    )

    M, mdim, jdim = count_dim(
        model_space_filename = filename_interaction,
        partition_filename = None,
        print_dimensions = False,
        debug = False,
        parity = parity,
        proton_partition = [configuration.configuration for configuration in proton_configurations_formatted],
        neutron_partition = [configuration.configuration for configuration in neutron_configurations_formatted],
        total_partition = total_configurations_formatted,
    )
    mdim_original: int = mdim[-1]
    vum.addstr(y_offset, 0, f"{filename_interaction}, {filename_partition}")
    vum.addstr(y_offset + 1, 0, f"M-scheme dim (M={M[-1]}): {mdim[-1]:d} ({mdim[-1]:.2e})")
    vum.addstr(y_offset + 2, 0, f"n proton, neutron configurations: {n_proton_configurations}, {n_neutron_configurations}")
    vum.addstr(y_offset + 3, 0, f"n valence protons, neutrons: {n_valence_protons}, {n_valence_neutrons}")
    vum.addstr(y_offset + 4, 0, f"n core protons, neutrons: {n_core_protons}, {n_core_neutrons}")
    vum.addstr(y_offset + 5, 0, f"{parity = }")
    vum.addstr(y_offset + 6, 0, "parity current configuration = None")

    new_proton_configurations: list[list[int]] = []
    new_neutron_configurations: list[list[int]] = []

    analyse_existing_configuration(
        vum = vum,
        proton_configurations_formatted = proton_configurations_formatted,
        neutron_configurations_formatted = neutron_configurations_formatted,
        input_wrapper = input_wrapper,
        model_space = model_space,
        y_offset = y_offset,
    )
    if input_wrapper("Add new proton configuration? (y/n)") == "y":
        while True:
            draw_shell_map(vum=vum, model_space=model_space, is_proton=True, is_neutron=False)
            occupation = _prompt_user_for_configuration(
                vum = vum,
                nucleon = "proton",
                model_space = model_space[:n_proton_orbitals],
                n_valence_nucleons = n_valence_protons,
                input_wrapper = input_wrapper,
                parity = parity,
                y_offset = y_offset,
            )
            if occupation:
                new_proton_configurations.append(occupation)
                proton_configurations_formatted.append(
                    ConfigurationParameters(
                        idx = len(proton_configurations_formatted),
                        configuration = occupation,
                        parity = calculate_configuration_parity(
                            configuration = occupation,
                            model_space = model_space_proton
                        )
                    )
                )
                
                total_configurations_formatted.clear()
                for p_idx in range(len(proton_configurations_formatted)):   # NOTE: Can make this more efficient.
                    for n_idx in range(len(neutron_configurations_formatted)):
                        total_configurations_formatted.append([p_idx, n_idx])
                
                M, mdim, jdim = count_dim(
                    model_space_filename = filename_interaction,
                    partition_filename = None,
                    print_dimensions = False,
                    debug = False,
                    parity = parity,
                    proton_partition = [configuration.configuration for configuration in proton_configurations_formatted],
                    neutron_partition = [configuration.configuration for configuration in neutron_configurations_formatted],
                    total_partition = total_configurations_formatted,
                )
                vum.addstr(y_offset + 1, 0, f"M-scheme dim (M={M[-1]}): {mdim[-1]:d} ({mdim[-1]:.2e}) (original {mdim_original:d} ({mdim_original:.2e}))")
                vum.addstr(y_offset + 2, 0, f"n proton, neutron configurations: {n_proton_configurations} + {len(new_proton_configurations)}, {n_neutron_configurations} + {len(new_neutron_configurations)}")
                
                if input_wrapper("Add another proton configuration? (y/n)") == "y":
                    continue
                else:
                    break

            elif occupation is None:
                """
                Quit signal. Do not keep the current configuration,
                but keep earlier defined new configurations and quit
                the prompt.
                """
                draw_shell_map(vum=vum, model_space=model_space, is_proton=True, is_neutron=False)
                if input_wrapper("Add another proton configuration? (y/n)") == "y":
                    continue
                else:
                    break

    if input_wrapper("Add new neutron configuration? (y/n)") == "y":
        while True:
            draw_shell_map(vum=vum, model_space=model_space, is_proton=False, is_neutron=True)
            occupation = _prompt_user_for_configuration(
                vum = vum,
                nucleon = "neutron",
                model_space = model_space[n_neutron_orbitals:],
                n_valence_nucleons = n_valence_neutrons,
                input_wrapper = input_wrapper,
                parity = parity,
                y_offset = y_offset,
            )
            if occupation:
                new_neutron_configurations.append(occupation)
                neutron_configurations_formatted.append(
                    ConfigurationParameters(
                        idx = len(neutron_configurations_formatted),
                        configuration = occupation,
                        parity = calculate_configuration_parity(
                            configuration = occupation,
                            model_space = model_space_neutron
                        )
                    )
                )

                total_configurations_formatted.clear()
                for p_idx in range(len(proton_configurations_formatted)):   # NOTE: Can make this more efficient.
                    for n_idx in range(len(neutron_configurations_formatted)):
                        total_configurations_formatted.append([p_idx, n_idx])
                
                M, mdim, jdim = count_dim(
                    model_space_filename = filename_interaction,
                    partition_filename = None,
                    print_dimensions = False,
                    debug = False,
                    parity = parity,
                    proton_partition = [configuration.configuration for configuration in proton_configurations_formatted],
                    neutron_partition = [configuration.configuration for configuration in neutron_configurations_formatted],
                    total_partition = total_configurations_formatted,
                )
                vum.addstr(y_offset + 1, 0, f"M-scheme dim (M={M[-1]}): {mdim[-1]:d} ({mdim[-1]:.2e}) (original {mdim_original}) ({mdim_original:.2e}))")
                vum.addstr(y_offset + 2, 0, f"n proton, neutron configurations: {n_proton_configurations} + {len(new_proton_configurations)}, {n_neutron_configurations} + {len(new_neutron_configurations)}")

                if input_wrapper("Add another neutron configuration? (y/n)") == "y":
                    continue
                else:
                    break

            elif occupation is None:
                """
                Quit signal. Do not keep the current configuration,
                but keep earlier defined new configurations and quit
                the prompt.
                """
                draw_shell_map(vum=vum, model_space=model_space, is_proton=False, is_neutron=True)
                if input_wrapper("Add another neutron configuration? (y/n)") == "y":
                    continue
                else:
                    break

    n_new_proton_configurations = len(new_proton_configurations)
    n_new_neutron_configurations = len(new_neutron_configurations)
    n_total_proton_configurations = n_new_proton_configurations + n_proton_configurations
    n_total_neutron_configurations = n_new_neutron_configurations + n_neutron_configurations

    if (not n_new_neutron_configurations) and (not n_new_proton_configurations):
        return "No new configurations. Skipping creation of new .ptn file."

    with open(filename_partition_edited, "w") as outfile:
        """
        Write edited data to new partition file.
        """
        outfile.write(header)
        outfile.write(f" {n_total_proton_configurations} {n_total_neutron_configurations}\n")
        outfile.write("# proton partition\n")
        
        for configuration in proton_configurations:
            outfile.write(configuration)

        for i in range(n_new_proton_configurations):
            outfile.write(
                f"{i + n_proton_configurations + 1:6d}     "    # +1 because .ptn indices start at 1.
                f"{str(new_proton_configurations[i]).strip('[]').replace(',', ' ')}"
                "\n"
            )
        outfile.write("# neutron partition\n")

        for configuration in neutron_configurations:
            outfile.write(configuration)

        for i in range(n_new_neutron_configurations):
            outfile.write(
                f"{i + n_neutron_configurations + 1:6d}     "    # +1 because .ptn indices start at 1.
                f"{str(new_neutron_configurations[i]).strip('[]').replace(',', ' ')}"
                "\n"
            )
        outfile.write("# partition of proton and neutron\n")
        outfile.write(f"{n_total_proton_configurations*n_total_neutron_configurations}\n")

        for p_idx in range(n_total_proton_configurations):
            """
            Write the proton-neutron configurations to file. This is
            really just pairing up all proton configuration indices
            with all neutron configuration indices.
            """
            for n_idx in range(n_total_neutron_configurations):
                outfile.write(f"{p_idx + 1:5d}{n_idx + 1:6d}\n")    # The .ptn indices start at 1.

    return (
        f"New configuration saved to {filename_partition_edited}"
        f" with {n_new_proton_configurations} new proton configurations"
        f" and {n_new_neutron_configurations} new neutron configurations"
    )

def _prompt_user_for_configuration(
    vum: Vum,
    nucleon: str,
    model_space: list[OrbitalParameters],
    n_valence_nucleons: int,
    input_wrapper: Callable,
    parity: int,
    y_offset: int,
) -> list | None:
        """
        Prompt the user for a new proton or neutron configuration,
        meaning that this function prompts the user for the occupation
        of all the orbitals in the model space and returns the
        configuration as a list of occupation numbers.
        """
        if nucleon == "proton":
            is_proton = True
            is_neutron = False

        elif nucleon == "neutron":
            is_proton = False
            is_neutron = True

        else:
            msg = f"Invalid nucleon parameter '{nucleon}'!"
            raise ValueError(msg)

        model_space_copy = sorted(  # Sort the orbitals based on the shell_model_order dict.
            model_space,
            key = lambda orbital: shell_model_order[f"{orbital.n}{spectroscopic_conversion[orbital.l]}{orbital.j}"],
        )
        n_remaining_nucleons: int = n_valence_nucleons
        vum.addstr(vum.n_rows - 2 - vum.command_log_length, 0, f"Please enter {nucleon} orbital occupation (f to fill, q to quit):")
        occupation: list[tuple[int, int]] = []
        occupation_parity: int = 1

        for orbital in model_space_copy:
            if n_remaining_nucleons == 0:
                """
                If there are no more valence nucleons to use, set the
                remaining occupations to 0.
                """
                occupation.append((orbital.idx, 0))
                vum.addstr(vum.n_rows - 3 - vum.command_log_length, 0, "Occupation of remaining orbitals set to 0.")
                continue

            while True:
                ans = input_wrapper(f"{orbital.idx + 1:2d} {orbital} (remaining: {n_remaining_nucleons})")
                if (ans == "q") or (ans == "quit") or (ans == "exit"): return None
                if ans == "f": ans = orbital.j + 1  # Fill the orbital.
                try:
                    ans = int(ans)
                except ValueError:
                    continue

                if (ans > (orbital.j + 1)) or (ans < 0):
                    vum.addstr(
                        vum.n_rows - 3 - vum.command_log_length, 0,
                        f"Allowed occupation for this orbital is [0, 1, ..., {orbital.j + 1}]"
                    )
                    continue
                
                # orbital_parity: int = (-1)**orbital.l
                # occupation_parity *= orbital_parity**ans
                occupation_parity *= orbital.parity**ans
                vum.addstr(y_offset + 6, 0, f"parity current configuration = {occupation_parity}")
                
                n_remaining_nucleons -= ans
                if ans > 0:
                    """
                    No point in re-drawing the line if the occupation is
                    unchanged.
                    """
                    draw_shell_map(
                        vum = vum,
                        model_space = model_space,
                        is_proton = is_proton,
                        is_neutron = is_neutron,
                        occupation = (orbital.idx, ans)
                    )
                break

            occupation.append((orbital.idx, ans))

            cum_occupation = sum(tup[1] for tup in occupation)
            if cum_occupation > n_valence_nucleons:
                vum.addstr(
                    vum.n_rows - 3 - vum.command_log_length, 0,
                    f"INVALID: Total occupation ({cum_occupation}) exceeds the number of valence {nucleon}s ({n_valence_nucleons})"
                )
                draw_shell_map(
                    vum = vum,
                    model_space = model_space,
                    is_proton = is_proton,
                    is_neutron = is_neutron,
                )
                return []
        
        cum_occupation = sum(tup[1] for tup in occupation)
        if cum_occupation < n_valence_nucleons:
            vum.addstr(
                vum.n_rows - 3 - vum.command_log_length, 0,
                f"INVALID: Total occupation ({cum_occupation}) does not use the total number of valence {nucleon}s ({n_valence_nucleons})"
            )
            draw_shell_map(
                vum = vum,
                model_space = model_space,
                is_proton = is_proton,
                is_neutron = is_neutron,
            )
            return []
        
        # if occupation_parity != parity:
        #     vum.addstr(
        #         vum.n_rows - 3 - vum.command_log_length, 0,
        #         f"INVALID: Parity of new occupation is {occupation_parity} while the parity of the current partition file is {parity}"
        #     )
            # draw_shell_map(
            #     vum = vum,
            #     model_space = model_space,
            #     is_proton = is_proton,
            #     is_neutron = is_neutron,
            # )
            # return []
        
        vum.addstr(vum.n_rows - 2 - vum.command_log_length, 0, vum.blank_line)
        occupation.sort(key=lambda tup: tup[0]) # Sort list of tuples based on the orbital.idx.
        return [tup[1] for tup in occupation]   # Return only the occupation numbers now sorted based on the orbital order of the .snt file.