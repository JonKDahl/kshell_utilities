import pkg_resources
from numpy.typing import NDArray
import numpy as np
from .loaders import _load_energy_logfile, _load_transition_logfile

def test_load_energy_logfile():
    levels: NDArray = _load_energy_logfile(
        path = pkg_resources.resource_filename('kshell_utilities', 'test_files/log_V50_GCLSTsdpfsdgix5pn_j0p.txt')
    )
    expected_energies = [
        -392.15904, -391.87918, -391.28807, -391.17057, -390.44002, -390.06541,
        -389.86772, -389.83919, -389.31714, -389.06729, -388.784,   -388.59289,
        -388.57039, -388.40539, -388.1968,  -388.14303, -388.04195, -387.77982,
        -387.63565, -387.56545, -387.45116, -387.43385, -387.30063, -387.2544,
        -387.02201, -386.85552, -386.79288, -386.6574,  -386.64041, -386.62891,
        -386.51819, -386.50306, -386.45511, -386.41216, -386.31734, -386.26407,
        -386.21622, -386.12929, -386.11792, -385.96679, -385.92837, -385.86811,
        -385.77466, -385.72648, -385.66697, -385.55887, -385.53943, -385.46135,
        -385.45629, -385.44488, -385.39907, -385.34762, -385.33419, -385.27385,
        -385.23275, -385.14203, -385.08344, -385.01235, -385.00448, -384.96783,
        -384.93757, -384.92071, -384.88362, -384.85641, -384.8322,  -384.81149,
        -384.76652, -384.73499, -384.69545, -384.66275, -384.58908, -384.5749,
        -384.52536, -384.49007, -384.47427, -384.4308,  -384.39995, -384.37118,
        -384.35701, -384.32791, -384.2911,  -384.24597, -384.19671, -384.16197,
        -384.11927, -384.10432, -384.04675, -384.0059,  -383.9646,  -383.94497,
        -383.90206, -383.86877, -383.86056, -383.84362, -383.79145, -383.76175,
        -383.74647, -383.73498, -383.72184, -383.68725, -383.65797, -383.61139,
        -383.57793, -383.5467,  -383.52865, -383.50943, -383.47704, -383.44997,
        -383.43918, -383.42165, -383.41613, -383.37586, -383.35723, -383.32565,
        -383.29181, -383.26639, -383.25484, -383.24069, -383.23991, -383.22365,
        -383.20163, -383.1693,  -383.15186, -383.131,   -383.11096, -383.10213,
        -383.05318, -383.03786, -382.99332, -382.97311, -382.95468, -382.93878,
        -382.93625, -382.91026, -382.90846, -382.88592, -382.85452, -382.82076,
        -382.8078,  -382.7849,  -382.78209, -382.73696, -382.73514, -382.71719,
        -382.69036, -382.66774, -382.65989, -382.64508, -382.62155, -382.61111,
        -382.60313, -382.59006, -382.57579, -382.56519, -382.51692, -382.48697,
        -382.48151, -382.45994, -382.44407, -382.41855, -382.40847, -382.39294,
        -382.38223, -382.37415, -382.35276, -382.3342,  -382.32167, -382.3005,
        -382.28363, -382.2664,  -382.2642,  -382.24416, -382.21746, -382.18673,
        -382.18035, -382.15111, -382.14444, -382.12779, -382.12307, -382.09488,
        -382.07123, -382.06352, -382.04711, -382.04102, -381.99469, -381.98959,
        -381.98293, -381.95451, -381.94813, -381.93173, -381.92391, -381.91682,
        -381.89859, -381.87117, -381.8568,  -381.85164, -381.82438, -381.82337,
        -381.79418, -381.77844,
    ]
    expected_indices = [
        0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,
        14,  15,  16,  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,  27,
        28,  29,  30,  31,  32,  33,  34,  35,  36,  37,  38,  39,  40,  41,
        42,  43,  44,  45,  46,  47,  48,  49,  50,  51,  52,  53,  54,  55,
        56,  57,  58,  59,  60,  61,  62,  63,  64,  65,  66,  67,  68,  69,
        70,  71,  72,  73,  74,  75,  76,  77,  78,  79,  80,  81,  82,  83,
        84,  85,  86,  87,  88,  89,  90,  91,  92,  93,  94,  95,  96,  97,
        98,  99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
        112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
        126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139,
        140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153,
        154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167,
        168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181,
        182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195,
        196, 197, 198, 199,
    ]
    expected_parities = [1]*len(expected_energies)
    expected_j = [0]*len(expected_energies)
    expected_Hcm = [0]*len(expected_energies)

    assert np.all(expected_energies == levels[:, 0])
    assert np.all(expected_j == levels[:, 1])
    assert np.all(expected_parities == levels[:, 2])
    assert np.all(expected_indices == levels[:, 3])
    assert np.all(expected_Hcm == levels[:, 4])

def test_load_transition_logfile():
    transitions_E1, transitions_M1, transitions_E2 = _load_transition_logfile(
        path = pkg_resources.resource_filename('kshell_utilities', 'test_files/log_V50_GCLSTsdpfsdgix5pn_tr_j2n_j2n.txt')
    )
    expected_transitions_E2 = [
        [2, -1, 0, -392.049, 2, -1, 0, -392.049, 0.0, 96.95693633, 96.95693633],
        [2, -1, 1, -391.739, 2, -1, 0, -392.049, 0.31, 2.04087199, 2.04087199],
        [2, -1, 2, -391.501, 2, -1, 0, -392.049, 0.548, 3.47928543, 3.47928543],
        [2, -1, 3, -391.421, 2, -1, 0, -392.049, 0.628, 22.83326127, 22.83326127],
        [2, -1, 4, -391.405, 2, -1, 0, -392.049, 0.644, 23.93839124, 23.93839124],
        [2, -1, 5, -391.138, 2, -1, 0, -392.049, 0.912, 1.99307071, 1.99307071]
    ]

    assert expected_transitions_E2 == transitions_E2
    assert [] == transitions_E1
    assert [] == transitions_M1

    transitions_E1, transitions_M1, transitions_E2 = _load_transition_logfile(
        path = pkg_resources.resource_filename('kshell_utilities', 'test_files/log_V50_GCLSTsdpfsdgix5pn_tr_j2p_j4n.txt')
    )
    expected_transitions_E1 = [
        [4, -1, 0, -392.585, 2, 1, 0, -393.605, 1.021, 5.38e-06, 3.23e-06],
        [4, -1, 179, -387.12, 2, 1, 199, -384.604, -2.516, 1e-08, 1e-08],
        [4, -1, 180, -387.096, 2, 1, 199, -384.604, -2.492, 1.9e-07, 1.2e-07],
        [4, -1, 181, -387.087, 2, 1, 199, -384.604, -2.483, 1.123e-05, 6.74e-06],
        [4, -1, 182, -387.072, 2, 1, 199, -384.604, -2.467, 6e-08, 3e-08],
        [4, -1, 183, -387.06, 2, 1, 199, -384.604, -2.456, 8.2e-07, 4.9e-07],
        [4, -1, 184, -387.056, 2, 1, 199, -384.604, -2.451, 9.2e-07, 5.5e-07]
    ]
    expected_transitions_M1 = [
        [4, -1, 0, -392.585, 2, 1, 0, -393.605, 1.021, 5.38e-06, 3.23e-06],
        [4, -1, 1, -392.297, 2, 1, 0, -393.605, 1.308, 8.079e-05, 4.847e-05]
    ]
    expected_transitions_E2 = [
        [4, -1, 190, -387.016, 2, 1, 199, -384.604, -2.411, 1.6e-06, 9.6e-07],
        [4, -1, 191, -387.01, 2, 1, 199, -384.604, -2.406, 1.58e-06, 9.5e-07],
        [4, -1, 192, -387.005, 2, 1, 199, -384.604, -2.401, 6.3e-06, 3.78e-06]
    ]

    assert expected_transitions_E1 == transitions_E1
    assert expected_transitions_M1 == transitions_M1
    assert expected_transitions_E2 == transitions_E2