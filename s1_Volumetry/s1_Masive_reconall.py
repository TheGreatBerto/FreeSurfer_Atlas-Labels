# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 13:07:27 2021

@author: The Great Berto
"""

import os
from time import time

#Estimate the time of execution (10 hours per subject)
initial_time = time()

#Personalize your PATHS: Enter the path of T1 folder, freerun.sh.
Subjects_dir = '/home/neuroimage/fsl/CurrentRM/'
freerun_path = '/home/neuroimage/fsl/FreeSurfer/freerun.sh'

content = os.listdir(Subjects_dir)

for item in content:
    suj_name = item[7:10]
    print('Performing ' + suj_name + ' recon-all')
    os.system('bash ' + freerun_path + ' recon-all -i ' + 
    Subjects_dir + item + ' -subject ' + suj_name + ' -all')
         
         
#Estimate the time of execution (10 hours per subject)
final_time = time()
time_lapse = final_time - initial_time

if time_lapse < 60:
    print ('The code ran in ' + str(time_lapse) + ' seconds')
if time_lapse > 60 and time_lapse < 3600:
    minutes = time_lapse // 60
    seconds = time_lapse % 60
    print ('The code ran in ' + str(minutes) + ' minutes and ' + str(seconds) + ' seconds')
if time_lapse > 3600:
    minutes = time_lapse // 60
    hours = minutes // 60
    minutes = minutes % 60
    seconds = time_lapse % 60
    print ('The code ran in ' + str(hours) + ' hours, '+ str(minutes) + ' minutes and ' + str(seconds) + ' seconds')
