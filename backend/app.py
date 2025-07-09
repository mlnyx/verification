import uvicorn
from fastapi import FastAPI, UploadFile, Form
import shutil
import os
from eval import (
    load_json_file, group_annotations, build_category_map,
    compute_stats, summarize, BASE_DIR, GT_FOLDER, PRED_FOLDER
)

app = FastAPI()


def save_upload_file(upload_file: UploadFile, folder: str) -> str:
    """업로드된 파일을 지정 폴더에 저장"""
    file_path = os.path.join(BASE_DIR, folder, upload_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path


def prepare_data(gt_path: str, pred_path: str):
    """GT와 Prediction JSON 데이터를 로드하고 파싱"""
    gt_data = load_json_file(gt_path)
    pred_data = load_json_file(pred_path)
    if not (gt_data and pred_data):
        return None, None, None, "Invalid or empty JSON files."
    gt_anns = group_annotations(gt_data.get('annotations', []))
    pred_anns = group_annotations(pred_data.get('annotations', []))
    cat_map = build_category_map(gt_data.get('categories', []))
    return gt_anns, pred_anns, cat_map, None


@app.post("/evaluate/")
async def evaluate_endpoint(gt_file: UploadFile, pred_file: UploadFile, threshold: float = Form(...)):
    """평가 API 엔드포인트"""
    gt_path = save_upload_file(gt_file, GT_FOLDER)
    pred_path = save_upload_file(pred_file, PRED_FOLDER)

    gt_anns, pred_anns, cat_map, error = prepare_data(gt_path, pred_path)
    if error:
        return {"error": error}

    stats = compute_stats(gt_anns, pred_anns, threshold)
    results = summarize(stats, cat_map)

    return {"iou_threshold": threshold, "results": results}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
