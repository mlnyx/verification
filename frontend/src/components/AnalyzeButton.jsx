import React from "react";

const AnalyzeButton = ({ onClick, disabled }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full p-3 mt-4 font-semibold rounded transition
        ${
          disabled
            ? "bg-gray-300 text-gray-500 cursor-not-allowed"
            : "bg-blue-600 text-white hover:bg-blue-700"
        }`}
    >
      분석 시작
    </button>
  );
};

export default AnalyzeButton;
