# 2화 Reference 이미지 교체 프리뷰

기존 저작권 문제가 있던 reference.jpg를 Unsplash 무료 이미지로 교체하고, 관련 이미지 14개를 전부 재생성한 결과.

Source: https://unsplash.com/photos/wRiVI9B1bek (Unsplash License)

## 참조 사진 vs ControlNet 결과

| 참조 사진 | txt2img | OpenPose |
|:---:|:---:|:---:|
| ![ref](reference.jpg) | ![txt2img](result_txt2img.png) | ![openpose](result_openpose.png) |

## 전처리 맵

| OpenPose | Canny | Depth |
|:---:|:---:|:---:|
| ![map_op](map_openpose.png) | ![map_ca](map_canny.png) | ![map_de](map_depth.png) |

## ControlNet 비교 (OpenPose / Canny / Depth)

| 참조 사진 | OpenPose | Canny | Depth |
|:---:|:---:|:---:|:---:|
| ![ref](reference.jpg) | ![openpose](result_openpose.png) | ![canny](result_canny.png) | ![depth](result_depth.png) |

## Strength 비교

| 0.3 | 1.0 | 1.5 | 1.8 |
|:---:|:---:|:---:|:---:|
| ![s03](cmp_strength_03.png) | ![s10](cmp_strength_10.png) | ![s15](cmp_strength_15.png) | ![s18](cmp_strength_18.png) |

## End Percent 비교

| 0.3 | 0.8 | 1.0 |
|:---:|:---:|:---:|
| ![e03](cmp_endpct_03.png) | ![e08](cmp_endpct_08.png) | ![e10](cmp_endpct_10.png) |
