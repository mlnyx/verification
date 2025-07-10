import pandas as pd

def save_results_to_excel(summary, file_path="result.xlsx"):
    df = pd.DataFrame([
        {
            "라벨 이름": label,
            "전체 탐지 개수": data["total_gt"],
            "일치 개수": data["detected"],
            "정확도(%)": data["accuracy"],
            "IoU threshold": data["threshold"]
        }
        for label, data in summary.items()
    ])
    df.to_excel(file_path, index=False)
    print(f"결과가 {file_path} 파일로 저장되었습니다.")
