export async function fetchFileList() {
  // 예시 API 요청 (실제 엔드포인트로 변경 필요)
  const response = await fetch("/api/file-list");
  return response.json();
}

export async function evaluateFiles(gt, ai, threshold) {
  // 예시 API 요청 (실제 엔드포인트로 변경 필요)
  const response = await fetch("/api/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ gt, ai, threshold }),
  });
  return response.json();
}
