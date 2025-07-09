import axios from "axios";

export const fetchFileList = () => {
  return axios.get("http://localhost:8000/list-files/");
};

export const evaluateFiles = (gt, ai, threshold = 0.7) => {
  const formData = new FormData();
  formData.append("gt_filename", gt);
  formData.append("pred_filename", ai);
  formData.append("threshold", threshold);

  return axios.post("http://localhost:8000/evaluate-by-name/", formData);
};
