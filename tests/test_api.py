from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)


def test_sweet_suit_success():
    """
    성공 케이스: 올바른 데이터를 입력했을 때 API가 예상대로 작동하는지 테스트
    """
    files = {
        "image_front_file": (
            "image_front.jpg",
            open("tests/test_data/image_front.jpg", "rb"),
        ),
        "image_side_file": (
            "image_side.jpg",
            open("tests/test_data/image_side.jpg", "rb"),
        ),
        "json_front_file": (
            "depth_front.json",
            open("tests/test_data/depth_front.json", "rb"),
        ),
        "json_side_file": (
            "depth_side.json",
            open("tests/test_data/depth_side.json", "rb"),
        ),
    }
    response = client.post("/api/v1.0/sweet_suit/upper", files=files)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"


# def test_sweet_suit_missing_file():
#     """
#     실패 케이스: 필수 파일이 누락되었을 때 적절한 에러 반환 확인
#     """
#     files = {
#         "image_front_file": (
#             "image_front.jpg",
#             open("tests/test_data/image_front.jpg", "rb"),
#         ),
#         # image_side_file 누락
#         "json_front_file": (
#             "depth_front.json",
#             open("tests/test_data/depth_front.json", "rb"),
#         ),
#         "json_side_file": (
#             "depth_side.json",
#             open("tests/test_data/depth_side.json", "rb"),
#         ),
#     }
#     response = client.post("/api/v1.0/sweet_suit/upper", files=files)
#     assert response.status_code == 422  # HTTP 422 Unprocessable Entity


# def test_sweet_suit_invalid_file_format():
#     """
#     실패 케이스: 잘못된 파일 형식을 입력했을 때 적절한 에러 반환 확인
#     """
#     files = {
#         "image_front_file": (
#             "image_front.txt",
#             open("tests/test_data/invalid.txt", "rb"),
#         ),  # 잘못된 형식
#         "image_side_file": (
#             "image_side.jpg",
#             open("tests/test_data/image_side.jpg", "rb"),
#         ),
#         "json_front_file": (
#             "depth_front.json",
#             open("tests/test_data/depth_front.json", "rb"),
#         ),
#         "json_side_file": (
#             "depth_side.json",
#             open("tests/test_data/depth_side.json", "rb"),
#         ),
#     }
#     response = client.post("/api/v1.0/sweet_suit/upper", files=files)
#     assert response.status_code == 400  # HTTP 400 Bad Request
