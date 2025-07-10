import json
from collections import defaultdict
import numpy as np
from PIL import Image, ImageDraw

class Evaluator:
    def __init__(self, gt_path, ai_path, iou_thresholds, img_size=(2000, 2000)):
        self.gt_json = self._load_json(gt_path)
        self.ai_json = self._load_json(ai_path)
        self.categories = self.gt_json.get("categories", [])
        self.caries_ids = {11, 12, 13}
        self.cat_map = self._build_category_map()
        self.iou_thresholds = iou_thresholds
        self.img_size = img_size

    def _load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}

    def _build_category_map(self):
        cat_map = {}
        for cat in self.categories:
            cat_id = cat.get("id")
            cat_map[cat_id] = "caries" if cat_id in self.caries_ids else cat.get("name")
        return cat_map

    def _polygon_to_mask(self, polygon):
        mask = Image.new('L', self.img_size, 0)
        draw = ImageDraw.Draw(mask)
        points = [tuple(polygon[i:i+2]) for i in range(0, len(polygon), 2)]
        draw.polygon(points, outline=1, fill=1)
        return np.array(mask)

    def _compute_iou(self, poly1, poly2):
        mask1 = self._polygon_to_mask(poly1)
        mask2 = self._polygon_to_mask(poly2)
        inter = np.logical_and(mask1, mask2).sum()
        union = np.logical_or(mask1, mask2).sum()
        return inter / union if union else 0.0

    def _is_same_group(self, gt_id, pred_id):
        both_caries = gt_id in self.caries_ids and pred_id in self.caries_ids
        return both_caries or (gt_id == pred_id)

    def _match_pred(self, gt_ann, pred_list, threshold):
        for pred_ann in pred_list:
            if not self._is_same_group(gt_ann["category_id"], pred_ann["category_id"]):
                continue
            iou = self._compute_iou(gt_ann["segmentation"][0], pred_ann["segmentation"][0])
            if iou >= threshold:
                return True
        return False

    def _group_annotations(self, anns):
        grouped = defaultdict(list)
        for ann in anns:
            key = (ann["image_id"], ann["category_id"])
            grouped[key].append(ann)
        return grouped

    def _process_single_gt(self, gt_ann, pred_list):
        cat_id = gt_ann["category_id"]
        threshold = self.iou_thresholds.get(cat_id, 0.5)
        return self._match_pred(gt_ann, pred_list, threshold)

    def _update_stats(self, stats, group_id, detected):
        stats[group_id]["total"] += 1
        if detected:
            stats[group_id]["detected"] += 1

    def compute_stats(self):
        gt_anns = self._group_annotations(self.gt_json.get("annotations", []))
        pred_anns = self._group_annotations(self.ai_json.get("annotations", []))
        stats = defaultdict(lambda: {"total": 0, "detected": 0})

        for (img_id, cat_id), gt_list in gt_anns.items():
            group_id = cat_id if cat_id not in self.caries_ids else next(iter(self.caries_ids))
            pred_list = pred_anns.get((img_id, cat_id), [])

            for gt_ann in gt_list:
                detected = self._process_single_gt(gt_ann, pred_list)
                self._update_stats(stats, group_id, detected)

        return stats

    def summarize(self, stats):
        summary = {}
        for cat_id, counts in stats.items():
            total = counts["total"]
            detected = counts["detected"]
            acc = (detected / total * 100) if total else 0.0
            label = self.cat_map.get(cat_id, f"Unknown({cat_id})")
            threshold = self.iou_thresholds.get(cat_id, 0.5)
            summary[label] = {
                "total_gt": total,
                "detected": detected,
                "accuracy": round(acc, 2),
                "threshold": threshold
            }
        return summary
