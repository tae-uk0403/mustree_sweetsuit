# 모바일 기반 신체 치수 측정 API for 달콤정장

이 API는 **취업준비생을 대상으로 정장 대여 서비스를 제공하는 달콤정장**을 위해 개발된 모바일 기반 비대면 신체 치수 측정 서비스입니다. 사용자는 모바일 기기만으로 자신의 신체 치수를 측정하고, 비대면으로 정장 사이즈를 확인할 수 있습니다.

## API 정보
- ### **API Swagger**
     **`http://203.252.147.202:8200/docs`**

- ### **Request parameters**
     - **Path Parameter**
          - `upper_or_lower` (str) : 측정할 신체 부위 (`upper` 또는 `lower`)
               - `upper` : 상체 측정
               - `lower` : 하체 측정

     - **Headers**
          - `api_key`: API 호출에 필요한 인증 키 (의존성 검사 사용)
     - **Files**
          - `image_front_file`: 신체 앞면 이미지 (PNG 형식)
          - `image_side_file`: 신체 측면 이미지 (PNG 형식)
          - `json_front_file`: 앞면 3D 깊이 데이터 (JSON 형식)
          - `json_side_file`: 측면 3D 깊이 데이터 (JSON 형식)

- ### **Response**
     성공적인 요청 시, 응답으로 신체 측정 결과가 포함된 ZIP 파일을 반환합니다.

     - **파일명**: `{upper_or_lower}_result.zip`
     - **내용물**:
          - `key_measure_result.png`: 신체 둘레 측정 결과 이미지
          - `result_circum.json`: 신체 둘레 측정 결과 JSON 데이터


## Getting Started

## 주요 기능

- **측정 신체부위 자동 detection** : Hrnet기반 모델을 신체 데이터로 transfer-learning하여 측정 신체부위를 Kepoint Detection
- **신체 치수 측정** : 아이폰의 Lidar 센서의 depth 정보와 카메라로 찍은 RGB 이미지를 매칭하여 길이 계산
- **전체 신체 둘레 계산** : 신체 부위의 앞, 옆 둘레를 회귀식으로 전체 둘레를 추정

## 고도화 연구
### 1. Edge detection 기반 keypoint 보정 알고리즘 개발
### 2. 배경제거를 통한 Keypoint Detection 정확도 향상



### 정확도

LiDAR 센서의 깊이 데이터를 활용해 평균 **96%의 상대 오차**로 신체 치수를 측정할 수 있습니다. 이는 의류 대여와 같은 비대면 피팅 서비스에서 필요한 수준의 정밀도를 충족합니다.

다음은 본 연구에서 얻은 주요 실험 결과입니다.

| 신체 부위 | 측정 오차 (%) |
|-----------|---------------|
| 허리 둘레 | 4% 미만       |
| 가슴 둘레 | 8% 미만       |
| 골반 둘레 | 일부 7.8%     |
| 엉덩이 둘레 | 2.6% 미만   |

- 신체 둘레 측정에서 전체적으로 8% 이내의 상대 오차를 기록했습니다.
- 골반 둘레 측정에서 일부 오차가 있었으나, 이는 복잡한 3D 구조와 관련이 있습니다.
- **depth map을 활용한 키포인트 보정**은 측정 정확도 향상에 중요한 역할을 했습니다.


## 업데이트 내역
