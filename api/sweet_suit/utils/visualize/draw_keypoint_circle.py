import numpy as np
import json
import cv2
from pathlib import Path




def draw_keypoint_circle(task_folder_path, img_file, key_result, result_name):
        # 예측한 keypoints 좌표들에 점 찍은 이미지 생성하고 확인 (필요없으면 생략)
    k = cv2.imread(img_file)
    # print('key result is : ', key_result)
    
    for i in range(len(key_result)):
        cv2.circle(k, (int(key_result[i, 0]), int(key_result[i, 1])), 8, [255, 0, 0], -1)
        cv2.putText(k, str(i),(int(key_result[i, 0]), int(key_result[i, 1])), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0, color=(255, 20, 147), thickness=2, lineType=cv2.LINE_AA,)
    final_img_path = str(task_folder_path/ result_name )
    # print("final_img_path", final_img_path)
    cv2.imwrite(final_img_path, k)