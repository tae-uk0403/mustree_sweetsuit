from .functions import get_world_xyz_array
from .functions import measure_3D_distance2
from .class_dict import measure_dict


def measure_keypoint_distances(
    task_folder_path,
    model_name,
    gender,
    model_position_name,
    keypoints,
    result_dict,
    depth_file,
):
    """측정 대상의 3D 거리 계산."""
    world_xyz_array = get_world_xyz_array(
        str(task_folder_path / depth_file), rgb_h=1920
    )
    result_dict = measure_3D_distance2(
        task_folder_path,
        model_name,
        gender,
        result_dict,
        measure_dict[model_position_name],
        keypoints,
        world_xyz_array,
        rgb_depth_ratio=7.5,
    )
    return result_dict
