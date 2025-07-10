import os
from eval import load_json_file, group_annotations, build_category_map, compute_stats, summarize
from result import save_results_to_excel

# ======================
# 설정 부분
# ======================
GT_FOLDER = "./backend/data/GT"
AI_FOLDER = "./backend/data/AI"
GT_FILENAME = "PC.json"        # 비교할 GT 파일 이름
AI_FILENAME = "250311_pc_output.json"        # 비교할 AI 파일 이름
IOU_THRESHOLD = 0.5            # IoU 임계값
IMG_SIZE = (2000, 2000)        # 마스크 생성 시 사용할 이미지 크기
EXCEL_SAVE_PATH = "result.xlsx" # 저장할 엑셀 파일 이름

# ======================
# 파일 경로
# ======================
gt_path = os.path.join(GT_FOLDER, GT_FILENAME)
ai_path = os.path.join(AI_FOLDER, AI_FILENAME)

# ======================
# JSON 로드
# ======================
gt_json = load_json_file(gt_path)
ai_json = load_json_file(ai_path)

# ======================
# 데이터 준비
# ======================
gt_anns = group_annotations(gt_json.get("annotations", []))
ai_anns = group_annotations(ai_json.get("annotations", []))
cat_map = build_category_map(gt_json.get("categories", []))

# ======================
# 평가 수행
# ======================
stats = compute_stats(gt_anns, ai_anns, IOU_THRESHOLD, IMG_SIZE)
summary = summarize(stats, cat_map)

# ======================
# 결과 출력 및 저장
# ======================
save_results_to_excel(summary, EXCEL_SAVE_PATH)
