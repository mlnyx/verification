import React from "react";

const ResultTable = ({ results }) => {
  if (!results) return null;

  const categories = Object.entries(results);

  return (
    <div className="mt-8 bg-white rounded shadow overflow-x-auto">
      <table className="min-w-full text-sm text-gray-700">
        <thead className="bg-gray-200">
          <tr>
            <th className="px-4 py-2 text-left">카테고리</th>
            <th className="px-4 py-2 text-right">Total GT</th>
            <th className="px-4 py-2 text-right">Detected</th>
            <th className="px-4 py-2 text-right">Accuracy (%)</th>
          </tr>
        </thead>
        <tbody>
          {categories.map(([category, data]) => (
            <tr key={category} className="border-t">
              <td className="px-4 py-2">{category}</td>
              <td className="px-4 py-2 text-right">{data.total_gt}</td>
              <td className="px-4 py-2 text-right">{data.detected}</td>
              <td className="px-4 py-2 text-right">{data.accuracy}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ResultTable;
