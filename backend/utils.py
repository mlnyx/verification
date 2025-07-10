import os

def list_json(folder, desc="파일"):
    files = [f for f in os.listdir(folder) if f.endswith('.json')]
    print(f"\n📄 {desc}")
    for i, f in enumerate(files, 1):
        print(f"[{i}] {f}")
    idx = int(input(f"{desc} 번호 선택: ")) - 1
    return files[idx]

def get_categories(json_obj):
    cat_list = json_obj.get("categories", [])
    for cat in cat_list:
        print(f"{cat['name']} (id: {cat['id']})")
    return {cat['id']: cat['name'] for cat in cat_list}

def auto_generate_mapping(gt_cats, ai_cats):
    """이름 기반 자동 매핑"""
    mapping = {}
    gt_names = {v.lower().replace(" ", ""): k for k, v in gt_cats.items()}
    for ai_id, ai_name in ai_cats.items():
        simplified_ai = ai_name.lower().replace(" ", "")
        matched_gt_id = None
        for gt_simple_name, gt_id in gt_names.items():
            if simplified_ai in gt_simple_name or gt_simple_name in simplified_ai:
                matched_gt_id = gt_id
                break
        if matched_gt_id:
            mapping[ai_id] = matched_gt_id
    return mapping

def print_auto_mapping(mapping, gt_cats, ai_cats):
    print("\n🔎 자동 생성된 매핑")
    for ai_id, gt_id in mapping.items():
        print(f"AI {ai_cats[ai_id]} (id: {ai_id}) ➜ GT {gt_cats[gt_id]} (id: {gt_id})")

def input_manual_mapping(gt_cats, ai_cats):
    print("\n💬 매핑 예: 11:21,12:22")
    mapping_str = input("GT id → AI id 매핑을 입력하세요: ")
    mapping = {}
    for pair in mapping_str.split(","):
        if ":" in pair:
            gt_id, ai_id = map(int, pair.split(":"))
            mapping[ai_id] = gt_id
    return mapping

def apply_category_mapping(ai_json, id_mapping):
    for ann in ai_json.get("annotations", []):
        old_id = ann["category_id"]
        if old_id in id_mapping:
            ann["category_id"] = id_mapping[old_id]
    return ai_json

def show_categories(cat_map, caries_ids):
    print("\n[라벨 목록 및 ID]")
    printed = set()
    for cid, name in cat_map.items():
        if name == "caries":
            if "caries" not in printed:
                print(f"caries (group ids: {caries_ids})")
                printed.add("caries")
        else:
            print(f"{name} (id: {cid})")

def get_threshold_input(prompt, default_val):
    val = input(f"{prompt} (기본 {default_val}): ")
    return float(val) if val.strip() else default_val

def parse_special_ids():
    ids_str = input("개별 설정할 id들 (쉼표, Enter=없음): ")
    if not ids_str.strip():
        return []
    return [int(x.strip()) for x in ids_str.split(",") if x.strip()]

def assign_threshold(thresholds, cid, value):
    thresholds[cid] = value

def set_thresholds(cat_map, caries_ids):
    default_t = get_threshold_input("기본 IoU threshold", 0.5)
    special_ids = parse_special_ids()

    thresholds = {}
    entered_caries = False

    for cid, name in cat_map.items():
        if name == "caries":
            if entered_caries:
                assign_threshold(thresholds, cid, thresholds["caries_group"])
                continue
            t = get_threshold_input("caries (group)", default_t)
            thresholds["caries_group"] = t
            assign_threshold(thresholds, cid, t)
            entered_caries = True
        elif cid in special_ids:
            t = get_threshold_input(f"{name} (id: {cid})", default_t)
            assign_threshold(thresholds, cid, t)
        else:
            assign_threshold(thresholds, cid, default_t)

    thresholds.pop("caries_group", None)
    return thresholds
