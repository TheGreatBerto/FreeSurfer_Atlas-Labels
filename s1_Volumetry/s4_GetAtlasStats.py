# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:30:15 2022

@author: The Great Berto
"""


#Instructions:

#Change the paths, add a proyect code to find your subjects and adjust 
    #the measures that you want to calculate

#Modules to import
import os
from time import time
import pandas as pd
import numpy as np
import statsmodels.api as sm

#Estimate the time of execution
initial_time = time()

#Personalize your PATHS: Enter the path of freesurfer's Subjects folder, 
    #freerun.sh, atlases, ColorLut, hemispheres, output path & proyect code
Subjects_dir = '/usr/local/freesurfer/subjects/'
freerun_path = '/home/neuroimage/fsl/FreeSurfer/freerun.sh'
Atlases = ['aparc.DKTatlas40']
wmColorLut_path = '/home/neuroimage/fsl/FreeSurfer/DKColorLUT.txt'
hemispheres = ['lh', 'rh']
Output_dir = '/home/neuroimage/fsl/stats/'
proyect_code = 'Suj'

#desired measures : volume (gray a white matter volume), thickness, thicknessstd, meancurv, 
    #gauscurv, foldind, curvind and area (don't ommit area if you want to measure mixed ROIs stats/
    #Don't ommit wmvolume if you want to correct volume measures by ICV or TBV)
measures = ['volume', 'wmvolume', 'thickness', 'thicknessstd', 'meancurv', 'gauscurv', 'foldind', 'curvind', 'area']
#Correction factors to volumetry
CorrectionFactors = ['ICV', 'TBV'] #to correct by intra craneal volume and total brain volume respectively

#Create output dir if not exist
if not os.path.isdir(Output_dir): 
    os.mkdir(Output_dir)
    
#list your directories
content = os.listdir(Subjects_dir)
content.sort()
directories = []
for item in content:
    if os.path.isdir(Subjects_dir + item + '/') and item.startswith(proyect_code):
        directories.append(item)#Calculate the time of ex
        
#Prepare the command lines       
Subjects_command = ''
if 'volume' in measures:
    wmstats_command = []
    for Atlas in Atlases:
        wmstats_command.append('')
        
#Goes throw the directories selected creating stats to each subject 
    #sbased on each segmentation       
for directory in directories:
    print ('Working on ' + directory)
    for Atlas in Atlases:
        for hemisphere in hemispheres:
            if not os.path.isfile(Subjects_dir + directory + '/stats/' + hemisphere + '.' + Atlas + '.stats'):
                os.system ('bash ' + freerun_path + ' mris_anatomical_stats -a ' + 
                Subjects_dir + directory + '/label/' + hemisphere + '.' + Atlas + '.annot -f ' 
                + Subjects_dir + directory + '/stats/' + hemisphere + '.' + Atlas + 
                '.stats -b ' + directory + ' ' + hemisphere )
        
        if 'volume' in measures:
            if not os.path.isfile(Subjects_dir + directory + '/stats/wm' + Atlas + '.stats'):
                os.system ('bash ' + freerun_path + ' mri_segstats --seg ' + Subjects_dir +
                directory + '/label/wm' + Atlas + '.nii --ctab ' + wmColorLut_path + 
                ' --sum ' + Subjects_dir + directory + '/stats/wm' + Atlas + 
                '.stats --pv ' + Subjects_dir + directory + '/mri/norm.mgz --excludeid 0 --brainmask ' + 
                Subjects_dir + directory + '/mri/brainmask.mgz --in ' + Subjects_dir + directory + 
                '/mri/norm.mgz --in-intensity-name norm --in-intensity-units MR --subject ' +
                directory + ' --surf-wm-vol --etiv')
                
            wmstats_command[Atlases.index(Atlas)] = (wmstats_command[Atlases.index(Atlas)] + '-i ' + 
            Subjects_dir + directory + '/stats/wm' + Atlas + '.stats ')
    
    Subjects_command = Subjects_command + directory + ' '

#Use the stats files previously created to build a freesurfer table and a Data dict
    #with all the data for each desired measure    
Data = dict()
for Atlas in Atlases:
    Data[Atlas] = dict()
    for measure in measures:
        if measure == 'wmvolume':
            os.system ('bash ' + freerun_path + ' asegstats2table ' + wmstats_command[Atlases.index(Atlas)] +
            '--tablefile ' + Output_dir + proyect_code + '_wm' + Atlas + 'volume.txt')
            Data[Atlas]['wm_volume'] = pd.read_table (Output_dir + proyect_code + '_wm' + Atlas + 'volume.txt')
            Data[Atlas]['wm_volume']['Measure:volume'] = directories
            Data[Atlas]['wm_volume'] = Data[Atlas]['wm_volume'].rename(index=str, columns={'Measure:volume' : 'Subjects'})
        
        else:
            Data[Atlas][measure] = pd.DataFrame()
            for hemisphere in hemispheres:
                os.system ('bash ' + freerun_path + ' aparcstats2table --hemi ' + 
                hemisphere + ' --subjects ' + Subjects_command + '--parc ' + Atlas + ' --meas ' + 
                measure + ' --tablefile ' + Output_dir + proyect_code + '_' + hemisphere + '_' + Atlas + 
                measure + '.txt')
                Data[Atlas][measure] = pd.concat([Data[Atlas][measure], pd.read_table (Output_dir + proyect_code + '_' +
                hemisphere + '_' + Atlas + measure + '.txt')], axis=1)
            Data[Atlas][measure] = Data[Atlas][measure].drop(['rh.' + Atlas + '.' + measure], axis=1)
            Data[Atlas][measure] = Data[Atlas][measure].rename(index=str, columns={('lh.' + Atlas + '.' + measure) : 'Subjects'})
            
os.system ('bash ' + freerun_path + ' asegstats2table --subjects ' + Subjects_command + ' --meas volume --tablefile ' + Output_dir + 
proyect_code + '_' + 'SubcorticalVol.txt')
Data['Subcortical'] = dict()
Data['Subcortical']['volume'] = pd.read_table(Output_dir + proyect_code + '_' + 'SubcorticalVol.txt')
Data['Subcortical']['volume'] = Data['Subcortical']['volume'].rename(index=str, columns={'Measure:volume' : 'Subjects'})
                               
#Correct the volume measurment by the correction factors using proportional and residual method
print ('Performing volume correction by ICV and TBV using proportional and residual method')
if 'volume' in measures:
    ICV = Data['Subcortical']['volume']['EstimatedTotalIntraCranialVol']
    TBV = Data['Subcortical']['volume']['BrainSegVol']
    for Atlas in Data.keys():
        str_match = [s for s in Data[Atlas].keys() if 'volume' in s]
        for volume in str_match:
            for factor in CorrectionFactors:
                Data[Atlas][factor + '_pro_corrected_' + volume] = pd.DataFrame(index = range(0, len(directories)))
                Data[Atlas][factor + '_pro_corrected_' + volume]['Subjects'] = directories
                Data[Atlas][factor + '_res_corrected_' + volume] = pd.DataFrame(index = range(0, len(directories)))
                Data[Atlas][factor + '_res_corrected_' + volume]['Subjects'] = directories
                ROIs = list(Data[Atlas][volume].columns)
                ROIs.pop(ROIs.index([s for s in ROIs if 'Subjects' in s][0]))
                for ROI in ROIs:
                    ROI_values = Data[Atlas][volume][ROI]
                    if factor == 'ICV': 
                        factor_mean = sum(ICV)/len(ICV)
                        factor_val  = ICV
                        x = sm.add_constant(ICV)
                    if factor == 'TBV': 
                        factor_mean = sum(TBV)/len(TBV)
                        factor_val  = TBV
                        x = sm.add_constant(TBV)
                    regression_model = sm.OLS(ROI_values,x)
                    results = regression_model.fit()
                    beta = results.params[1]
                    Data[Atlas][factor + '_res_corrected_' + volume][ROI] = np.array(ROI_values - beta*(factor_val-factor_mean))
                    Data[Atlas][factor + '_pro_corrected_' + volume][ROI] = np.array((ROI_values/factor_val)*factor_mean)
    
#Save each element in Data into an excel
print ('Saving data into xlsx files')
for Atlas in Data.keys():
    if not os.path.isdir(Output_dir + Atlas + '/'): 
        os.mkdir(Output_dir + Atlas + '/')
    for dat in Data[Atlas].keys():
        Data[Atlas][dat].to_excel(Output_dir + Atlas + '/' + dat + '.xlsx')
    
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