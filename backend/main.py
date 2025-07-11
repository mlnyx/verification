import os
import json
from eval import Evaluator
from utils import list_json, get_categories, auto_generate_mapping, print_auto_mapping, input_manual_mapping, apply_category_mapping, show_categories, set_thresholds
from result import save_results_to_excel

GT_FOLDER = "./backend/data/GT"
AI_FOLDER = "./backend/data/AI"
IMG_SIZE = (2000, 2000)
EXCEL_PATH = "result.xlsx"

# 파일 선택
gt_file = list_json(GT_FOLDER, "GT 파일")
ai_file = list_json(AI_FOLDER, "AI 파일")

gt_path = os.path.join(GT_FOLDER, gt_file)
ai_path = os.path.join(AI_FOLDER, ai_file)

# JSON 로드
with open(gt_path, 'r', encoding='utf-8') as f:
    gt_json = json.load(f)
with open(ai_path, 'r', encoding='utf-8') as f:
    ai_json = json.load(f)

# 카테고리 출력
print("\nGT 라벨")
gt_cats = get_categories(gt_json)
print("\nAI 라벨")
ai_cats = get_categories(ai_json)

# 자동 매핑
auto_mapping = auto_generate_mapping(gt_cats, ai_cats)
print_auto_mapping(auto_mapping, gt_cats, ai_cats)

# 사용자 확인
confirm = input("\n자동 매핑을 사용할까요? (Enter = 예, n = 직접 입력): ")
if confirm.strip().lower() == "n":
    manual_mapping = input_manual_mapping(gt_cats, ai_cats)
    final_mapping = manual_mapping
else:
    final_mapping = auto_mapping

# AI JSON에 매핑 적용
ai_json = apply_category_mapping(ai_json, final_mapping)

# 임시 파일 저장
temp_ai_path = "./backend/data/AI/_temp_mapped_ai.json"
with open(temp_ai_path, 'w', encoding='utf-8') as f:
    json.dump(ai_json, f, indent=2)

# Evaluator
tmp_eval = Evaluator(gt_path, temp_ai_path, {}, IMG_SIZE)
show_categories(tmp_eval.cat_map, tmp_eval.caries_ids)
thresh = set_thresholds(tmp_eval.cat_map, tmp_eval.caries_ids)

eval_final = Evaluator(gt_path, temp_ai_path, thresh, IMG_SIZE)
stats = eval_final.compute_stats()
summary = eval_final.summarize(stats)
sorted_summary = dict(sorted(summary.items(), key=lambda x: x[1]["accuracy"], reverse=True))

save_results_to_excel(sorted_summary, EXCEL_PATH)
