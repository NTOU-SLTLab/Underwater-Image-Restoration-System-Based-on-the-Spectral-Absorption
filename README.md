Hierarchical Regression Network for Spectral Reconstruction from RGB Images
https://github.com/zhaoyuzhi/Hierarchical-Regression-Network-for-Spectral-Reconstruction-from-RGB-Images

先用resize調整圖像尺寸

1.影像光譜重建：test1.py程式原始碼
python test1.py --val_path "D:/11053022/20231127/Hierarchical/0410/0417_ref_mat" --baseroot "D:/11053022/20231127/Hierarchical/0410/0417_ref"
使用Hierarchical Regression Network技術，將標準RGB影像轉換為高光譜數據。此技術通過四層層級回歸網路（HRNet），分別處理影像的低頻和高頻訊息，最終合併成一個高光譜影像，涵蓋31個不同波長的光譜通道。

2.水下影像水深估測：01_L.py
透過已知深度數據，利用波長500nm處的光譜強度差異進行水深估算。
輸出的資料夾為依據深度存的
raw_mat_depth
ref_mat_depth
depth

3.衰減係數計算：02_C.py
基於水深值和物體與相機之間距離計算衰減係數。結合原始光譜數據和水色還原後的光譜數據進行分析，使用加權平均法計算衰減係數。
輸出的資料夾為
c_values

4.光譜數據補償：03_wavelengths.py
光譜數據補償：對光譜數據進行調整，補償水深和物體與相機距離引起的光譜變化。
輸出的資料夾為
attenuation

5.輸出影像：04_clean.py
將補償後的光譜數據映射到RGB空間，利用基於CIE 1964標準色度的相機響應函數和數學算法進行轉換。考慮每個波長的光強度和色彩平衡，以生成真實反映原始水下環境的RGB影像。
輸出的資料夾為
attenuation_img


