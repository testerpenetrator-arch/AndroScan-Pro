const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
export async function login(email: string, password: string) {
  const res = await fetch(`${API}/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
  if (!res.ok) throw new Error("Credenciales inválidas");
  return res.json();
}
export async function getOrganizations(token: string) {
  const res = await fetch(`${API}/organizations`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("No fue posible cargar organizaciones");
  return res.json();
}
export async function getDashboard(token: string, organizationId: string) {
  const res = await fetch(`${API}/organizations/${organizationId}/dashboard`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("No fue posible cargar el dashboard");
  return res.json();
}

export async function getAdminSettings(token: string, organizationId: string) {
  const res = await fetch(`${API}/organizations/${organizationId}/admin/settings`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error(res.status === 403 ? "Tu rol no permite administrar esta organización" : "No fue posible cargar la configuración");
  return res.json();
}
export async function updateAdminSettings(token: string, organizationId: string, payload: Record<string, unknown>) {
  const res = await fetch(`${API}/organizations/${organizationId}/admin/settings`, { method: "PUT", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error("No fue posible guardar la configuración");
  return res.json();
}
export async function getToolPolicy(token: string, organizationId: string) {
  const res = await fetch(`${API}/organizations/${organizationId}/admin/tools`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("No fue posible cargar las herramientas habilitadas");
  return res.json();
}
export async function updateToolPolicy(token: string, organizationId: string, enabled_tools: string[]) {
  const res = await fetch(`${API}/organizations/${organizationId}/admin/tools`, { method: "PUT", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }, body: JSON.stringify({ enabled_tools }) });
  if (!res.ok) throw new Error("No fue posible guardar las herramientas");
  return res.json();
}


async function checkResponse(res: Response, fallback: string) {
  if (res.ok) return res.json();
  let message = fallback;
  try {
    const payload = await res.json();
    if (typeof payload.detail === "string") message = payload.detail;
    else if (payload.detail) message = JSON.stringify(payload.detail);
  } catch {}
  throw new Error(message);
}

export async function getApplications(token: string, organizationId: string) {
  const res = await fetch(`${API}/organizations/${organizationId}/applications`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return checkResponse(res, "No fue posible consultar las aplicaciones");
}

export async function createApplication(
  token: string,
  organizationId: string,
  payload: { name: string; package_name: string }
) {
  const res = await fetch(`${API}/organizations/${organizationId}/applications`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
  return checkResponse(res, "No fue posible registrar la aplicación");
}

export async function uploadApk(
  token: string,
  organizationId: string,
  applicationId: string,
  file: File,
  versionName: string,
  versionCode: string
) {
  const form = new FormData();
  form.append("file", file);
  if (versionName.trim()) form.append("version_name", versionName.trim());
  if (versionCode.trim()) form.append("version_code", versionCode.trim());

  const res = await fetch(
    `${API}/organizations/${organizationId}/applications/${applicationId}/apk`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: form
    }
  );
  return checkResponse(res, "No fue posible cargar el APK");
}

export async function startAnalysis(
  token: string,
  organizationId: string,
  versionId: string
) {
  const res = await fetch(
    `${API}/organizations/${organizationId}/versions/${versionId}/analyses`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return checkResponse(res, "No fue posible iniciar el análisis");
}
