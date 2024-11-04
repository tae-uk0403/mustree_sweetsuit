import numpy as np
import json
import cv2
from pathlib import Path
from ..keypoint.fix_keypoint import fix_keypoint
from ..visualize.draw_keypoint_circle import draw_keypoint_circle


# def get_world_xyz_array(pointcloud_path, rgb_h):
#     """
#     :param pointcloud_path: json 파일. cx, cy, 초기 z값이 쌍으로 있어야 한다. 또한, Camera Parameter 정보가 필요하다.
#     cx, cy, z : [cx : 0~depth_w, cy : 0~depth_h, z : initial value of z at taking a depth]
#     Intrinsic Parameters : [Focal Length : "fl x, y", Principal point : "depth width and height"]
#     Extrinsic Parameters : [Rotation Matrix : "rot", Translation Vector : "pos x, y, z"]
#     :param rgb_h: height of the rgb image
#     :return: world_xyz_array, shape : [depth_w, depth_h, 3]
#     """
#     with open (pointcloud_path, "r") as f:
#         depth_json = json.load(f)
#         # depth_w = depth_json['Width']
#         # depth_h = depth_json['Height']
#         depth_w = 256
#         depth_h = 192
#         fl_x = depth_json["fl"]["x"]
#         fl_y = depth_json["fl"]["y"]
#         rgb_depth_ratio = rgb_h/depth_h

#         camera_depth_array = np.zeros((depth_w, depth_h), dtype=np.float64)
#         for i in range(len(depth_json['Depth'])):
#             x=i%depth_w
#             y=i//depth_w
#             camera_depth_array[x][y] = depth_json['Depth'][i]


#         camera_xyz_array = []

#         # 거리를 실측할 수 있는 world_xyz_array를 만들기 전에 먼저 camera_xyz_array를 만든다.
#         # height부터 채우느냐, i부터 채우느냐에 따라 마지막 world_xyz_array가 달라질 수 있다.
#         # 현재 (24. 04. 18) 반팔 옷에 대해 테스트할 때는 height부터 채워야 실측이 제대로 된다.
#         for i in range(depth_w):
#             for j in range(depth_h):
#                 z = camera_depth_array[i][j]
#                 x = (j - depth_w / 2) * z / (fl_x / rgb_depth_ratio)
#                 y = (i - depth_h / 2) * z / (fl_y / rgb_depth_ratio)
#                 camera_xyz_array.append([x, y, z])

#         camera_xyz_array = np.array(camera_xyz_array)

#         # world_xyz_array를 만들기 위한 Rotation Matrix 만들기
#         R_camera_to_world = np.array(
#             [[depth_json['m00'], depth_json['m01'], depth_json['m02'], depth_json['m03']],
#              [depth_json['m10'], depth_json['m11'], depth_json['m12'], depth_json['m13']],
#              [depth_json['m20'], depth_json['m21'], depth_json['m22'], depth_json['m23']],
#              [depth_json['m30'], depth_json['m31'], depth_json['m32'], depth_json['m33']]])
#         R_camera_to_world = R_camera_to_world[0:3, 0:3]

#         # world_xyz_array를 만들기 위한 Translation Vector 만들기
#         T_camera_to_world = np.array([depth_json['Pos']['x'], depth_json['Pos']['y'], depth_json['Pos']['z']])

#         # camera_xyz_array, Rotation Matrix, Translation Vector를 활용하여 world_xyz_array를 만든다.
#         world_xyz_array = np.dot(camera_xyz_array, R_camera_to_world) + T_camera_to_world

#         # [256, 192, 3] shape으로 만든다.
#         world_xyz_array = world_xyz_array.reshape((256, 192, 3))
#         # world_xyz_array = np.flip(world_xyz_array, axis=1)

#         return world_xyz_array

def get_world_xyz_array(pointcloud_path, rgb_h):
    
    with open(pointcloud_path) as f:
        depth_json = json.load(f)
    depth_values = depth_json["Depth"]
    depth_w = 256
    depth_h = 192
    fl_x = depth_json['fl']['x']
    fl_y = depth_json['fl']['y']
    xyz_array = []
    k = 0
    for i in range(depth_h):
        for j in range(depth_w):
            z = depth_values[k]
            x = (j - 256 / 2) * z / (fl_x / 7.5)
            y = (i - 192 / 2) * z / (fl_y / 7.5)
            xyz_array.append([x, y, z])
            k += 1

    R_camera_to_world = np.array([[depth_json['m00'], depth_json['m01'], depth_json['m02'], depth_json['m03']],
                                  [depth_json['m10'], depth_json['m11'], depth_json['m12'], depth_json['m13']],
                                  [depth_json['m20'], depth_json['m21'], depth_json['m22'], depth_json['m23']],
                                  [depth_json['m30'], depth_json['m31'], depth_json['m32'], depth_json['m33']]])

    R_camera_to_world = R_camera_to_world[0:3, 0:3]

    T_camera_to_world  = np.array([depth_json['Pos']['x'], depth_json['Pos']['y'], depth_json['Pos']['z']])

    world_xyz = np.dot(xyz_array, R_camera_to_world) + T_camera_to_world

    world_xyz_array = world_xyz.reshape((192, 256, 3))
    world_xyz_array = np.rot90(world_xyz_array, k=-1)

    return world_xyz_array


# def measure_distance(task_folder_path, measure_dict, detected_keypoints, world_xyz_array, rgb_depth_ratio, RGB_image, api_key):
#     """
#     :param measure_dict: class_dict.py에 정의하는 class별 측정 대상에 대한 정보 dictionary. key : 측정 대상의 이름, value: 측정 대상이 되는 두 개의 keypoint index
#     :param detected_keypoints: rgb image를 keypoint detection 모델에 입력하여 나온 결과. [x, y] 쌍으로 이루어진 점 좌표 리스트. shape : [점 개수, 2]
#     :param world_xyz_array: [256, 192, 3] 형태의 world_xyz_array
#     :param rgb_depth_ratio: height of rgb / height of depth or height of rgb / height of world_xyz_array 아마도 height of world_xzy_array = height of depth
#     :return: 측정 대상별 길이 dictionary
#     """
  
#     measure_result_dict = {}

#     for measure_name, measure_points in measure_dict.items():
#         # print('measure points is ' , measure_points)
#         # print('measure dict is' , measure_dict)
        
#         target_point_1 = np.array(np.array(detected_keypoints[measure_points[0] - 1]) / rgb_depth_ratio, dtype=np.int64)
#         target_point_2 = np.array(np.array(detected_keypoints[measure_points[1] - 1]) / rgb_depth_ratio, dtype=np.int64)
        
#         measure_result_dict[measure_name] = np.linalg.norm(
#             world_xyz_array[target_point_1[1], target_point_1[0]] - world_xyz_array[target_point_2[1], target_point_2[0]]) * 100
        
#         detected_keypoints_1 = detected_keypoints[measure_points[0] - 1]
#         detected_keypoints_2 = detected_keypoints[measure_points[1] - 1]
#         # print(f"measure name is {measure_name}, measure length is {measure_result_dict[measure_name]}, detected depth keypoints is {target_point_1}, {target_point_2}")
        
        
        
#         json_file_path = Path( task_folder_path / 'result_circum.json')

#         with open(json_file_path, 'r') as json_file:
#             data = json.load(json_file)
            
#         data['다리'] = round(measure_result_dict[measure_name],0)
        
#         with open(json_file_path, 'w') as json_file:
#             json.dump(data, json_file, indent=4, ensure_ascii=False)
#         point1 = (detected_keypoints_1[0], detected_keypoints_1[1])
#         point2 = (detected_keypoints_2[0], detected_keypoints_2[1])
        
#         json_model_name = 'leg'
#         text = '{0} : {1:.2f}cm'.format(json_model_name,measure_result_dict[measure_name])
#         print("text is : " , text)
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         font_scale = 1.3
#         thickness = 4
#         (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
#         start_x = point1[0] + (point2[0] - point1[0] - text_width) / 2
#         start_y = int((point2[0] + point2[1]) / 2)
        
        
#         bg_color = (255, 255, 255)  # 흰색 배경
#         border_color = (100, 150, 255)
#         text_color = (0, 0, 0)  # 검정색 텍스트

#         # 배경 사각형 좌표 계산
#         bg_start_x = int((point1[0] + point2[0]) / 2 + 20)
#         bg_start_y = int((point1[1]+point2[1] / 2) - text_height - baseline - 50)
#         bg_end_x = int(( point1[0] + point2[0] ) / 2 + text_width + 110)
#         bg_end_y = int((point1[1]+point2[1] / 2) + baseline - 30)

        
        
#         # 배경 사각형 그리기
#         cv2.rectangle(RGB_image, (bg_start_x-10, bg_start_y), (bg_end_x, bg_end_y), bg_color, -1)
        
#         # 배경 테두리 그리기
#         cv2.rectangle(RGB_image, (bg_start_x-10, bg_start_y), (bg_end_x, bg_end_y), border_color, 4)

#         # 텍스트 넣기
#         cv2.putText(RGB_image, text ,(((bg_end_x - bg_start_x) - text_width) // 2 + bg_start_x , ((bg_end_y - bg_start_y) - text_height) // 2 + bg_start_y + 2 *baseline  ), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 4)    
        
#         # 직선 넣기
#         cv2.line(RGB_image, (int(point1[0]),int(point1[1])), (int(point2[0]),int(point2[1])), (255, 255, 255), thickness=10, lineType=cv2.LINE_AA)

#         # keypoint 원 그리기
#         cv2.circle(RGB_image, (int(point1[0]),int(point1[1])), 12, (100, 150, 255), -1)
#         cv2.circle(RGB_image, (int(point2[0]),int(point2[1])), 12, (100, 150, 255), -1)
        
    # return measure_result_dict, RGB_image


# def abcd(a,b,c,d):
#     """
#     :return: 측정대상별 Dictionary = {"어깨":{"길이":54, "키포인트":[[1000, 500], [1100, 500]]}, "가슴":{}, ...} 
#     """


# def measure_3D_distance(task_folder_path, model_name, measure_dict, detected_keypoints, world_xyz_array, rgb_depth_ratio, RGB_image, prior_circum, api_key):
#     """
#     :param measure_dict: class_dict.py에 정의하는 class별 측정 대상에 대한 정보 dictionary. key : 측정 대상의 이름, value: 측정 대상이 되는 두 개의 keypoint index
#     :param detected_keypoints: rgb image를 keypoint detection 모델에 입력하여 나온 결과. [x, y] 쌍으로 이루어진 점 좌표 리스트. shape : [점 개수, 2]
#     :param world_xyz_array: [256, 192, 3] 형태의 world_xyz_array
#     :param rgb_depth_ratio: height of rgb / height of depth or height of rgb / height of world_xyz_array 아마도 height of world_xzy_array = height of depth
#     :return: 측정 대상별 길이 dictionary
#     """

#     measure_3d_result_dict = {}

#     for measure_name, measure_points in measure_dict.items():

#         target_point_1 = np.array(np.array(detected_keypoints[0]) / rgb_depth_ratio, dtype=np.int64)
#         target_point_2 = np.array(np.array(detected_keypoints[1]) / rgb_depth_ratio, dtype=np.int64)
        
#         #print("original keypont : ",[target_point_1,target_point_2])
#         # target_point = fix_keypoint(world_xyz_array, target_point_1[1], [target_point_1[0],target_point_2[0]])
#         # target_point_1 = target_point[0]
#         # target_point_2 = target_point[1]
#         # print("fixed keypoint : ", target_point)
        
        
#         length_3d = 0
#         for i in range(target_point_1[0],target_point_2[0]):  
#             try : 
#                 pixel_length = np.linalg.norm(
#                     world_xyz_array[target_point_1[1],i] - world_xyz_array[target_point_1[1],i+1]) * 100
#                 if api_key == "android":
#                     pixel_length = pixel_length / 4.25
#                 if pixel_length <5:
#                     length_3d += pixel_length
#             except :
#                 pixel_length = 0
#             # print(i, np.linalg.norm(
#             #     world_xyz_array[target_point_1[1],i] - world_xyz_array[target_point_1[1],i+1]) * 100)
        
#         sum_circum = prior_circum + length_3d
#         if prior_circum != 0:
#             if model_name == 'chest':
#                 sum_circum = sum_circum*1.427
#             elif model_name == 'waist':
#                 sum_circum = sum_circum*1.322
#             elif model_name == 'pelvis':
#                 sum_circum = sum_circum*1.322
#             elif model_name == 'hips':
#                 sum_circum = sum_circum*1.53
        
#         print('prior_circum : ', prior_circum)
#         print('length_3d : ', length_3d)
#         print('sum_circum :', sum_circum)
#         measure_3d_result_dict[measure_name] = sum_circum
        
        
#         if model_name == 'chest':
#             json_model_name = '가슴'
#         elif model_name == 'waist':
#             json_model_name = '허리'
#         elif model_name == 'pelvis':
#             json_model_name = '골반'
#         elif model_name == 'hips':
#             json_model_name = '엉덩이'
        
#         json_file_path = Path( task_folder_path / 'result_circum.json')

#         if prior_circum != 0:
#             try:
#                 with open(json_file_path, 'r', encoding='utf-8') as json_file:
#                     data = json.load(json_file)
#                 print("json_model_name is : ", json_model_name)
#                 data[json_model_name] = round(sum_circum,0)
#                 print("json data is ", data)
#                 with open(json_file_path, 'w', encoding='utf-8') as json_file:
#                     json.dump(data, json_file, indent=4, ensure_ascii=False)
                    
#                 print("try")
#             except :
#                 print(f"{json_file_path} 파일이 존재하지 않습니다.")
                
#                 data = {
#                     json_model_name : round(sum_circum, 0)
#                 }
#                 print("except")
                
#                 with open(json_file_path, 'w', encoding='utf-8') as json_file:
#                     json.dump(data, json_file, indent=4, ensure_ascii=False)       


        
        
#         point1 = (int(detected_keypoints[0][0]), int(detected_keypoints[0][1]))
#         point2 = (int(detected_keypoints[1][0]), int(detected_keypoints[1][1]))
        
        
#         # 타원의 중심과 축 설정
#         center = (int((point1[0] + point2[0]) // 2), int(point1[1]))
#         axes = (abs(point1[0] - point2[0]) // 2, abs(point1[0] - point2[0]) // 6)  # 수평 축과 수직 축
        
#         real_center = ((point1[0] + point2[0]) / 2, point1[1])
#         real_axes = (abs(point1[0] - point2[0]) / 2, abs(point1[0] - point2[0]) / 6)  # 수평 축과 수직 축
        
#         angle = 0  # 회전 각도 (0도)
#         start_angle = -30  # 타원의 시작 각도
#         end_angle = 210
#         # 타원의 끝 각도 i

#         # 그림자 설정
#         shadow_offset = (10, 10)  # 그림자 오프셋
#         shadow_color = (100, 100, 100)  # 그림자 색상 (어두운 회색)
#         border_width = 3  # 그림자 두께

#         # 그림자 타원 그리기
#         #shadow_center = (center[0] + shadow_offset[0], center[1] + shadow_offset[1])
#         #cv2.ellipse(img, shadow_center, axes, angle, start_angle, end_angle, shadow_color, thickness=border_width, lineType=cv2.LINE_AA)
#         start_radian = np.radians(start_angle)
#         end_radian = np.radians(end_angle)

#         print('point1', (point1[0],point1[1]))
#         fixed_angle = [-35,215]
#         axes_w = real_axes[0] / np.cos(np.radians(fixed_angle[0]))

#         fixed_center = (int(real_center[0]), int(real_center[1] + axes_w * np.sin(np.radians(-fixed_angle[0])) / 6))
#         fixed_axes = (int(axes_w), int(axes_w//6))
#         print(axes_w)

#         # cv2.ellipse(img, center, axes, angle, start_angle, end_angle, (255, 0, 0), thickness=border_width, lineType=cv2.LINE_AA)
#         cv2.ellipse(RGB_image, fixed_center, fixed_axes, angle, fixed_angle[0], fixed_angle[1], (255, 255, 255), thickness=10, lineType=cv2.LINE_AA)
#         cv2.circle(RGB_image, (int(point1[0]),int(point1[1])), 12, (100, 150, 255), -1)
#         cv2.circle(RGB_image, (int(point2[0]),int(point1[1])), 12, (100, 150, 255), -1)
                

   
    

            
#         text = '{0} : {1:.2f}cm'.format(model_name ,measure_3d_result_dict[measure_name])
#         print("text is : " , text)
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         font_scale = 1.3
#         thickness = 4
#         (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

#         # 텍스트 시작 위치 계산
#         start_x = detected_keypoints[0][0] + (detected_keypoints[1][0] - detected_keypoints[0][0] - text_width) / 2
#         start_y = int((detected_keypoints[0][1] + detected_keypoints[1][1]) / 2)

#         # 배경 색상과 텍스트 색상 설정
#         bg_color = (255, 255, 255)  # 흰색 배경
#         border_color = (100, 150, 255)
#         text_color = (0, 0, 0)  # 검정색 텍스트

#         # 배경 사각형 좌표 계산
#         bg_start_x = int(start_x-45)
#         bg_start_y = int(start_y - text_height - baseline-10)
#         bg_end_x = int(start_x + text_width+45)
#         bg_end_y = int(start_y + baseline + 10)

#         # 배경 사각형 그리기
#         cv2.rectangle(RGB_image, (bg_start_x, bg_start_y), (bg_end_x, bg_end_y), bg_color, -1)
#         cv2.rectangle(RGB_image, (bg_start_x, bg_start_y), (bg_end_x, bg_end_y), border_color, 4)

#         # 텍스트 그리기
#         cv2.putText(RGB_image, text, (int(start_x), int(start_y)), font, font_scale, text_color, thickness)

        
        
#     return measure_3d_result_dict, RGB_image



# def measure_3D_distance2(task_folder_path, model_name, measure_3d_result_dict, measure_dict, detected_keypoints, world_xyz_array, rgb_depth_ratio, RGB_image, api_key):
#     """
#     :param measure_dict: class_dict.py에 정의하는 class별 측정 대상에 대한 정보 dictionary. key : 측정 대상의 이름, value: 측정 대상이 되는 두 개의 keypoint index
#     :param detected_keypoints: rgb image를 keypoint detection 모델에 입력하여 나온 결과. [x, y] 쌍으로 이루어진 점 좌표 리스트. shape : [점 개수, 2]
#     :param world_xyz_array: [256, 192, 3] 형태의 world_xyz_array
#     :param rgb_depth_ratio: height of rgb / height of depth or height of rgb / height of world_xyz_array 아마도 height of world_xzy_array = height of depth
#     :return: 측정 대상별 길이 dictionary
#     """

#     for measure_name, measure_points in measure_dict.items():

#         target_point_1 = np.array(np.array(detected_keypoints[measure_points[0]-1]) / rgb_depth_ratio, dtype=np.int64)
#         target_point_2 = np.array(np.array(detected_keypoints[measure_points[1]-1]) / rgb_depth_ratio, dtype=np.int64)
        
#         #print("original keypont : ",[target_point_1,target_point_2])
#         # target_point = fix_keypoint(world_xyz_array, target_point_1[1], [target_point_1[0],target_point_2[0]])
#         # target_point_1 = target_point[0]
#         # target_point_2 = target_point[1]
#         # print("fixed keypoint : ", target_point)
        
#         if measure_name == "leg":
#             print("original keypont : ",[target_point_1,target_point_2])
#             target_point_1 = fix_keypoint2(task_folder_path, world_xyz_array, target_point_1[1], target_point_1[0])
#             target_point_2 = fix_keypoint2(task_folder_path, world_xyz_array, target_point_2[1], target_point_2[0])
#             print("fixed keypont : ",[target_point_1,target_point_2])
                        
#             pixel_length = np.linalg.norm(
#                 world_xyz_array[target_point_1[1],target_point_1[0]] - world_xyz_array[target_point_2[1],target_point_2[0]]) * 100
#             if api_key == "android":
#                 pixel_length = pixel_length / 4.25
#             measure_3d_result_dict[measure_name] = pixel_length
#             return measure_3d_result_dict, RGB_image
        
#         print("original keypont : ",[target_point_1,target_point_2])
        
#         target_point = fix_keypoint(task_folder_path, world_xyz_array, target_point_1[1], [target_point_1[0],target_point_2[0]])
#         target_point_1 = target_point[0]
#         target_point_2 = target_point[1]
#         print("fixed keypoint : ", target_point)
        
#         length_3d = 0
#         for i in range(target_point_1[0],target_point_2[0]-1):  
#             try :
#                 pixel_length = np.linalg.norm(
#                     world_xyz_array[target_point_1[1],i] - world_xyz_array[target_point_1[1],i+1]) * 100
                
#                 if api_key == "android":
#                     pixel_length = pixel_length / 4.25
                
#                 if pixel_length <3:
#                     length_3d += pixel_length
#             except :
#                 pixel_length = 0
#             # print(i, np.linalg.norm(
#             #     world_xyz_array[target_point_1[1],i] - world_xyz_array[target_point_1[1],i+1]) * 100)
            
#         print("measure name is : ", measure_name)
        
        
#         if measure_3d_result_dict.get(measure_name, None) is not None:
#             print("first value : ", measure_3d_result_dict[measure_name] )
#             measure_3d_result_dict[measure_name] += length_3d 
#             print("second value : ", length_3d)
            
#             print("before multiple number : ", measure_3d_result_dict[measure_name] )
#             if measure_name == 'chest':
#                 measure_3d_result_dict[measure_name] = measure_3d_result_dict[measure_name]*1.427
#                 json_model_name = '가슴'
#             elif measure_name == 'waist':
#                 measure_3d_result_dict[measure_name] = measure_3d_result_dict[measure_name]*1.322
#                 json_model_name = '허리'
#             elif measure_name == 'pelvis':
#                 measure_3d_result_dict[measure_name] = measure_3d_result_dict[measure_name]*1.322
#                 json_model_name = '골반'
#             elif measure_name == 'hips':
#                 measure_3d_result_dict[measure_name] = measure_3d_result_dict[measure_name]*1.53
#                 json_model_name = '엉덩이'
            
#             json_file_path = Path( task_folder_path / 'result_circum.json')
            
#             try:
#                 with open(json_file_path, 'r', encoding='utf-8') as json_file:
#                     data = json.load(json_file)
#                 data[json_model_name] = round(measure_3d_result_dict[measure_name],0)
#                 with open(json_file_path, 'w', encoding='utf-8') as json_file:
#                     json.dump(data, json_file, indent=4, ensure_ascii=False)
                    
#             except :
                
#                 data = {
#                     json_model_name : round(measure_3d_result_dict[measure_name], 0)
#                 }                
#                 with open(json_file_path, 'w', encoding='utf-8') as json_file:
#                     json.dump(data, json_file, indent=4, ensure_ascii=False)    
                    
            
#         else:
#             measure_3d_result_dict[measure_name] = length_3d

        
#     return measure_3d_result_dict, RGB_image


# def visualize_result(detected_keypoints, RGB_image, measure_name, measure_3d_result_dict):
    
    
#     point1 = (int(detected_keypoints[0][0]), int(detected_keypoints[0][1]))
#     point2 = (int(detected_keypoints[1][0]), int(detected_keypoints[1][1]))
    
    
#     # 타원의 중심과 축 설정
#     center = (int((point1[0] + point2[0]) // 2), int(point1[1]))
#     axes = (abs(point1[0] - point2[0]) // 2, abs(point1[0] - point2[0]) // 6)  # 수평 축과 수직 축
    
#     real_center = ((point1[0] + point2[0]) / 2, point1[1])
#     real_axes = (abs(point1[0] - point2[0]) / 2, abs(point1[0] - point2[0]) / 6)  # 수평 축과 수직 축
    
#     angle = 0  # 회전 각도 (0도)
#     start_angle = -30  # 타원의 시작 각도
#     end_angle = 210
#     # 타원의 끝 각도 i

#     # 그림자 설정
#     shadow_offset = (10, 10)  # 그림자 오프셋
#     shadow_color = (100, 100, 100)  # 그림자 색상 (어두운 회색)
#     border_width = 3  # 그림자 두께

#     # 그림자 타원 그리기
#     #shadow_center = (center[0] + shadow_offset[0], center[1] + shadow_offset[1])
#     #cv2.ellipse(img, shadow_center, axes, angle, start_angle, end_angle, shadow_color, thickness=border_width, lineType=cv2.LINE_AA)
#     start_radian = np.radians(start_angle)
#     end_radian = np.radians(end_angle)

#     fixed_angle = [-35,215]
#     axes_w = real_axes[0] / np.cos(np.radians(fixed_angle[0]))

#     fixed_center = (int(real_center[0]), int(real_center[1] + axes_w * np.sin(np.radians(-fixed_angle[0])) / 6))
#     fixed_axes = (int(axes_w), int(axes_w//6))

#     # cv2.ellipse(img, center, axes, angle, start_angle, end_angle, (255, 0, 0), thickness=border_width, lineType=cv2.LINE_AA)
#     cv2.ellipse(RGB_image, fixed_center, fixed_axes, angle, fixed_angle[0], fixed_angle[1], (255, 255, 255), thickness=10, lineType=cv2.LINE_AA)
#     cv2.circle(RGB_image, (int(point1[0]),int(point1[1])), 12, (100, 150, 255), -1)
#     cv2.circle(RGB_image, (int(point2[0]),int(point1[1])), 12, (100, 150, 255), -1)
            




        
#     text = '{0} : {1:.2f}cm'.format(measure_name ,measure_3d_result_dict[measure_name])
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     font_scale = 1.3
#     thickness = 4
#     (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

#     # 텍스트 시작 위치 계산
#     start_x = detected_keypoints[0][0] + (detected_keypoints[1][0] - detected_keypoints[0][0] - text_width) / 2
#     start_y = int((detected_keypoints[0][1] + detected_keypoints[1][1]) / 2)

#     # 배경 색상과 텍스트 색상 설정
#     bg_color = (255, 255, 255)  # 흰색 배경
#     border_color = (100, 150, 255)
#     text_color = (0, 0, 0)  # 검정색 텍스트

#     # 배경 사각형 좌표 계산
#     bg_start_x = int(start_x-45)
#     bg_start_y = int(start_y - text_height - baseline-10)
#     bg_end_x = int(start_x + text_width+45)
#     bg_end_y = int(start_y + baseline + 10)

#     # 배경 사각형 그리기
#     cv2.rectangle(RGB_image, (bg_start_x, bg_start_y), (bg_end_x, bg_end_y), bg_color, -1)
#     cv2.rectangle(RGB_image, (bg_start_x, bg_start_y), (bg_end_x, bg_end_y), border_color, 4)

#     # 텍스트 그리기
#     cv2.putText(RGB_image, text, (int(start_x), int(start_y)), font, font_scale, text_color, thickness)
#     return RGB_image

# def visualize_result_2d(task_folder_path, detected_keypoints, RGB_image, measure_name, measure_result_dict):
    
    
#     json_file_path = Path(task_folder_path / 'result_circum.json')

#     with open(json_file_path, 'r') as json_file:
#         data = json.load(json_file)
        
#     data['다리'] = round(measure_result_dict[measure_name],0)
    
#     with open(json_file_path, 'w') as json_file:
#         json.dump(data, json_file, indent=4, ensure_ascii=False)
#     point1 = (int(detected_keypoints[0][0]), int(detected_keypoints[0][1]))
#     point2 = (int(detected_keypoints[1][0]), int(detected_keypoints[1][1]))
    
#     json_model_name = 'leg'
#     text = '{0} : {1:.2f}cm'.format(json_model_name,measure_result_dict[measure_name])
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     font_scale = 1.3
#     thickness = 4
#     (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
#     start_x = point1[0] + (point2[0] - point1[0] - text_width) / 2
#     start_y = int((point2[0] + point2[1]) / 2)
    
    
#     bg_color = (255, 255, 255)  # 흰색 배경
#     border_color = (100, 150, 255)
#     text_color = (0, 0, 0)  # 검정색 텍스트

#     # 배경 사각형 좌표 계산
#     bg_start_x = int((point1[0] + point2[0]) / 2 + 20)
#     bg_start_y = int((point1[1]+point2[1] / 2) - text_height - baseline - 50)
#     bg_end_x = int(( point1[0] + point2[0] ) / 2 + text_width + 110)
#     bg_end_y = int((point1[1]+point2[1] / 2) + baseline - 30)

    
    
#     # 배경 사각형 그리기
#     cv2.rectangle(RGB_image, (bg_start_x-10, bg_start_y), (bg_end_x, bg_end_y), bg_color, -1)
    
#     # 배경 테두리 그리기
#     cv2.rectangle(RGB_image, (bg_start_x-10, bg_start_y), (bg_end_x, bg_end_y), border_color, 4)

#     # 텍스트 넣기
#     cv2.putText(RGB_image, text ,(((bg_end_x - bg_start_x) - text_width) // 2 + bg_start_x , ((bg_end_y - bg_start_y) - text_height) // 2 + bg_start_y + 2 *baseline  ), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 4)    
    
#     # 직선 넣기
#     cv2.line(RGB_image, (int(point1[0]),int(point1[1])), (int(point2[0]),int(point2[1])), (255, 255, 255), thickness=10, lineType=cv2.LINE_AA)

#     # keypoint 원 그리기
#     cv2.circle(RGB_image, (int(point1[0]),int(point1[1])), 12, (100, 150, 255), -1)
#     cv2.circle(RGB_image, (int(point2[0]),int(point2[1])), 12, (100, 150, 255), -1)
    
#     return RGB_image
        
        
        
        
        
        
        
        
        
        
        
        
        
########################** code refactoring **###################


import numpy as np
import json
from pathlib import Path

def adjust_keypoints(task_folder_path, world_xyz_array, target_point_1, target_point_2):
    print("Original keypoints:", [target_point_1, target_point_2])
    target_point_1, target_point_2 = fix_keypoint(task_folder_path, world_xyz_array, target_point_1[1], [target_point_1[0], target_point_2[0]])
    print("Adjusted keypoints:", [target_point_1, target_point_2])
    return target_point_1, target_point_2



def calculate_3d_length(world_xyz_array, target_point_1, target_point_2, api_key):
    length_3d = 0
    for i in range(target_point_1[0], target_point_2[0] - 1):
        try:
            pixel_length = np.linalg.norm(
                world_xyz_array[target_point_1[1], i] - world_xyz_array[target_point_1[1], i + 1]) * 100
            if api_key == "android":
                pixel_length /= 4.25
            if pixel_length < 3:
                length_3d += pixel_length
        except IndexError:
            continue
    return length_3d



def apply_measurement_scaling(measure_3d_result_dict, measure_name):
    scaling_factors = {
        'chest': 1.427,
        'waist': 1.322,
        'pelvis': 1.322,
        'hips': 1.53
    }
    model_name_map = {
        'chest': '가슴',
        'waist': '허리',
        'pelvis': '골반',
        'hips': '엉덩이'
    }
    if measure_name in scaling_factors:
        measure_3d_result_dict[measure_name] *= scaling_factors[measure_name]
        json_model_name = model_name_map[measure_name]
    else:
        json_model_name = measure_name
    return json_model_name



def save_measurement_to_json(task_folder_path, json_model_name, measure_value):
    json_file_path = Path(task_folder_path) / 'result_circum.json'
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        data[json_model_name] = round(measure_value, 0)
    except FileNotFoundError:
        data = {json_model_name: round(measure_value, 0)}
        
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)



def measure_3D_distance2(task_folder_path, model_name, measure_3d_result_dict, measure_dict, detected_keypoints, world_xyz_array, rgb_depth_ratio, RGB_image, api_key):
    for measure_name, measure_points in measure_dict.items():
        target_point_1 = np.array(np.array(detected_keypoints[measure_points[0] - 1]) / rgb_depth_ratio, dtype=np.int64)
        target_point_2 = np.array(np.array(detected_keypoints[measure_points[1] - 1]) / rgb_depth_ratio, dtype=np.int64)
        
        if measure_name == "leg":
            target_point_1, target_point_2 = adjust_keypoints(task_folder_path, world_xyz_array, target_point_1, target_point_2)
            pixel_length = np.linalg.norm(
                world_xyz_array[target_point_1[1], target_point_1[0]] - world_xyz_array[target_point_2[1], target_point_2[0]]) * 100
            if api_key == "android":
                pixel_length /= 4.25
            measure_3d_result_dict[measure_name] = pixel_length
            return measure_3d_result_dict, RGB_image
        
        # 3D 길이 계산
        target_point_1, target_point_2 = adjust_keypoints(task_folder_path, world_xyz_array, target_point_1, target_point_2)
        length_3d = calculate_3d_length(world_xyz_array, target_point_1, target_point_2, api_key)
        
        # 결과 저장
        if measure_name in measure_3d_result_dict:
            measure_3d_result_dict[measure_name] += length_3d
            json_model_name = apply_measurement_scaling(measure_3d_result_dict, measure_name)
            save_measurement_to_json(task_folder_path, json_model_name, measure_3d_result_dict[measure_name])
        else:
            measure_3d_result_dict[measure_name] = length_3d

    return measure_3d_result_dict, RGB_image

        
# ## 둘레 시각화
# def visualize_result(detected_keypoints, RGB_image, measure_name, measure_3d_result_dict):

#     # 키포인트 설정
#     point1 = (int(detected_keypoints[0][0]), int(detected_keypoints[0][1]))
#     point2 = (int(detected_keypoints[1][0]), int(detected_keypoints[1][1]))

#     # 타원 중심과 축 설정
#     real_center = ((point1[0] + point2[0]) / 2, point1[1])
#     real_axes = (abs(point1[0] - point2[0]) / 2, abs(point1[0] - point2[0]) / 6)
#     fixed_angle = [-35, 215]
#     axes_w = real_axes[0] / np.cos(np.radians(fixed_angle[0]))

#     # 타원 중심 및 축 계산
#     fixed_center = (int(real_center[0]), int(real_center[1] + axes_w * np.sin(np.radians(-fixed_angle[0])) / 6))
#     fixed_axes = (int(axes_w), int(axes_w // 6))

#     # 타원, 키포인트 원 그리기
#     cv2.ellipse(RGB_image, fixed_center, fixed_axes, 0, fixed_angle[0], fixed_angle[1], (255, 255, 255), thickness=10, lineType=cv2.LINE_AA)
#     cv2.circle(RGB_image, point1, 12, (100, 150, 255), -1)
#     cv2.circle(RGB_image, point2, 12, (100, 150, 255), -1)

#     # 측정값 텍스트 생성
#     text = f'{measure_name} : {measure_3d_result_dict[measure_name]:.2f}cm'
#     font, font_scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 1.3, 4
#     (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

#     # 텍스트 배경 위치 계산
#     start_x = int(point1[0] + (point2[0] - point1[0] - text_width) / 2)
#     start_y = int((point1[1] + point2[1]) / 2)
#     bg_start_x, bg_start_y = start_x - 45, start_y - text_height - baseline - 10
#     bg_end_x, bg_end_y = start_x + text_width + 45, start_y + baseline + 10

#     # 배경 및 텍스트 추가
#     cv2.rectangle(RGB_image, (bg_start_x, bg_start_y), (bg_end_x, bg_end_y), (255, 255, 255), -1)
#     cv2.rectangle(RGB_image, (bg_start_x, bg_start_y), (bg_end_x, bg_end_y), (100, 150, 255), 4)
#     cv2.putText(RGB_image, text, (start_x, start_y), font, font_scale, (0, 0, 0), thickness)

#     return RGB_image



# ## 길이 시각화
# def visualize_result_2d(task_folder_path, detected_keypoints, RGB_image, measure_name, measure_result_dict):
#     """
#     """
    
#     # 측정 결과를 JSON 파일에 저장
#     json_file_path = Path(task_folder_path) / 'result_circum.json'
#     try:
#         with open(json_file_path, 'r') as json_file:
#             data = json.load(json_file)
#     except FileNotFoundError:
#         data = {}

#     data['다리'] = round(measure_result_dict[measure_name], 0)

#     with open(json_file_path, 'w') as json_file:
#         json.dump(data, json_file, indent=4, ensure_ascii=False)
    
#     # 키포인트 설정
#     point1 = tuple(map(int, detected_keypoints[0]))
#     point2 = tuple(map(int, detected_keypoints[1]))
    
#     # 측정값 텍스트 생성
#     text = f'{measure_name} : {measure_result_dict[measure_name]:.2f}cm'
    
#     # 시각화 - 배경 사각형과 텍스트 넣기
#     font, font_scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 1.3, 4
#     (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

#     text_start_x = (point1[0] + point2[0]) // 2
#     text_start_y = (point1[1] + point2[1]) // 2
#     bg_start = (text_start_x - 10, text_start_y - text_height - baseline - 10)
#     bg_end = (text_start_x + text_width + 20, text_start_y + baseline + 10)

#     cv2.rectangle(RGB_image, bg_start, bg_end, (255, 255, 255), -1)  # 배경 사각형
#     cv2.rectangle(RGB_image, bg_start, bg_end, (100, 150, 255), 4)   # 배경 테두리
#     cv2.putText(RGB_image, text, (text_start_x, text_start_y + text_height), font, font_scale, (0, 0, 0), thickness)  # 텍스트

#     # 측정 구간 직선 및 키포인트 원 그리기
#     cv2.line(RGB_image, point1, point2, (255, 255, 255), thickness=10, lineType=cv2.LINE_AA)
#     cv2.circle(RGB_image, point1, 12, (100, 150, 255), -1)
#     cv2.circle(RGB_image, point2, 12, (100, 150, 255), -1)

#     return RGB_image