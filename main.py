from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import FileResponse
from datetime import datetime
from typing import Literal, Annotated
from pathlib import Path
import os
import zipfile
import logging
import time
import cProfile
import pstats
import io

# 의존성 함수 임포트
from api.sweet_suit.sweet_suit import run_sweet_suit2

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

app = FastAPI(
    title="Mustree Sweetsuit API",
    version="0.0.0",
    openapi_tags=[{"name": "API Reference"}],
)

UpperOrLower = Literal["upper", "lower"]


def save_file(file: UploadFile, path: Path):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)  # 부모 디렉토리 생성
        with path.open("wb") as f:  # 동기적으로 파일 열기
            f.write(file.file.read())  # 파일 읽고 쓰기
        logging.info(f"File saved successfully: {path}")
    except Exception as e:
        logging.error(f"Failed to save file {path}: {e}")
        raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")


def prepare_task_folder(upper_or_lower: str) -> Path:
    now_date = datetime.now().strftime("%Y%m%d%H%M%S%f")
    task_folder = Path(
        f"api/sweet_suit/temp_process_task_files/{upper_or_lower}/{now_date}"
    )
    task_folder.mkdir(parents=True, exist_ok=True)  # 디렉토리 생성
    logging.info(f"Task folder prepared at: {task_folder}")
    return task_folder


@app.post(
    "/api/v1.0/sweet_suit/{upper_or_lower}",
    tags=["API Reference"],
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
)
async def sweet_suit(
    upper_or_lower: UpperOrLower,
    image_front_file: Annotated[
        UploadFile, File(media_type="image/png", description="Front body image")
    ],
    image_side_file: Annotated[
        UploadFile, File(media_type="image/png", description="Side body image")
    ],
    json_front_file: Annotated[
        UploadFile, File(media_type="text/json", description="Front depth data")
    ],
    json_side_file: Annotated[
        UploadFile, File(media_type="text/json", description="Side depth data")
    ],
):
    """
    **사용자 신체 측정을 위한 API**

    - **upper_or_lower**: 상체(`upper`) 또는 하체(`lower`)를 지정합니다.
    - **image_front_file**: 신체 앞면 이미지.
    - **image_side_file**: 신체 측면 이미지.
    - **json_front_file**: 앞면 3D 깊이 데이터.
    - **json_side_file**: 측면 3D 깊이 데이터.

    **Response**:
    - 측정 결과가 포함된 이미지 파일을 ZIP 형식으로 반환합니다.
    """
    # cProfile을 사용하여 프로파일링 시작
    pr = cProfile.Profile()
    pr.enable()  # 프로파일링 시작

    start_time = time.time()  # 시작 시간 기록

    try:
        logging.info("Preparing task folder...")

        task_folder = prepare_task_folder(upper_or_lower)
        print(task_folder)
        # 파일 저장
        save_file(image_front_file, task_folder / "image_front.jpg")
        save_file(image_side_file, task_folder / "image_side.jpg")
        save_file(json_front_file, task_folder / "depth_front.json")
        save_file(json_side_file, task_folder / "depth_side.json")

        # 측정 실행
        _, result_image_path = run_sweet_suit2(
            task_folder, upper_or_lower, upper_or_lower
        )

        # ZIP 파일 생성
        zip_file_path = task_folder / f"{upper_or_lower}_result.zip"
        with zipfile.ZipFile(zip_file_path, "w") as zipf:
            for file_name in ["key_measure_result.png", "result_circum.json"]:
                file_path = task_folder / file_name
                if file_path.exists():
                    zipf.write(file_path, arcname=os.path.basename(file_path))
                else:
                    logging.warning(f"Missing expected file: {file_name}")

        logging.info(f"Returning ZIP file: {zip_file_path}")

        end_time = time.time()  # 종료 시간 기록
        elapsed_time = end_time - start_time  # 경과 시간 계산
        logging.info(f"Elapsed time: {elapsed_time:.2f} seconds")  # 경과 시간 로그

        return FileResponse(
            zip_file_path,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={upper_or_lower}_result.zip"
            },
        )

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    finally:
        pr.disable()  # 프로파일링 종료
        # 프로파일링 결과를 메모리에 저장
        s = io.StringIO()
        sortby = pstats.SortKey.CUMULATIVE  # 누적 시간 기준으로 정렬
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()  # 프로파일링 결과 출력
        logging.info(s.getvalue())  # 로그에 프로파일링 결과 기록
