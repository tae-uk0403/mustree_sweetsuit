import cv2
import torch
import numpy as np
import asyncio

import torchvision.transforms as transforms
from . import pose_hrnet
from ..measure.class_dict import *
from .inference import *
from .transforms import get_affine_transform, transform_preds

import cv2
import matplotlib.pyplot as plt


def find_keypoint(
    task_folder_path, body_position, model_name, model_position, image_name
):

    model = pose_hrnet.get_pose_net(is_train=False).cuda()
    pretraind_model = (
        f"api/sweet_suit/removed_bg_model/{body_position}/{model_position}.pth"
    )
    model.load_state_dict(torch.load(pretraind_model), strict=True)

    c, s, r = (
        np.array([719.5, 959.5]),
        np.array([11.368751, 15.158334]),
        0,
    )  # center, scale, rotation
    # 이미지 크기에 맞는 [1920, 1440] c, s, r 이다.
    if body_position == "lower":
        c, s, r = (
            np.array([719.5, 1440]),
            np.array([5, 6.6666]),
            0,
        )  # center, scale, rotation
        # c는 [x,y]임 지금 이미지에서는 [719.5, 959.5]가 center가 되는 것

    # 필요한 transform 불러오기
    trans = get_affine_transform(c, s, r, [288, 384])
    print("trans shape is : ", trans.shape)

    # evaluation mode
    model.eval()

    # [1920, 1440] 크기의 이미지 파일
    img_file = str(task_folder_path / image_name)

    # input 전처리
    data_numpy = cv2.imread(img_file, cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)
    input = cv2.warpAffine(
        data_numpy,
        trans,
        (288, 384),  # 이 모델의 input size는 (288, 384)로 고정이다.
        flags=cv2.INTER_LINEAR,
    )

    input_img_rgb = cv2.cvtColor(input, cv2.COLOR_BGR2RGB)

    # 6. 변환된 이미지 저장
    save_path = str(task_folder_path / "transformed_image.jpg")
    cv2.imwrite(save_path, input_img_rgb)

    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    )

    it = transforms.Compose(
        [
            transforms.ToTensor(),
            normalize,
        ]
    )

    input = it(input)
    input = torch.unsqueeze(input, 0).cuda()

    with torch.no_grad():

        cat_idx = 1  # gt_class_keypoints_dict 즉, 어떤 객체 클래스인지를 말한다. 여기서는 반팔로 테스트할 것이기 때문에 1을 넣었는데,
        # 아마 모든 클래스를 1로 학습했을 것이기 때문에 1을 그대로 사용하면 될 것이다. 물론 1: (n, n)은 바꿔야 함.

        channel_mask = torch.zeros((1, 294, 1)).cuda(non_blocking=True).float()
        cat_ids = [cat_idx]

        # gt_class_keypoints_dict를 통해 해당 클래스에서 찾을 점들의 인덱스 중 처음과 끝을 저장
        cat_idx_start = class_dict[model_position][int(cat_idx)][0]
        cat_idx_end = class_dict[model_position][int(cat_idx)][1]

        # 해당 클래스에서 찾을 점들을 인덱싱하기 위한 channel_mask 변경
        for j, cat_id in enumerate(cat_ids):
            rg = class_dict[model_position][int(cat_id)]
            index = (
                torch.tensor(
                    [list(range(rg[0], rg[1]))],
                    device=channel_mask.device,
                    dtype=channel_mask.dtype,
                )
                .transpose(1, 0)
                .long()
            )
            channel_mask[j].scatter_(0, index, 1)

        output = model(input)
        output = output * channel_mask.unsqueeze(3)

        # preds_local은 작은 사이즈 (정확히는 히트맵 사이즈)에서 찾은 점들의 위치이다.
        preds_local, maxvals = get_final_preds(output.detach().cpu().numpy(), c, s)

        # preds로 원래 이미지 크기 [1920, 1400] 에서의 점의 위치를 찾는다.
        preds = preds_local.copy()
        for tt in range(preds_local.shape[0]):
            preds[tt] = transform_preds(preds_local[tt], c, s, [72, 96])

        f_preds = preds[0][cat_idx_start:cat_idx_end]

    key_result = np.array(f_preds)  # 최종 keypoints 좌표들
    return key_result


async def async_find_keypoints(
    task_folder_path, upper_or_lower, model_name, model_name_with_position, image_name
):
    """비동기로 키포인트 탐지 처리"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        find_keypoint,
        task_folder_path,
        upper_or_lower,
        model_name,
        model_name_with_position,
        image_name,
    )
