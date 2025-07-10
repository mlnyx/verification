import pandas as pd

def save_results_to_excel(summary, file_path="result.xlsx"):
    df = pd.DataFrame([
        {"라벨 이름": k, "전체 탐지 개수": v["total_gt"],
         "일치 개수": v["detected"], "정확도(%)": v["accuracy"],
         "IoU threshold": v["threshold"]}
        for k, v in summary.items()
    ])
    df.to_excel(file_path, index=False)
    print(f" {file_path} 저장 완료!")
