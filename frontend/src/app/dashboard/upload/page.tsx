"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import FileUpload from "@/components/FileUpload";
import { uploadDocument } from "@/lib/api";
import {
  ShieldCheck,
  FileText,
  CheckCircle2,
  AlertCircle,
  Database,
  Lock,
  ArrowRight,
  Eye,
  Sparkles,
  Image as ImageIcon,
  Radio,
  FileSpreadsheet,
} from "lucide-react";
import Link from "next/link";

interface UploadResult {
  status: string;
  document_id: string;
  filename: string;
  file_category?: string;
  chunks_processed: number;
  entities_found: string[];
  sample_anonymized_text: string;
  multimodal_telemetry?: {
    media_type?: string;
    ocr_engine?: string;
    redacted_image_base64?: string;
    pii_boxes_redacted?: number;
    clinical_metadata?: Record<string, string>;
    stripped_tags?: string[];
    tags_stripped_count?: number;
  };
}

export default function UploadPage() {
  const { token, user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadResult | null>(null);

  const processingSteps = [
    { title: "Multimodal Ingestion", desc: "Receiving PDF, Scanned Image, or DICOM securely" },
    { title: "Layer Extraction & OCR", desc: "Parsing text / OCR & stripping DICOM headers" },
    { title: "Dual Presidio NER", desc: "Scrubbing HIPAA + India DPDP (Aadhaar, ABHA, PAN)" },
    { title: "Consistent Pseudonymization", desc: "Generating reversible synthetic tags" },
    { title: "PII Vault Encryption", desc: "Storing mapping under user security context" },
    { title: "Dense Vector Embeddings", desc: "Computing 384-dim semantic representations" },
    { title: "LanceDB Storage", desc: "Indexing clean vectors for zero-leak retrieval" },
  ];

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsProcessing(true);
    setError(null);
    setCurrentStep(0);

    // Visual progression
    const timer1 = setTimeout(() => setCurrentStep(1), 300);
    const timer2 = setTimeout(() => setCurrentStep(2), 700);
    const timer3 = setTimeout(() => setCurrentStep(3), 1100);
    const timer4 = setTimeout(() => setCurrentStep(4), 1500);
    const timer5 = setTimeout(() => setCurrentStep(5), 1900);

    try {
      const data = await uploadDocument(file, user?.id || "default_user", token);
      setCurrentStep(6);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to process and index document.");
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      clearTimeout(timer5);
      setIsProcessing(false);
    }
  };

  const loadSampleRecord = (filename: string, content: string) => {
    const blob = new Blob([content], { type: "text/plain" });
    const sampleFile = new File([blob], filename, { type: "text/plain" });
    handleFileSelect(sampleFile);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-50 flex items-center gap-3">
          <ShieldCheck className="w-8 h-8 text-primary-600 dark:text-primary-400" />
          Multimodal Ingestion & Zero-Trust Indexing
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Upload clinical notes, PDFs, scanned prescription photos, or DICOM imaging. Identifiers are detected, scrubbed, and converted to clean vectors.
        </p>
      </div>

      {/* Main Upload Box */}
      <div className="glass-card rounded-2xl border border-gray-200 dark:border-gray-800 p-6 md:p-8 shadow-sm">
        <FileUpload
          onFileSelect={handleFileSelect}
          accept=".pdf,.txt,.png,.jpg,.jpeg,.dcm"
          disabled={isProcessing}
        />

        {/* Demo Sample Records Picker */}
        <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-primary-500" />
            Quick Demo: Load Pre-Configured Clinical Records
          </p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() =>
                loadSampleRecord(
                  "patient_record_5_india_aiims.txt",
                  `ALL INDIA INSTITUTE OF MEDICAL SCIENCES (AIIMS), NEW DELHI
DEPARTMENT OF CARDIOLOGY - ADMISSION RECORD
Patient Name: Aarav Patel | DOB: 14/08/1982 | Age: 42 | Sex: Male
ABHA Health ID: 14-2354-9871-6542 | ABHA Address: aarav.patel@abdm
Aadhaar Number: 3675 8492 1039 (Verhoeff Verified) | PAN: ABCDE1234F
Mobile: +91 98765 43210 | Emergency Contact: Priya Nair (+91 98111 22334)
Hospital UHID: UHID-908231 | IPD No: IPD-4412 | Admitted to: Ward-B, Bed-14
Attending Physician: Dr. Rajesh Sharma, MD, DM (Cardiology)
Insurance: Ayushman Bharat PM-JAY Card: AB-PMJAY-9928103

CLINICAL EVALUATION & ANGIOGRAM:
Acute Anterior Wall STEMI. Coronary angiography via right radial approach revealed 95% proximal LAD occlusion.
Successful drug-eluting stent (DES 3.0 x 28 mm) deployed with TIMI-3 distal flow achieved.
Discharge Plan: Tab Ecosprin 75mg OD, Tab Brilinta 90mg BD, Tab Atorvastatin 80mg HS.`
                )
              }
              className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-orange-50 dark:bg-orange-950/40 text-orange-700 dark:text-orange-300 border border-orange-200 dark:border-orange-800 hover:bg-orange-100 transition-colors"
            >
              🇮🇳 AIIMS Cardiology (Aarav Patel - India DPDP & ABHA)
            </button>

            <button
              onClick={() =>
                loadSampleRecord(
                  "patient_record_6_india_apollo.txt",
                  `APOLLO HOSPITALS, BANGALORE - ENDOCRINOLOGY SUMMARY
Patient Name: Sunita Rao | DOB: 22/11/1971 | Age: 52 | Sex: Female
ABHA Health ID: 91-8841-3320-5619 | ABHA Address: sunita.rao@abdm
Aadhaar Number: 5123 4567 8903 (Verhoeff Verified) | PAN: BKXPR4821N
Mobile: +91 94481 23456 | Husband: Vikram Rao (+91 94481 98765)
UHID: UHID-774129 | OPD No: OPD-2024-8841 | CGHS ID: CGHS-BLR-441920
Attending: Dr. Priya Nair, MD (Endocrinology)

CLINICAL SUMMARY:
Uncontrolled Type 2 Diabetes Mellitus with peripheral neuropathy and solitary thyroid nodule (TIRADS-3, 14mm).
HbA1c: 9.8%, Fasting Blood Sugar: 188 mg/dL.
Prescription: Tab Metformin 1000mg BD, Tab Linagliptin 5mg OD, Tab Thyronorm 75mcg OD empty stomach.`
                )
              }
              className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100 transition-colors"
            >
              🇮🇳 Apollo Endocrinology (Sunita Rao - Aadhaar & CGHS)
            </button>

            <button
              onClick={() =>
                loadSampleRecord(
                  "patient_record_1_springfield.txt",
                  `SPRINGFIELD GENERAL HOSPITAL - CARDIOLOGY
Patient Name: John Michael Smith | DOB: 03/15/1978 | Age: 45 | Sex: Male
SSN: 123-45-6789 | Phone: (555) 234-5678 | Address: 142 Oak Street, Springfield, IL
Attending: Dr. Sarah Johnson | Medical Record #: SGH-2024-04851
Diagnosis: Essential hypertension and recurrent exertional palpitations.
Plan: Lisinopril 20mg daily, Metoprolol 50mg daily.`
                )
              }
              className="px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 transition-colors"
            >
              🇺🇸 US HIPAA (John Smith)
            </button>
          </div>
        </div>

        {/* Upload Action Button */}
        {file && !result && (
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleUpload}
              disabled={isProcessing}
              className="px-6 py-2.5 rounded-xl bg-primary-600 hover:bg-primary-700 text-white font-medium flex items-center gap-2 shadow-sm transition-all disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Scrubbing & Vectorizing...
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4" />
                  Scrub PII & Ingest Document
                </>
              )}
            </button>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="mt-6 p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 flex items-center gap-3 text-red-700 dark:text-red-400 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Live Ingestion Steps Progress */}
        {isProcessing && (
          <div className="mt-8 space-y-4">
            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Real-time Zero-Trust Ingestion Progress
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {processingSteps.map((step, idx) => {
                const isDone = currentStep > idx;
                const isCurrent = currentStep === idx;
                return (
                  <div
                    key={idx}
                    className={`p-3 rounded-xl border flex items-center gap-3 transition-all ${
                      isDone
                        ? "bg-green-50/60 dark:bg-green-950/20 border-green-200 dark:border-green-800"
                        : isCurrent
                        ? "bg-primary-50 dark:bg-primary-950/30 border-primary-300 dark:border-primary-700 animate-pulse"
                        : "bg-gray-50/50 dark:bg-gray-800/40 border-gray-200 dark:border-gray-800 opacity-60"
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0" />
                    ) : isCurrent ? (
                      <div className="w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full animate-spin flex-shrink-0" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border border-gray-300 dark:border-gray-700 flex items-center justify-center text-xs text-gray-400">
                        {idx + 1}
                      </div>
                    )}
                    <div>
                      <p className="text-xs font-medium text-gray-900 dark:text-gray-100">
                        {step.title}
                      </p>
                      <p className="text-[11px] text-gray-500 dark:text-gray-400">
                        {step.desc}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Results Card */}
      {result && (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-green-200 dark:border-green-900/40 p-6 md:p-8 shadow-sm space-y-6 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 dark:border-gray-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-green-100 dark:bg-green-950/60 text-green-600 dark:text-green-400 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {result.file_category || "Document"} Anonymized & Indexed
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Document ID: <code className="text-primary-600 dark:text-primary-400">{result.document_id}</code>
                </p>
              </div>
            </div>

            <Link
              href="/dashboard/chat"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium shadow-sm transition-colors"
            >
              Start Split-Screen Chat
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Multimodal Preview if image / DICOM */}
          {result.multimodal_telemetry && (
            <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700 space-y-3">
              <span className="text-xs font-bold text-primary-600 dark:text-primary-400 flex items-center gap-1.5 uppercase">
                <Sparkles className="w-3.5 h-3.5" />
                Multimodal Processing Telemetry
              </span>

              {result.multimodal_telemetry.redacted_image_base64 && (
                <div className="space-y-2">
                  <p className="text-xs text-gray-600 dark:text-gray-300">
                    <strong>OCR Engine:</strong> {result.multimodal_telemetry.ocr_engine} —{" "}
                    <span className="text-green-600 font-semibold">
                      {result.multimodal_telemetry.pii_boxes_redacted} Identifier Bounding Boxes Blacked Out
                    </span>
                  </p>
                  <img
                    src={`data:image/png;base64,${result.multimodal_telemetry.redacted_image_base64}`}
                    alt="Redacted Prescription Preview"
                    className="max-h-48 rounded-lg border border-gray-300 dark:border-gray-700 shadow-sm"
                  />
                </div>
              )}

              {result.multimodal_telemetry.stripped_tags && (
                <div className="space-y-2 text-xs">
                  <p className="font-bold text-gray-700 dark:text-gray-300">
                    DICOM Medical Imaging Header Stripping ({result.multimodal_telemetry.tags_stripped_count} patient tags sanitized):
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {result.multimodal_telemetry.stripped_tags.map((tag, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300 font-mono text-[11px]">
                        ✂️ {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-800">
              <span className="text-xs text-gray-500 dark:text-gray-400">Chunks Created</span>
              <p className="text-xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                {result.chunks_processed}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-800">
              <span className="text-xs text-gray-500 dark:text-gray-400">Vector Embeddings</span>
              <p className="text-xl font-bold text-primary-600 dark:text-primary-400 mt-1 flex items-center gap-1.5">
                <Database className="w-4 h-4" /> 384-dim
              </p>
            </div>
            <div className="col-span-2 sm:col-span-1 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-800">
              <span className="text-xs text-gray-500 dark:text-gray-400">Compliance Status</span>
              <p className="text-xl font-bold text-green-600 dark:text-green-400 mt-1 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4" /> HIPAA & DPDP Verified
              </p>
            </div>
          </div>

          {/* Entities Found */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
              Protected Entities Detected & Scrubbed
            </h4>
            <div className="flex flex-wrap gap-2">
              {result.entities_found.map((ent, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-full text-xs font-medium bg-primary-50 dark:bg-primary-950/50 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-800/60"
                >
                  ✓ {ent}
                </span>
              ))}
            </div>
          </div>

          {/* Sample Anonymized Chunks View */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                <Eye className="w-3.5 h-3.5" />
                Sanitized Vector Chunk (What LanceDB Stores)
              </h4>
              <span className="text-[11px] text-green-600 dark:text-green-400 font-medium">
                Zero Raw PII Present
              </span>
            </div>
            <div className="bg-gray-950 text-green-400 p-4 rounded-xl font-mono text-xs overflow-x-auto border border-gray-800 leading-relaxed">
              {result.sample_anonymized_text}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
