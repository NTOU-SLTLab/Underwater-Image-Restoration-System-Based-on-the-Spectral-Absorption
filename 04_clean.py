import os
import cv2 as cv
import numpy as np
import h5py
from os.path import basename, join, splitext

def projectToRGB(hsIm, cameraResponse):
    C, H, W = hsIm.shape
    rgbIm_reshaped = np.dot(hsIm.reshape(C, H*W).T, cameraResponse).reshape(H, W, 3)
    return rgbIm_reshaped

def savePNG(image, path):
    cv.imwrite(path, cv.cvtColor((image * 255).astype(np.uint8), cv.COLOR_RGB2BGR))

base_folder = "D:/11053022/20231127/Hierarchical/0410"
filtersPath = "D:/11053022/20231127/Hierarchical/Hierarchical-Regression-Network-for-Spectral-Reconstruction-from-RGB-Images-master/official scoring code/resources/cie_1964_w_gain.npz"
filters = np.load(filtersPath)['filters']
BIT_8 = 256

depth_folders = os.listdir(join(base_folder, 'attenuation'))
for depth_folder in depth_folders:
    if depth_folder.startswith("depth"):
        compensate_folder = join(base_folder, "attenuation", depth_folder)
        save_folder = join(base_folder, "attenuation_img", depth_folder)
        
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        for file in os.listdir(compensate_folder):
            if file.endswith(".mat"):
                filePath = join(compensate_folder, file)
                with h5py.File(filePath, 'r') as f:
                    cube = np.array(f['corrected_cube'])
                rgbIm = np.true_divide(projectToRGB(cube, filters), BIT_8)

                fileName = splitext(basename(filePath))[0]
                path = join(save_folder, fileName + '.png')
                savePNG(rgbIm, path)