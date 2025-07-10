import os
from eval import CARIES_GROUP_IDS

def select_json_file(folder, desc="파일"):
    files = [f for f in os.listdir(folder) if f.endswith('.json')]
    print(f"\n {desc} 목록")
    for idx, f in enumerate(files, 1):
        print(f"[{idx}] {f}")
    choice = int(input(f"{desc} 번호를 선택하세요: ")) - 1
    return files[choice]

def create_category_map(categories):
    cat_map = {}
    printed = set()

    print("\n[라벨 목록 및 ID]\n----------------------------")
    for cat in categories:
        cat_id = cat["id"]
        if cat_id in CARIES_GROUP_IDS:
            if "caries" not in printed:
                print(f"caries (group ids: {CARIES_GROUP_IDS})")
                printed.add("caries")
            cat_map[cat_id] = "caries"
        else:
            print(f"{cat['name']} (id: {cat_id})")
            cat_map[cat_id] = cat["name"]
    return cat_map

def get_default_threshold():
    default_input = input("\n기본 IoU threshold 값을 입력하세요 (Enter = 0.5): ")
    return float(default_input) if default_input.strip() else 0.5

def get_special_ids():
    special_input = input("개별 IoU threshold를 설정할 라벨 id들을 쉼표로 입력하세요 (예: 11,17) (Enter = 없음): ")
    return [int(x.strip()) for x in special_input.split(",") if x.strip()] if special_input.strip() else []

def input_threshold_for_label(label_name, default_threshold):
    inp = input(f"{label_name} → IoU threshold 입력 (기본 {default_threshold}): \n")
    return float(inp) if inp.strip() else default_threshold

def get_iou_thresholds(cat_map):
    default_threshold = get_default_threshold()
    special_ids = get_special_ids()

    iou_thresholds = {}
    entered_groups = set()

    for cat_id, cat_name in cat_map.items():
        if cat_name == "caries":
            if "caries" in entered_groups:
                iou_thresholds[cat_id] = iou_thresholds["caries_group"]
                continue
            threshold = input_threshold_for_label("caries (group)", default_threshold)
            iou_thresholds["caries_group"] = threshold
            iou_thresholds[cat_id] = threshold
            entered_groups.add("caries")
        elif cat_id in special_ids:
            threshold = input_threshold_for_label(f"{cat_name} (id: {cat_id})", default_threshold)
            iou_thresholds[cat_id] = threshold
        else:
            iou_thresholds[cat_id] = default_threshold

    iou_thresholds.pop("caries_group", None)
    return iou_thresholds, default_threshold
