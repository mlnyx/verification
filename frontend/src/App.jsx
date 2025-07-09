import React from "react";
import Header from "./components/Header";

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="p-8">
        <h2 className="text-2xl font-semibold mb-4">AI 검증 프로그램</h2>
        <p className="text-gray-700">
          GT, AI 파일을 선택 후 분석을 진행하세요.
        </p>
      </main>
    </div>
  );
}

export default App;
