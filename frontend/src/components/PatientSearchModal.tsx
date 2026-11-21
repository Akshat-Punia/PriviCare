"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  Search,
  X,
  User,
  Shield,
  FileText,
  Activity,
  HeartPulse,
  Stethoscope,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";

interface Patient {
  uhid: string;
  name: string;
  age: number;
  gender: string;
  blood_group?: string;
  department: string;
  abha_id?: string;
  aadhaar?: string;
  phone?: string;
  primary_diagnosis?: string;
  reports_count?: number;
}

const DEFAULT_PATIENTS: Patient[] = [
  {
    uhid: "UHID-982143",
    name: "Rajesh Sharma",
    age: 54,
    gender: "Male",
    blood_group: "B+",
    department: "Cardiology",
    abha_id: "91-4412-3390-1123",
    aadhaar: "9823 4410 7721",
    phone: "+91 98765 43210",
    primary_diagnosis: "Acute Coronary Syndrome, Mid-LAD DES Stent, Essential Hypertension",
    reports_count: 2,
  },
  {
    uhid: "UHID-447219",
    name: "Priya Patel",
    age: 46,
    gender: "Female",
    blood_group: "O+",
    department: "Oncology",
    abha_id: "91-8823-1104-5590",
    aadhaar: "4412 8890 2231",
    phone: "+91 98112 34567",
    primary_diagnosis: "Infiltrating Ductal Carcinoma (Grade II), ER/PR+, Post-Paclitaxel",
    reports_count: 2,
  },
  {
    uhid: "UHID-551029",
    name: "Amit Kumar",
    age: 62,
    gender: "Male",
    blood_group: "A+",
    department: "Pulmonology",
    abha_id: "91-3310-7744-8891",
    aadhaar: "7721 3340 9912",
    phone: "+91 98223 45678",
    primary_diagnosis: "Severe COPD Exacerbation, Chronic Bronchitis, Type 2 Respiratory Failure",
    reports_count: 1,
  },
];

interface PatientSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPatient?: (patient: Patient) => void;
}

export default function PatientSearchModal({
  isOpen,
  onClose,
  onSelectPatient,
}: PatientSearchModalProps) {
  const [query, setQuery] = useState("");
  const [selectedDept, setSelectedDept] = useState("ALL");
  const [patients, setPatients] = useState<Patient[]>(DEFAULT_PATIENTS);
  const [selectedUhid, setSelectedUhid] = useState<string>("UHID-982143");

  // Fetch clinical patients if API is reachable
  useEffect(() => {
    if (!isOpen) return;
    const fetchPatients = async () => {
      try {
        const res = await fetch("/api/clinical/patients");
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            setPatients(
              data.map((p: any) => ({
                uhid: p.uhid,
                name: p.name,
                age: p.age,
                gender: p.gender,
                blood_group: p.blood_group,
                department: p.department || "General",
                abha_id: p.abha_id,
                aadhaar: p.aadhaar,
                phone: p.phone,
                primary_diagnosis: p.primary_diagnosis,
                reports_count: p.reports ? p.reports.length : 1,
              }))
            );
          }
        }
      } catch {
        // Fallback to default mock patient registry
      }
    };
    fetchPatients();
  }, [isOpen]);

  // Keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (isOpen) onClose();
      } else if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  const filteredPatients = useMemo(() => {
    const q = query.toLowerCase().trim();
    return patients.filter((p) => {
      const matchDept =
        selectedDept === "ALL" ||
        p.department.toLowerCase() === selectedDept.toLowerCase();
      if (!matchDept) return false;
      if (!q) return true;

      return (
        p.name.toLowerCase().includes(q) ||
        p.uhid.toLowerCase().includes(q) ||
        (p.abha_id && p.abha_id.toLowerCase().includes(q)) ||
        (p.aadhaar && p.aadhaar.toLowerCase().includes(q)) ||
        (p.primary_diagnosis && p.primary_diagnosis.toLowerCase().includes(q)) ||
        p.department.toLowerCase().includes(q)
      );
    });
  }, [patients, query, selectedDept]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-start justify-center p-4 pt-16 overflow-y-auto animate-fade-in"
      onClick={onClose}
    >
      <div
        className="max-w-2xl w-full bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 overflow-hidden flex flex-col max-h-[85vh] my-4"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50/80 dark:bg-gray-950/80 flex items-center gap-3">
          <Search className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <input
            type="text"
            placeholder="Search patient by Name, UHID, ABHA ID, Aadhaar, Diagnosis, Department..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="flex-1 bg-transparent text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none font-medium"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Filter Pills */}
        <div className="px-4 py-2.5 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex items-center gap-2 overflow-x-auto text-xs">
          <span className="text-gray-400 font-medium">Department:</span>
          {["ALL", "Cardiology", "Oncology", "Pulmonology"].map((dept) => (
            <button
              key={dept}
              onClick={() => setSelectedDept(dept)}
              className={`px-3 py-1 rounded-full font-semibold transition-all ${
                selectedDept === dept
                  ? "bg-primary-600 text-white shadow-sm"
                  : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
              }`}
            >
              {dept === "ALL" ? "All Departments" : dept}
            </button>
          ))}
        </div>

        {/* Search Results List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2.5 max-h-[50vh]">
          {filteredPatients.length === 0 ? (
            <div className="py-10 text-center text-gray-400 space-y-2">
              <User className="w-10 h-10 mx-auto text-gray-300 dark:text-gray-700" />
              <p className="text-sm font-medium">No matching patient records found.</p>
              <p className="text-xs text-gray-500">
                Try searching by patient UHID (e.g. 982143), full name, or clinical condition.
              </p>
            </div>
          ) : (
            filteredPatients.map((p) => {
              const isActive = p.uhid === selectedUhid;
              return (
                <div
                  key={p.uhid}
                  onClick={() => {
                    setSelectedUhid(p.uhid);
                    onSelectPatient?.(p);
                    onClose();
                  }}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between gap-3 ${
                    isActive
                      ? "bg-primary-50/80 dark:bg-primary-950/40 border-primary-400 dark:border-primary-700 shadow-sm"
                      : "bg-white dark:bg-gray-800/60 border-gray-200 dark:border-gray-800 hover:border-primary-300 dark:hover:border-primary-700 hover:bg-primary-50/20"
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm shadow-sm flex-shrink-0 ${
                        isActive
                          ? "bg-primary-600 text-white"
                          : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                      }`}
                    >
                      {p.name
                        .split(" ")
                        .map((w) => w[0])
                        .slice(0, 2)
                        .join("")}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-sm text-gray-900 dark:text-gray-100 truncate">
                          {p.name}
                        </span>
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300 font-semibold">
                          {p.uhid}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                          {p.department}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                        {p.age} Yrs • {p.gender} • Blood {p.blood_group || "N/A"} •{" "}
                        <span className="italic text-gray-600 dark:text-gray-300">
                          {p.primary_diagnosis || "Clinical Record"}
                        </span>
                      </p>
                      <div className="flex items-center gap-3 mt-1 text-[10px] text-gray-400">
                        {p.abha_id && (
                          <span className="flex items-center gap-1">
                            <Shield className="w-3 h-3 text-teal-500" /> ABHA: {p.abha_id}
                          </span>
                        )}
                        {p.aadhaar && (
                          <span className="flex items-center gap-1">
                            <Activity className="w-3 h-3 text-blue-500" /> Aadhaar: {p.aadhaar}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <FileText className="w-3 h-3 text-indigo-500" />{" "}
                          {p.reports_count} Report{p.reports_count === 1 ? "" : "s"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex-shrink-0">
                    {isActive ? (
                      <span className="px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 font-bold text-[10px] flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Active
                      </span>
                    ) : (
                      <button
                        type="button"
                        className="px-3 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-xs font-semibold shadow transition-all"
                      >
                        Select
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Bar */}
        <div className="p-3 bg-gray-50 dark:bg-gray-950 border-t border-gray-200 dark:border-gray-800 flex items-center justify-between text-xs text-gray-500">
          <span>{filteredPatients.length} patient record(s) indexed in secure vault</span>
          <span className="text-gray-400">
            Press <kbd className="px-1.5 py-0.5 rounded bg-gray-200 dark:bg-gray-800 font-mono text-[10px]">Esc</kbd> to close
          </span>
        </div>
      </div>
    </div>
  );
}
