"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Shield, Mail, Lock, Loader2, AlertCircle, User, Stethoscope, HeartPulse, ShieldCheck, CheckCircle2 } from "lucide-react";

export default function LoginPage() {
  const [portal, setPortal] = useState<"doctor" | "patient">("doctor");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [patientId, setPatientId] = useState("14-2354-9871-6542");
  const [patientPin, setPatientPin] = useState("123456");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleDoctorSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please fill in all doctor credentials");
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid doctor credentials");
    } finally {
      setLoading(false);
    }
  };

  const handlePatientSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      router.push("/dashboard/user");
    }, 400);
  };

  const quickPatientLogin = (uhid: string) => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      router.push(`/dashboard/user?uhid=${uhid}`);
    }, 300);
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden p-4">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-teal-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950" />
      <div
        className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%230066ff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      {/* Decorative blobs */}
      <div className="absolute top-20 left-20 w-72 h-72 bg-blue-400/20 dark:bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-teal-400/20 dark:bg-teal-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 w-full max-w-md">
        {/* Logo Header */}
        <div className="text-center mb-6 animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 via-indigo-600 to-teal-600 rounded-2xl shadow-xl shadow-blue-500/20 mb-3">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-black tracking-tight text-gray-900 dark:text-white">
            PriviCare
          </h1>
          <p className="text-xs uppercase tracking-wider font-semibold text-gray-500 dark:text-gray-400 mt-0.5">
            Care In Every Data Beat
          </p>
          <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900">
            {portal === "doctor" ? (
              <>
                <Stethoscope className="w-3.5 h-3.5" /> Doctor Clinical Portal
              </>
            ) : (
              <>
                <ShieldCheck className="w-3.5 h-3.5 text-teal-600" /> Ayushman Bharat (ABDM) Patient Portal
              </>
            )}
          </div>
        </div>

        {/* Dual-Portal Segmented Selector */}
        <div className="grid grid-cols-2 p-1.5 bg-gray-100 dark:bg-gray-800/80 rounded-2xl mb-4 border border-gray-200 dark:border-gray-700">
          <button
            type="button"
            onClick={() => setPortal("doctor")}
            className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              portal === "doctor"
                ? "bg-white dark:bg-gray-900 text-blue-600 dark:text-blue-400 shadow-sm border border-gray-200 dark:border-gray-700"
                : "text-gray-500 hover:text-blue-600"
            }`}
          >
            <Stethoscope className="w-3.5 h-3.5" /> Doctor Portal
          </button>
          <button
            type="button"
            onClick={() => setPortal("patient")}
            className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
              portal === "patient"
                ? "bg-white dark:bg-gray-900 text-teal-600 dark:text-teal-400 shadow-sm border border-gray-200 dark:border-gray-700"
                : "text-gray-500 hover:text-teal-600"
            }`}
          >
            <User className="w-3.5 h-3.5" /> Patient & Citizen
          </button>
        </div>

        {/* DOCTOR SECTION */}
        {portal === "doctor" ? (
          <form
            onSubmit={handleDoctorSubmit}
            className="glass-card p-6 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-xl space-y-4 animate-fade-in"
          >
            {error && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-400 text-xs">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Doctor ID / Registered Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="DR-SARAH-JOHNSON"
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Clinical Vault Passkey
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-xs focus:ring-2 focus:ring-blue-500 outline-none"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl text-xs shadow-md transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Authenticating...
                </>
              ) : (
                "Authenticate & Open Clinical Suite"
              )}
            </button>

            {/* Quick Demo Doctor Fill */}
            <div className="pt-3 border-t border-gray-200 dark:border-gray-800">
              <button
                type="button"
                onClick={() => {
                  setEmail("DR-SARAH-JOHNSON");
                  setPassword("PriviDoctor2026!");
                }}
                className="w-full py-2 px-3 rounded-lg border border-blue-200 dark:border-blue-900/60 bg-blue-50/60 dark:bg-blue-950/30 text-[11px] font-semibold text-blue-800 dark:text-blue-300 flex items-center justify-between"
              >
                <span>Dr. Sarah Johnson (Cardiology)</span>
                <span className="font-mono text-[10px]">Fortis Escorts</span>
              </button>
            </div>
          </form>
        ) : (
          /* PATIENT SECTION */
          <form
            onSubmit={handlePatientSubmit}
            className="glass-card p-6 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-xl space-y-4 animate-fade-in"
          >
            <div className="p-3 rounded-xl bg-teal-50 dark:bg-teal-950/40 border border-teal-200 dark:border-teal-900/60 text-xs text-teal-900 dark:text-teal-200">
              <div className="font-bold flex items-center gap-1.5 mb-1 text-teal-800 dark:text-teal-300">
                <ShieldCheck className="w-4 h-4 text-teal-600" /> ABDM & India DPDP Act Verified Portal
              </div>
              Access your digital health card, daily prescriptions, vitals telemetry, and 24/7 recovery AI assistant.
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                ABDM 14-Digit ABHA ID / Mobile / UHID
              </label>
              <input
                type="text"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                placeholder="14-2354-9871-6542"
                className="w-full px-3.5 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-xs font-mono focus:ring-2 focus:ring-teal-500 outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Personal Passcode / Zero-Knowledge PIN
              </label>
              <input
                type="password"
                value={patientPin}
                onChange={(e) => setPatientPin(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-xs font-mono focus:ring-2 focus:ring-teal-500 outline-none"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white font-semibold rounded-xl text-xs shadow-md transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Opening Dashboard...
                </>
              ) : (
                "Authenticate & Open Patient Dashboard"
              )}
            </button>

            {/* 1-Click Patient Profiles */}
            <div className="pt-3 border-t border-gray-200 dark:border-gray-800 space-y-2">
              <div className="text-[11px] font-semibold text-gray-500 text-center">
                Instant 1-Click Verified Patients:
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => quickPatientLogin("UHID-982143")}
                  className="p-2 rounded-xl border border-teal-200 bg-teal-50/50 hover:bg-teal-100 text-left transition-colors"
                >
                  <div className="font-bold text-[11px] text-teal-800">Rajesh Sharma</div>
                  <div className="text-[10px] text-gray-500">Cardiology</div>
                </button>
                <button
                  type="button"
                  onClick={() => quickPatientLogin("UHID-447219")}
                  className="p-2 rounded-xl border border-teal-200 bg-teal-50/50 hover:bg-teal-100 text-left transition-colors"
                >
                  <div className="font-bold text-[11px] text-teal-800">Priya Patel</div>
                  <div className="text-[10px] text-gray-500">Neurology</div>
                </button>
                <button
                  type="button"
                  onClick={() => quickPatientLogin("UHID-551029")}
                  className="p-2 rounded-xl border border-teal-200 bg-teal-50/50 hover:bg-teal-100 text-left transition-colors"
                >
                  <div className="font-bold text-[11px] text-teal-800">Amit Kumar</div>
                  <div className="text-[10px] text-gray-500">Pulmonology</div>
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
