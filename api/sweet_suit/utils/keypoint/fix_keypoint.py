import cv2
import numpy as np
from pathlib import Path


def fix_keypoint(task_folder_path, world_xyz_array, keypoint_y, keypoint_x_list):
    """
    XYZ 배열을 기반으로 Canny 엣지 감지 수행 후, 주어진 키포인트 좌표에서 가장 가까운 엣지 좌표 반환.
    """
    edges = detect_edges(world_xyz_array)

    closest_points = find_closest_edge_points(edges, keypoint_y, keypoint_x_list)
    save_edges_image(edges, task_folder_path, closest_points)

    return closest_points


def detect_edges(world_xyz_array):
    """
    XYZ 배열의 크기를 기반으로 깊이 정보를 정규화하고, Canny 엣지 감지를 수행하여 엣지 배열 반환.
    """
    depth_magnitude = np.sqrt(np.sum(np.square(world_xyz_array), axis=2))
    normalized_depth = normalize_depth(depth_magnitude)
    edges = cv2.Canny(normalized_depth, 10, 50)
    return edges


def save_edges_image(edges, task_folder_path, closest_points):
    """
    감지된 엣지를 PNG 이미지로 저장, 그리고 각 좌표에 표시.
    """
    # edges 이미지를 복사하여 그 위에 circle과 text를 추가
    annotated_edges = edges.copy()
    for i in range(2):
        # 좌표에 원 그리기
        cv2.circle(
            annotated_edges,
            (int(closest_points[i][0]), int(closest_points[i][1])),
            8,
            (255, 0, 0),
            -1,
        )
        # 좌표에 텍스트 추가
        cv2.putText(
            annotated_edges,
            str(i),
            (int(closest_points[i][0]), int(closest_points[i][1])),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=(255, 20, 147),
            thickness=1,
            lineType=cv2.LINE_AA,
        )

    # 이미지를 저장할 경로 설정
    output_path = (
        Path(task_folder_path)
        / f"edges_image_{closest_points[0][0]}_{closest_points[0][1]}.png"
    )

    # 최종 이미지 저장
    cv2.imwrite(str(output_path), annotated_edges)


def find_closest_edge_points(edges, keypoint_y, keypoint_x_list):
    """
    주어진 Y 좌표와 각 X 좌표에서 가장 가까운 엣지 포인트를 계산
    """
    x_list = np.where(edges[keypoint_y] == 255)[0]  # keypoint_y 줄의 엣지 포인트 X 좌표
    answer_1, answer_2 = get_nearest_points(x_list, keypoint_x_list)
    return [answer_1 + 1, keypoint_y], [answer_2 - 1, keypoint_y]


def get_nearest_points(x_list, keypoint_x_list):
    """
    keypoint y좌표 상의 edge 중 keypoint x 좌표와 가장 가까운 x 좌표 반환
    """
    min_value_1, min_value_2 = 255, 255
    answer_1, answer_2 = [], []

    for x in x_list:
        if abs(x - keypoint_x_list[0]) < min_value_1:
            answer_1.append(x)
            min_value_1 = abs(x - keypoint_x_list[0])
        if abs(x - keypoint_x_list[1]) < min_value_2:
            answer_2.append(x)
            min_value_2 = abs(x - keypoint_x_list[1])

    if len(answer_1) == 0:
        answer_1.append(keypoint_x_list[0])
    if len(answer_2) == 0:
        answer_2.append(keypoint_x_list[1])

    return answer_1[-1], answer_2[-1]


def normalize_depth(depth_array):
    """
    깊이 배열을 0-255 범위로 정규화
    """
    return (
        (depth_array - depth_array.min())
        / (depth_array.max() - depth_array.min())
        * 255
    ).astype(np.uint8)
