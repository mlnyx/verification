import React, { useState, useEffect } from "react";
import { fetchFileList, evaluateFiles } from "../api";
import { DEFAULT_THRESHOLD } from "../constants";

function App() {
  const [gtFiles, setGtFiles] = useState([]);
  const [aiFiles, setAiFiles] = useState([]);
  const [selectedGT, setSelectedGT] = useState("");
  const [selectedAI, setSelectedAI] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchFileList()
      .then((res) => {
        setGtFiles(res.gt_files);
        setAiFiles(res.ai_files);
      })
      .catch(console.error);
  }, []);

  const handleAnalyze = async () => {
    if (!selectedGT || !selectedAI) return;
    setLoading(true);
    setResult(null);

    try {
      const res = await evaluateFiles(
        selectedGT,
        selectedAI,
        DEFAULT_THRESHOLD
      );
      setResult(res.results);
    } catch (error) {
      alert("분석 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h2>AI 검증 프로그램</h2>
      <p>GT, AI 파일을 선택 후 분석을 진행하세요.</p>

      <div>
        <label>
          GT 파일:
          <select
            value={selectedGT}
            onChange={(e) => setSelectedGT(e.target.value)}
          >
            <option value="">선택하세요</option>
            {gtFiles.map((file) => (
              <option key={file} value={file}>
                {file}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div>
        <label>
          AI 파일:
          <select
            value={selectedAI}
            onChange={(e) => setSelectedAI(e.target.value)}
          >
            <option value="">선택하세요</option>
            {aiFiles.map((file) => (
              <option key={file} value={file}>
                {file}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button
        onClick={handleAnalyze}
        disabled={!selectedGT || !selectedAI || loading}
      >
        {loading ? "분석 중..." : "분석"}
      </button>

      {result && (
        <div>
          <h3>결과</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
