# Analysis Framework for SACLA experiments
if not otherwise marked (c) by Felix Zimmermann for PTB Berlin



## Kuschel2023 Beamtime
This has been written for the Kuschel2023 beamtime, but is quite general and can easily be adapeted to other imaging beamtimes at SACLA BL3 and similiar.

## Overview  (WIP)
# exp_config.py:
  defines the experiment settings to be used by the other objects
  
# data_helper.py: 
  Some General Data Access Functions.
    Here are some wrapper functions to get the latest run, time of runs, tags, detector images, daq-data, etc.
  
  Of special interest are 
    - Detector: A Wrapper Object for Imaging Detector
    - DBReader: A Wrapper for reading DAQ data such as motor positions, shutter etc.
    - Run: An object representing a particular run with some imaging detectors and important information from the database. Gets the information defined in the exp_config as input
    A run is iterable and indexable to get the information for a single "Shot"
    - Shot: One FEL event. Contains the data from the DAQ-Objects and the imaging detectors used.

    An example how to use these is provided in example.py

# accumulators.py
  taken from https://github.com/skuschel/generatorpipeline, provides objects for simple means of taking the mean, max, quantile estimations etc.
  for copyright, see there.

# calculators.py
  similar in vein. some helper objects to calculate histograms with fixed bins, a priority-queue to keep the top-k elements etc

# filters.py
  an example how to implement shot-filtering. We used filtering on shutter-open and and the sampleX-scanning-motor speed (to remove acceleration phases).

# radial_profile.py
  taken from https://github.com/fzimmermann89/idi for radial profiles.


The suggested work flow is to loop over shots in  Run-object to perform analysis. This can nicely be done in parallel for many runs using the queue-system at sacla.
The example uses analyse.py to perform some analysis and write out the results per run.


# Workflow
These results are then used to generate relevenant plots in an ipynb notebook.

My suggestions to use jupyter efficiently as SACLA is:
  - connect via vpn
  - open an ssh connection with local port forwarding, i.e. ssh -L 55555:localhost:55555 xhpcfep01
  - start an interactive job on one of the queues, i.e. qsub -I or similar
  - load the relavent modules, i.e.
    source /home/blstaff/SACLAtool_py3.7
    module load SACLA_tool/1.0.0
    module load python/SACLA_python-3.7/offline
  - start an jupyter lab some port, e.g. 555555
  - remote port forward from the compute node back to the login node via ssh -R 55555:localhost:55555
  - the last to steps have to run in parallel. you can either use screens, tmus or similar to achieve that
now you can access an jupyter from you localhost:555555

Here, in the future some additional explainations will be added :)


# Licence
This is a somewhat tricky thing. Currently it is: All rights are reserved.
But Participants of any joined beamtime with me are hereby granted unlimited rights to reuse, modify, share, and relicense (!) under BSD/MIT/Apache if desired
under the condition that copyright notices are kept intact. 
Attribution by forking is appreciated.
Please feel free to contact to support are usage outside of these terms.
