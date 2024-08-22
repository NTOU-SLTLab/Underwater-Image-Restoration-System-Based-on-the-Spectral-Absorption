import os
import numpy as np
import h5py
import matplotlib.pyplot as plt
from imageio import imread

base_path = 'D:/11053022/20231127/Hierarchical/0410/'
c_values_folder_path = os.path.join(base_path, 'c_values/')

if not os.path.exists(c_values_folder_path):
    os.makedirs(c_values_folder_path)

wave_lengths = np.linspace(400, 700, 31)

depth_folders = [f for f in os.listdir(os.path.join(base_path, 'raw_mat_depth')) if f.startswith('depth_')]
for depth_folder in depth_folders:
    L = int(depth_folder.split('_')[-1])

    green_folder_path = os.path.join(base_path, f'raw_mat_depth/{depth_folder}/')
    light_folder_path = os.path.join(base_path, f'ref_mat_depth/{depth_folder}/')
    depth_green_folder_path = os.path.join(base_path, f'depth/{depth_folder}')
    output_file_name = f'{L}_c_value.mat'

    c_values_lists = [[] for _ in range(len(wave_lengths))]

    depth_green_images = {os.path.splitext(f)[0]: imread(os.path.join(depth_green_folder_path, f))
                          for f in os.listdir(depth_green_folder_path) if f.endswith('.jpeg')}

    for light_file, green_file in zip(sorted(os.listdir(light_folder_path)), sorted(os.listdir(green_folder_path))):
        light_path = os.path.join(light_folder_path, light_file)
        green_path = os.path.join(green_folder_path, green_file)

        file_basename = os.path.splitext(light_file)[0]

        with h5py.File(light_path, 'r') as file:
            light_data = np.array(file['cube'])
        with h5py.File(green_path, 'r') as file:
            green_data = np.array(file['cube'])

        depth_green_image = depth_green_images[file_basename]
        if depth_green_image.ndim == 3:
            depth = np.mean(depth_green_image, axis=2)
        else:
            depth = depth_green_image
        depth = 255 - depth
        depth_values = (depth / 255) * (5 - 0.1) + 0.1

        for i, wl in enumerate(wave_lengths):
            valid_mask = (green_data[i] > 0) & (light_data[i] > 0)
            depth_values = np.resize(depth, green_data[i].shape)[valid_mask]
            green_values = green_data[i][valid_mask]
            light_values = light_data[i][valid_mask]
            c_values = -np.log(light_values / green_values) / (L + depth_values)
            c_values_lists[i].extend(c_values)

    c_values_center = []
    for i, c_values_wl in enumerate(c_values_lists):
        if len(c_values_wl) > 0:
            median_c_value = np.median(c_values_wl)
            weights = 1.0 / (np.abs(c_values_wl - median_c_value) + 1e-6)
            centroid = np.average(c_values_wl, weights=weights)
        else:
            centroid = np.nan
        c_values_center.append((wave_lengths[i], centroid))

    output_file_path = os.path.join(c_values_folder_path, output_file_name)
    with h5py.File(output_file_path, 'w') as file:
        file.create_dataset('c_values_center', data=np.array(c_values_center, dtype=float))

    plot_file_name = f'c_values_center_plot_{L}.png'
    wave_lengths_array, c_values_array = zip(*c_values_center)
    plt.figure(figsize=(10, 6))
    plt.plot(wave_lengths_array, c_values_array, marker='o')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('C values Centroid')
    plt.title(f'C Values Centroid / Wavelengths at Depth {L}')
    plt.grid(True)
    plot_file_path = os.path.join(c_values_folder_path, plot_file_name)
    plt.savefig(plot_file_path)
    plt.close()
