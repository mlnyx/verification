import React from "react";

const FileSelector = ({ type, files, selectedFile, onChange }) => {
  return (
    <div className="mb-4">
      <label className="block mb-1 font-medium text-gray-700">
        {type} 파일 선택
      </label>
      <select
        value={selectedFile}
        onChange={(e) => onChange(e.target.value)}
        className="w-full p-2 border rounded"
      >
        <option value="">파일을 선택하세요</option>
        {files.map((file) => (
          <option key={file} value={file}>
            {file}
          </option>
        ))}
      </select>
    </div>
  );
};

export default FileSelector;
