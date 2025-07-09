import React from "react";

const ResultCard = ({ category, data }) => {
  const accuracyColor =
    data.accuracy >= 80
      ? "bg-green-400"
      : data.accuracy >= 50
      ? "bg-yellow-400"
      : "bg-red-400";

  return (
    <div className="rounded-3xl bg-white/70 backdrop-blur-lg border border-gray-200 shadow-2xl p-6 transition transform hover:-translate-y-1 hover:shadow-3xl duration-300">
      <h3 className="text-lg font-bold text-gray-800 mb-3">{category}</h3>
      <p className="text-gray-700">
        <strong>Total GT:</strong> {data.total_gt}
      </p>
      <p className="text-gray-700">
        <strong>Detected:</strong> {data.detected}
      </p>
      <p className="text-gray-700">
        <strong>Accuracy:</strong> {data.accuracy}%
      </p>
      <div className="w-full bg-gray-200 rounded-full h-2.5 mt-3">
        <div
          className={`${accuracyColor} h-2.5 rounded-full transition-all duration-500`}
          style={{ width: `${data.accuracy}%` }}
        ></div>
      </div>
    </div>
  );
};

export default ResultCard;
