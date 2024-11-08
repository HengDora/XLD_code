import os
from tqdm import tqdm

def rename_files(directory, prefix):
    """重命名目录下的所有文件，加上前缀"""
    files = os.listdir(directory)
    for filename in tqdm(files, desc=f"Processing files in {directory}"):
        if filename.startswith(prefix):
            continue  # 如果文件已经有相应的前缀，则跳过
        os.rename(
            os.path.join(directory, filename),
            os.path.join(directory, f"{prefix}_{filename}")
        )

def rename_scenes(directory):
    # test_pic
    test_pic_dir = os.path.join(directory, "test_pic")
    if os.path.exists(test_pic_dir):
        test_sub_dirs = [os.path.join(test_pic_dir, d) for d in os.listdir(test_pic_dir) if os.path.isdir(os.path.join(test_pic_dir, d))]
        for test_sub_dir in test_sub_dirs:
            rename_files(test_sub_dir, "eval")

    # train_pic
    train_pic_dir = os.path.join(directory, "train_pic")
    if os.path.exists(train_pic_dir):
        # 直接对 train_pic 下的文件进行重命名，而不是子目录
        rename_files(train_pic_dir, "train")

if __name__ == '__main__':
    directories = [
        "data/carla_pic_0603_Town01",
        "data/carla_pic_0603_Town02",
        "data/carla_pic_0603_Town03",
        "data/carla_pic_0603_Town04",
        "data/carla_pic_0603_Town05",
        "data/carla_pic_0603_Town10"
    ]

    for directory in directories:
        rename_scenes(directory)
