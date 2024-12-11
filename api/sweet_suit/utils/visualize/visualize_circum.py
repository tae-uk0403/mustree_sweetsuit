import numpy as np
import json
import cv2
from pathlib import Path


## 둘레 시각화
def visualize_result(
    detected_keypoints, RGB_image, measure_name, measure_3d_result_dict
):

    # 키포인트 설정
    point1 = (int(detected_keypoints[0][0]), int(detected_keypoints[0][1]))
    point2 = (int(detected_keypoints[1][0]), int(detected_keypoints[1][1]))

    # 타원 중심과 축 설정
    real_center = ((point1[0] + point2[0]) / 2, point1[1])
    real_axes = (abs(point1[0] - point2[0]) / 2, abs(point1[0] - point2[0]) / 6)
    fixed_angle = [-35, 215]
    axes_w = real_axes[0] / np.cos(np.radians(fixed_angle[0]))

    # 타원 중심 및 축 계산
    fixed_center = (
        int(real_center[0]),
        int(real_center[1] + axes_w * np.sin(np.radians(-fixed_angle[0])) / 6),
    )
    fixed_axes = (int(axes_w), int(axes_w // 6))

    # 타원, 키포인트 원 그리기
    cv2.ellipse(
        RGB_image,
        fixed_center,
        fixed_axes,
        0,
        fixed_angle[0],
        fixed_angle[1],
        (255, 255, 255),
        thickness=10,
        lineType=cv2.LINE_AA,
    )
    cv2.circle(RGB_image, point1, 12, (100, 150, 255), -1)
    cv2.circle(RGB_image, (point2[0], point1[1]), 12, (100, 150, 255), -1)

    # 측정값 텍스트 생성
    text = f"{measure_name} : {measure_3d_result_dict[measure_name]:.2f}cm"
    font, font_scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 1.3, 4
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )

    # 텍스트 배경 위치 계산
    start_x = int(point1[0] + (point2[0] - point1[0] - text_width) / 2)
    start_y = int((point1[1] + point2[1]) / 2)
    bg_start_x, bg_start_y = start_x - 45, start_y - text_height - baseline - 10
    bg_end_x, bg_end_y = start_x + text_width + 45, start_y + baseline + 10

    # 배경 및 텍스트 추가
    cv2.rectangle(
        RGB_image, (bg_start_x, bg_start_y), (bg_end_x, bg_end_y), (255, 255, 255), -1
    )
    cv2.rectangle(
        RGB_image, (bg_start_x, bg_start_y), (bg_end_x, bg_end_y), (100, 150, 255), 4
    )
    cv2.putText(
        RGB_image, text, (start_x, start_y), font, font_scale, (0, 0, 0), thickness
    )

    return RGB_image


## 길이 시각화
def visualize_result_2d(
    task_folder_path, detected_keypoints, RGB_image, measure_name, measure_result_dict
):

    # 측정 결과를 JSON 파일에 저장
    json_file_path = Path(task_folder_path) / "result_circum.json"
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {}

    data["다리"] = round(measure_result_dict[measure_name], 0)

    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    # 키포인트 설정
    point1 = tuple(map(int, detected_keypoints[0]))
    point2 = tuple(map(int, detected_keypoints[1]))

    # 측정값 텍스트 생성
    text = f"{measure_name} : {measure_result_dict[measure_name]:.2f}cm"

    # 시각화 - 배경 사각형과 텍스트 넣기
    font, font_scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 1.3, 4
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )

    text_start_x = (point1[0] + point2[0]) // 2
    text_start_y = (point1[1] + point2[1]) // 2
    bg_start = (text_start_x - 10, text_start_y - text_height - baseline - 10)
    bg_end = (text_start_x + text_width + 20, text_start_y + baseline + 10)

    cv2.rectangle(RGB_image, bg_start, bg_end, (255, 255, 255), -1)  # 배경 사각형
    cv2.rectangle(RGB_image, bg_start, bg_end, (100, 150, 255), 4)  # 배경 테두리
    cv2.putText(
        RGB_image,
        text,
        (text_start_x, text_start_y + text_height),
        font,
        font_scale,
        (0, 0, 0),
        thickness,
    )  # 텍스트

    # 측정 구간 직선 및 키포인트 원 그리기
    cv2.line(
        RGB_image, point1, point2, (255, 255, 255), thickness=10, lineType=cv2.LINE_AA
    )
    cv2.circle(RGB_image, point1, 12, (100, 150, 255), -1)
    cv2.circle(RGB_image, point2, 12, (100, 150, 255), -1)

    return RGB_image
