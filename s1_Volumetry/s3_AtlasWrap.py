# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 14:56:53 2021

@author: The Great Berto
"""

import os
from time import time
import shutil

#Estimate the time of execution
initial_time = time()

#Personalize your PATHS: Enter the Freesurfer Subject and Output folder paths, freerun.sh,
    #Atlases to wrap, proyect code and template where the atlases were segmented
Freesurfer_dir = '/usr/local/freesurfer/subjects/'
Output_dir = '/home/neuroimage/fsl/2test/cluster2FS/test_atlases/'
freerun_path = '/home/neuroimage/fsl/FreeSurfer/freerun.sh'
Atlases = ['myAAL', 'lobes']
hemispheres = ['lh', 'rh']
proyect_code = 'rU'
Template = 'fsaverage'
Overwrite = False
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
    for Atlas in Atlases:
        print ('Wrapping ' + Atlas + ' atlas to freesurfer ' + directory + ' space')
        for hemisphere in hemispheres:
            if not os.path.isfile(Freesurfer_dir + directory  + '/label/' + hemisphere + '.' + Atlas + '.annot') or Overwrite:
                os.system ('bash ' + freerun_path + ' mri_surf2surf --s ' + Template + 
                ' --trgsubject ' + directory + ' --hemi ' + hemisphere + ' --sval-annot '
                + Freesurfer_dir + Template + '/label/' + hemisphere + '.' + Atlas + '.annot' +
                ' --tval ' + Freesurfer_dir + directory + '/label/' + hemisphere + '.' + 
                Atlas + '.annot' )
                shutil.copy(Freesurfer_dir + directory + '/label/' + hemisphere + '.' + 
                Atlas + '.annot', Output_dir + directory + '/' + hemisphere + '.' + 
                Atlas + '.annot')
            
        print ('      Calculating white matter ROIs on ' + directory)
        if not os.path.isfile(Freesurfer_dir + directory  + '/label/wm' + Atlas + '.nii') or Overwrite:
            os.system ('bash ' + freerun_path + ' mri_aparc2aseg --s ' + directory + 
                ' --labelwm --hypo-as-wm --rip-unknown --volmask --o ' + Freesurfer_dir + 
                directory + '/label/wm' + Atlas + '.nii --annot ' + Atlas)
            
        print ('      Wraping ' + Atlas + ' from freesurfer to native ' + directory + ' space')
        if not os.path.isfile(Output_dir + directory + '/' + Atlas + '.nii') or Overwrite:
            os.system ('bash ' + freerun_path + ' mri_label2vol --seg ' + Freesurfer_dir + 
                directory + '/label/wm' + Atlas + '.nii --temp ' + Freesurfer_dir + directory + '/mri/rawavg.mgz --o ' + 
                Output_dir + directory + '/' + Atlas + '.nii --regheader ' + Freesurfer_dir + 
                directory + '/label/wm' + Atlas + '.nii')


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
