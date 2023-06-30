import numpy as np
from pathlib import Path
import accumulators


## Here are some simple filters:

def filter_xstep(run):
    """
    filter on steps in sampleX2 greater than 0.9 * the median step
    """
    def apply(good_shots=None):
        if good_shots is None:
            good_shots = np.arange(len(run))
    
        step_x = np.gradient(run.sampleX2[good_shots])
        step_x_threshold=np.median(step_x) * 0.9
        if np.max(step_x) > 1e-6:
            good_shots=good_shots[step_x>step_x_threshold]
        return good_shots
    
    return apply

def filter_shutter(run):
    """
    filter on open shutter
    """
    def apply(good_shots=None):
        if good_shots is None:
            good_shots = np.arange(len(run))
        good_shots=good_shots[run.shutter_open[good_shots]>0]
        return good_shots

    return apply





