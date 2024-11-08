import enum
import os
import numpy as np
import json
from scipy.spatial.transform import Rotation as R
from tqdm import tqdm

ORIGINAL_SIZE = [[1280, 1920], [1280, 1920], [1280, 1920], [884, 1920], [884, 1920]]

def pose_unreal2opencv(c2w_mat):
    translation = c2w_mat[:3, 3]
    rot = R.from_matrix(c2w_mat[:3, :3])
    rot_vec = rot.as_rotvec()

    rot_vec_new = rot_vec[[1, 2, 0]]
    rot_vec_new[0] *= -1
    rot_vec_new[2] *= -1

    rot = R.from_rotvec(rot_vec_new)
    
    translation_new = translation[[1, 2, 0]]
    translation_new[1] *= -1

    c2w_mat = np.eye(4)
    c2w_mat[:3, :3] = rot.as_matrix()
    c2w_mat[:3, 3] = translation_new

    rot = np.eye(4)
    rot[1, 1] = -1
    rot[2, 2] = -1
    c2w_mat = c2w_mat @ rot
    return c2w_mat

def load_calibrations(scene_path, data_set, start_timestep, end_timestep, num_cams=1, camera_list=[0]):
    """
    Load the camera intrinsics, extrinsics, timestamps, etc.
    Compute the camera-to-world matrices, ego-to-world matrices, etc.
    """
    _intrinsics = []
    cam_to_egos = []

    # Loading intrinsics and extrinsics with progress bar
    for i in tqdm(range(num_cams), desc="Loading camera intrinsics and extrinsics"):
        # Load camera intrinsics
        intrinsic = np.loadtxt(
            os.path.join(scene_path, "intrinsics", f"{i}.txt")
        )
        fx, fy, cx, cy = intrinsic[0], intrinsic[1], intrinsic[2], intrinsic[3]
        intrinsic = np.array([[fx, 0, cx, 0], [0, fy, cy, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        _intrinsics.append([fx, fy, cx, cy])

        # Load camera extrinsics
        cam_to_ego = np.loadtxt(
            os.path.join(scene_path, "extrinsics", f"{i}.txt")
        )
        cam_to_egos.append(cam_to_ego)

    cam_to_worlds = []
    intrinsics, cam_ids = [], []
    timestamps, timesteps = [], []
    prefix = "train" if "train" in data_set else "eval"

    # Processing time steps with progress bar
    for t in tqdm(range(start_timestep, end_timestep), desc="Processing time steps"):
        with open(os.path.join(scene_path, data_set, f"{prefix}_camera_extrinsics_{t:06d}.json"), 'r') as file:
            ego_to_world_current = np.array(json.load(file)['transform_matrix'])
        
        for cam_id in camera_list:
            cam_ids.append(cam_id)

            cam_to_ego = cam_to_egos[cam_id]
            cam2world = pose_unreal2opencv(ego_to_world_current @ cam_to_ego)
            cam_to_worlds.append(cam2world)

            intrinsics.append(_intrinsics[cam_id])
            timestamps.append(t - start_timestep)
            timesteps.append(t - start_timestep)

    return intrinsics, cam_to_worlds, cam_ids

def generate_json_file(scene_path, num_cams, camera_list, offset_meters=0):
    json_content = {"camera_model": "OPENCV", "frames": []}

    # Generating JSON file with progress bar
    intrinsics, cam_to_worlds, cam_ids = load_calibrations(scene_path, "train_pic", 5, 155, num_cams=num_cams, camera_list=camera_list)
    for i, (intrinsic, c2w, cam_id) in tqdm(enumerate(zip(intrinsics, cam_to_worlds, cam_ids)), desc="Generating training frames", total=len(cam_to_worlds)):
        frame = {
            "file_path": f"../{scene_path}/train_pic/train_camera{cam_id}_{(i // num_cams + 5):05d}.png",
            "transform_matrix": c2w.tolist(),
            "fl_x": intrinsic[0],
            "fl_y": intrinsic[1],
            "cx": intrinsic[2],
            "cy": intrinsic[3],
            "h": ORIGINAL_SIZE[cam_id][0],
            "w": ORIGINAL_SIZE[cam_id][1],
        }
        json_content['frames'].append(frame)

    test_num_cams, test_camera_list = 1, [0]
    intrinsics, cam_to_worlds, cam_ids = load_calibrations(scene_path, f"test_pic/offset_left_{offset_meters}m", 2, 30, num_cams=test_num_cams, camera_list=test_camera_list)
    for i, (intrinsic, c2w, cam_id) in tqdm(enumerate(zip(intrinsics, cam_to_worlds, cam_ids)), desc="Generating testing frames", total=len(cam_to_worlds)):
        if i // test_num_cams == 30:
            break
        frame = {
            "file_path": f"../{scene_path}/test_pic/offset_left_{offset_meters}m/eval_camera{cam_id}_{(i // test_num_cams + 2):05d}.png",
            "transform_matrix": c2w.tolist(),
            "fl_x": intrinsic[0],
            "fl_y": intrinsic[1],
            "cx": intrinsic[2],
            "cy": intrinsic[3],
            "h": ORIGINAL_SIZE[cam_id][0],
            "w": ORIGINAL_SIZE[cam_id][1],
        }
        json_content['frames'].append(frame)

    json_path = scene_path.split("/")[-1] + f"_cam{num_cams}"
    os.makedirs(json_path, exist_ok=True)
    with open(os.path.join(json_path, "transforms.json"), "w") as f:
        f.write(json.dumps(json_content, indent=4))

# Generate JSON files with progress bar
for town in ["Town01", "Town02", "Town03", "Town04", "Town05", "Town10"]:
    generate_json_file(scene_path=f"data/carla_pic_0603_{town}", num_cams=1, camera_list=[0], offset_meters=1)
    generate_json_file(scene_path=f"data/carla_pic_0603_{town}", num_cams=3, camera_list=[1, 0, 2], offset_meters=1)
