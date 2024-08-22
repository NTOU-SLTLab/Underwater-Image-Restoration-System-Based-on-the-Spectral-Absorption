import os
import numpy as np
import h5py
from imageio import imread

base_folder_path = 'D:/11053022/20231127/Hierarchical/0410'

depth_folders = os.listdir(os.path.join(base_folder_path, 'raw_mat_depth'))
for depth_folder in depth_folders:
    L = int(depth_folder.split('_')[-1])
    green_folder_path = os.path.join(base_folder_path, f'raw_mat_depth/{depth_folder}')
    depth_image_folder_path = os.path.join(base_folder_path, f'depth/{depth_folder}')
    c_values_path = os.path.join(base_folder_path, f'c_values/{L}_c_value.mat')
    output_folder_path = os.path.join(base_folder_path, f'attenuation/depth_{L}')

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    with h5py.File(c_values_path, 'r') as file:
        c_values = np.array(file['c_values_center'])[:, 1]
    num_wavelengths = len(c_values)

    depth_images = {os.path.splitext(f)[0]: os.path.join(depth_image_folder_path, f)
                    for f in os.listdir(depth_image_folder_path) if f.endswith('.jpeg')}
    depth_values = {}
    for filename in os.listdir(green_folder_path):
        file_basename = os.path.splitext(filename)[0]
        if filename.endswith(".mat") and file_basename in depth_images:
            file_path = os.path.join(green_folder_path, filename)
            depth_image_path = depth_images[file_basename]

            with h5py.File(file_path, 'r') as file:
                data = np.array(file['cube'])
                attrs = {attr: file['cube'].attrs[attr] for attr in file['cube'].attrs}

            corrected_data = np.empty((data.shape[0], data.shape[2], data.shape[1]))
            for i in range(data.shape[0]):
                corrected_data[i] = np.fliplr(np.rot90(data[i], -1))

            depth_image = imread(depth_image_path)
            if depth_image.ndim == 3:
                depth = np.mean(depth_image, axis=2)
            else:
                depth = depth_image
            depth_inverted = 255 - depth
            depth_scaled = (depth_inverted / 255) * (5 - 0.1) + 0.1

            for i in range(num_wavelengths):
                c = c_values[i]
                F_corrected = corrected_data[i] * (np.exp(c * (L + depth_scaled)))
                corrected_data[i] = np.clip(F_corrected, 0, 1)

            output_file_path = os.path.join(output_folder_path, filename)
            with h5py.File(output_file_path, 'w') as file:
                dset = file.create_dataset('corrected_cube', data=corrected_data)
                for attr_name, attr_value in attrs.items():
                    dset.attrs[attr_name] = attr_value

depth_values_txt_path = os.path.join(base_folder_path, 'depth_values.txt')
with open(depth_values_txt_path, 'w') as file:
    for image_name, depths in depth_values.items():
        file.write(image_name + ':\n')
        for row in depths:
             file.write(' '.join(map(str, row)) + '\n')
        file.write('\n')


