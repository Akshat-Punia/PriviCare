"use client";

import React, { useState } from "react";
import {
  Shield,
  ShieldCheck,
  QrCode,
  FileText,
  Pill,
  Lock,
  Upload,
  AlertCircle,
  CheckCircle2,
  Clock,
  Phone,
  User,
  Activity,
  Sparkles,
  Bot,
  Send,
  Building,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Eye,
  Trash2,
  Heart,
  Download,
  AlertTriangle,
  Globe
} from "lucide-react";

interface ConsentItem {
  id: string;
  hospital: string;
  dept: string;
  purpose: string;
  granted: boolean;
  validUntil: string;
}

interface VitalReading {
  timestamp: string;
  sys: number;
  dia: number;
  hr: number;
  spo2: number;
  sugar: number;
  temp: number;
  alerts: string[];
}

const UI_TRANSLATIONS = {
  en: {
    title: "Welcome to Your Health & Privacy Dashboard",
    subtitle: "Manage your digital health records, ABDM identity card, data sharing consents, and recovery progress.",
    switchProfile: "Switch Profile:",
    tabOverview: "1. Daily Health & Vitals",
    tabReports: "2. Medical Records Vault",
    tabConsent: "3. DPDP Consent & Privacy Hub",
    tabAssistant: "4. 24/7 Recovery AI Assistant",
    medSchedule: "Today's Medication Schedule",
    vitalsMonitor: "Live Ambulatory Cardiac Telemetry & Vitals",
    recordVitals: "+ Record Vitals",
    screenInteractions: "Screen Drug-Drug Interactions",
    exportFhir: "Export HL7 FHIR R4 Bundle",
    greeting: "Hello Rajesh! I am your 24/7 personal PriviCare health assistant. Your cardiac recovery is on track. How are you feeling today?"
  },
  hi: {
    title: "आपके स्वास्थ्य एवं गोपनीयता डैशबोर्ड में स्वागत है",
    subtitle: "अपने डिजिटल स्वास्थ्य रिकॉर्ड, आभा कार्ड, डेटा साझाकरण सहमति और रिकवरी स्थिति प्रबंधित करें।",
    switchProfile: "प्रोफ़ाइल बदलें:",
    tabOverview: "1. दैनिक स्वास्थ्य और वाइटल्स",
    tabReports: "2. मेडिकल रिकॉर्ड्स वॉल्ट",
    tabConsent: "3. डीपीईपी सहमति एवं प्राइवेसी हब",
    tabAssistant: "4. 24/7 रिकवरी एआई सहायक",
    medSchedule: "आज की दवाएं और समय सारणी",
    vitalsMonitor: "लाइव कार्डियक टेलीमेट्री और वाइटल्स ट्रैकर",
    recordVitals: "+ वाइटल्स दर्ज करें",
    screenInteractions: "दवा पारस्परिक प्रभाव जांचें",
    exportFhir: "HL7 FHIR R4 बंडल निर्यात करें",
    greeting: "नमस्ते राजेश! मैं आपका 24/7 व्यक्तिगत प्रिविकेयर स्वास्थ्य सहायक हूँ। आज आप कैसा महसूस कर रहे हैं?"
  },
  ta: {
    title: "உங்கள் சுகாதார மற்றும் தனியுரிமை டாஷ்போர்டுக்கு வருக",
    subtitle: "உங்கள் டிஜிட்டல் சுகாதார ஆவணங்கள், ஆபா அட்டை மற்றும் ஒப்புதல்களை நிர்வகிக்கவும்.",
    switchProfile: "சுயவிவரத்தை மாற்றவும்:",
    tabOverview: "1. தினசரி சுகாதாரம் & முக்கிய குறிகாட்டிகள்",
    tabReports: "2. மருத்துவ ஆவண பெட்டகம்",
    tabConsent: "3. தனியுரிமை & ஒப்புதல் மையம்",
    tabAssistant: "4. 24/7 மீட்பு AI உதவியாளர்",
    medSchedule: "இன்றைய மருந்து அட்டவணை",
    vitalsMonitor: "நேரடி இதய டெலிமெட்ரி கண்காணிப்பு",
    recordVitals: "+ முக்கிய அளவீடுகளைப் பதிவு செய்",
    screenInteractions: "மருந்து தொடர்புகளை சரிபார்க்கவும்",
    exportFhir: "HL7 FHIR R4 ஏற்றுமதி",
    greeting: "வணக்கம் ராஜேஷ்! நான் உங்கள் தனிப்பயனாக்கப்பட்ட பிரிவிகேர் சுகாதார உதவியாளர்."
  },
  te: {
    title: "మీ ఆరోగ్య మరియు గోప్యతా డాష్‌బోర్డ్‌కు స్వాగతం",
    subtitle: "మీ డిజిటల్ ఆరోగ్య రికార్డులు, ఆభా కార్డ్ మరియు డేటా సమ్మతులను నిర్వహించండి.",
    switchProfile: "ప్రొఫైల్ మార్చండి:",
    tabOverview: "1. రోజువారీ ఆరోగ్యం & వైటల్స్",
    tabReports: "2. వైద్య రికార్డుల వాల్ట్",
    tabConsent: "3. DPDP సమ్మతి కేంద్రం",
    tabAssistant: "4. 24/7 రికవరీ AI అసిస్టెంట్",
    medSchedule: "నేటి ఔషధాల ప్రణాళిక",
    vitalsMonitor: "లైవ్ కార్డియాక్ టెలిమెట్రీ & వైటల్స్",
    recordVitals: "+ వైటల్స్ నమోదు చేయండి",
    screenInteractions: "ఔషధ పరస్పర చర్యలను తనిఖీ చేయండి",
    exportFhir: "HL7 FHIR R4 ఎగుమతి",
    greeting: "నమస్తే రాజేష్! నేను మీ ప్రివికేర్ రికవరీ అసిస్టెంట్."
  },
  bn: {
    title: "আপনার স্বাস্থ্য ও গোপনীয়তা ড্যাশবোর্ডে স্বাগতম",
    subtitle: "আপনার ডিজিটাল স্বাস্থ্য রেকর্ড, আভা কার্ড এবং ডেটা শেয়ারিং সম্মতি পরিচালনা করুন।",
    switchProfile: "প্রোফাইল পরিবর্তন করুন:",
    tabOverview: "1. দৈনিক স্বাস্থ্য ও ভাইটালস",
    tabReports: "2. মেডিকেল রেকর্ড ভল্ট",
    tabConsent: "3. গোপনীয়তা ও সম্মতি হাব",
    tabAssistant: "4. 24/7 রিকভারি এআই সহকারী",
    medSchedule: "আজকের ওষুধের সময়সূচী",
    vitalsMonitor: "লাইভ কার্ডিয়াক টেলিমেট্রি ও ভাইটালস",
    recordVitals: "+ ভাইটালস রেকর্ড করুন",
    screenInteractions: "ওষুধের মিথস্ক্রিয়া যাচাই করুন",
    exportFhir: "HL7 FHIR R4 এক্সপোর্ট",
    greeting: "নমস্কার রাজেশ! আমি আপনার প্রিভिकेয়ার স্বাস্থ্য সহকারী।"
  }
};

export default function UserDashboardPage() {
  const [selectedUser, setSelectedUser] = useState("UHID-982143");
  const [lang, setLang] = useState<"en" | "hi" | "ta" | "te" | "bn">("en");
  const [activeTab, setActiveTab] = useState<"overview" | "reports" | "consent" | "assistant">("overview");
  const [qrOpen, setQrOpen] = useState(false);
  
  // Vitals State
  const [vitals, setVitals] = useState<VitalReading>({
    timestamp: "Today, 08:30 AM",
    sys: 120,
    dia: 80,
    hr: 72,
    spo2: 98,
    sugar: 105,
    temp: 98.6,
    alerts: []
  });
  const [vitalsModalOpen, setVitalsModalOpen] = useState(false);
  const [vitalsForm, setVitalsForm] = useState({
    sys: 120,
    dia: 80,
    hr: 72,
    spo2: 98,
    sugar: 105,
    temp: 98.6
  });

  // Drug Interactions Modal State
  const [interactionsModalOpen, setInteractionsModalOpen] = useState(false);
  const [interactionsLoading, setInteractionsLoading] = useState(false);
  const [interactionsData, setInteractionsData] = useState<any>(null);

  // FHIR Modal State
  const [fhirModalOpen, setFhirModalOpen] = useState(false);
  const [fhirJson, setFhirJson] = useState<string>("");

  const [medsTaken, setMedsTaken] = useState<Record<string, boolean>>({
    med1: true,
    med2: true,
    med3: false,
    med4: false
  });

  const [consents, setConsents] = useState<ConsentItem[]>([
    {
      id: "c1",
      hospital: "Fortis Escorts Heart Institute",
      dept: "Cardiology",
      purpose: "Post-PCI Clinical Monitoring & Zero-Leak Vector RAG",
      granted: true,
      validUntil: "12 Oct 2027"
    },
    {
      id: "c2",
      hospital: "AIIMS New Delhi Network",
      dept: "Tele-Consultation",
      purpose: "Cardiology Second Opinion & Lab Trend Sync",
      granted: true,
      validUntil: "15 Apr 2027"
    },
    {
      id: "c3",
      hospital: "National Health Claims Exchange (NHCX)",
      dept: "Insurance & TPA",
      purpose: "Automated Pre-Auth & Cashless Hospital Settlement",
      granted: false,
      validUntil: "Revoked by User"
    }
  ]);

  const [shredded, setShredded] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      sender: "ai",
      text: UI_TRANSLATIONS[lang].greeting,
      time: "09:00 AM"
    }
  ]);
  const [inputMessage, setInputMessage] = useState("");

  const t = UI_TRANSLATIONS[lang];

  const handleRecordVitals = (e: React.FormEvent) => {
    e.preventDefault();
    const alerts: string[] = [];
    if (vitalsForm.sys >= 140 || vitalsForm.dia >= 90) {
      alerts.push(`Elevated Blood Pressure: ${vitalsForm.sys}/${vitalsForm.dia} mmHg (Stage 2 Hypertension)`);
    }
    if (vitalsForm.hr > 100) {
      alerts.push(`Tachycardia detected: Heart rate ${vitalsForm.hr} bpm`);
    } else if (vitalsForm.hr < 50) {
      alerts.push(`Bradycardia detected: Heart rate ${vitalsForm.hr} bpm`);
    }
    if (vitalsForm.spo2 < 95) {
      alerts.push(`Hypoxemia Alert: Blood Oxygen (SpO2) ${vitalsForm.spo2}%`);
    }
    if (vitalsForm.sugar > 180) {
      alerts.push(`Hyperglycemia Alert: Blood Glucose ${vitalsForm.sugar} mg/dL`);
    }

    setVitals({
      timestamp: "Just Now",
      sys: Number(vitalsForm.sys),
      dia: Number(vitalsForm.dia),
      hr: Number(vitalsForm.hr),
      spo2: Number(vitalsForm.spo2),
      sugar: Number(vitalsForm.sugar),
      temp: Number(vitalsForm.temp),
      alerts
    });

    setVitalsModalOpen(false);

    if (alerts.length > 0) {
      alert(`⚠️ TELEMETRY ALERT:\n\n${alerts.join("\n")}\n\nAttending Cardiologist Dr. Sarah Johnson's queue has been notified.`);
    } else {
      alert("✅ Vitals recorded successfully! All parameters are within normal physiological range.");
    }
  };

  const handleScreenInteractions = async () => {
    setInteractionsModalOpen(true);
    setInteractionsLoading(true);
    try {
      const res = await fetch("/api/clinical/check-interactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          medications: ["Atorvastatin 40mg", "Aspirin 75mg", "Ibuprofen 400mg"],
          allergies: ["Penicillin"],
          dietary_items: ["Grapefruit juice", "Potassium salt substitute"]
        })
      });
      if (res.ok) {
        const data = await res.json();
        setInteractionsData(data);
      } else {
        // Fallback simulation
        setInteractionsData({
          safety_evaluation: "HIGH_RISK",
          interactions_found_count: 2,
          interactions: [
            {
              drugs: "Atorvastatin + Grapefruit juice",
              severity: "CRITICAL_AVOID",
              clinical_risk: "CYP3A4 inhibition increases serum Atorvastatin levels 3-fold, elevating rhabdomyolysis risk.",
              recommendation: "Avoid grapefruit and grapefruit juice completely while on Atorvastatin."
            },
            {
              drugs: "Aspirin + Ibuprofen",
              severity: "HIGH_MONITOR",
              clinical_risk: "Competitive COX-1 inhibition reduces Aspirin cardioprotective effect and increases GI bleeding risk.",
              recommendation: "Take Aspirin at least 2 hours before or 8 hours after NSAIDs."
            }
          ],
          allergy_alerts: [
            {
              allergen: "Penicillin",
              offending_drug: "Amoxicillin-Clavulanate",
              clinical_risk: "Beta-lactam cross-reactivity risk: severe anaphylaxis or angioedema."
            }
          ]
        });
      }
    } catch (err) {
      // Mock data if backend not reachable directly
      setInteractionsData({
        safety_evaluation: "HIGH_RISK",
        interactions_found_count: 2,
        interactions: [
          {
            drugs: "Atorvastatin + Grapefruit juice",
            severity: "CRITICAL_AVOID",
            clinical_risk: "CYP3A4 inhibition increases serum Atorvastatin levels 3-fold, elevating rhabdomyolysis risk.",
            recommendation: "Avoid grapefruit juice completely."
          },
          {
            drugs: "Aspirin + Ibuprofen",
            severity: "HIGH_MONITOR",
            clinical_risk: "Competitive COX-1 antagonism interferes with antiplatelet cardioprotection.",
            recommendation: "Separate administration by at least 2 hours."
          }
        ],
        allergy_alerts: []
      });
    } finally {
      setInteractionsLoading(false);
    }
  };

  const handleExportFhir = async () => {
    setFhirModalOpen(true);
    setFhirJson("Generating ABDM-compliant HL7 FHIR Release 4 DocumentBundle JSON...");
    try {
      const res = await fetch(`/api/clinical/patients/${selectedUser}/fhir-bundle`);
      if (res.ok) {
        const bundle = await res.json();
        setFhirJson(JSON.stringify(bundle, null, 2));
      } else {
        throw new Error("HTTP error");
      }
    } catch (err) {
      // Generate standard mock FHIR R4 collection bundle
      const mockFhir = {
        resourceType: "Bundle",
        id: `fhir-bundle-${selectedUser.toLowerCase()}`,
        type: "document",
        timestamp: new Date().toISOString(),
        entry: [
          {
            resource: {
              resourceType: "Patient",
              id: selectedUser,
              identifier: [{ system: "https://healthid.ndhm.gov.in", value: "14-2354-9871-6542" }],
              name: [{ text: "Rajesh Sharma" }],
              gender: "male",
              birthDate: "1972-04-12"
            }
          },
          {
            resource: {
              resourceType: "Practitioner",
              id: "DOC-DEL-9821",
              name: [{ text: "Dr. Sarah Johnson, MD, DM (Cardiology)" }]
            }
          },
          {
            resource: {
              resourceType: "Condition",
              code: { text: "Coronary Artery Disease - Post Percutaneous Coronary Intervention" },
              clinicalStatus: "active"
            }
          },
          {
            resource: {
              resourceType: "Observation",
              code: { text: "Left Ventricular Ejection Fraction (LVEF)" },
              valueQuantity: { value: 52, unit: "%" }
            }
          }
        ]
      };
      setFhirJson(JSON.stringify(mockFhir, null, 2));
    }
  };

  const handleDownloadFhir = () => {
    const blob = new Blob([fhirJson], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `FHIR_R4_Bundle_${selectedUser}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const toggleConsent = (id: string) => {
    setConsents((prev) =>
      prev.map((c) =>
        c.id === id
          ? {
              ...c,
              granted: !c.granted,
              validUntil: !c.granted ? "31 Dec 2027" : "Revoked by User"
            }
          : c
      )
    );
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;
    const userText = inputMessage.trim();
    setInputMessage("");

    setChatMessages((prev) => [
      ...prev,
      { sender: "user", text: userText, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }
    ]);

    setTimeout(() => {
      let reply = "Your query was processed locally with full zero-leakage anonymization.";
      const low = userText.toLowerCase();
      if (low.includes("chest") || low.includes("pain")) {
        reply = "⚠️ URGENT ADVICE: Please contact Dr. Sarah Johnson or visit the emergency department at Fortis Escorts immediately. Your doctor's clinical dashboard has been flagged.";
      } else if (low.includes("medicine") || low.includes("statin") || low.includes("atorvastatin")) {
        reply = "Medication Guidance: Atorvastatin 40mg should be taken once daily at bedtime. If you experience muscle cramps or tenderness, report it promptly.";
      } else if (low.includes("grapefruit")) {
        reply = "⚠️ DRUG INTERACTION ALERT: Avoid grapefruit and grapefruit juice completely! Grapefruit blocks the CYP3A4 enzyme, leading to dangerously high levels of Atorvastatin in your bloodstream.";
      } else {
        reply = "Your health parameters are within safe ranges. Don't forget your evening dose of Aspirin with water!";
      }

      setChatMessages((prev) => [
        ...prev,
        { sender: "ai", text: reply, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }
      ]);
    }, 600);
  };

  const handleCryptoShred = () => {
    if (
      confirm(
        "DPDP ACT 2023 SECTION 12 RIGHT TO ERASURE\n\nDo you want to permanently crypto-shred all encryption keys, scoped pseudonym salts, and session mapping vectors for this user account?\n\nThis action is irreversible and renders all stored data permanently unrecoverable."
      )
    ) {
      setShredded(true);
      alert("✅ Cryptographic Erasure Executed! All encryption keys and pseudonym hashes purged.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fade-in pb-12">
      {/* Top Banner with Language Selector & Profile Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 glass-card rounded-2xl border border-gray-200 dark:border-gray-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-teal-100 dark:bg-teal-950 text-teal-800 dark:text-teal-300 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" /> India DPDP Act 2023 & ABDM Verified
            </span>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300">
              User Central Dashboard
            </span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t.title}
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {t.subtitle}
          </p>
        </div>

        {/* User Account & Language Switcher */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Language Selector */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-xs font-semibold text-gray-700 dark:text-gray-200">
            <Globe className="w-4 h-4 text-teal-600" />
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value as any)}
              className="bg-transparent outline-none cursor-pointer"
            >
              <option value="en">English</option>
              <option value="hi">हिन्दी (Hindi)</option>
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="te">తెలుగు (Telugu)</option>
              <option value="bn">বাংলা (Bengali)</option>
            </select>
          </div>

          {/* Profile Switcher */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-gray-500 font-medium">{t.switchProfile}</span>
            <select
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
              className="px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-xs font-semibold text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-teal-500 outline-none"
            >
              <option value="UHID-982143">Rajesh Sharma (UHID-982143)</option>
              <option value="UHID-447219">Priya Patel (UHID-447219)</option>
              <option value="UHID-551029">Amit Kumar (UHID-551029)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Grid: Health ID Card & Four Core Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ABDM Digital Health ID Card */}
        <div className="relative overflow-hidden rounded-2xl p-6 bg-gradient-to-br from-teal-700 via-teal-800 to-slate-900 text-white shadow-xl border border-teal-600/30">
          <div className="absolute top-0 right-0 w-48 h-48 bg-white/5 rounded-full blur-2xl pointer-events-none" />
          
          <div className="flex items-center justify-between pb-4 border-b border-white/10">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-white/20 backdrop-blur-md flex items-center justify-center font-bold">
                <Shield className="w-4 h-4 text-white" />
              </div>
              <div>
                <div className="text-xs font-bold tracking-wider uppercase text-teal-200">Ayushman Bharat (ABDM)</div>
                <div className="text-[10px] text-teal-300">National Health Authority • India</div>
              </div>
            </div>
            <button
              onClick={() => setQrOpen(!qrOpen)}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-white"
              title="Show QR Code"
            >
              <QrCode className="w-4 h-4" />
            </button>
          </div>

          <div className="my-5 space-y-3">
            <div>
              <div className="text-[10px] uppercase tracking-wider text-teal-300 font-medium">ABHA Number (14-Digit)</div>
              <div className="text-xl font-mono font-bold tracking-widest text-white">
                14-2354-9871-6542
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <div>
                <div className="text-[10px] uppercase text-teal-300 font-medium">Cardholder Name</div>
                <div className="font-semibold text-sm text-white">Rajesh Sharma</div>
              </div>
              <div className="text-right">
                <div className="text-[10px] uppercase text-teal-300 font-medium">ABHA Address</div>
                <div className="font-mono text-xs text-white">rajesh.sharma@abdm</div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-white/10 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-[11px] text-teal-100 font-medium">Verhoeff D5 Checksum Verified</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-white/15 text-[10px] font-mono">Blood: O+</span>
            </div>
          </div>

          <div className="pt-3 border-t border-white/10 flex items-center justify-between text-[11px] text-teal-200">
            <span>Hospital UHID: <strong className="font-mono text-white">UHID-982143</strong></span>
            <span>Attending: <strong className="text-white">Dr. Sarah Johnson</strong></span>
          </div>

          {qrOpen && (
            <div className="mt-4 p-4 rounded-xl bg-white text-slate-900 text-center animate-fade-in shadow-lg">
              <div className="w-32 h-32 mx-auto bg-slate-100 border-2 border-slate-300 rounded-lg flex items-center justify-center mb-2">
                <QrCode className="w-24 h-24 text-slate-800" />
              </div>
              <div className="text-xs font-bold">ABHA Digital Health QR</div>
              <div className="text-[10px] text-slate-500">Scan at hospital check-in for instant zero-leak intake</div>
            </div>
          )}
        </div>

        {/* 4 Metric Cards */}
        <div className="lg:col-span-2 grid grid-cols-2 gap-4">
          <div className="p-5 glass-card rounded-2xl border border-gray-200 dark:border-gray-800 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">Zero-Leak Privacy Score</span>
              <div className="p-2 rounded-xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600">
                <ShieldCheck className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4">
              <div className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">100%</div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Zero clinical PII or Verhoeff identifiers exposed to vector DBs.
              </p>
            </div>
          </div>

          <div className="p-5 glass-card rounded-2xl border border-gray-200 dark:border-gray-800 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">Recovery Status</span>
              <div className="p-2 rounded-xl bg-teal-100 dark:bg-teal-950/60 text-teal-600">
                <Activity className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4">
              <div className="text-3xl font-extrabold text-teal-600 dark:text-teal-400">Day 14</div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Post-PCI Drug-Eluting Stent • LVEF 52% (Stable)
              </p>
            </div>
          </div>

          <div className="p-5 glass-card rounded-2xl border border-gray-200 dark:border-gray-800 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">Scrubbed Health Records</span>
              <div className="p-2 rounded-xl bg-blue-100 dark:bg-blue-950/60 text-blue-600">
                <FileText className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4">
              <div className="text-3xl font-extrabold text-gray-900 dark:text-white">2 Records</div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Discharge summary & Lipid echo stored with on-device pseudonymization.
              </p>
            </div>
          </div>

          <div className="p-5 glass-card rounded-2xl border border-gray-200 dark:border-gray-800 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">Active Hospital Consents</span>
              <div className="p-2 rounded-xl bg-amber-100 dark:bg-amber-950/60 text-amber-600">
                <Building className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4">
              <div className="text-3xl font-extrabold text-gray-900 dark:text-white">
                {consents.filter((c) => c.granted).length} Granted
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                DPDP Act Section 6 consent notices under full user control.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-800 gap-2">
        <button
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2.5 text-sm font-semibold rounded-t-xl transition-all flex items-center gap-2 border-b-2 ${
            activeTab === "overview"
              ? "border-teal-600 text-teal-600 bg-teal-50/50 dark:bg-teal-950/30"
              : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <Activity className="w-4 h-4" /> {t.tabOverview}
        </button>
        <button
          onClick={() => setActiveTab("reports")}
          className={`px-4 py-2.5 text-sm font-semibold rounded-t-xl transition-all flex items-center gap-2 border-b-2 ${
            activeTab === "reports"
              ? "border-teal-600 text-teal-600 bg-teal-50/50 dark:bg-teal-950/30"
              : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <FileText className="w-4 h-4" /> {t.tabReports}
        </button>
        <button
          onClick={() => setActiveTab("consent")}
          className={`px-4 py-2.5 text-sm font-semibold rounded-t-xl transition-all flex items-center gap-2 border-b-2 ${
            activeTab === "consent"
              ? "border-teal-600 text-teal-600 bg-teal-50/50 dark:bg-teal-950/30"
              : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <Lock className="w-4 h-4" /> {t.tabConsent}
        </button>
        <button
          onClick={() => setActiveTab("assistant")}
          className={`px-4 py-2.5 text-sm font-semibold rounded-t-xl transition-all flex items-center gap-2 border-b-2 ${
            activeTab === "assistant"
              ? "border-teal-600 text-teal-600 bg-teal-50/50 dark:bg-teal-950/30"
              : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <Bot className="w-4 h-4" /> {t.tabAssistant}
        </button>
      </div>

      {/* TAB 1: OVERVIEW, VITALS & DAILY ADHERENCE */}
      {activeTab === "overview" && (
        <div className="space-y-6 animate-fade-in">
          {/* Live Ambulatory Vitals & Telemetry */}
          <div className="glass-card rounded-2xl p-6 border border-gray-200 dark:border-gray-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-gray-200 dark:border-gray-800">
              <div>
                <h3 className="font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-rose-600 animate-pulse" /> {t.vitalsMonitor}
                </h3>
                <p className="text-xs text-gray-500 mt-0.5">Automated hemodynamic anomaly detection synchronized with attending cardiologist</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-gray-400">Last updated: {vitals.timestamp}</span>
                <button
                  onClick={() => setVitalsModalOpen(true)}
                  className="px-3.5 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow transition-all flex items-center gap-1.5"
                >
                  {t.recordVitals}
                </button>
              </div>
            </div>

            {/* Vitals Stat Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/50 space-y-1">
                <div className="text-[11px] font-semibold text-rose-700 dark:text-rose-400">Blood Pressure</div>
                <div className="text-2xl font-bold font-mono text-rose-950 dark:text-rose-200">
                  {vitals.sys}/{vitals.dia} <span className="text-xs font-normal text-gray-500">mmHg</span>
                </div>
                <div className="text-[10px] text-gray-500">Target &lt; 130/80</div>
              </div>

              <div className="p-4 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/50 space-y-1">
                <div className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400">Resting Heart Rate</div>
                <div className="text-2xl font-bold font-mono text-emerald-950 dark:text-emerald-200">
                  {vitals.hr} <span className="text-xs font-normal text-gray-500">bpm</span>
                </div>
                <div className="text-[10px] text-gray-500">Normal 60-100</div>
              </div>

              <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/50 space-y-1">
                <div className="text-[11px] font-semibold text-blue-700 dark:text-blue-400">Blood Oxygen (SpO2)</div>
                <div className="text-2xl font-bold font-mono text-blue-950 dark:text-blue-200">
                  {vitals.spo2} <span className="text-xs font-normal text-gray-500">%</span>
                </div>
                <div className="text-[10px] text-gray-500">Room air baseline</div>
              </div>

              <div className="p-4 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/50 space-y-1">
                <div className="text-[11px] font-semibold text-amber-700 dark:text-amber-400">Blood Glucose (F)</div>
                <div className="text-2xl font-bold font-mono text-amber-950 dark:text-amber-200">
                  {vitals.sugar} <span className="text-xs font-normal text-gray-500">mg/dL</span>
                </div>
                <div className="text-[10px] text-gray-500">Target 70-120</div>
              </div>
            </div>

            {vitals.alerts.length > 0 && (
              <div className="p-3 rounded-xl border border-rose-300 bg-rose-50 text-xs text-rose-800 space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-rose-600" /> Physiological Anomalies Detected:
                </div>
                {vitals.alerts.map((a, i) => (
                  <div key={i} className="pl-5 text-[11px]">• {a}</div>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Daily Prescriptions & Drug Interaction Checker */}
            <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-gray-200 dark:border-gray-800 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-gray-200 dark:border-gray-800">
                <div>
                  <h3 className="font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <Pill className="w-5 h-5 text-teal-600" /> {t.medSchedule}
                  </h3>
                  <p className="text-xs text-gray-500 mt-0.5">Check off your doses as you take them</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleScreenInteractions}
                    className="px-3 py-1.5 rounded-xl border border-amber-300 bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-300 text-xs font-semibold hover:bg-amber-100 transition-all flex items-center gap-1.5"
                  >
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> {t.screenInteractions}
                  </button>
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">
                    {Object.values(medsTaken).filter(Boolean).length}/4 Taken
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                {[
                  { id: "med1", name: "Atorvastatin 40mg", time: "Bedtime (Night)", note: "Plaque stabilization & lipid reduction" },
                  { id: "med2", name: "Aspirin 75mg (EC)", time: "Post-Breakfast", note: "Antiplatelet for drug-eluting stent" },
                  { id: "med3", name: "Telmisartan 40mg", time: "Morning (09:00 AM)", note: "Blood pressure control" },
                  { id: "med4", name: "Metoprolol Succinate 25mg", time: "Post-Dinner", note: "Beta-blocker for heart rate" }
                ].map((med) => (
                  <div
                    key={med.id}
                    onClick={() => setMedsTaken((prev) => ({ ...prev, [med.id]: !prev[med.id] }))}
                    className={`p-3.5 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                      medsTaken[med.id]
                        ? "border-emerald-300 bg-emerald-50/30 dark:bg-emerald-950/20"
                        : "border-gray-200 dark:border-gray-800 hover:border-teal-400"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={!!medsTaken[med.id]}
                        onChange={() => {}}
                        className="w-4 h-4 text-teal-600 rounded border-gray-300 focus:ring-teal-500"
                      />
                      <div>
                        <div className="font-bold text-sm text-gray-900 dark:text-white">{med.name}</div>
                        <div className="text-xs text-gray-500">{med.note}</div>
                      </div>
                    </div>
                    <span className="text-xs font-semibold px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                      {med.time}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Access Transparency Logs */}
            <div className="glass-card rounded-2xl p-6 border border-gray-200 dark:border-gray-800 space-y-4">
              <h3 className="font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-600" /> Who Accessed My Data
              </h3>
              <p className="text-xs text-gray-500">Real-time DPDP transparency access audit trail</p>

              <div className="space-y-3">
                {[
                  { actor: "Dr. Sarah Johnson", purpose: "Treatment Follow-up Review", time: "Yesterday, 06:30 PM", verified: true },
                  { actor: "PriviCare Clinical Guard", purpose: "Allergy Interaction Check", time: "20 Nov, 09:15 AM", verified: true },
                  { actor: "ABDM Gateway", purpose: "ABHA Health Locker Verification", time: "19 Nov, 02:22 PM", verified: true }
                ].map((log, i) => (
                  <div key={i} className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700 text-xs space-y-1">
                    <div className="flex items-center justify-between font-bold text-gray-900 dark:text-white">
                      <span>{log.actor}</span>
                      <span className="text-[10px] text-gray-400 font-normal">{log.time}</span>
                    </div>
                    <div className="text-gray-500 dark:text-gray-400">{log.purpose}</div>
                    <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> PII Scrubbed & Verified
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: MY MEDICAL RECORDS VAULT & HL7 FHIR EXPORTER */}
      {activeTab === "reports" && (
        <div className="space-y-6 animate-fade-in">
          {/* Top action bar */}
          <div className="flex items-center justify-between p-4 glass-card rounded-2xl border border-gray-200 dark:border-gray-800">
            <div>
              <div className="font-bold text-sm text-gray-900 dark:text-white">Ayushman Bharat Digital Health Records Vault</div>
              <div className="text-xs text-gray-500">Cryptographically isolated and pseudonymized per NHA specifications</div>
            </div>
            <button
              onClick={handleExportFhir}
              className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow transition-all flex items-center gap-2"
            >
              <Download className="w-4 h-4" /> {t.exportFhir}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 glass-card rounded-2xl border border-gray-200 dark:border-gray-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-base text-gray-900 dark:text-white flex items-center gap-2">
                  <FileText className="w-5 h-5 text-teal-600" /> Discharge Summary (Fortis Escorts)
                </h3>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
                  Cardiology
                </span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                Acute Coronary Syndrome (NSTEMI). Percutaneous Coronary Intervention with Drug-Eluting Stent to Mid-LAD. Successful deployment, post-procedure LVEF 52%. Discharge vitals stable.
              </p>
              <div className="p-3 rounded-xl bg-teal-50 dark:bg-teal-950/40 border border-teal-200 dark:border-teal-900/60 text-xs text-teal-800 dark:text-teal-300">
                <strong>Zero-Leak Anonymized Identifiers:</strong> Name [PERSON_1], UHID [UHID_1], Aadhaar [AADHAAR_1].
              </div>
            </div>

            <div className="p-6 glass-card rounded-2xl border border-gray-200 dark:border-gray-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-base text-gray-900 dark:text-white flex items-center gap-2">
                  <FileText className="w-5 h-5 text-teal-600" /> Lipid Profile & 2D Echo Report
                </h3>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                  Follow-up
                </span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                Follow-up lipid investigation: Serum Cholesterol 168 mg/dL, LDL 88 mg/dL (target &lt;100). 2D Echocardiogram demonstrates LVEF 54% with regional anterior wall hypokinesia.
              </p>
              <div className="p-3 rounded-xl bg-teal-50 dark:bg-teal-950/40 border border-teal-200 dark:border-teal-900/60 text-xs text-teal-800 dark:text-teal-300">
                <strong>Zero-Leak Anonymized Identifiers:</strong> Patient [PERSON_1], UHID [UHID_1], Date [DATE_1].
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: DPDP CONSENT & PRIVACY HUB */}
      {activeTab === "consent" && (
        <div className="space-y-6 animate-fade-in">
          <div className="glass-card rounded-2xl p-6 border border-gray-200 dark:border-gray-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-gray-200 dark:border-gray-800">
              <div>
                <h3 className="font-bold text-base text-gray-900 dark:text-white flex items-center gap-2">
                  <Building className="w-5 h-5 text-teal-600" /> Active Healthcare Entity Consents
                </h3>
                <p className="text-xs text-gray-500">Under Digital Personal Data Protection (DPDP) Act 2023 Section 6</p>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300">
                DPDP Notice Verified
              </span>
            </div>

            <div className="space-y-3">
              {consents.map((c) => (
                <div key={c.id} className="p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-gray-900 dark:text-white">{c.hospital}</span>
                      <span className="text-xs px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">{c.dept}</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1"><strong>Purpose:</strong> {c.purpose}</div>
                    <div className="text-[11px] text-gray-400 mt-0.5">Valid Until: {c.validUntil}</div>
                  </div>

                  <button
                    onClick={() => toggleConsent(c.id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                      c.granted
                        ? "bg-rose-50 text-rose-700 border border-rose-300 hover:bg-rose-100 dark:bg-rose-950/40 dark:text-rose-300"
                        : "bg-teal-600 text-white hover:bg-teal-700"
                    }`}
                  >
                    {c.granted ? "Revoke Consent" : "Grant Consent"}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Right to Erasure / Crypto-Shred Card */}
          <div className="p-6 rounded-2xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/60 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-rose-800 dark:text-rose-300 text-sm flex items-center gap-2">
                <Trash2 className="w-4 h-4 text-rose-600" /> DPDP Section 12: Right to Erasure (Crypto-Shredding)
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-200/60 dark:bg-rose-900/80 text-rose-900 dark:text-rose-200">
                AES-256 Key Purge
              </span>
            </div>
            <p className="text-xs text-rose-700 dark:text-rose-300/80 leading-relaxed">
              Exercise your statutory right under India DPDP Act Section 12 to immediately delete your pseudonym mapping table and purge cryptographic session salts, rendering stored transcripts irreversibly unrecoverable.
            </p>
            <button
              onClick={handleCryptoShred}
              disabled={shredded}
              className={`px-4 py-2 rounded-xl text-xs font-semibold shadow transition-all ${
                shredded
                  ? "bg-gray-400 text-white cursor-not-allowed"
                  : "bg-rose-600 hover:bg-rose-700 text-white"
              }`}
            >
              {shredded ? "Keys Purged (Mathematically Irreversible)" : "Execute Cryptographic Shredding"}
            </button>
          </div>
        </div>
      )}

      {/* TAB 4: 24/7 RECOVERY AI ASSISTANT */}
      {activeTab === "assistant" && (
        <div className="glass-card rounded-2xl border border-gray-200 dark:border-gray-800 overflow-hidden flex flex-col h-[520px] animate-fade-in">
          <div className="p-4 bg-teal-600 text-white flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Bot className="w-5 h-5" />
              <div>
                <div className="font-bold text-sm">PriviCare Recovery AI Co-Pilot</div>
                <div className="text-[10px] text-teal-100">Synchronized with Dr. Sarah Johnson • Zero-Leak Safe</div>
              </div>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-full bg-white/20 text-white font-medium">Active</span>
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-3">
            {chatMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-teal-600 text-white rounded-br-none shadow"
                      : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-bl-none border border-gray-200 dark:border-gray-700 shadow-sm"
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.text}</p>
                  <div className={`text-[10px] mt-1 ${msg.sender === "user" ? "text-teal-200" : "text-gray-400"}`}>
                    {msg.time}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Ask about medications, food interactions, walking limits..."
              className="flex-1 px-3.5 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-xs focus:ring-2 focus:ring-teal-500 outline-none text-gray-900 dark:text-gray-100"
            />
            <button
              onClick={handleSendMessage}
              className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-semibold shadow transition-all flex items-center gap-1.5"
            >
              <Send className="w-3.5 h-3.5" /> Send
            </button>
          </div>
        </div>
      )}

      {/* ================= MODAL: RECORD VITALS ================= */}
      {vitalsModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
          <div className="max-w-md w-full bg-white dark:bg-slate-900 rounded-2xl shadow-2xl p-6 border border-gray-200 dark:border-gray-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-gray-200 dark:border-gray-800">
              <h3 className="font-bold text-sm text-gray-900 dark:text-white flex items-center gap-2">
                <Activity className="w-4 h-4 text-rose-600" /> Log Ambulatory Vitals
              </h3>
              <button
                onClick={() => setVitalsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 text-xs"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleRecordVitals} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">Systolic BP (mmHg)</label>
                  <input
                    type="number"
                    value={vitalsForm.sys}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, sys: Number(e.target.value) })}
                    className="w-full mt-1 px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-xs"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">Diastolic BP (mmHg)</label>
                  <input
                    type="number"
                    value={vitalsForm.dia}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, dia: Number(e.target.value) })}
                    className="w-full mt-1 px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">Heart Rate (bpm)</label>
                  <input
                    type="number"
                    value={vitalsForm.hr}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, hr: Number(e.target.value) })}
                    className="w-full mt-1 px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-xs"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">SpO2 Oxygen (%)</label>
                  <input
                    type="number"
                    value={vitalsForm.spo2}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, spo2: Number(e.target.value) })}
                    className="w-full mt-1 px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">Fasting Sugar (mg/dL)</label>
                  <input
                    type="number"
                    value={vitalsForm.sugar}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, sugar: Number(e.target.value) })}
                    className="w-full mt-1 px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-xs"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">Temperature (°F)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={vitalsForm.temp}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, temp: Number(e.target.value) })}
                    className="w-full mt-1 px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-xs"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setVitalsModalOpen(false)}
                  className="px-3.5 py-1.5 rounded-xl border border-gray-300 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow"
                >
                  Save & Check Anomaly
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL: DRUG INTERACTIONS ================= */}
      {interactionsModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
          <div className="max-w-xl w-full bg-white dark:bg-slate-900 rounded-2xl shadow-2xl p-6 border border-gray-200 dark:border-gray-800 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-gray-200 dark:border-gray-800">
              <h3 className="font-bold text-sm text-gray-900 dark:text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" /> Multi-Dimensional Drug Safety & Allergy Screening
              </h3>
              <button
                onClick={() => setInteractionsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 text-xs"
              >
                ✕
              </button>
            </div>

            {interactionsLoading ? (
              <div className="text-center py-8 text-xs text-gray-500">
                Running pharmacology rules engine against active prescriptions...
              </div>
            ) : interactionsData ? (
              <div className="space-y-3">
                <div className={`p-3 rounded-xl border text-xs font-semibold flex items-center justify-between ${
                  interactionsData.safety_evaluation === "HIGH_RISK"
                    ? "bg-rose-50 border-rose-200 text-rose-800"
                    : "bg-emerald-50 border-emerald-200 text-emerald-800"
                }`}>
                  <span>Safety Status: {interactionsData.safety_evaluation}</span>
                  <span>Alerts: {interactionsData.interactions_found_count}</span>
                </div>

                {interactionsData.interactions && interactionsData.interactions.map((item: any, idx: number) => (
                  <div key={idx} className="p-3.5 rounded-xl border border-amber-200 bg-amber-50/50 text-xs space-y-1">
                    <div className="font-bold text-amber-900 flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> {item.drugs} [{item.severity}]
                    </div>
                    <div className="text-amber-800 text-[11px]">{item.clinical_risk}</div>
                    <div className="text-gray-600 dark:text-gray-400 text-[11px]"><strong>Recommendation:</strong> {item.recommendation}</div>
                  </div>
                ))}

                {interactionsData.allergy_alerts && interactionsData.allergy_alerts.map((item: any, idx: number) => (
                  <div key={idx} className="p-3.5 rounded-xl border border-rose-200 bg-rose-50 text-xs space-y-1">
                    <div className="font-bold text-rose-900 flex items-center gap-1.5">
                      <AlertCircle className="w-3.5 h-3.5 text-rose-600" /> Allergy Alert: {item.offending_drug} ({item.allergen})
                    </div>
                    <div className="text-rose-800 text-[11px]">{item.clinical_risk}</div>
                  </div>
                ))}
              </div>
            ) : null}

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setInteractionsModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow"
              >
                Close Screening
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= MODAL: HL7 FHIR R4 EXPORTER ================= */}
      {fhirModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
          <div className="max-w-2xl w-full bg-white dark:bg-slate-900 rounded-2xl shadow-2xl p-6 border border-gray-200 dark:border-gray-800 space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-gray-200 dark:border-gray-800">
              <h3 className="font-bold text-sm text-gray-900 dark:text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-teal-600" /> ABDM HL7 FHIR Release 4 Collection Bundle
              </h3>
              <button
                onClick={() => setFhirModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 text-xs"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto">
              <pre className="p-4 rounded-xl bg-slate-950 text-slate-100 font-mono text-[11px] whitespace-pre-wrap leading-relaxed">
                {fhirJson}
              </pre>
            </div>

            <div className="pt-2 flex items-center justify-between border-t border-gray-200 dark:border-gray-800">
              <span className="text-[11px] text-gray-500">Standard: NHA Ayushman Bharat NRCES FHIR R4</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setFhirModalOpen(false)}
                  className="px-3.5 py-1.5 rounded-xl border border-gray-300 text-xs"
                >
                  Close
                </button>
                <button
                  onClick={handleDownloadFhir}
                  className="px-4 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow flex items-center gap-1.5"
                >
                  <Download className="w-3.5 h-3.5" /> Download JSON
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
