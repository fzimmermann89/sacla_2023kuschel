# zimmf for beamtime kuschel2023

import numpy as np
def attenuator_eh5_silicon_thickness(pulses):
    """
    Converts pulses into Silicon thickness in m.
    xfel_bl_3_st_5_motor_facility_29/position
    """
    
    motorpulses = np.array((226200, 179059, 166522, 154238, 135266, 91636, 79067, 66630, 54075, 41718, 22601))
    thickness = np.array((0, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 1.5, 2.0, 2.5, 3.0)) * 1e-3
    
    return thickness[np.abs(motorpulses[None, :] - pulses[:, None]).argmin(axis=1)]
