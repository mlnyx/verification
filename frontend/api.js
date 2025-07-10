export async function fetchFileList() {
  const response = await fetch("/api/file-list");
  return response.json();
}

export async function evaluateFiles(gt, ai, threshold) {
  const formData = new FormData();
  formData.append("gt_filename", gt);
  formData.append("pred_filename", ai);
  formData.append("threshold", threshold);

  const response = await fetch("/api/evaluate", {
    method: "POST",
    body: formData,
  });

  return response.json();
}
