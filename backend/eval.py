import json
from collections import defaultdict
import numpy as np
from PIL import Image, ImageDraw

CARIES_GROUP_IDS = {11, 12, 13}

def load_json_file(path):
    """JSON 파일 로드"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {path}: {e}")
        return {}

def polygon_to_mask(polygon, img_size):
    """폴리곤 좌표를 마스크 이미지로 변환"""
    mask = Image.new('L', img_size, 0)
    draw = ImageDraw.Draw(mask)
    points = [tuple(polygon[i:i+2]) for i in range(0, len(polygon), 2)]
    draw.polygon(points, outline=1, fill=1)
    return np.array(mask)

def compute_iou(poly1, poly2, img_size):
    """두 폴리곤 간 IoU 계산"""
    mask1 = polygon_to_mask(poly1, img_size)
    mask2 = polygon_to_mask(poly2, img_size)
    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()
    return intersection / union if union else 0.0

def group_annotations(annotations):
    """(image_id, category_id) 기준으로 annotation 그룹화"""
    grouped = defaultdict(list)
    for ann in annotations:
        key = (ann.get('image_id'), ann.get('category_id'))
        grouped[key].append(ann)
    return grouped

def build_category_map(categories):
    """category_id ↔ name 매핑 생성"""
    cat_map = {}
    for cat in categories:
        cat_id = cat.get('id')
        cat_map[cat_id] = 'caries' if cat_id in CARIES_GROUP_IDS else cat.get('name')
    return cat_map

def is_same_group(gt_id, pred_id):
    """두 category_id가 같은 그룹인지 판단"""
    return (gt_id in CARIES_GROUP_IDS and pred_id in CARIES_GROUP_IDS) or gt_id == pred_id

def is_gt_detected(gt_ann, pred_list, threshold, img_size):
    """GT annotation이 예측에서 검출되었는지 판단"""
    return any(
        is_same_group(gt_ann['category_id'], pred['category_id']) and
        compute_iou(gt_ann['segmentation'][0], pred['segmentation'][0], img_size) >= threshold
        for pred in pred_list
    )

def compute_stats(gt_anns, pred_anns, threshold, img_size):
    """IoU threshold 기준으로 통계 계산"""
    stats = defaultdict(lambda: {'total': 0, 'detected': 0})
    for (img_id, cat_id), gt_list in gt_anns.items():
        group_id = cat_id if cat_id not in CARIES_GROUP_IDS else next(iter(CARIES_GROUP_IDS))
        stats[group_id]['total'] += len(gt_list)
        preds = pred_anns.get((img_id, cat_id), [])
        stats[group_id]['detected'] += sum(is_gt_detected(gt, preds, threshold, img_size) for gt in gt_list)
    return stats

def summarize(stats, cat_map):
    """통계를 정리해 카테고리별 성능 요약"""
    results = {}
    for cat_id, cnt in stats.items():
        total, detected = cnt['total'], cnt['detected']
        acc = (detected / total * 100) if total else 0.0
        name = cat_map.get(cat_id, f'Unknown({cat_id})')
        results[name] = {
            'total_gt': total,
            'detected': detected,
            'accuracy': round(acc, 2)
        }
    return results
