from fastapi import FastAPI, Form
import os
from eval import (
    load_json_file, group_annotations, build_category_map,
    compute_stats, summarize, BASE_DIR, GT_FOLDER, PRED_FOLDER
)

app = FastAPI()

def get_file_path(folder: str, filename: str) -> str:
    """지정된 폴더에서 파일 경로 생성"""
    return os.path.join(BASE_DIR, folder, filename)

def prepare_annotations(gt_path: str, pred_path: str):
    """JSON 파일을 로드하고 annotation과 카테고리 맵 반환"""
    gt_data = load_json_file(gt_path)
    pred_data = load_json_file(pred_path)
    if not (gt_data and pred_data):
        return None, None, None, "Invalid or empty JSON files."
    gt_anns = group_annotations(gt_data.get('annotations', []))
    pred_anns = group_annotations(pred_data.get('annotations', []))
    cat_map = build_category_map(gt_data.get('categories', []))
    return gt_anns, pred_anns, cat_map, None

@app.post("/evaluate-by-name/")
async def evaluate_by_name(gt_filename: str = Form(...), pred_filename: str = Form(...), threshold: float = Form(...)):
    gt_path = get_file_path(GT_FOLDER, gt_filename)
    pred_path = get_file_path(PRED_FOLDER, pred_filename)

    gt_anns, pred_anns, cat_map, error = prepare_annotations(gt_path, pred_path)
    if error:
        return {"error": error}

    stats = compute_stats(gt_anns, pred_anns, threshold)
    results = summarize(stats, cat_map)

    return {"iou_threshold": threshold, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
