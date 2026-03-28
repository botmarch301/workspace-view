# 3화. 얼굴 교체 — ReActor로 원하는 얼굴 넣기

*AI 이미지 생성 실전 가이드 | 여성 캐릭터 일러스트를 만들며 배운 것들*

---

## 들어가며

2화에서 ControlNet으로 포즈를 잡는 방법을 다뤘다. 원하는 포즈는 나오는데, 얼굴이 마음에 들지 않을 수 있다. 매번 다른 얼굴이 나오고, 특정 얼굴을 재현하기도 어렵다.

이 문제를 해결하는 방법이 얼굴 교체(face swap)다. 참조 사진에서 얼굴 정보를 추출하고, 생성된 이미지의 얼굴을 교체한다.

| 원본 (생성 이미지) | 참조 얼굴 | 교체 결과 |
|:---:|:---:|:---:|
| ![before](images/real_before.png) | ![source](images/face_source.jpg) | ![after](images/real_swap_cf05.png) |


## ReActor란

ReActor는 ComfyUI에서 사용할 수 있는 얼굴 교체 확장이다. InsightFace의 얼굴 인식 모델과 inswapper 모델을 사용해서, 한 이미지의 얼굴을 다른 이미지의 얼굴로 교체한다.

기본 원리:

1. 참조 이미지에서 얼굴을 감지하고 특징(embedding)을 추출한다
2. 대상 이미지에서 교체할 얼굴을 감지한다
3. 참조 얼굴의 특징을 대상 얼굴에 합성한다
4. (선택) 얼굴 복원 모델로 품질을 보정한다


## 환경 준비

### ReActor 설치

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/Gourieff/ComfyUI-ReActor
cd ComfyUI-ReActor
pip install -r requirements.txt
```

!!! warning "기존 저장소 차단"
    `comfyui-reactor-node`(소문자, 하이픈) 저장소는 GitHub에서 차단됐다. `ComfyUI-ReActor`(대문자, 하이픈 없음)가 현재 사용 가능한 저장소다.

### 모델 다운로드

ReActor에 필요한 모델은 두 가지다.

1. **inswapper_128.onnx** — 얼굴 교체 핵심 모델
2. **InsightFace 모델** — 얼굴 감지/인식

inswapper_128.onnx는 직접 다운로드해서 `models/insightface/` 디렉토리에 넣는다.

```bash
cd ComfyUI/models/insightface/
wget https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx
```

InsightFace 모델(buffalo_l)은 첫 실행 시 자동으로 다운로드된다. 약 326MB다.

### 얼굴 복원 모델

ReActor 첫 실행 시 얼굴 복원 모델도 자동 다운로드된다.

| 모델 | 용도 | 크기 |
|------|------|------|
| CodeFormer | 얼굴 품질 복원. weight로 강도 조절 가능 | 359MB |
| GFPGANv1.3 / v1.4 | 얼굴 품질 복원. 고정 강도 | 332MB |
| GPEN-BFR-512 | 얼굴 복원 (ONNX 기반) | 271MB |

첫 실행에 약 1.3GB의 모델이 다운로드된다. 시간이 걸리므로 기다려야 한다.


## 워크플로 구성

기본 txt2img 워크플로에 ReActor 노드를 추가한다.

```
[체크포인트] → [프롬프트] → [KSampler] → [VAE 디코드] → [ReActorFaceSwap] → [저장]
                                                              ↑
                                                    [참조 얼굴 이미지]
```

핵심 노드:

1. **Load Image** — 참조할 얼굴 이미지를 불러온다
2. **ReActorFaceSwap** — 얼굴 교체를 수행한다

### ReActorFaceSwap 주요 설정

| 설정 | 설명 | 기본값 |
|------|------|--------|
| swap_model | 교체 모델 | inswapper_128.onnx |
| facedetection | 얼굴 감지 방식 | retinaface_resnet50 |
| face_restore_model | 복원 모델 | none / codeformer / GFPGAN |
| face_restore_visibility | 복원 적용 강도 | 1.0 |
| codeformer_weight | CodeFormer 충실도 | 0.5 |
| input_faces_index | 대상 이미지에서 교체할 얼굴 번호 | 0 (첫 번째 얼굴) |
| source_faces_index | 참조 이미지에서 사용할 얼굴 번호 | 0 |


## 얼굴 복원 모델 비교

ReActor의 얼굴 교체는 해상도가 128x128로 고정이다. 교체된 얼굴을 원본 해상도에 맞춰 확대하면 흐릿해진다. 이때 얼굴 복원 모델이 디테일을 보정한다.

| 복원 없음 | GFPGAN | CodeFormer 0.5 |
|:---:|:---:|:---:|
| ![raw](images/real_swap_raw.png) | ![gfpgan](images/real_swap_gfpgan.png) | ![cf05](images/real_swap_cf05.png) |

- **복원 없음**: 교체된 얼굴이 흐릿하다. 배경과 몸의 선명도와 차이가 난다.
- **GFPGAN**: 선명해지지만 피부가 과하게 매끈해질 수 있다.
- **CodeFormer**: 자연스러운 보정. weight로 강도를 조절할 수 있다.

### CodeFormer weight

CodeFormer의 weight는 복원 충실도를 조절한다. 낮을수록 원본(교체된 얼굴)에 가깝고, 높을수록 적극적으로 보정한다.

| Weight 0.3 | Weight 0.5 | Weight 1.0 |
|:---:|:---:|:---:|
| ![cf03](images/real_swap_cf03.png) | ![cf05](images/real_swap_cf05.png) | ![cf10](images/real_swap_cf10.png) |

차이는 미세하다. 0.5가 일반적으로 적절한 균형점이다. 얼굴이 너무 흐릿하면 weight를 올리고, 과하게 보정된 느낌이면 내린다.


## 참조 이미지 선택

얼굴 교체의 품질은 참조 이미지에 크게 좌우된다.

**좋은 참조 이미지:**
- 얼굴이 정면에 가까운 각도
- 조명이 균일하다
- 표정이 자연스럽다
- 해상도가 충분하다

**나쁜 참조 이미지:**
- 극단적인 측면 각도
- 강한 그림자가 얼굴을 가린다
- 과한 표정 (입을 크게 벌리거나 눈을 감은 경우)
- 저해상도

여러 장의 참조 이미지를 써서 결과를 비교하고, 가장 자연스러운 것을 고르는 과정이 필요하다.


## 스타일을 맞춰야 한다

처음에 애니메 스타일 이미지에 실사 얼굴을 교체해봤다. 결과는 이랬다.

| 애니메 원본 | 애니메 + 얼굴 교체 |
|:---:|:---:|
| ![anime_before](images/before_swap.png) | ![anime_after](images/swap_codeformer_05.png) |

몸은 애니메인데 얼굴만 실사다. 실제로 쓸 수 없는 수준이다.

같은 참조 얼굴을 실사 스타일 이미지에 교체하면 결과가 완전히 달라진다.

| 실사 원본 | 실사 + 얼굴 교체 |
|:---:|:---:|
| ![real_before](images/real_before.png) | ![real_after](images/real_swap_cf05.png) |

ReActor의 inswapper 모델은 실사 얼굴 데이터로 학습됐다. 실사 이미지에서 작동하도록 만들어진 도구를 애니메 이미지에 쓰면 당연히 어색하다. 얼굴 교체를 쓸 거라면 생성 이미지의 스타일을 실사 또는 반실사로 맞추는 것이 전제다.

프롬프트에서 "anime, cartoon, illustration"을 네거티브에 넣고, "realistic, photorealistic"을 포지티브에 넣는 것만으로도 결과가 크게 달라진다.


## 삽질 기록

### 기존 ReActor 저장소 차단

`comfyui-reactor-node` 저장소가 GitHub에서 접근 차단되어 있었다. 클론 시 403 에러가 난다. `ComfyUI-ReActor`(대소문자 주의)가 현재 사용 가능한 저장소다. AI 이미지 도구는 저장소가 자주 이동하거나 차단되므로, 설치 실패 시 이름이 바뀌었는지 먼저 확인한다.

### 첫 실행 시 대량 다운로드

ReActor를 처음 실행하면 얼굴 복원 모델(codeformer, GFPGANv1.3, GFPGANv1.4, GPEN), InsightFace 모델(buffalo_l), NSFW 감지 모델이 자동으로 다운로드된다. 총 약 2GB. 첫 실행이 유독 느리면 다운로드가 진행 중인 것이다. ComfyUI 로그를 확인하면 진행 상황을 볼 수 있다.

### inswapper 모델 위치

inswapper_128.onnx의 위치에 주의해야 한다. `models/insightface/` 디렉토리에 넣어야 한다. `models/insightface/models/` 안에 넣으면 인식하지 못할 수 있다.


## 정리

3화에서 배운 것:

- **ReActor**로 생성된 이미지의 얼굴을 참조 사진의 얼굴로 교체할 수 있다
- **inswapper_128.onnx**가 교체 핵심 모델이다
- **얼굴 복원 모델**(CodeFormer, GFPGAN)로 교체 후 품질을 보정한다
- **CodeFormer weight 0.5**가 일반적으로 적절한 균형점이다
- 애니메와 실사 간 **스타일 불일치**는 완전히 해결하기 어렵다
- 참조 이미지는 **정면, 균일 조명, 자연스러운 표정**이 기본이다

포즈(ControlNet)와 얼굴(ReActor)을 제어할 수 있게 됐다. 다음 화에서는 생성된 이미지의 해상도를 높이는 업스케일 방법을 다룬다.

---

*이전: [2화. 구도와 포즈 — ControlNet 입문](ai-image-guide-02-controlnet.md)*
*다음: [4화. 업스케일 — 해상도 높이기]*
