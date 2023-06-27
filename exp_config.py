# zimmf for beamtime kuschel2023

from attenuator import attenuator_eh5_silicon_thickness
import numpy as np

# add point data here. format is one of
# name: databasekey
# name: databasekey, scalefactor
# name: databasekey, scalefuntion

database_keys = {
    "sampleX1": ("xfel_bl_3_st_5_motor_user_19/position", -0.0125e-6), #according to taito
    "sampleX2": ("xfel_bl_3_st_5_motor_facility_14/position", 0.5e-6),
    "sampleZ1": ("xfel_bl_3_st_5_motor_user_18/position", 0.05e-6),
    "sampleZ2": ("xfel_bl_3_st_5_motor_facility_16/position", -1e-6),
    "attenuator_eh_5_Si_mm": ("xfel_bl_3_st_5_motor_facility_29/position", attenuator_eh5_silicon_thickness),
    "crystalTheta_pulses": "xfel_bl_3_st_1_motor_67/position",  # TODO: calibration
}

# Add 2d detectors here
detector_keys = {
    "spectrometer": "MPCCD-1N0-M07-006",
    "side_ccd":"MPCCD-2N0-M02-003",
    "forward_ccd":"MPCCD-2N0-M02-001",
}

# format:
# name: float
# if set to 1.0, we work with ADUs ;)
detector_ev_per_adu_0 = {
    "spectrometer": 1.0,
    "side_ccd": 1.0,
    "forward_ccd": 1.0,
}

# format:
# name: path to .npy
detector_dark_files_0 = {
    "spectrometer": None,
    "side_ccd": None,#"/UserData/kuschel/2023TRsHardXray/data/darks/side_1312796.npy",
    "forward_ccd": None, #"/UserData/kuschel/2023TRsHardXray/data/darks/forward_1312796.npy",
}

# spectrometer settings while on iron
spectrometer_ev_per_pixel = 0.346
spectrometer_center_ev = 6390.4
spectrometer_axis_iron = np.arange(-512,512)*spectrometer_ev_per_pixel+spectrometer_center_ev
