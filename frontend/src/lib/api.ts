/**
 * HealthGuard AI — Frontend API Client.
 *
 * Provides typed methods for:
 * - Authentication (Login, Register, Get User, Switch Governance Role)
 * - Document Upload (PDF, TXT, Scanned Images, DICOM .dcm)
 * - Split-Screen Clinical Chat with Zero-Trust Telemetry & Role Gating
 * - Live Compliance Audit Logs & CSV/JSON Export
 * - Vector Store "X-Ray" Inspector
 * - Automated Red-Team Privacy Stress Test
 * - India DPDP Act Section 12 Cryptographic Shredding
 * - Compliance Profile (HIPAA / DPDP / DUAL) & Confidence Thresholds
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function authHeaders(token?: string | null): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// ---------------------------------------------------------------------------
// Authentication & RBAC
// ---------------------------------------------------------------------------
export async function loginAPI(email: string, password: string) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Authentication failed");
  }
  return res.json();
}

export async function registerAPI(username: string, email: string, password: string, role: string = "doctor") {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password, role }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Registration failed");
  }
  return res.json();
}

export async function getCurrentUser(token: string) {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    headers: authHeaders(token),
  });
  if (!res.ok) {
    throw new Error("Could not validate session");
  }
  return res.json();
}

export async function switchUserRole(role: string, token: string) {
  const res = await fetch(`${API_BASE}/api/auth/switch-role`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ role }),
  });
  if (!res.ok) {
    throw new Error("Failed to switch role");
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Document Upload (Multimodal: PDF, TXT, Scanned Images, DICOM)
// ---------------------------------------------------------------------------
export async function uploadDocument(file: File, userId?: string, token?: string | null) {
  const formData = new FormData();
  formData.append("file", file);
  if (userId) {
    formData.append("user_id", userId);
  }

  const headers: HeadersInit = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Document upload failed");
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Clinical Chat (RAG + Role-Gated Re-Identification)
// ---------------------------------------------------------------------------
export async function sendChatMessage(
  message: string,
  userId: string = "default_user",
  token?: string | null,
  role: string = "doctor"
) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({
      message,
      user_id: userId,
      role,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Chat query failed");
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Audit Trail & Compliance Reporting
// ---------------------------------------------------------------------------
export async function getAuditLogs(limit: number = 100) {
  const res = await fetch(`${API_BASE}/api/audit/logs?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch audit logs");
  return res.json();
}

export async function inspectVectorStore() {
  const res = await fetch(`${API_BASE}/api/audit/vector-store`);
  if (!res.ok) throw new Error("Failed to inspect vector store");
  return res.json();
}

export function getExportAuditReportUrl(format: "json" | "csv" = "json") {
  return `${API_BASE}/api/audit/export?format=${format}`;
}

// ---------------------------------------------------------------------------
// Automated Red-Team Privacy Stress Test
// ---------------------------------------------------------------------------
export async function runStressTest() {
  const res = await fetch(`${API_BASE}/api/audit/stress-test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Stress test failed");
  return res.json();
}

// ---------------------------------------------------------------------------
// Compliance Profile & Confidence Thresholds
// ---------------------------------------------------------------------------
export async function getComplianceConfig() {
  const res = await fetch(`${API_BASE}/api/compliance/config`);
  if (!res.ok) throw new Error("Failed to fetch compliance config");
  return res.json();
}

export async function updateComplianceConfig(profile?: string, scoreThreshold?: number) {
  const res = await fetch(`${API_BASE}/api/compliance/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      compliance_profile: profile,
      score_threshold: scoreThreshold,
    }),
  });
  if (!res.ok) throw new Error("Failed to update compliance config");
  return res.json();
}

// ---------------------------------------------------------------------------
// DPDP Section 12 Crypto-Shredding & Vault Inspection
// ---------------------------------------------------------------------------
export async function cryptoShredPatient(userId: string = "default_user", patientTag?: string) {
  const res = await fetch(`${API_BASE}/api/vault/crypto-shred`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      patient_tag: patientTag,
    }),
  });
  if (!res.ok) throw new Error("Crypto-shredding request failed");
  return res.json();
}

export async function getVaultMappings(userId: string = "default_user") {
  const res = await fetch(`${API_BASE}/api/vault/mappings?user_id=${encodeURIComponent(userId)}`);
  if (!res.ok) throw new Error("Failed to retrieve vault mappings");
  return res.json();
}
