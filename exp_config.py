from attenuator import attenuator_eh5_silicon_thickness

#add point data here. format is one of
#name: databasekey
#name: databasekey, scalefactor
#name: databasekey, scalefuntion

database_keys={
'sampleX1' : ('xfel_bl_3_st_5_motor_user_19/position',-0.025e-6),
'sampleX2' : ('xfel_bl_3_st_5_motor_facility_14/position',0.5e-6),
'sampleZ1' : ('xfel_bl_3_st_5_motor_user_18/position',0.005e-6),
'sampleZ2' : ('xfel_bl_3_st_5_motor_facility_16/position',-1e-6),
'attenuator_eh_5_Si_mm':('xfel_bl_3_st_5_motor_facility_29/position',attenuator_eh5_silicon_thickness),
"crystalTheta_pulses": "xfel_bl_3_st_1_motor_67/position" #TODO: calibration
}

#Add 2d detectors here
detector_keys={
    "spectrometer":"MPCCD-1N0-M06-004",
      #"side_ccd":"MPCCD-2N0-M02-003",
      #"forward_ccd":"MPCCD-2N0-M02-001",
}