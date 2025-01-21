from rembg import remove
import asyncio


def remove_background(input_path, output_path):
    """이미지의 배경을 제거하고 결과를 저장합니다."""
    with open(input_path, "rb") as i, open(output_path, "wb") as o:
        o.write(remove(i.read()))


async def async_remove_background(input_path, output_path):
    """비동기로 배경 제거 처리"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, remove_background, input_path, output_path)
