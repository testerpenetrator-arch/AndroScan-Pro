import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { getDashboard, getOrganizations, login, getAdminSettings, updateAdminSettings, getToolPolicy, updateToolPolicy, getApplications, createApplication, uploadApk, startAnalysis } from "./services/api";
import type { Dashboard } from "./types/dashboard";

const labels: Record<string,string> = { COMPLETED:"Completado", RUNNING:"Ejecutando", QUEUED:"En cola", PREPARING:"Preparando", PROCESSING_RESULTS:"Procesando", FAILED:"Fallido", CANCELLED:"Cancelado", CREATED:"Creado", PENDING:"Pendiente", CONFIRMED:"Confirmado", DISMISSED:"Descartado" };

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("androscan_token") || "");
  const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState("");
  const [orgs, setOrgs] = useState<any[]>([]); const [org, setOrg] = useState(""); const [data, setData] = useState<Dashboard | null>(null);
  const [appName, setAppName] = useState("");
  const [packageName, setPackageName] = useState("");
  const [versionName, setVersionName] = useState("");
  const [versionCode, setVersionCode] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadBusy, setUploadBusy] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");


  async function enter(e: FormEvent) { e.preventDefault(); setError(""); try { const r=await login(email,password); localStorage.setItem("androscan_token",r.access_token); setToken(r.access_token); } catch(err:any){setError(err.message)} }

  async function submitUpload(e: FormEvent) {
    e.preventDefault();
    setUploadError("");
    setUploadMessage("");

    if (!org) {
      setUploadError("Selecciona una organización antes de continuar.");
      return;
    }
    if (!selectedFile) {
      setUploadError("Selecciona un archivo APK.");
      return;
    }
    if (!selectedFile.name.toLowerCase().endsWith(".apk")) {
      setUploadError("El archivo seleccionado debe tener extensión .apk.");
      return;
    }

    setUploadBusy(true);
    let apkUploaded = false;

    try {
      const applications = await getApplications(token, org);
      const existing = applications.find(
        (item: any) => item.package_name === packageName.trim()
      );

      const application = existing || await createApplication(token, org, {
        name: appName.trim(),
        package_name: packageName.trim()
      });

      const version = await uploadApk(
        token, org, application.id, selectedFile, versionName, versionCode
      );
      apkUploaded = true;

      const analysis = await startAnalysis(token, org, version.id);

      setUploadMessage(
        `APK validado y análisis aceptado en la cola. Estado: ${analysis.state || "QUEUED"}.`
      );
      setSelectedFile(null);
      setData(await getDashboard(token, org));
    } catch (err: any) {
      setUploadError(
        apkUploaded
          ? `El APK se cargó, pero no se pudo iniciar el análisis: ${err.message}`
          : err.message || "Ocurrió un error al cargar el APK."
      );
    } finally {
      setUploadBusy(false);
    }
  }

  useEffect(()=>{ if(token) getOrganizations(token).then(x=>{setOrgs(x); if(x[0]) setOrg(x[0].id)}).catch(e=>setError(e.message)); },[token]);
  useEffect(()=>{ if(token && org) getDashboard(token,org).then(setData).catch(e=>setError(e.message)); },[token,org]);
  if(!token) return <main className="login"><form className="login-card" onSubmit={enter}><div className="brand">ANDRO<span>SCAN</span></div><p>Plataforma de análisis de seguridad Android</p><input aria-label="Correo" type="email" placeholder="Correo" value={email} onChange={e=>setEmail(e.target.value)} required/><input aria-label="Contraseña" type="password" placeholder="Contraseña" value={password} onChange={e=>setPassword(e.target.value)} required/><button>Iniciar sesión</button>{error&&<div className="error">{error}</div>}</form></main>;
  return <main className="app"><header><div><div className="brand">ANDRO<span>SCAN</span></div><small>Security Analysis Console</small></div><div className="header-actions"><select value={org} onChange={e=>setOrg(e.target.value)}>{orgs.map(o=><option key={o.id} value={o.id}>{o.name}</option>)}</select><button className="ghost" onClick={()=>{localStorage.removeItem("androscan_token");setToken("")}}>Salir</button></div></header>
    {error&&<div className="error banner">{error}</div>}
    {org && <AdminPanel token={token} organizationId={org} />}
    {!data?<div className="loading">Cargando dashboard…</div>:<><section className="hero"><div><span className="eyebrow">F9.8 · DASHBOARD</span><h1>Visión general de seguridad</h1><p>Estado operativo de aplicaciones, análisis y hallazgos de la organización seleccionada.</p></div></section>
    <section className="panel upload-panel">
      <div className="panel-title">
        <h2>Subir APK y analizar</h2>
        <span>ANÁLISIS ESTÁTICO</span>
      </div>
      <form className="upload-form" onSubmit={submitUpload}>
        <label>
          Nombre de la aplicación
          <input value={appName} onChange={e => setAppName(e.target.value)}
            placeholder="Mi aplicación Android" maxLength={200} required />
        </label>
        <label>
          Nombre del paquete
          <input value={packageName} onChange={e => setPackageName(e.target.value)}
            placeholder="com.ejemplo.aplicacion"
            pattern="[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+"
            title="Ejemplo: com.ejemplo.aplicacion" maxLength={255} required />
        </label>
        <div className="upload-columns">
          <label>
            Versión (opcional)
            <input value={versionName} onChange={e => setVersionName(e.target.value)}
              placeholder="1.0.0" maxLength={120} />
          </label>
          <label>
            Código de versión (opcional)
            <input value={versionCode} onChange={e => setVersionCode(e.target.value)}
              placeholder="1" maxLength={120} />
          </label>
        </div>
        <label className="file-picker">
          Archivo APK
          <input key={selectedFile ? selectedFile.name : "no-file"}
            type="file" accept=".apk,application/vnd.android.package-archive"
            onChange={e => setSelectedFile(e.target.files?.[0] || null)}
            required />
          <small>Selecciona un APK autorizado para realizar pruebas.</small>
        </label>
        {selectedFile && <p className="file-selected">Seleccionado: {selectedFile.name} · {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>}
        <button type="submit" disabled={uploadBusy || !org}>
          {uploadBusy ? "Procesando…" : "Subir APK y solicitar análisis"}
        </button>
        {uploadMessage && <p className="success" role="status">{uploadMessage}</p>}
        {uploadError && <p className="error" role="alert">{uploadError}</p>}
      </form>
    </section>
    <section className="metrics">{[["Aplicaciones",data.counts.applications],["Versiones APK",data.counts.versions],["Análisis",data.counts.analyses],["Hallazgos",data.counts.findings],["Pendientes",data.counts.pending_findings],["Críticos",data.counts.critical_findings],["Altos",data.counts.high_findings]].map(([a,b])=><article className="metric" key={a as string}><span>{a}</span><strong>{b}</strong></article>)}</section>
    <section className="grid"><article className="panel"><div className="panel-title"><h2>Análisis recientes</h2><span>{data.analyses.length}</span></div><div className="table">{data.analyses.map(a=><div className="row" key={a.id}><div><b>{a.application_name}</b><small>{a.package_name}{a.version_name?` · ${a.version_name}`:""}</small></div><span className={`status ${a.state.toLowerCase()}`}>{labels[a.state]||a.state}</span><strong>{a.finding_count}</strong></div>)}{!data.analyses.length&&<div className="empty">No hay análisis registrados.</div>}</div></article>
    <article className="panel"><div className="panel-title"><h2>Hallazgos recientes</h2><span>{data.findings.length}</span></div><div className="table">{data.findings.map(f=><div className="row" key={f.id}><div><b>{f.title}</b><small>{f.application_name} · {f.category}</small></div><span className={`severity ${f.severity.toLowerCase()}`}>{f.severity}</span><span className="priority">{f.priority}</span></div>)}{!data.findings.length&&<div className="empty">No hay hallazgos registrados.</div>}</div></article></section></>}
  </main>;
}


function AdminPanel({ token, organizationId }: { token: string; organizationId: string }) {
  const [settings, setSettings] = useState<any>(null);
  const [tools, setTools] = useState<string[]>([]);
  const [availableTools, setAvailableTools] = useState<any[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [forbidden, setForbidden] = useState(false);
  useEffect(() => {
    let alive = true;
    Promise.all([getAdminSettings(token, organizationId), getToolPolicy(token, organizationId)])
      .then(([s, t]) => { if (alive) { setSettings(s); setTools(t.enabled_tools); setAvailableTools(t.available_tools); setForbidden(false); } })
      .catch((e: Error) => { if (alive) { setError(e.message); setForbidden(true); } });
    return () => { alive = false; };
  }, [token, organizationId]);
  if (forbidden) return null;
  if (!settings) return <section className="panel admin-panel"><h2>Administración</h2><p>{error || "Cargando configuración…"}</p></section>;
  async function saveSettings() {
    setError(""); setMessage("");
    try { const updated = await updateAdminSettings(token, organizationId, settings); setSettings(updated); setMessage("Configuración guardada."); }
    catch (e: any) { setError(e.message); }
  }
  async function saveTools() {
    setError(""); setMessage("");
    try { const updated = await updateToolPolicy(token, organizationId, tools); setTools(updated.enabled_tools); setMessage("Herramientas guardadas."); }
    catch (e: any) { setError(e.message); }
  }
  return <section className="panel admin-panel">
    <div className="panel-title"><h2>Administración de la organización</h2><span>F9.12</span></div>
    <p className="admin-note">Los cambios se aplican según las capacidades implementadas. La concurrencia y la retención automática aún requieren integración del planificador.</p>
    <div className="admin-form">
      <label>Tamaño máximo APK (MB)<input type="number" min="1" max="500" value={settings.max_apk_size_mb} onChange={e=>setSettings({...settings,max_apk_size_mb:Number(e.target.value)})}/></label>
      <label>Análisis simultáneos (política)<input type="number" min="1" max="50" value={settings.max_concurrent_analyses} onChange={e=>setSettings({...settings,max_concurrent_analyses:Number(e.target.value)})}/></label>
      <label>Tiempo máximo (segundos)<input type="number" min="60" max="3600" value={settings.analysis_timeout_seconds} onChange={e=>setSettings({...settings,analysis_timeout_seconds:Number(e.target.value)})}/></label>
      <label>Retención (días)<input type="number" min="1" max="3650" value={settings.retention_days} onChange={e=>setSettings({...settings,retention_days:Number(e.target.value)})}/></label>
    </div>
    <div className="admin-toggles">
      <label><input type="checkbox" checked={settings.ai_assistance_enabled} onChange={e=>setSettings({...settings,ai_assistance_enabled:e.target.checked, ...(e.target.checked?{}:{external_ai_enabled:false})})}/> Asistencia IA local habilitada</label>
      <label><input type="checkbox" checked={settings.external_ai_enabled} disabled={!settings.ai_assistance_enabled} onChange={e=>setSettings({...settings,external_ai_enabled:e.target.checked})}/> Proveedor IA externo autorizado (sin integración activa)</label>
    </div>
    <button onClick={saveSettings}>Guardar parámetros</button>
    <h3>Herramientas de análisis estático</h3>
    <div className="admin-toggles">{availableTools.map(t=><label key={t.id}><input type="checkbox" checked={tools.includes(t.id)} onChange={e=>setTools(e.target.checked?[...tools,t.id]:tools.filter(x=>x!==t.id))}/>{t.name} <small>{t.version}</small></label>)}</div>
    <button onClick={saveTools} disabled={!tools.length}>Guardar herramientas</button>
    {message&&<p className="success">{message}</p>}{error&&<p className="error">{error}</p>}
  </section>;
}
