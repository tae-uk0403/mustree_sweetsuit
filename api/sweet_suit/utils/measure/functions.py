import numpy as np
import json
from pathlib import Path
from ..keypoint.fix_keypoint import fix_keypoint
from ..visualize.draw_keypoint_circle import draw_keypoint_circle
import json


def get_world_xyz_array(pointcloud_path, rgb_h):

    with open(pointcloud_path) as f:
        depth_json = json.load(f)
    depth_values = depth_json["Depth"]
    depth_w = 256
    depth_h = 192
    fl_x = depth_json["fl"]["x"]
    fl_y = depth_json["fl"]["y"]
    xyz_array = []
    k = 0
    for i in range(depth_h):
        for j in range(depth_w):
            z = depth_values[k]
            x = (j - 256 / 2) * z / (fl_x / 7.5)
            y = (i - 192 / 2) * z / (fl_y / 7.5)
            xyz_array.append([x, y, z])
            k += 1

    R_camera_to_world = np.array(
        [
            [
                depth_json["m00"],
                depth_json["m01"],
                depth_json["m02"],
                depth_json["m03"],
            ],
            [
                depth_json["m10"],
                depth_json["m11"],
                depth_json["m12"],
                depth_json["m13"],
            ],
            [
                depth_json["m20"],
                depth_json["m21"],
                depth_json["m22"],
                depth_json["m23"],
            ],
            [
                depth_json["m30"],
                depth_json["m31"],
                depth_json["m32"],
                depth_json["m33"],
            ],
        ]
    )

    R_camera_to_world = R_camera_to_world[0:3, 0:3]

    T_camera_to_world = np.array(
        [depth_json["Pos"]["x"], depth_json["Pos"]["y"], depth_json["Pos"]["z"]]
    )

    world_xyz = np.dot(xyz_array, R_camera_to_world) + T_camera_to_world

    world_xyz_array = world_xyz.reshape((192, 256, 3))
    world_xyz_array = np.rot90(world_xyz_array, k=-1)

    return world_xyz_array


def adjust_keypoints(task_folder_path, world_xyz_array, target_point_1, target_point_2):
    print("Original keypoints:", [target_point_1, target_point_2])
    target_point_1, target_point_2 = fix_keypoint(
        task_folder_path,
        world_xyz_array,
        target_point_1[1],
        [target_point_1[0], target_point_2[0]],
    )
    print("Adjusted keypoints:", [target_point_1, target_point_2])
    return target_point_1, target_point_2


def calculate_3d_length(world_xyz_array, target_point_1, target_point_2):
    length_3d = 0
    for i in range(target_point_1[0], target_point_2[0] - 1):
        try:
            pixel_length = (
                np.linalg.norm(
                    world_xyz_array[target_point_1[1], i]
                    - world_xyz_array[target_point_1[1], i + 1]
                )
                * 100
            )
            if pixel_length < 3:
                length_3d += pixel_length
        except IndexError:
            continue
    return length_3d


def apply_measurement_scaling(measure_3d_result_dict, measure_name):
    scaling_factors = {"chest": 1.427, "waist": 1.322, "pelvis": 1.322, "hips": 1.53}
    model_name_map = {
        "chest": "가슴",
        "waist": "허리",
        "pelvis": "골반",
        "hips": "엉덩이",
    }
    if measure_name in scaling_factors:
        measure_3d_result_dict[measure_name] *= scaling_factors[measure_name]
        json_model_name = model_name_map[measure_name]
    else:
        json_model_name = measure_name
    return json_model_name


def save_measurement_to_json(task_folder_path, json_model_name, measure_value):
    json_file_path = Path(task_folder_path) / "result_circum.json"
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        data[json_model_name] = round(measure_value, 0)
    except FileNotFoundError:
        data = {json_model_name: round(measure_value, 0)}

    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def measure_3D_distance2(
    task_folder_path,
    model_name,
    measure_3d_result_dict,
    measure_dict,
    detected_keypoints,
    world_xyz_array,
    rgb_depth_ratio,
    RGB_image,
):
    for measure_name, measure_points in measure_dict.items():
        target_point_1 = np.array(
            np.array(detected_keypoints[measure_points[0] - 1]) / rgb_depth_ratio,
            dtype=np.int64,
        )
        target_point_2 = np.array(
            np.array(detected_keypoints[measure_points[1] - 1]) / rgb_depth_ratio,
            dtype=np.int64,
        )

        if measure_name == "leg":
            target_point_1, target_point_2 = adjust_keypoints(
                task_folder_path, world_xyz_array, target_point_1, target_point_2
            )
            pixel_length = (
                np.linalg.norm(
                    world_xyz_array[target_point_1[1], target_point_1[0]]
                    - world_xyz_array[target_point_2[1], target_point_2[0]]
                )
                * 100
            )
            measure_3d_result_dict[measure_name] = pixel_length
            return measure_3d_result_dict, RGB_image

        # 3D 길이 계산
        target_point_1, target_point_2 = adjust_keypoints(
            task_folder_path, world_xyz_array, target_point_1, target_point_2
        )
        length_3d = calculate_3d_length(world_xyz_array, target_point_1, target_point_2)

        # 결과 저장
        if measure_name in measure_3d_result_dict:
            measure_3d_result_dict[measure_name] += length_3d
            json_model_name = apply_measurement_scaling(
                measure_3d_result_dict, measure_name
            )
            save_measurement_to_json(
                task_folder_path, json_model_name, measure_3d_result_dict[measure_name]
            )
        else:
            measure_3d_result_dict[measure_name] = length_3d

    return measure_3d_result_dict, RGB_image
