import React from "react";
import ResultCard from "./ResultCard";

const ResultGrid = ({ results }) => {
  if (!results) return null;

  const categories = Object.entries(results);

  return (
    <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {categories.map(([category, data]) => (
        <ResultCard key={category} category={category} data={data} />
      ))}
    </div>
  );
};

export default ResultGrid;
