"use client";

import React, { useCallback, useState, useRef } from "react";
import { Upload, FileText, X, Camera } from "lucide-react";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  disabled?: boolean;
}

export default function FileUpload({
  onFileSelect,
  accept = ".pdf,.txt,.png,.jpg,.jpeg,.dcm",
  disabled = false,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        const file = files[0];
        setSelectedFile(file);
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        setSelectedFile(files[0]);
        onFileSelect(files[0]);
      }
    },
    [onFileSelect]
  );

  const clearFile = () => {
    setSelectedFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
        disabled
          ? "opacity-50 cursor-not-allowed border-gray-300 dark:border-gray-700"
          : isDragging
          ? "border-primary-500 bg-primary-50 dark:bg-primary-950/30 scale-[1.02]"
          : "border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500 cursor-pointer"
      }`}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleFileInput}
        className="hidden"
        disabled={disabled}
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileInput}
        className="hidden"
        disabled={disabled}
      />

      {selectedFile ? (
        <div className="flex items-center justify-center gap-3">
          <FileText className="w-8 h-8 text-primary-500" />
          <div className="text-left">
            <p className="font-medium text-gray-900 dark:text-gray-100">
              {selectedFile.name}
            </p>
            <p className="text-sm text-gray-500">
              {(selectedFile.size / 1024).toFixed(1)} KB
            </p>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              clearFile();
            }}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <>
          <Upload
            className={`w-12 h-12 mx-auto mb-4 transition-colors ${
              isDragging
                ? "text-primary-500"
                : "text-gray-400 dark:text-gray-500"
            }`}
          />
          <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
            Drop your file here, or{" "}
            <span className="text-primary-600 dark:text-primary-400">
              browse
            </span>
          </p>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Supports PDF, TXT, Scanned Images (PNG/JPG with OCR Redaction), and DICOM (.dcm)
          </p>
          <div className="mt-4 flex items-center justify-center">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                if (!disabled) cameraInputRef.current?.click();
              }}
              className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900 border border-indigo-200 dark:border-indigo-800 shadow-sm transition-all"
            >
              <Camera className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              Scan Document with Camera
            </button>
          </div>
        </>
      )}
    </div>
  );
}
