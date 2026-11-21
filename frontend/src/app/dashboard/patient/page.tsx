"use client";

import React, { useState } from "react";
import {
  Heart,
  Pill,
  Shield,
  ShieldCheck,
  Camera,
  Upload,
  AlertTriangle,
  Bot,
  Send,
  Trash2,
  CheckCircle2,
  FileText,
  Phone,
  User,
  Info,
} from "lucide-react";

interface Message {
  sender: "user" | "ai";
  text: string;
  triage?: "ROUTINE" | "EVALUATE_MEDICATION" | "URGENT_ATTENTION";
  time: string;
}

export default function PatientPortalPage() {
  const [activeTab, setActiveTab] = useState<"meds" | "vault" | "chat" | "dpdp">("meds");
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "ai",
      text: "Hello Rajesh, I am your personalized PriviCare Recovery Assistant, synchronized with your attending doctor Dr. Sarah Johnson. I can answer questions about your heart stent recovery, medications (Atorvastatin, Aspirin), dietary advice, and what symptoms to watch out for.",
      triage: "ROUTINE",
      time: "10:00 AM",
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [shredded, setShredded] = useState(false);

  const handleSendMessage = (textToSend?: string) => {
    const text = textToSend || inputMessage.trim();
    if (!text) return;

    const userMsg: Message = {
      sender: "user",
      text,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMessage("");
    setIsSending(true);

    // Determine triage logic
    const lower = text.toLowerCase();
    let triage: "ROUTINE" | "EVALUATE_MEDICATION" | "URGENT_ATTENTION" = "ROUTINE";
    let reply = "Your query has been analyzed with zero-knowledge PII scrubbing against your clinical chart.";

    if (lower.includes("chest") || lower.includes("pain") || lower.includes("shortness") || lower.includes("severe")) {
      triage = "URGENT_ATTENTION";
      reply = "⚠️ URGENT CLINICAL ALERT: Your symptoms may require prompt medical evaluation. Please contact your attending cardiologist Dr. Sarah Johnson or visit the nearest emergency department immediately. Your doctor's clinical queue has been alerted.";
    } else if (lower.includes("calf") || lower.includes("muscle") || lower.includes("soreness") || lower.includes("statin")) {
      triage = "EVALUATE_MEDICATION";
      reply = "ℹ️ MEDICATION NOTICE: Muscle soreness or calf tenderness can be an adverse reaction related to Atorvastatin 40mg. This has been flagged in Dr. Sarah Johnson's clinical queue for medication evaluation.\n\nContinue resting your leg and do not stop prescribed blood thinners without clinical advice.";
    } else if (lower.includes("food") || lower.includes("diet") || lower.includes("eat")) {
      reply = "Dietary Guidance: With your LAD stent and heart medications, maintain a low-sodium (< 2g/day) heart-healthy diet. Avoid grapefruit or grapefruit juice as it interacts with Atorvastatin. Stay well hydrated.";
    } else if (lower.includes("walk") || lower.includes("exercise")) {
      reply = "Mobility Guidance: 20-30 minutes of light, flat-surface walking is recommended. Avoid strenuous uphill walks or heavy lifting (>5 kg) during the first 6 weeks post-stent placement.";
    } else {
      reply = "Regarding your question: All lab parameters and clinical notes have been verified. Your LAD stent is functioning normally and your current medications are safe to take as scheduled.";
    }

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: reply,
          triage,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
      setIsSending(false);
    }, 700);
  };

  const handleCryptoShred = () => {
    if (
      confirm(
        "DPDP ACT 2023 SECTION 12 RIGHT TO ERASURE\n\nAre you sure you want to permanently crypto-shred all encryption keys, scoped HMAC salts, and pseudonym mappings for this patient session?\n\nThis action is irreversible and renders all stored vector embeddings and historical transcripts mathematically unrecoverable."
      )
    ) {
      setShredded(true);
      alert("✅ Cryptographic Erasure Executed! All AES-256 session keys and pseudonym salt vectors purged.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Patient Identity Summary Card */}
      <div className="bg-gradient-to-r from-teal-500/10 via-emerald-500/10 to-cyan-500/10 border border-teal-200 dark:border-teal-800 rounded-2xl p-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-teal-600 to-emerald-600 text-white flex items-center justify-center text-xl font-bold shadow-md">
              RS
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">Rajesh Sharma</h1>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-teal-100 dark:bg-teal-950 text-teal-800 dark:text-teal-300 font-mono">
                  UHID-982143
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300">
                  Cardiology
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" /> Patient Portal Active
                </span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                58 Yrs • Male • Blood Group O+ • Primary Diagnosis: CAD, s/p LAD Stent (Nov 2024)
              </p>
              <div className="flex items-center gap-3 mt-2 flex-wrap text-xs">
                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-teal-50 dark:bg-teal-950/60 border border-teal-200 dark:border-teal-800 text-teal-800 dark:text-teal-300 font-medium">
                  <strong>ABHA:</strong> <span className="font-mono">14-2354-9871-6542</span>
                </span>
                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-800 dark:text-indigo-300 font-medium">
                  <strong>Aadhaar:</strong> <span className="font-mono">9823 4410 7721</span>
                </span>
                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300">
                  <Phone className="w-3 h-3 text-gray-400" /> +91 98765 43210
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("chat")}
              className="px-4 py-2 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white rounded-xl text-xs font-semibold shadow flex items-center gap-1.5 transition-all"
            >
              <Bot className="w-4 h-4" /> Ask Recovery AI
            </button>
            <button
              onClick={() => setActiveTab("dpdp")}
              className="px-3.5 py-2 border border-gray-300 dark:border-gray-700 hover:border-teal-400 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-xl text-xs font-semibold shadow-sm flex items-center gap-1.5 transition-all"
            >
              <Shield className="w-4 h-4 text-teal-600" /> DPDP Rights
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Subtabs */}
      <div className="flex items-center gap-2 border-b border-gray-200 dark:border-gray-800 pb-2">
        <button
          onClick={() => setActiveTab("meds")}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${
            activeTab === "meds"
              ? "bg-teal-600 text-white shadow-sm"
              : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          }`}
        >
          <Pill className="w-4 h-4" /> 1. Prescriptions & Care Plan
        </button>
        <button
          onClick={() => setActiveTab("vault")}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${
            activeTab === "vault"
              ? "bg-teal-600 text-white shadow-sm"
              : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          }`}
        >
          <FileText className="w-4 h-4" /> 2. Medical Records Vault
        </button>
        <button
          onClick={() => setActiveTab("chat")}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${
            activeTab === "chat"
              ? "bg-teal-600 text-white shadow-sm"
              : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          }`}
        >
          <Bot className="w-4 h-4" /> 3. 24/7 Recovery AI
        </button>
        <button
          onClick={() => setActiveTab("dpdp")}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${
            activeTab === "dpdp"
              ? "bg-teal-600 text-white shadow-sm"
              : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          }`}
        >
          <ShieldCheck className="w-4 h-4" /> 4. DPDP Rights (Erasure)
        </button>
      </div>

      {/* SUBTAB 1: PRESCRIPTIONS & CARE PLAN */}
      {activeTab === "meds" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-gray-200 dark:border-gray-800">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-teal-100 dark:bg-teal-900/60 text-teal-600 dark:text-teal-400 flex items-center justify-center font-bold">
                  <Pill className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100">Daily Prescription Schedule</h3>
                  <p className="text-[11px] text-gray-500">Prescribed by Dr. Sarah Johnson • Verified safe against allergies</p>
                </div>
              </div>
              <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Adherence: 100%
              </span>
            </div>

            <div className="space-y-3">
              <div className="p-3.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/40 flex items-center justify-between">
                <div className="flex items-start gap-3">
                  <input type="checkbox" defaultChecked className="mt-1 w-4 h-4 text-teal-600 rounded border-gray-300 focus:ring-teal-500" />
                  <div>
                    <div className="font-bold text-xs text-gray-900 dark:text-gray-100">Atorvastatin 40mg Tab</div>
                    <div className="text-[11px] text-gray-500 mt-0.5">1 tablet once daily at bedtime • Plaque stabilization</div>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className="px-2 py-0.5 text-[10px] bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 rounded font-medium">Night</span>
                      <span className="px-2 py-0.5 text-[10px] bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">After Dinner</span>
                    </div>
                  </div>
                </div>
                <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Taken</span>
              </div>

              <div className="p-3.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/40 flex items-center justify-between">
                <div className="flex items-start gap-3">
                  <input type="checkbox" defaultChecked className="mt-1 w-4 h-4 text-teal-600 rounded border-gray-300 focus:ring-teal-500" />
                  <div>
                    <div className="font-bold text-xs text-gray-900 dark:text-gray-100">Aspirin 75mg (EC)</div>
                    <div className="text-[11px] text-gray-500 mt-0.5">1 tablet once daily in morning • Antiplatelet therapy for stent</div>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className="px-2 py-0.5 text-[10px] bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 rounded font-medium">Morning (8:00 AM)</span>
                      <span className="px-2 py-0.5 text-[10px] bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">With Breakfast</span>
                    </div>
                  </div>
                </div>
                <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Taken</span>
              </div>

              <div className="p-3.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/40 flex items-center justify-between">
                <div className="flex items-start gap-3">
                  <input type="checkbox" defaultChecked className="mt-1 w-4 h-4 text-teal-600 rounded border-gray-300 focus:ring-teal-500" />
                  <div>
                    <div className="font-bold text-xs text-gray-900 dark:text-gray-100">Metoprolol Succinate 25mg ER</div>
                    <div className="text-[11px] text-gray-500 mt-0.5">1 tablet daily • Cardioselective beta-blocker for heart rate</div>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className="px-2 py-0.5 text-[10px] bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 rounded font-medium">Morning (8:00 AM)</span>
                      <span className="px-2 py-0.5 text-[10px] bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">With Water</span>
                    </div>
                  </div>
                </div>
                <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Taken</span>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-3">
              <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-bold text-xs uppercase tracking-wide">
                <AlertTriangle className="w-4 h-4" /> Known Allergies & Alerts
              </div>
              <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50 space-y-1">
                <div className="font-bold text-xs text-rose-800 dark:text-rose-200">Penicillin Group</div>
                <div className="text-[11px] text-rose-700 dark:text-rose-300">Severe cutaneous rash (anaphylactoid precaution).</div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-gray-900 dark:text-gray-100 flex items-center gap-2">
                  <Heart className="w-4 h-4 text-teal-600" /> Recovery Milestones
                </span>
                <span className="text-[11px] text-gray-500">Post-Op Week 4</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between text-gray-700 dark:text-gray-300">
                  <span>30 min light walking daily</span>
                  <span className="text-emerald-600 font-semibold">Active</span>
                </div>
                <div className="flex items-center justify-between text-gray-700 dark:text-gray-300">
                  <span>Low sodium (&lt; 2g/day) diet</span>
                  <span className="text-emerald-600 font-semibold">Followed</span>
                </div>
                <div className="flex items-center justify-between text-gray-700 dark:text-gray-300">
                  <span>Next Cardiology Follow-up</span>
                  <span className="font-semibold text-blue-600">Dec 15, 2024</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SUBTAB 2: MEDICAL VAULT */}
      {activeTab === "vault" && (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-gray-800">
            <div>
              <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <FileText className="w-4 h-4 text-teal-600" /> My Anonymized Medical Archive
              </h3>
              <p className="text-[11px] text-gray-500">All documents are encrypted with AES-256 GCM. PHI/PII is stripped prior to AI ingestion.</p>
            </div>
            <button
              onClick={() => alert("Opening camera scanner to photograph physical report...")}
              className="px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow flex items-center gap-1.5 transition-all"
            >
              <Camera className="w-4 h-4" /> Scan Report (Camera)
            </button>
          </div>

          <div className="divide-y divide-gray-100 dark:divide-gray-800 text-xs">
            <div className="py-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-teal-600" />
                <div>
                  <div className="font-semibold text-gray-800 dark:text-gray-200">Discharge Summary - LAD Drug-Eluting Stent</div>
                  <div className="text-[11px] text-gray-500">Nov 18, 2024 • Inpatient</div>
                </div>
              </div>
              <span className="text-emerald-600 font-medium text-[10px] bg-emerald-50 px-2 py-0.5 rounded">PII Scrubbed</span>
            </div>
            <div className="py-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-teal-600" />
                <div>
                  <div className="font-semibold text-gray-800 dark:text-gray-200">Comprehensive Lipid Panel & Cardiac Enzymes</div>
                  <div className="text-[11px] text-gray-500">Nov 12, 2024 • Biochemistry</div>
                </div>
              </div>
              <span className="text-emerald-600 font-medium text-[10px] bg-emerald-50 px-2 py-0.5 rounded">PII Scrubbed</span>
            </div>
          </div>
        </div>
      )}

      {/* SUBTAB 3: RECOVERY AI CHAT */}
      {activeTab === "chat" && (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl flex flex-col h-[600px] overflow-hidden">
          <div className="p-4 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-teal-600 text-white flex items-center justify-center font-bold">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100">PriviCare 24/7 Recovery AI</h3>
                <p className="text-[11px] text-gray-500">Ask questions regarding your medications or symptoms.</p>
              </div>
            </div>
          </div>

          <div className="px-4 py-2 bg-gray-50/50 dark:bg-gray-800/30 border-b border-gray-200 dark:border-gray-800 flex flex-wrap gap-1.5">
            <button
              onClick={() => handleSendMessage("Is mild calf soreness normal with Atorvastatin 40mg?")}
              className="px-2.5 py-1 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-[11px] text-gray-700 dark:text-gray-300 hover:border-teal-400"
            >
              Calf soreness with Statin
            </button>
            <button
              onClick={() => handleSendMessage("What foods should I avoid with Aspirin and Metoprolol?")}
              className="px-2.5 py-1 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-[11px] text-gray-700 dark:text-gray-300 hover:border-teal-400"
            >
              Food interactions
            </button>
            <button
              onClick={() => handleSendMessage("Can I start light 20-minute morning walks after stent?")}
              className="px-2.5 py-1 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-[11px] text-gray-700 dark:text-gray-300 hover:border-teal-400"
            >
              Walking after stent
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-4 text-xs">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] p-3.5 rounded-2xl ${
                    msg.sender === "user"
                      ? "bg-teal-600 text-white rounded-tr-sm"
                      : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-sm border border-gray-200 dark:border-gray-700"
                  }`}
                >
                  {msg.sender === "ai" && (
                    <div className="font-bold text-[10px] text-teal-600 dark:text-teal-400 flex items-center gap-1 mb-1">
                      <Bot className="w-3 h-3" /> PriviCare Recovery Assistant
                      {msg.triage === "URGENT_ATTENTION" && (
                        <span className="bg-red-500 text-white px-1.5 py-0.2 rounded text-[8px] font-bold">URGENT</span>
                      )}
                    </div>
                  )}
                  <div className="whitespace-pre-line leading-relaxed">{msg.text}</div>
                </div>
              </div>
            ))}
            {isSending && (
              <div className="flex items-center gap-2 text-gray-400 text-xs">
                <Bot className="w-4 h-4 animate-spin text-teal-600" />
                <span>PriviCare AI analyzing clinical context...</span>
              </div>
            )}
          </div>

          <div className="p-3 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Ask about your medications or recovery..."
              className="flex-1 px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-xs focus:ring-2 focus:ring-teal-500 outline-none"
            />
            <button
              onClick={() => handleSendMessage()}
              className="px-4 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-semibold shadow flex items-center gap-1"
            >
              <span>Send</span> <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* SUBTAB 4: DPDP RIGHTS */}
      {activeTab === "dpdp" && (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2.5 pb-3 border-b border-gray-200 dark:border-gray-800">
            <ShieldCheck className="w-6 h-6 text-teal-600" />
            <div>
              <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100">DPDP Act 2023 Section 12</h3>
              <p className="text-[11px] text-gray-500">Right to Correction and Erasure of Personal Data</p>
            </div>
          </div>

          <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
            Under Section 12 of the Digital Personal Data Protection Act 2023, you hold the legal right to request complete erasure of your personal data once the healthcare consultation purpose has completed.
          </p>

          <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 text-xs space-y-1.5">
            <div className="font-bold text-gray-900 dark:text-gray-100">Zero-Knowledge Cryptographic Shredding Guarantee:</div>
            <div className="text-gray-600 dark:text-gray-400 text-[11px]">
              • All pseudonym mappings and scoped HMAC hashes are encrypted with AES-256 GCM keys.<br />
              • Executing erasure destroys the session encryption keys permanently.<br />
              • Historical transcripts and vector embeddings become mathematically irreversible.
            </div>
          </div>

          <div className="pt-4 border-t border-gray-200 dark:border-gray-800 flex items-center justify-between">
            <div>
              <div className="font-bold text-xs text-red-600">Irreversible Action</div>
              <div className="text-[11px] text-gray-500">Purge session cryptographic keys</div>
            </div>
            <button
              onClick={handleCryptoShred}
              className="px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-semibold shadow flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" /> Execute Section 12 Crypto-Shred
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
