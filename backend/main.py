import os
from eval import load_json_file, group_annotations, compute_stats, summarize
from result import save_results_to_excel
from utils import select_json_file, create_category_map, get_iou_thresholds

# 설정
GT_FOLDER = "./backend/data/GT"
AI_FOLDER = "./backend/data/AI"
IMG_SIZE = (2000, 2000)
EXCEL_SAVE_PATH = "result.xlsx"

# GT & AI 파일 선택
GT_FILENAME = select_json_file(GT_FOLDER, "GT 파일")
AI_FILENAME = select_json_file(AI_FOLDER, "AI 파일")

gt_path = os.path.join(GT_FOLDER, GT_FILENAME)
ai_path = os.path.join(AI_FOLDER, AI_FILENAME)

# JSON 로드
gt_json = load_json_file(gt_path)
ai_json = load_json_file(ai_path)

# 어노테이션 준비
gt_anns = group_annotations(gt_json.get("annotations", []))
ai_anns = group_annotations(ai_json.get("annotations", []))
categories = gt_json.get("categories", [])

# 카테고리 map 생성
cat_map = create_category_map(categories)

# threshold 입력
iou_thresholds, default_threshold = get_iou_thresholds(cat_map)

# 평가 수행
stats = compute_stats(gt_anns, ai_anns, iou_thresholds, IMG_SIZE)
summary = summarize(stats, cat_map)

# summary에 threshold 추가
for cat_name, data in summary.items():
    for cat_id, name in cat_map.items():
        if name == cat_name:
            data["threshold"] = iou_thresholds.get(cat_id, default_threshold)
            break

# 정확도 기준 정렬
sorted_summary = dict(sorted(summary.items(), key=lambda x: x[1]["accuracy"], reverse=True))

# 엑셀 저장
save_results_to_excel(sorted_summary, EXCEL_SAVE_PATH)
