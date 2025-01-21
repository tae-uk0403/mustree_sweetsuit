import cv2

from .draw_keypoint_circle import draw_keypoint_circle
from .visualize_circum import visualize_result_2d, visualize_result
from ..measure.measure import measure_dict


def create_keypoint_images(
    task_folder_path, img_front_path, img_side_path, front_keys, side_keys
):
    """키포인트가 표시된 이미지를 생성 및 저장합니다."""
    draw_keypoint_circle(
        task_folder_path, img_front_path, front_keys, "front_key_result.png"
    )
    draw_keypoint_circle(
        task_folder_path, img_side_path, side_keys, "side_key_result.png"
    )


def visualize_measurement_results(
    task_folder_path, model_name, keypoints, result_dict, original_image_path
):
    """측정 결과를 이미지에 시각화."""
    image = cv2.imread(original_image_path)
    for measure_name, measure_points in measure_dict[model_name].items():
        detected_keypoints = [
            keypoints[measure_points[0] - 1],
            keypoints[measure_points[1] - 1],
        ]
        if measure_name == "leg":
            image = visualize_result_2d(
                task_folder_path, detected_keypoints, image, measure_name, result_dict
            )
        else:
            image = visualize_result(
                detected_keypoints, image, measure_name, result_dict
            )
    return image
