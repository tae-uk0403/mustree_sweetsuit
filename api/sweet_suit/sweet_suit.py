import cv2
import asyncio
from pathlib import Path
import pandas as pd
from rembg import remove
import logging
import time

from .utils.keypoint.preprocess import async_remove_background
from .utils.measure.class_dict import measure_dict
from .utils.measure.measure import measure_keypoint_distances
from .utils.visualize.visualize import (
    create_keypoint_images,
    visualize_measurement_results,
)
from .utils.keypoint.find_keypoint import async_find_keypoints
from .utils.visualize.visualize import (
    create_keypoint_images,
    visualize_measurement_results,
)


async def run_sweet_suit(task_folder_path, upper_or_lower, model_name, gender):
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

    rem_start_time = time.time()
    # 비동기로 배경 제거
    await asyncio.gather(
        async_remove_background(img_file_front, rembg_img_front),
        async_remove_background(img_file_side, rembg_img_side),
    )
    rem_end_time = time.time()
    removing_background_time = rem_end_time - rem_start_time
    logging.info(f"removing_background_time: {removing_background_time:.2f} seconds")

    # 비동기로 키포인트 탐지
    find_keypoint_start_time = time.time()
    front_keys, side_keys = await asyncio.gather(
        async_find_keypoints(
            task_folder_path,
            upper_or_lower,
            model_name,
            front_model_name,
            "rembg_image_front.jpg",
        ),
        async_find_keypoints(
            task_folder_path,
            upper_or_lower,
            model_name,
            side_model_name,
            "rembg_image_side.jpg",
        ),
    )
    find_keypoint_end_time = time.time()
    find_keypoint_time = find_keypoint_end_time - find_keypoint_start_time
    logging.info(f"finding_keypoint_time: {find_keypoint_time:.2f} seconds")

    # 키포인트 이미지 생성 (디버깅 용도)
    make_keyimage_start_time = time.time()

    create_keypoint_images(
        task_folder_path, rembg_img_front, rembg_img_side, front_keys, side_keys
    )
    make_keyimage_end_time = time.time()
    make_keyimage_time = make_keyimage_end_time - make_keyimage_start_time
    logging.info(f"making_keypoint_2image_image_time: {make_keyimage_time:.2f} seconds")

    # 측정 준비
    measure_circum_start_time = time.time()

    measure_3d_result_dict = {}
    measure_3d_result_dict = measure_keypoint_distances(
        task_folder_path,
        model_name,
        gender,
        side_model_name,
        side_keys,
        measure_3d_result_dict,
        "depth_side.json",
    )
    measure_3d_result_dict = measure_keypoint_distances(
        task_folder_path,
        model_name,
        gender,
        front_model_name,
        front_keys,
        measure_3d_result_dict,
        "depth_front.json",
    )
    measure_circum_end_time = time.time()
    measure_circum_time = measure_circum_end_time - measure_circum_start_time
    logging.info(f"measuring_2image_circum_time: {measure_circum_time:.2f} seconds")

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
