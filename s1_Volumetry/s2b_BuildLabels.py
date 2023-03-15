# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 16:50:22 2022

@author: The Great Berto
"""

import os
import shutil
from time import time
from datetime import datetime
import numpy as np
import Tkinter as tk

#Define the function needed
def repeat_lh():
    hemisphere = 'lh'
    os.system('bash ' + freerun_path + ' tksurfer -label ' + hemisphere + '.' + Template + '_' + 
        Mask_name[:-4] + ' ' + Template + ' ' + hemisphere + ' inflated')     
    shutil.copy(Freesurfer_dir + Template + '/label/' + hemisphere + '.' + Template + '_' + Mask_name[:-4] + '.label', 
        Images_path +  hemisphere + '.' + Template + '_' + Mask_name[:-4] + '_corrected.label') 
    root.destroy() 
def repeat_rh():
    hemisphere = 'rh'
    os.system('bash ' + freerun_path + ' tksurfer -label ' + hemisphere + '.' + Template + '_' + 
        Mask_name[:-4] + ' ' + Template + ' ' + hemisphere + ' inflated')     
    shutil.copy(Freesurfer_dir + Template + '/label/' + hemisphere + '.' + Template + '_' + Mask_name[:-4] + '.label', 
        Images_path +  hemisphere + '.' + Template + '_' + Mask_name[:-4] + '_corrected.label')
    root.destroy()     
def Finish():
    scape[0] = 1
    root.destroy() 

#Estimate the time of execution
initial_time = time()

#Personalize your PATHS: Enter the Freesurfer and Image paths as well as mask, 
    #source subject and template names. Add freerun.sh path and hemispheres 
    #where the mask will be proyected,
Images_path = '/home/neuroimage/fsl/2test/cluster2FS/'
Mask_names   = ['30to43Hz_niioverlay.nii']
Parcellation_name = 'Parcellation.annot'
srcSuj      = 'MNI152lin_T1_1mm.nii'
Freesurfer_dir = '/usr/local/freesurfer/subjects/'
Template = 'fsaverage'
freerun_path = '/home/neuroimage/fsl/FreeSurfer/freerun.sh'
hemispheres = ['lh', 'rh']


Overwrite = False

#Register source subject to the template space
print ('Registering source subject to ' + Template + ' space')
os.system('bash ' + freerun_path + ' fslregister --s ' + Template + ' --mov ' + 
    Images_path + srcSuj + ' --reg ' + Images_path + srcSuj[:-4] + 'to' + Template + '.dat')
    
#Initialize the command of labels to merge into an annot file    
labels_command = dict()
for hemisphere in hemispheres:
    labels_command[hemisphere] = ' '


if not os.path.isfile(Freesurfer_dir + Template + '/label/' + 'lh.' + Parcellation_name) and not os.path.isfile(Freesurfer_dir + Template + '/label/' + 'rh.' + Parcellation_name) or Overwrite:
    #Initialize and fill wm and surface ColorLUT txt files
    ColorLUT = open(Images_path + Parcellation_name[:-6] + 'ColorLUT.txt','w')
    ColorLUT.write('#$Id: ' + Parcellation_name[:-6] + 'ColorLUT.txt,v 1.70.2.7 ' + datetime.today().strftime('%Y/%m/%d %H:%M:%S') +  ' nicks Exp $' + ' \n')
    ColorLUT.write('\n')
    ColorLUT.write('#No. Label Name:                        R   G   B   A \n')
    ColorLUT.close()
    
    wmColorLUT = open(Images_path + 'wm' + Parcellation_name[:-6] + 'ColorLUT.txt','w')
    wmColorLUT.write('#$Id: ' + 'wm' + Parcellation_name[:-6] + 'ColorLUT.txt' + ',v 1.70.2.7 ' + datetime.today().strftime('%Y/%m/%d %H:%M:%S') +  ' nicks Exp $' + ' \n')
    wmColorLUT.write('\n')
    wmColorLUT.write('#No. Label Name:                        R   G   B   A \n')
    wmColorLUT.close()
    
    for Mask_name in Mask_names:
        
        vector = (np.random.rand(3)*100).astype(int)
        ColorLUT = open(Images_path + Parcellation_name[:-6] + 'ColorLUT.txt','a')
        ColorLUT.write( str(Mask_names.index(Mask_name) + 1) + '  ' + Mask_name[:-4] + (' ' * (37 - len(Mask_name[:-4]))) + str(vector[0]) + '  ' + str(vector[1]) + '  ' + str(vector[2]) + '  0\n')
        ColorLUT.close()
        
    for hemisphere in hemispheres:
        for Mask_name in Mask_names: 
            if hemisphere == 'lh' and (Mask_names.index(Mask_name) + 1)<10:   prfx = '300'
            elif hemisphere == 'lh' and (Mask_names.index(Mask_name) + 1)>=10:   prfx = '30'    
            elif hemisphere == 'rh' and (Mask_names.index(Mask_name) + 1)<10:   prfx = '400'
            elif hemisphere == 'rh' and (Mask_names.index(Mask_name) + 1)>=10:   prfx = '40'    

            vector = (np.random.rand(3)*100).astype(int)
            wmColorLUT = open(Images_path + 'wm' + Parcellation_name[:-6] + 'ColorLUT.txt','a')
            wmColorLUT.write( prfx + str(Mask_names.index(Mask_name) + 1) + '  ' + hemisphere + '_' + Mask_name[:-4] + '_wm' + (' ' * (28 - len(Mask_name[:-4]))) + str(vector[0]) + '  ' + str(vector[1]) + '  ' + str(vector[2]) + '  0\n')
            wmColorLUT.close()

    
    #Goes through each Mask to build them as labels into a template surface    
    for Mask_name in Mask_names:
        
        print ("Working on " + Mask_name)
        
        #Check the adjustment of the ROI to the template space
        print ("    Let's see...")
        os.system('bash ' + freerun_path +' tkmedit ' + Template + ' T1.mgz -overlay ' + 
            Images_path + Mask_name + ' -overlay-reg ' + Images_path + srcSuj[:-4] + 
            'to' + Template + '.dat -fthresh 0.5 -surface lh.white -aux-surface rh.white')
        
        #Adjust the ROI to Template space
        print ("    Adjusting ROI")
        os.system('bash ' + freerun_path + ' mri_vol2vol --reg ' + Images_path + srcSuj[:-4] + 
            'to' + Template + '.dat --mov ' + Images_path + Mask_name + ' --fstarg --o ' +
            Images_path + Template + '_' + Mask_name)
        
        #Transform ROI into a surface and make a label
        for hemisphere in hemispheres:
            
            if os.path.isfile(Freesurfer_dir + Template + '/label/' + hemisphere + '.' + Template + '_' + Mask_name[:-4] + '.label') or Overwrite:
                print ("    Ignoring " + hemisphere + ' ' + Mask_name + ': Already segmented')
            
            else: 
                print ("    Loading " + hemisphere + ' label')
                os.system('bash ' + freerun_path + ' mri_vol2surf --src ' + Images_path + 
                    Template + '_' + Mask_name + ' --regheader ' + Template + ' --projfrac 0.5 --hemi ' + 
                    hemisphere + ' --out ' + Images_path +  hemisphere + '_' + Template + '_' + Mask_name[:-4] + '.mgh')
            
                os.system('bash ' + freerun_path + ' mri_cor2label --i ' + Images_path +  
                    hemisphere + '_' + Template + '_' + Mask_name[:-4] + '.mgh --surf '  +  
                    Template + ' ' + hemisphere + ' --id 1 --l ' + Images_path +  hemisphere + 
                    '.' + Template + '_' + Mask_name[:-4] + '.label')
                    
                shutil.copy(Images_path +  hemisphere + '.' + Template + '_' + Mask_name[:-4] + '.label', 
                    Freesurfer_dir + Template + '/label/' + hemisphere + '.' + Template + '_' + Mask_name[:-4] + '.label')
                    
                os.system('bash ' + freerun_path + ' tksurfer -label ' + hemisphere + '.' + Template + '_' + 
                    Mask_name[:-4] + ' ' + Template + ' ' + hemisphere + ' inflated')
                    
                shutil.copy(Freesurfer_dir + Template + '/label/' + hemisphere + '.' + Template + '_' + Mask_name[:-4] + '.label', 
                    Images_path +  hemisphere + '.' + Template + '_' + Mask_name[:-4] + '_corrected.label')
                    
            labels_command[hemisphere] = labels_command[hemisphere] + '--l ' + Freesurfer_dir + Template + '/label/' + hemisphere + '.' + Template + '_' + Mask_name[:-4] + '.label '
        
        #Check the labels or finish your work
        scape = [0]
        while scape[0] == 0:
            root = tk.Tk()
            root.config(width=550, height=120)
            root.title("Let's exploit your insecurities; Are you sure about your work?")
            
            #Lh Button
            boton = tk.Button(root, text=" Lh  ", font='arial 9 bold', command = lambda:repeat_lh(), background='orange')
            boton.place(x=60, y=10)
            label = tk.Label(text = 'Show me left label')
            label.config(font=('Arial', 9, 'bold'))
            label.place(x=120, y=15)
            
            #Rh Button
            boton = tk.Button(root, text=" Rh  ", font='arial 9 bold', command = lambda:repeat_rh(), background='orange')
            boton.place(x=285, y=10)
            label = tk.Label(text = 'Show me right label')
            label.config(font=('Arial', 9, 'bold'))
            label.place(x=345, y=15)
            
            #Continue Button
            boton = tk.Button(root, text="Yeah", font='arial 9 bold', command = lambda: Finish(), background='green')
            boton.place(x=60, y=80)
            label = tk.Label(text = 'Yes, my work is sacred')
            label.config(font=('Arial', 9, 'bold'))
            label.place(x=120, y=85)
            
            root.mainloop()
        
    #Transform Labels into a surface and make a label
    for hemisphere in hemispheres:    
        os.system('bash ' + freerun_path + ' mris_label2annot --s ' + Template + 
            ' --h ' + hemisphere + ' --ctab ' + Images_path + Parcellation_name[:-6] + 'ColorLUT.txt --a ' + 
            Parcellation_name[:-6] + labels_command[hemisphere] + '--nhits nhits.mgh')
   
#Estimate the time of execution
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
