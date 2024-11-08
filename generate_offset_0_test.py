import os
import json
import shutil
import numpy as np
from tqdm import tqdm  # 引入 tqdm 库

def generate_test(scene_path):
    # 确保 test_pic 和 offset_left_0m 目录存在
    test_pic_path = os.path.join(scene_path, "test_pic")
    offset_left_0m_path = os.path.join(test_pic_path, "offset_left_0m")

    if not os.path.exists(test_pic_path):
        os.mkdir(test_pic_path)
    
    if not os.path.exists(offset_left_0m_path):
        os.mkdir(offset_left_0m_path)
    
    # 即使 offset_left_0m 已经存在，也继续进行文件复制
    # 定义开始、结束时间步和间隔
    start_timestep, end_timestep, gap = 0, 150, 5

    # 初始化 tqdm 进度条
    total_files = (end_timestep - start_timestep) // gap * 2  # 每个时间步有两个文件
    with tqdm(total=total_files, desc=f"Copying files for {scene_path}", unit="file") as pbar:
        # 遍历时间步，尝试复制文件
        for i, t in enumerate(range(start_timestep, end_timestep, gap)):
            src_json_file = os.path.join(scene_path, "train_pic", f"camera_extrinsics_{t:06d}.json")
            src_png_file = os.path.join(scene_path, "train_pic", f"camera0_{t:05d}.png")

            dst_json_file = os.path.join(offset_left_0m_path, f"camera_extrinsics_{i:06d}.json")
            dst_png_file = os.path.join(offset_left_0m_path, f"camera0_{i:05d}.png")

            # 检查源文件是否存在
            if os.path.exists(src_json_file):
                shutil.copyfile(src_json_file, dst_json_file)
                pbar.update(1)  # 更新进度条
            else:
                print(f"Warning: Source JSON file {src_json_file} does not exist.")

            if os.path.exists(src_png_file):
                shutil.copyfile(src_png_file, dst_png_file)
                pbar.update(1)  # 更新进度条
            else:
                print(f"Warning: Source PNG file {src_png_file} does not exist.")

# 调用函数生成测试数据
generate_test("data/carla_pic_0603_Town01")
generate_test("data/carla_pic_0603_Town02")
generate_test("data/carla_pic_0603_Town03")
generate_test("data/carla_pic_0603_Town04")
generate_test("data/carla_pic_0603_Town05")
generate_test("data/carla_pic_0603_Town10")
