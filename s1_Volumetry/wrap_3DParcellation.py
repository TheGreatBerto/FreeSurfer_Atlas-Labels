# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 17:38:16 2023

@author: neuroimage
"""
import os
from time import time

initial_time = time()

Freesurfer_dir = '/usr/local/freesurfer/subjects/'
Output_dir = '/home/neuroimage/fsl/2test/cluster2FS/vascular_aseg/'
freerun_path = '/home/neuroimage/fsl/FreeSurfer/freerun.sh'
Parcelation = 'aparc+aseg'
proyect_code = 'rU'
Overwrite = True
#Create output dir if not exist
if not os.path.isdir(Output_dir): 
    os.mkdir(Output_dir)

#list your directories
content = os.listdir(Freesurfer_dir)
directories = []
for item in content:
    if item.startswith(proyect_code): directories.append(item)


#Goes throught each directory wrapping each atlas into the subject space, Calculating
    #the white matter ROIs of each atlas and transform it into the native subject space
    #from freesurfer space. Finally copy the atlases into the output path
for directory in directories:
    if not os.path.isdir(Output_dir + directory + '/'): 
        os.mkdir(Output_dir + directory + '/')
  
    print ('      Wraping ' + Parcelation + ' from freesurfer to native ' + directory + ' space')
    if not os.path.isfile(Output_dir + directory + '/' + Parcelation + '.nii') or Overwrite:
        os.system ('bash ' + freerun_path + ' mri_label2vol --seg ' + Freesurfer_dir + 
            directory + '/mri/' + Parcelation + '.mgz --temp ' + Freesurfer_dir + directory + '/mri/rawavg.mgz --o ' + 
            Output_dir + directory + '/' + Parcelation + '.nii --regheader ' + Freesurfer_dir + 
            directory + '/mri/' + Parcelation + '.mgz')


#Estimate the time of execution (5-7 minutes per subject)
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
