# felix zimmermann, github.com/fzimmermann89 for beamtime kuschel2023
# This is the main settings file to adjust

from attenuator import attenuator_eh5_silicon_thickness
import numpy as np

# add point data here. format is one of
# name: databasekey
# name: databasekey, scalefactor
# name: databasekey, scalefuntion
database_keys = {
    #"sampleX1": ("xfel_bl_3_st_5_motor_user_19/position", -0.0125e-6), 
    "sampleX2": ("xfel_bl_3_st_5_motor_facility_14/position", 0.5e-6),
    "sampleZ1": ("xfel_bl_3_st_5_motor_user_18/position", 0.05e-6),
    #"sampleZ2": ("xfel_bl_3_st_5_motor_facility_16/position", -1e-6),
    "sampleY": ("xfel_bl_3_st_5_motor_facility_10/position", 0.25e-6),
    "attenuator_eh_5_Si_m": ("xfel_bl_3_st_5_motor_facility_29/position", attenuator_eh5_silicon_thickness),
    "crystalTheta_pulses": "xfel_bl_3_st_1_motor_67/position",  # TODO: calibration
    "diode" :"xfel_bl_3_st_5_direct_bm_1_pd/charge",
    "shutter_open" :"xfel_bl_3_shutter_1_open_valid/status"

}

# Add 2d detectors here
detector_keys = {
    "spectrometer": "MPCCD-1N0-M07-006",
    "side_ccd":"MPCCD-2N0-M02-003",
    "forward_ccd":"MPCCD-2N0-M02-001",
}


#Adjust darkfile paths here
# format:
# name: path to folder containing  .npy for the detector. each files has to be named *_{timestamp}.npy
# and the file with the timestamp closest to the run's middle time will be used.
detector_dark_paths = {
    "spectrometer": None,
    "side_ccd": "/work/kuschel/2023TRsHardXray/scratch/ulmer/data/darks/side/",
    "forward_ccd": "/work/kuschel/2023TRsHardXray/scratch/ulmer/data/darks/side/",
}


#### Custom settings for the experiment #####
# spectrometer settings while on iron
spectrometer_ev_per_pixel_fe = 0.346
spectrometer_center_ev_fe = 6390.4
spectrometer_axis_iron = np.arange(-512,512)*spectrometer_ev_per_pixel_fe+spectrometer_center_ev_fe

# spectrometer settings while on gold
spectrometer_ev_per_pixel_au = 0.817
spectrometer_center_ev_au = 9674.6
spectrometer_axis_gold= np.arange(-512,512)*spectrometer_ev_per_pixel_au+spectrometer_center_ev_au
