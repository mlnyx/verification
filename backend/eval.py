import json
from collections import defaultdict
import numpy as np
from PIL import Image, ImageDraw


class PolygonUtils:
    """폴리곤 관련 도구 함수 모음 (마스크 변환, IoU 계산 등)"""

    @staticmethod
    def polygon_to_mask(polygon, img_size):
        """폴리곤 좌표를 마스크(바이너리 이미지)로 변환"""
        mask = Image.new('L', img_size, 0)
        draw = ImageDraw.Draw(mask)
        points = [tuple(polygon[i:i+2]) for i in range(0, len(polygon), 2)]
        draw.polygon(points, outline=1, fill=1)
        return np.array(mask)

    @staticmethod
    def compute_mask_iou(poly1, poly2, img_size):
        """두 폴리곤의 IoU 계산"""
        assert len(poly1) > 0 and len(poly2) > 0, "Polygon segmentation 데이터가 비어있습니다."
        mask1 = PolygonUtils.polygon_to_mask(poly1, img_size)
        mask2 = PolygonUtils.polygon_to_mask(poly2, img_size)
        inter = np.logical_and(mask1, mask2).sum()
        union = np.logical_or(mask1, mask2).sum()
        return inter / union if union else 0.0


class AnnotationMatcher:
    """GT ↔ Pred 매칭을 담당하는 클래스 (strict 1:1 matching 지원)"""

    def __init__(self, caries_ids):
        self.caries_ids = caries_ids
        self.main_caries_id = next(iter(caries_ids))

    def is_same_group(self, gt_id, pred_id):
        """
        평가할 때 GT와 예측 라벨이 같은지 확인
        - caries 그룹은 하나로 묶어서 처리
        - 그 외는 category_id가 같아야 함
        """
        both_caries = gt_id in self.caries_ids and pred_id in self.caries_ids
        return both_caries or (gt_id == pred_id)

    def match_gt_to_preds(self, gt_ann, pred_list, threshold, used_preds, img_size):
        """
        GT annotation 하나에 대해 pred_list에서 IoU threshold 이상 매칭되는 예측 찾기
        - 매칭된 pred는 used_preds에 True로 표시
        """
        for idx, pred_ann in enumerate(pred_list):
            if used_preds[idx]:
                continue
            if not self.is_same_group(gt_ann["category_id"], pred_ann["category_id"]):
                continue

            iou = PolygonUtils.compute_mask_iou(gt_ann["segmentation"][0], pred_ann["segmentation"][0], img_size)
            if iou >= threshold:
                used_preds[idx] = True
                return True
        return False


class Evaluator:
    """전체 평가를 담당하는 클래스"""

    def __init__(self, gt_path, ai_path, iou_thresholds, caries_ids, img_size=(2000, 2000)):
        self.gt_json = self._load_json(gt_path)
        self.ai_json = self._load_json(ai_path)
        self.categories = self.gt_json.get("categories", [])
        self.iou_thresholds = iou_thresholds
        self.img_size = img_size
        self.matcher = AnnotationMatcher(caries_ids)
        self.main_caries_id = next(iter(caries_ids))
        self.cat_map = self._build_category_map(caries_ids)
        self.caries_ids = caries_ids 

    def _load_json(self, path):
        """JSON 파일을 읽어서 딕셔너리 반환"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}

    def _build_category_map(self, caries_ids):
        """category ID와 이름 매핑 생성"""
        cat_map = {}
        for cat in self.categories:
            cat_id = cat.get("id")
            cat_map[cat_id] = "caries" if cat_id in caries_ids else cat.get("name")
        return cat_map

    def _group_annotations(self, anns):
        """이미지 + 카테고리 기준으로 annotation 그룹화"""
        grouped = defaultdict(list)
        for ann in anns:
            key = (ann["image_id"], ann["category_id"])
            grouped[key].append(ann)
        return grouped

    def _get_image_size(self, image_id):
        """image_id에 맞는 이미지 크기(width, height)를 반환"""
        for img in self.gt_json.get("images", []):
            if img["id"] == image_id:
                return (img["width"], img["height"])
        return self.img_size  # 못 찾으면 기본값 반환

    def compute_stats(self):
        """전체 GT와 예측 annotation에 대해 통계 계산"""
        gt_anns = self._group_annotations(self.gt_json.get("annotations", []))
        pred_anns = self._group_annotations(self.ai_json.get("annotations", []))
        stats = defaultdict(lambda: {"total": 0, "detected": 0, "fp": 0, "fn": 0})

        for (img_id, cat_id), gt_list in gt_anns.items():
            group_id = cat_id if cat_id not in self.matcher.caries_ids else self.main_caries_id
            pred_list = pred_anns.get((img_id, cat_id), [])
            self._process_group(gt_list, pred_list, group_id, cat_id, stats)

        return stats

    def _process_group(self, gt_list, pred_list, group_id, cat_id, stats):
        """GT 그룹과 pred_list를 평가하고 stats를 업데이트"""
        used_preds = [False] * len(pred_list)

        for gt_ann in gt_list:
            self._evaluate_single_gt(gt_ann, pred_list, used_preds, cat_id, group_id, stats)

        # 사용 안 된 pred 개수를 FP로 추가
        unused_preds = used_preds.count(False)
        stats[group_id]["fp"] += unused_preds
        stats[group_id]["fn"] = stats[group_id]["total"] - stats[group_id]["detected"]

    def _evaluate_single_gt(self, gt_ann, pred_list, used_preds, cat_id, group_id, stats):
        """GT annotation 하나 평가 및 stats 반영"""
        threshold = self.iou_thresholds.get(cat_id, 0.5)
        img_size = self._get_image_size(gt_ann["image_id"])
        detected = self.matcher.match_gt_to_preds(gt_ann, pred_list, threshold, used_preds, img_size)
        stats[group_id]["total"] += 1
        if detected:
            stats[group_id]["detected"] += 1

    def summarize(self, stats):
        """통계 요약 (카테고리별 총 개수, 검출 개수, 정확도, FP 등)"""
        summary = {}
        for cat_id, counts in stats.items():
            total = counts["total"]
            detected = counts["detected"]
            fp = counts["fp"]
            fn = counts["fn"]
            acc = (detected / total * 100) if total else 0.0
            label = self.cat_map.get(cat_id, f"Unknown({cat_id})")
            threshold = self.iou_thresholds.get(cat_id, 0.5)
            summary[label] = {
                "total_gt": total,
                "detected": detected,
                "fp": fp,
                "fn": fn,
                "accuracy": round(acc, 2),
                "threshold": threshold
            }
        return summary
