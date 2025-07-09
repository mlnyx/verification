import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import FileSelector from "./components/FileSelector";
import AnalyzeButton from "./components/AnalyzeButton";
import ResultGrid from "./components/ResultGrid";
import { fetchFileList, evaluateFiles } from "../api/evaluation";
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
        setGtFiles(res.data.gt_files);
        setAiFiles(res.data.ai_files);
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
      setResult(res.data.results);
    } catch (error) {
      alert("분석 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="p-8 max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold mb-4">AI 검증 프로그램</h2>
        <p className="text-gray-700 mb-6">
          GT, AI 파일을 선택 후 분석을 진행하세요.
        </p>

        <FileSelector
          type="GT"
          files={gtFiles}
          selectedFile={selectedGT}
          onChange={setSelectedGT}
        />
        <FileSelector
          type="AI"
          files={aiFiles}
          selectedFile={selectedAI}
          onChange={setSelectedAI}
        />

        <AnalyzeButton
          onClick={handleAnalyze}
          disabled={!selectedGT || !selectedAI || loading}
        />

        {loading && <p className="mt-4 text-blue-500">분석 중...</p>}
        {result && <ResultGrid results={result} />}
      </main>
    </div>
  );
}

export default App;
