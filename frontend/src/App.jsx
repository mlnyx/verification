import React, { useState } from "react";
import Header from "./components/Header";
import FileSelector from "./components/FileSelector";

function App() {
  const [gtFiles] = useState(["PC.json"]);
  const [aiFiles] = useState(["250311_pc_output.json"]);

  const [selectedGT, setSelectedGT] = useState("");
  const [selectedAI, setSelectedAI] = useState("");

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="p-8 max-w-xl mx-auto">
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
      </main>
    </div>
  );
}

export default App;
