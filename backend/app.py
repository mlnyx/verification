from fastapi import FastAPI, Form
import os
import uvicorn
from eval import (
    load_json_file, group_annotations, build_category_map,
    compute_stats, summarize, BASE_DIR, GT_FOLDER, PRED_FOLDER
)

app = FastAPI()


def build_file_path(folder: str, filename: str) -> str:
    """폴더와 파일명을 받아 파일 경로 반환"""
    return os.path.join(BASE_DIR, folder, filename)


def load_and_prepare(gt_path: str, pred_path: str):
    """GT와 AI JSON 로드 및 annotation 준비"""
    gt_data = load_json_file(gt_path)
    pred_data = load_json_file(pred_path)

    if not (gt_data and pred_data):
        return None, None, None, "Invalid or empty JSON files."

    gt_anns = group_annotations(gt_data.get('annotations', []))
    pred_anns = group_annotations(pred_data.get('annotations', []))
    cat_map = build_category_map(gt_data.get('categories', []))

    return gt_anns, pred_anns, cat_map, None


@app.post("/evaluate-by-name/")
async def evaluate(gt_filename: str = Form(...), pred_filename: str = Form(...), threshold: float = Form(...)):
    gt_path = build_file_path(GT_FOLDER, gt_filename)
    pred_path = build_file_path(PRED_FOLDER, pred_filename)

    gt_anns, pred_anns, cat_map, error = load_and_prepare(gt_path, pred_path)
    if error:
        return {"error": error}

    stats = compute_stats(gt_anns, pred_anns, threshold)
    results = summarize(stats, cat_map)

    return {"iou_threshold": threshold, "results": results}

@app.get("/list-files/")
async def list_files():
    gt_path = os.path.join(BASE_DIR, GT_FOLDER)
    ai_path = os.path.join(BASE_DIR, PRED_FOLDER)

    gt_files = [f for f in os.listdir(gt_path) if f.endswith(".json")]
    ai_files = [f for f in os.listdir(ai_path) if f.endswith(".json")]

    return {"gt_files": gt_files, "ai_files": ai_files}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
