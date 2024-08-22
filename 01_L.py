import os
import h5py
import numpy as np
import shutil
from scipy.interpolate import interp1d

green_folder_path = 'D:/11053022/20231127/Hierarchical/0410/green_mat/'
light_folder_path = 'D:/11053022/20231127/Hierarchical/0410/light_mat/'
reference_mat_folder = 'D:/11053022/20231127/Hierarchical/0410/ref_mat'
raw_mat_folder = 'D:/11053022/20231127/Hierarchical/0410/raw_mat'
depth_folder = 'D:/11053022/20231127/Hierarchical/0410/raw_depth/'
output_folder = 'D:/11053022/20231127/Hierarchical/0410/'  

output_file = os.path.join(output_folder, 'g_minus_l_depth.txt')

# 光譜範圍（400到700波長有31個）
wave_lengths = np.linspace(400, 700, 31)
# 取波長500
wave_length_500_index = np.argmin(np.abs(wave_lengths - 500))

# 估計深度
def estimate_depth(diff, max_diff):
    if diff == max_diff:
        return 20
    else:
        return 10 + 10 * (diff / max_diff)

# 計算差異和深度
def compute_difference_and_depth(folder_path_green, folder_path_light):
    differences = []
    depths = []
    for green_file_name in os.listdir(folder_path_green):
        if green_file_name.endswith('.mat'):
            light_file_name = green_file_name.replace('G-', 'O-')
        
            green_file_path = os.path.join(folder_path_green, green_file_name)
            with h5py.File(green_file_path, 'r') as green_file:
                green_data = green_file['cube'][:]
            light_file_path = os.path.join(folder_path_light, light_file_name)
            with h5py.File(light_file_path, 'r') as light_file:
                light_data = light_file['cube'][:]

            green_max_value = np.max(green_data[wave_length_500_index])
            light_max_value = np.max(light_data[wave_length_500_index])

            diff = abs(green_max_value - light_max_value)
            differences.append(diff)

    if differences:
        max_diff = max(differences)
        for diff in differences:
            depths.append(estimate_depth(diff, max_diff))
    return differences, depths

#  green_folder_path 和 light_folder_path 的深度
print("Calculating differences and depths for green and light folder images...")
differences, depths = compute_difference_and_depth(green_folder_path, light_folder_path)
interp_func = interp1d(differences, depths, kind='linear', bounds_error=False, fill_value='extrapolate')


def create_depth_folders(base_path, depth):
    depth_folder = os.path.join(base_path, f'depth_{int(depth)}')
    os.makedirs(depth_folder, exist_ok=True)
    return depth_folder
if not differences or not depths:
    print("No differences or depths calculated. Please check the input files in green and light folders.")
else:
    print("Differences:",[diff for diff in differences])
    print("Depths:", [int(depth) for depth in depths])
    print("Creating interpolation function...")
    interp_func = interp1d(differences, depths, kind='linear', bounds_error=False, fill_value='extrapolate')


print("Processing reference_mat_folder and raw_mat_folder images...")
processed_count = 0

with open(output_file, 'w') as f_out:
    for file_name in os.listdir(reference_mat_folder):
        if file_name.endswith('.mat'):
            base_name = os.path.splitext(file_name)[0] 
            jpeg_name = base_name + '.jpeg'  

            reference_mat_path = os.path.join(reference_mat_folder, file_name)
            raw_mat_path = os.path.join(raw_mat_folder, file_name)
            
            with h5py.File(reference_mat_path, 'r') as ref_mat_file:
                ref_mat_data = ref_mat_file['cube'][:]
            with h5py.File(raw_mat_path, 'r') as raw_mat_file:
                raw_mat_data = raw_mat_file['cube'][:]
            
            ref_mat_max_value = np.max(ref_mat_data[wave_length_500_index])
            raw_mat_max_value = np.max(raw_mat_data[wave_length_500_index])

            diff = abs(ref_mat_max_value - raw_mat_max_value)
            estimated_depth = interp_func(diff)

            ref_mat_depth_folder = create_depth_folders(os.path.join(output_folder, 'raw_mat_depth'), estimated_depth)
            raw_mat_depth_folder = create_depth_folders(os.path.join(output_folder, 'ref_mat_depth'), estimated_depth)
            
            shutil.copy(reference_mat_path, ref_mat_depth_folder)
            shutil.copy(raw_mat_path, raw_mat_depth_folder)

            jpeg_file_path = os.path.join(depth_folder, jpeg_name)
            if os.path.exists(jpeg_file_path):
                new_depth_folder = create_depth_folders(os.path.join(output_folder, 'depth'), estimated_depth)
                shutil.copy(jpeg_file_path, new_depth_folder)  

            f_out.write(f'{file_name}: 深度 = {estimated_depth:.0f} 公尺\n')
            processed_count += 1
            print(f"Processed {processed_count}/{len(os.listdir(reference_mat_folder))} files")
