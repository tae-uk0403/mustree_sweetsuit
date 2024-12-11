import cv2
import torch
import os
import torchvision.transforms as transforms
from .utils.keypoint import pose_hrnet
from .utils.keypoint.transforms import get_affine_transform, transform_preds
from .utils.measure.class_dict import measure_dict

# from .utils.inference import *
from .utils.measure.functions import get_world_xyz_array, measure_3D_distance2
from .utils.visualize.visualize_circum import visualize_result, visualize_result_2d
from .utils.keypoint.find_keypoint import find_keypoint2
from .utils.visualize.draw_keypoint_circle import draw_keypoint_circle

from pathlib import Path
import pandas as pd
from rembg import remove


import cv2
import json
from pathlib import Path


def run_sweet_suit2(task_folder_path, upper_or_lower, model_name, api_key):
    """
    전체 프로세스를 실행하여 배경 제거, 키포인트 탐지, 3D 거리 측정, 시각화 및 결과 저장.
    """
    front_model_name, side_model_name = (
        f"{model_name}_removed_front",
        f"{model_name}_removed_side",
    )
    img_file_front, img_file_side = (
        task_folder_path / "image_front.jpg",
        task_folder_path / "image_side.jpg",
    )
    rembg_img_front, rembg_img_side = (
        task_folder_path / "rembg_image_front.jpg",
        task_folder_path / "rembg_image_side.jpg",
    )

    # 배경 제거 후 이미지 저장
    remove_background(img_file_front, rembg_img_front)
    remove_background(img_file_side, rembg_img_side)

    # 키포인트 탐지
    front_keys = find_keypoints(
        task_folder_path,
        upper_or_lower,
        model_name,
        front_model_name,
        "rembg_image_front.jpg",
    )
    side_keys = find_keypoints(
        task_folder_path,
        upper_or_lower,
        model_name,
        side_model_name,
        "rembg_image_side.jpg",
    )

    # 키포인트 이미지 생성 (디버깅 용도)
    create_keypoint_images(
        task_folder_path, rembg_img_front, rembg_img_side, front_keys, side_keys
    )

    # 측정 준비
    measure_3d_result_dict = {}
    measure_3d_result_dict = measure_keypoint_distances(
        task_folder_path,
        model_name,
        side_model_name,
        side_keys,
        measure_3d_result_dict,
        api_key,
        "depth_side.json",
    )
    measure_3d_result_dict = measure_keypoint_distances(
        task_folder_path,
        model_name,
        front_model_name,
        front_keys,
        measure_3d_result_dict,
        api_key,
        "depth_front.json",
    )

    # 결과 시각화
    key_length_image = visualize_measurement_results(
        task_folder_path,
        front_model_name,
        front_keys,
        measure_3d_result_dict,
        img_file_front,
    )

    # 최종 이미지 저장
    final_img_path = task_folder_path / "key_measure_result.png"
    cv2.imwrite(str(final_img_path), key_length_image)

    return task_folder_path, final_img_path


def remove_background(input_path, output_path):
    """이미지의 배경을 제거하고 결과를 저장합니다."""
    with open(input_path, "rb") as i, open(output_path, "wb") as o:
        o.write(remove(i.read()))


def find_keypoints(
    task_folder_path, upper_or_lower, model_name, model_name_with_position, image_name
):
    """키포인트 탐지 함수 호출 및 결과 반환"""
    return find_keypoint2(
        task_folder_path,
        upper_or_lower,
        model_name,
        model_name_with_position,
        image_name,
    )


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


def measure_keypoint_distances(
    task_folder_path,
    model_name,
    model_position_name,
    keypoints,
    result_dict,
    api_key,
    depth_file,
):
    """측정 대상의 3D 거리 계산."""
    world_xyz_array = get_world_xyz_array(
        str(task_folder_path / depth_file), rgb_h=1920
    )
    result_dict, _ = measure_3D_distance2(
        task_folder_path,
        model_name,
        result_dict,
        measure_dict[model_position_name],
        keypoints,
        world_xyz_array,
        rgb_depth_ratio=7.5,
        RGB_image=cv2.imread(str(task_folder_path / "image_front.jpg")),
        api_key=api_key,
    )
    return result_dict


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
