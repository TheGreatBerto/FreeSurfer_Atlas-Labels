# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 12:55:15 2022

@author: The Great Berto
"""
#Advice!!!! in the inflated image, close the image in File->Quit, if you close the windows instead the script will break


import os
from time import time
import pandas as pd
import Tkinter as tk
def Set_Value(Data, index, value):
    Data[index] = value
    root.destroy()  
def Retry():
    root.destroy()    
def Retry_hem(hem, value):
    hem[0] = value
    root.destroy()

    

#Estimate the time of execution
initial_time = time()

#Personalize your PATHS: Enter the Freesurfer Subject and Output folder paths, freerun.sh,
    #Atlases to wrap, proyect code and template where the atlases were segmented
Freesurfer_dir = '/usr/local/freesurfer/subjects/'
Output_dir = '/home/neuroimage/fsl/Quality/'
freerun_path = '/home/neuroimage/fsl/FreeSurfer/freerun.sh'
hemispheres = ['lh', 'rh']
proyect_code = 'F'

#Create output dir if not exist
if not os.path.isdir(Output_dir): 
    os.mkdir(Output_dir)

#list your directories
content = os.listdir(Freesurfer_dir)
directories = []
for item in content:
    if item.startswith(proyect_code): directories.append(item)

#Create the QualityControl data
hem = pd.DataFrame()
QualityControl = pd.DataFrame()
QualityControl['Subjects'] = directories
QualityControl['MRI_Q'] = 0
QualityControl['FS_seg'] = 0
QualityControl['Inflated_Q'] = 0
QualityControl['Valid'] = 1

#Goes through each subject showing his image to be evaluated and clasifying his validity
for d in range(len(directories)):
    print('Evaluating subject ' + directories[d])
    #Quality check of raw T1
    while (QualityControl['MRI_Q'][d] == 0):
        os.system('bash ' + freerun_path + ' freeview -v ' + Freesurfer_dir + directories[d] + 
        '/mri/rawavg.mgz')
        root = tk.Tk()
        root.config(width=380, height=200)
        root.title("Quality of the raw MRI")
        #Great Button
        boton = tk.Button(root, text="Great", font='arial 9 bold', command = lambda:Set_Value(QualityControl['MRI_Q'], d, 1), background='green')
        boton.place(x=20, y=10)
        label = tk.Label(text = 'Without visible artifacts')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=15)
        #Good Button
        boton = tk.Button(root, text=" Good", font='arial 9 bold', command = lambda:Set_Value(QualityControl['MRI_Q'], d, 2), background='yellow')
        boton.place(x=20, y=45)
        label = tk.Label(text = 'Some artifacts')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=50)
        #Bad Button
        boton = tk.Button(root, text=" Bad  ", font='arial 9 bold', command = lambda:Set_Value(QualityControl['MRI_Q'], d, 3), background='orange')
        boton.place(x=20, y=80)
        label = tk.Label(text = 'Some artifacts and/or slightly blurred image')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=85)
        #Awful Button
        boton = tk.Button(root, text="Awful", font='arial 9 bold', command = lambda:Set_Value(QualityControl['MRI_Q'], d, 4), background='red')
        boton.place(x=20, y=115)
        label = tk.Label(text = 'Many artifacts or very blurred image')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=120)
        #Retry Button
        boton = tk.Button(root, text="Retry", command = lambda:Retry())
        boton.place(x=160, y=150)        
        root.mainloop()
    #Quality check of FreeSurfer Segmentation  
    while (QualityControl['FS_seg'][d] == 0):
        os.system('bash ' + freerun_path + ' tkmedit ' + directories[d] + 
        ' brainmask.mgz lh.white -aux-surface T1.mgz -aux-surface rh.white')
        root = tk.Tk()
        root.config(width=380, height=200)
        root.title("Quality of FreeSurfer Segmentation ")
        #Great Button
        boton = tk.Button(root, text="Great", font='arial 9 bold', command = lambda:Set_Value(QualityControl['FS_seg'], d, 1), background='green')
        boton.place(x=20, y=10)
        label = tk.Label(text = 'Perfect Segmentation')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=15)
        #Good Button
        boton = tk.Button(root, text=" Good", font='arial 9 bold', command = lambda:Set_Value(QualityControl['FS_seg'], d, 2), background='yellow')
        boton.place(x=20, y=45)
        label = tk.Label(text = 'Little errors in segmentation')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=50)
        #Bad Button
        boton = tk.Button(root, text=" Bad  ", font='arial 9 bold', command = lambda:Set_Value(QualityControl['FS_seg'], d, 3), background='orange')
        boton.place(x=20, y=80)
        label = tk.Label(text = 'A lot of errors in segmentation')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=85)
        #Awful Button
        boton = tk.Button(root, text="Awful", font='arial 9 bold', command = lambda:Set_Value(QualityControl['FS_seg'], d, 4), background='red')
        boton.place(x=20, y=115)
        label = tk.Label(text = "Grey and White matter don't differ")
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=120)
        #Retry Button
        boton = tk.Button(root, text="Retry", command = lambda:Retry())
        boton.place(x=160, y=150)        
        root.mainloop()
    #Quality check of FreeSurfer inflated image
    hem['now'] = ['lhrh']
    while (QualityControl['Inflated_Q'][d] == 0):
        if hem['now'][0] == 'lhrh':
            os.system('bash ' + freerun_path + ' tksurfer ' + directories[d] + 
            ' lh pial -curv')
            os.system('bash ' + freerun_path + ' tksurfer ' + directories[d] + 
            ' rh pial -curv')
        elif hem['now'][0] == 'lh':
            os.system('bash ' + freerun_path + ' tksurfer ' + directories[d] + 
            ' lh pial -curv')
        elif hem['now'][0] == 'rh':
            os.system('bash ' + freerun_path + ' tksurfer ' + directories[d] + 
            ' rh pial -curv')
        root = tk.Tk()
        root.config(width=380, height=200)
        root.title("Quality of inflated image")
        #Great Button
        boton = tk.Button(root, text="Great", font='arial 9 bold', command = lambda:Set_Value(QualityControl['Inflated_Q'], d, 1), background='green')
        boton.place(x=20, y=10)
        label = tk.Label(text = 'Homogeneous surface')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=15)
        #Good Button
        boton = tk.Button(root, text=" Good", font='arial 9 bold', command = lambda:Set_Value(QualityControl['Inflated_Q'], d, 2), background='yellow')
        boton.place(x=20, y=45)
        label = tk.Label(text = 'Small peaks and bright spots')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=50)
        #Bad Button
        boton = tk.Button(root, text=" Bad  ", font='arial 9 bold', command = lambda:Set_Value(QualityControl['Inflated_Q'], d, 3), background='orange')
        boton.place(x=20, y=80)
        label = tk.Label(text = 'Many peaks and bright spots')
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=85)
        #Awful Button
        boton = tk.Button(root, text="Awful", font='arial 9 bold', command = lambda:Set_Value(QualityControl['Inflated_Q'], d, 4), background='red')
        boton.place(x=20, y=115)
        label = tk.Label(text = "Loss of shape in the brain")
        label.config(font=('Arial', 9, 'bold'))
        label.place(x=100, y=120)
        #Retry Buttons
        boton = tk.Button(root, text="Retry Lh", command = lambda:Retry_hem(hem['now'], 'lh'))
        boton.place(x=50, y=150)
        boton = tk.Button(root, text="Retry Both", command = lambda:Retry_hem(hem['now'], 'lhrh'))
        boton.place(x=130, y=150)    
        boton = tk.Button(root, text="Retry Rh", command = lambda:Retry_hem(hem['now'], 'rh'))
        boton.place(x=220, y=150)                
        root.mainloop()
    
    if QualityControl['Inflated_Q'][d]==4 or QualityControl['FS_seg'][d]==4 or QualityControl['MRI_Q'][d]==4 or QualityControl['Inflated_Q'][d]+QualityControl['FS_seg'][d]+QualityControl['MRI_Q'][d]>6:
        QualityControl['Valid'][d]= 0
        
QualityControl.to_excel(Output_dir + proyect_code + '_QualityControl.xlsx')

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
