"""
- class dict : 대부분 1번에 점 개수만큼을 할당하면 될 것이다. 점 개수가 4개라면 1: (0, 4), 2:부터는 건드리지 않아도 된다.
- measure dict : 측정 대상이 되는 이름과 keypoint의 index 번호를 써준다. keypoint index는 라벨링할 때 찍은 점의 순서가 될 것이다.
  - 예를 들어, 가로가 0, 2 / 세로가 1, 3 이라면 {"Width": [0, 2], "Height": [1, 3]} 과 같이 정의하면 된다.
"""
"""
class_dict = {
    1: (0, 25), 2: (25, 58), 3: (58, 89), 4: (89, 128), 5: (128, 143),
    6: (143, 158), 7: (158, 168), 8: (168, 182), 9: (182, 190),
    10: (190, 219), 11: (219, 256), 12: (256, 275), 13: (275, 294)
}
"""

class_dict = {
  "clothes" : {
    1: (0, 25),
    2: (25, 58),
    3: (58, 89),
    4: (89, 128),
    5: (128, 143),
    6: (143, 158),
    7: (158, 168), 
    8: (168, 182), 
    9: (182, 190),
    10: (190, 219), 
    11: (219, 256), 
    12: (256, 275), 
    13: (275, 294)
  },
  "width" : {
    1: (0, 2)
  },
  "height" : {
    1: (0, 2)
  },
  "chest_waist" : {
    1 : (0, 4)
  },
  "handbag" : {
    1 : (0, 8)
  },
  "ice" : {
    1 : (0, 4)
  },
  "coffee_machine" : {
    1 : (0, 4)
  },
  "shoes" : {
    1 : (0, 4)
  },
  "biceps" : {
    1 : (0, 2)
  },
  "eye_horizontal" : {
    1 : (0, 2)
  },
  "tomato" : {
    1 : (0,4)
  },
  "tangerine" : {
    1 : (0,4)
  },
  "refrigerator" : {
    1 : (0,4)
  },
  "waist_upper_front" : {
    1 : (0,2)
  },
  "waist_upper_side" : {
    1 : (0,2)
  },
  "hips_lower_front" : {
    1 : (0,2)
  },
  "hips_lower_side" : {
    1 : (0,2)
  },
  "pelvis_lower_front" : {
    1 : (0,2)
  },
  "pelvis_lower_side" : {
    1 : (0,2)
  },
  "chest_upper_front" : {
    1 : (0,2)
  },
  "chest_upper_side" : {
    1 : (0,2)
  },
  "leg_lower_front" : {
    1 : (0,2)
  },
  "upper_removed_front" :{
    1 : (0, 4)
  },
  "upper_removed_side" :{
    1 : (0, 4)
  },
  "lower_removed_front" :{
    1 : (0, 6)
  },
  "lower_removed_side" :{
    1 : (0, 4)
  }
  
  
  
  
}

measure_dict = {
  "width": {
    "width" : [1, 2]
  },
  "height": {
    "height" : [1, 2]
  },
  "chest_waist": {
    "chest" : [1, 2],
    "waist" : [3, 4]
  },
  "handbag" : {
    "width" : [1, 3],
    "height" : [4, 8]
  },
  "ice":{
    "width": [1, 2],
    "height" : [1, 4]
  },
  "coffee_machine":{
    "width": [1, 2],
    "height" : [2, 3]
  },
  "refrigerator":{
    "width": [1, 2],
    "height" : [2, 3]
  },
  "waist_upper_side":{
    "waist": [1, 2]
  },
  "waist_upper_front":{
    "waist": [1, 2]
  },
  "hips_lower_side":{
    "hips": [1, 2]
  },
  "hips_lower_front":{
    "hips": [1, 2]
  }, 
  "pelvis_lower_side":{
    "pelvis": [1, 2]
  },
  "pelvis_lower_front":{
    "pelvis": [1, 2]
  },  
  "chest_upper_front":{
    "chest": [1, 2]
  },
  "chest_upper_side":{
    "chest": [1, 2]
  },
  "leg_lower_front":{
    "leg": [1, 2]
  }, 
  "upper_removed_side" :{
    "chest" : [1, 2],
    "waist" : [3, 4]
  },
  "upper_removed_front" :{
    "chest" : [1, 2],
    "waist" : [3, 4]
  },
  "lower_removed_front" :{
    "pelvis" : [1, 2],
    "hips" : [3, 4],
    "leg" : [5, 6]
  },
  "lower_removed_side" :{
    "pelvis" : [1, 2],
    "hips" : [3, 4]
  }
}


# Special Case : 재보시오

# clothes_measure_dict = {
#     "udlrpoint": {
#         1: [7, 16, 9, 23],
#         2: [7, 20, 11, 29],
#         3: [7, 16, 9, 23],
#         4: [7, 20, 11, 29],
#         5: [7, 11, 8, 14],
#         6: [7, 11, 8, 14],
#         7: [2, 6, 5, 9],
#         8: [2, 7, 6, 12],
#         9: [2, 6, 5, 7],
#         10: [7, 18, 9, 27],
#         11: [7, 22, 11, 33],
#         12: [7, 13, 12, 14],
#         13: [7, 13, 12, 14],
#         "default": [0, 0, 0, 0]
#     },
#     "meausreindex": {
#         1: {
#             "a": "Total-length",
#             "b": "Shoulder-length",
#             "c": "Waist-length",
#             "d": "Arm-length",
#             "e": "Arm-width"
#         },
#         2: {
#             "a": "Shoulder-length",
#             "b": "Chest-length",
#             "c": "Arm-length",
#             "d": "Waist-length"
#         },
#         3: {
#             "a": "Total-length",
#             "b": "Shoulder-length",
#             "c": "Waist-length",
#             "d": "Arm-length",
#             "e": "Arm-width"
#         },
#         4: {
#             "a": "Total-length",
#             "b": "Shoulder-length",
#             "c": "Waist-length",
#             "d": "Arm-length",
#             "e": "Arm-width"
#         },
#         5: {
#             "a": "Total-length",
#             "b": "Shoulder-length",
#             "c": "Waist-length"
#         },
#         6: {
#             "a": "Total-length",
#             "b": "Shoulder-length",
#             "c": "Waist-length"
#         },
#         7: {
#             "a": "Total-length",
#             "b": "Pants-waist-length",
#             "c": "Hole-width"
#         },
#         8: {
#             "a": "Pants-waist-length",
#             "b": "Pants-length",
#             "c": "Hole-width"
#         },
#         9: {
#             "a": "Pants-waist-length",
#             "b": "Hole-width",
#             "c": "Total-length"
#         },
#         10: {
#             "a": "Shoulder-length",
#             "b": "Chest-length",
#             "c": "Hole-width"
#         },
#         11: {
#             "a": "Total-length",
#             "b": "Shoulder-length",
#             "c": "Arm-length",
#             "d": "Arm-width",
#             "e": "OnePiece-bottom-length"
#         },
#         12: {
#             "a": "Total-length",
#             "b": "Shoulder-length",
#             "c": "OnePiece-bottom-length"
#         },
#         13: {
#             "a": "Total-length",
#             "b": "Shoulder-length",
#             "c": "OnePiece-bottom-length"
#         }
#     },
#     "measurepoint": {
#         1: {
#             "a": [1, 16],    # 총장
#             "b": [7, 25],    # 어깨
#             "c": [15, 17],    # 허리
#             "d": [7, 9],    # 소매길이
#             "e": [9, 10]    # 소매너비
#         },
#         2: {
#             "a": [7, 33],    # 어깨
#             "b": [17, 23],    # 가슴
#             "c": [7, 11],    # 소매길이
#             "d": [19, 21]    # 허리
#         },
#         3: {
#             "a": [1 ,16],    # 총장
#             "b": [7, 25],    # 어깨
#             "c": [15, 17],    # 허리
#             "d": [7, 9],    # 소매길이
#             "e": [9, 10]    # 소매너비
#         },
#         4: {
#             "a": [1, 20],    # 총장
#             "b": [7, 33],    # 어깨
#             "c": [19, 21],    # 허리
#             "d": [7, 11],    # 소매길이
#             "e": [11, 12]    # 소매너비
#         },
#         5: {
#             "a": [1, 11],    # 총장
#             "b": [7, 15],    # 어깨
#             "c": [10, 12]    # 허리
#         },
#         6: {
#             "a": [1, 11],    # 총장
#             "b": [7, 15],    # 어깨
#             "c": [10, 12]    # 허리
#         },
#         7: {
#             "a": [3, 9],    # 총장
#             "b": [1, 3],    # 허리
#             "c": [5, 6]    # 밑단
#         },
#         8: {
#             "a": [1, 3],    # 허리
#             "b": [2, 9],    # 밑위
#             "c": [6, 7]    # 밑단
#         },
#         9: {
#             "a": [1, 3],    # 허리
#             "b": [5, 7],    # 밑단
#             "c": [2, 6]    # 총장
#         },
#         10: {
#             "a": [7, 29],    # 어깨
#             "b": [13, 23],    # 가슴
#             "c": [17, 19]    # 밑단
#         },
#         11: {
#             "a": [1, 22],    # 총장
#             "b": [7, 37],    # 어깨
#             "c": [7, 11],    # 소매길이
#             "d": [11, 12],    # 소매너비
#             "e": [21, 23]    # 밑단
#         },
#         12: {
#             "a": [1, 13],    # 총장
#             "b": [7, 19],    # 어깨
#             "c": [12, 14]    # 밑단
#         },
#         13: {
#             "a": [1, 13],    # 총장
#             "b": [7, 19],    # 어깨
#             "c": [12, 14]    # 밑단
#         }
#     }
# }































