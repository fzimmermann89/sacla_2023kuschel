# felix zimmermann, github.com/fzimmermann89 for beamtime kuschel2023

from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from data_helper import *
import accumulators
from pathlib import Path
from filters import *
from calculators import *

import exp_config

def analyserun(runNR, max_shots=np.inf, step_shots=1):
    run=Run(exp_config.detector_keys,exp_config.database_keys, run=int(runNR))
    
    #accumulators
    spectrum_mean=accumulators.Mean()
    forward_mean=accumulators.Mean()
    forward_hist_mean=accumulators.Mean()
    forward_total = []
    side_mean=accumulators.Mean()
    side_max=accumulators.Maximum()
    side_hist_mean=accumulators.Mean()
    side_bright_pershot = []
    side_total = []
    spectrum=[]

    #calculators
    side_hist = Histogrammer(bins=200, range=(0,50000))
    forward_hist = Histogrammer(bins=200, range=(0,50000)) 
    side_bright_counter = RangeCounter(low=40) 
    top = topk(k=5) # 5 brightest images
    cut_noise=NoiseCutter(1000) #sets values below 1000ev to zero

    #shot filtering    
    good_shots = filter_shutter(run)(filter_xstep(run)())
    good_shots = good_shots[range(0,min(max_shots, len(good_shots)), step_shots)]

    print("good_shots:",good_shots)
    

    for i in tqdm(good_shots):
        shot = run[i]
        # do something with the data.

        #spectrometer
        current_spectrum = np.mean(shot.spectrometer, axis=1)
        spectrum_mean.accumulate(current_spectrum)
        spectrum.append(current_spectrum)

        #image detectors
        side_image = cut_noise(shot.side_ccd)
        side_image_sum = np.sum(side_image)
        forward_image = cut_noise(shot.forward_ccd)
        forward_image_sum = np.sum(forward_image)
        
        side_mean.accumulate(side_image)
        forward_mean.accumulate(forward_image)
        side_max.accumulate(shot.side_ccd)

        side_bright_pershot.append(side_bright_counter(shot.side_ccd))
        side_total.append(side_image_sum)
        forward_total.append(forward_image_sum)
        
        #brightest images
        dat = (forward_image_sum, side_image_sum, forward_image, side_image, i)
        brightness = forward_image_sum
        top.add(brightness,dat)
       
        #image hists
        side_hist_mean.accumulate(side_hist(shot.side_ccd))
        forward_hist_mean.accumulate(forward_hist(shot.forward_ccd))
    
    #get values of brightest images
    forward_top_image_sum,side_top_image_sum,forward_top_images,side_top_images,i_top_images=zip(*top.get())
    
    
    return to_dict(run, shots_taken=good_shots, side_mean=side_mean,forward_mean=forward_mean,side_hist_mean=side_hist_mean,forward_hist_mean=forward_hist_mean,forward_hist_centers=forward_hist.centers(),side_hist_centers=side_hist.centers(),side_bright_pershot=side_bright_pershot,side_max=side_max,side_total=side_total,forward_total=forward_total, runNR=runNR,spectrum_mean=spectrum_mean,spectrum=spectrum,spectrum_axis=exp_config.spectrometer_axis_gold, 
              forward_top_images=forward_top_images,    forward_top_image_sum=forward_top_image_sum,    side_top_image_sum=side_top_image_sum,    side_top_image=side_top_images,    i_top_images=i_top_images,)

if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("run")
    args=parser.parse_args()

    outpath=f"/work/kuschel/2023TRsHardXray/scratch/ulmer/data/run_data/data1_run{args.run}.npz"
    print("will save to",outpath)     
    data = analyserun(runNR=args.run)
    print("done", outpath)
    np.savez_compressed(outpath,**data)
