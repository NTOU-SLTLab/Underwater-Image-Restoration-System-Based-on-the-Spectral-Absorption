import numpy as np
import os

base_folder_path = 'D:/11053022/20231127/Hierarchical/0410'
depth_data_path = os.path.join(base_folder_path, 'depths_data.npy')

# 加載 depths_data
depths_data = np.load(depth_data_path, allow_pickle=True)

# 檢查載入的對象
print("Loaded object type:", type(depths_data))
print("Loaded object content:", depths_data)
