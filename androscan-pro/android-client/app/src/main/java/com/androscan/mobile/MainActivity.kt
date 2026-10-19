package com.androscan.mobile

import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.androscan.mobile.data.ApiClient
import com.androscan.mobile.data.copyUriToCache
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private val Ink = Color(0xFFEAFBFF)
private val Green = Color(0xFF00F5FF)
private val Canvas = Color(0xFF030611)
private val Panel = Color(0xFF081426)
private val Muted = Color(0xFF8CA7C3)
private val Pink = Color(0xFFFF2BD6)
private val Purple = Color(0xFF9B5CFF)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val api = ApiClient(applicationContext)
        setContent { MaterialTheme(colorScheme = darkColorScheme(primary = Green, secondary = Pink, tertiary = Purple, background = Canvas, surface = Panel, onBackground = Ink, onSurface = Ink)) { AndroScanApp(api) } }
    }
}

@Composable
private fun AndroScanApp(api: ApiClient) {
    val scope = rememberCoroutineScope()
    var signedIn by remember { mutableStateOf(api.isSignedIn()) }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var server by remember { mutableStateOf(api.baseUrl) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf("") }
    var info by remember { mutableStateOf("") }
    var organizations by remember { mutableStateOf<List<JSONObject>>(emptyList()) }
    var apps by remember { mutableStateOf<List<JSONObject>>(emptyList()) }
    var analyses by remember { mutableStateOf<List<JSONObject>>(emptyList()) }
    var findings by remember { mutableStateOf<List<JSONObject>>(emptyList()) }
    var reports by remember { mutableStateOf<List<JSONObject>>(emptyList()) }
    var org by remember { mutableStateOf<JSONObject?>(null) }
    var app by remember { mutableStateOf<JSONObject?>(null) }
    var selectedAnalysis by remember { mutableStateOf<JSONObject?>(null) }
    var newAppName by remember { mutableStateOf("") }
    var packageName by remember { mutableStateOf("") }

    fun runAction(action: suspend () -> Unit) {
        scope.launch {
            busy = true; error = ""; info = ""
            try { action() } catch (e: Exception) { error = e.message ?: "Ocurrió un error inesperado" }
            finally { busy = false }
        }
    }
    fun refreshOrgs() = runAction { organizations = api.organizations(); org = organizations.firstOrNull(); if (org != null) apps = api.applications(org!!.getString("id")) }

    val context = androidx.compose.ui.platform.LocalContext.current
    val apkPicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        if (uri != null && org != null && app != null) runAction {
            val temp: File = copyUriToCache(context, uri)
            try {
                val version = api.uploadApk(org!!.getString("id"), app!!.getString("id"), temp)
                val analysis = api.startAnalysis(org!!.getString("id"), version.getString("id"))
                info = "APK recibido y análisis encolado. Estado: ${analysis.optString("state", "CREATED")}."
                analyses = api.analyses(org!!.getString("id"), app!!.getString("id"))
            } finally { temp.delete() }
        }
    }

    Scaffold(containerColor = Canvas, topBar = {
        Row(Modifier.fillMaxWidth().background(Color(0xFF070D1C)).padding(horizontal = 20.dp, vertical = 18.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("ANDROSCAN", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Black, letterSpacing = 2.sp)
                Text("Mobile APK Security Console", color = Muted, fontSize = 11.sp)
            }
            if (signedIn) TextButton(onClick = { api.signOut(); signedIn = false; organizations = emptyList(); org = null; app = null; selectedAnalysis = null }) { Text("Cerrar sesión", color = Color.White) }
        }
    }) { padding ->
        if (!signedIn) {
            Column(Modifier.fillMaxSize().padding(padding).padding(24.dp), verticalArrangement = Arrangement.Center) {
                Text("Bienvenido", color = Green, fontSize = 30.sp, fontWeight = FontWeight.Bold)
                Text("Conéctate a tu servidor AndroScan", color = Muted, modifier = Modifier.padding(top = 6.dp, bottom = 24.dp))
                Field("URL base del servidor", server, { server = it }, keyboard = KeyboardType.Uri)
                Field("Correo electrónico", email, { email = it }, keyboard = KeyboardType.Email)
                OutlinedTextField(value = password, onValueChange = { password = it }, label = { Text("Contraseña") }, modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp), visualTransformation = PasswordVisualTransformation(), singleLine = true)
                if (error.isNotBlank()) ErrorText(error)
                Button(onClick = { runAction { api.baseUrl = server; api.login(email, password); signedIn = true; organizations = api.organizations(); org = organizations.firstOrNull(); if (org != null) apps = api.applications(org!!.getString("id")); password = "" } }, enabled = !busy && email.isNotBlank() && password.length >= 8 && server.isNotBlank(), modifier = Modifier.fillMaxWidth().padding(top = 14.dp), colors = ButtonDefaults.buttonColors(containerColor = Green)) { Text(if (busy) "Conectando…" else "Iniciar sesión") }
                Text("Usa HTTPS para conexiones remotas. No ingreses credenciales en servidores que no controles.", color = Muted, fontSize = 12.sp, modifier = Modifier.padding(top = 14.dp))
            }
        } else {
            LazyColumn(Modifier.fillMaxSize().padding(padding).padding(horizontal = 16.dp), verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(vertical = 16.dp)) {
                item { if (error.isNotBlank()) ErrorText(error); if (info.isNotBlank()) InfoCard(info); if (busy) LinearProgressIndicator(Modifier.fillMaxWidth(), color = Green) }
                item { SectionTitle("1 · Organización") }
                item {
                    if (organizations.isEmpty()) {
                        ActionButton("Actualizar organizaciones") { refreshOrgs() }
                    } else {
                        organizations.forEach { organization ->
                            SelectableCard(organization.optString("name"), organization.optString("slug"), org?.optString("id") == organization.optString("id")) {
                                org = organization; app = null; selectedAnalysis = null; analyses = emptyList(); findings = emptyList(); reports = emptyList()
                                runAction { apps = api.applications(organization.getString("id")) }
                            }
                        }
                    }
                }
                item { SectionTitle("2 · Aplicaciones") }
                item {
                    Column(Modifier.fillMaxWidth().background(Panel, RoundedCornerShape(16.dp)).padding(14.dp)) {
                        Field("Nombre de la aplicación", newAppName, { newAppName = it })
                        Field("Package name (ej. com.empresa.app)", packageName, { packageName = it })
                        ActionButton("Registrar aplicación") {
                            val selectedOrg = org
                            if (selectedOrg == null) error = "Selecciona una organización primero" else runAction {
                                api.createApplication(selectedOrg.getString("id"), newAppName.trim(), packageName.trim())
                                apps = api.applications(selectedOrg.getString("id")); newAppName = ""; packageName = ""; info = "Aplicación registrada."
                            }
                        }
                    }
                }
                items(apps, key = { it.optString("id") }) { item ->
                    SelectableCard(item.optString("name"), item.optString("package_name"), app?.optString("id") == item.optString("id")) {
                        app = item; selectedAnalysis = null; findings = emptyList(); reports = emptyList()
                        runAction { analyses = api.analyses(org!!.getString("id"), item.getString("id")) }
                    }
                }
                item {
                    SectionTitle("3 · Analizar APK")
                    Text("El archivo se envía al servidor para validación y análisis. AndroScan no ejecuta el APK en el teléfono.", color = Muted, fontSize = 13.sp, modifier = Modifier.padding(bottom = 8.dp))
                    ActionButton("Seleccionar APK y analizar") { if (org == null || app == null) error = "Selecciona organización y aplicación antes de cargar el APK" else apkPicker.launch(arrayOf("application/vnd.android.package-archive", "application/octet-stream")) }
                }
                item { SectionTitle("4 · Historial de análisis") }
                if (analyses.isEmpty()) item { Text("No hay análisis cargados para esta aplicación o aún no se ha seleccionado una.", color = Muted, fontSize = 13.sp) }
                items(analyses, key = { it.optString("id") }) { analysis ->
                    SelectableCard("Estado: ${analysis.optString("state")}", "ID ${analysis.optString("id").take(12)}… · ${analysis.optString("created_at")}", selectedAnalysis?.optString("id") == analysis.optString("id")) {
                        selectedAnalysis = analysis
                        runAction { findings = api.findings(org!!.getString("id"), analysis.getString("id")); reports = api.reports(org!!.getString("id"), analysis.getString("id")) }
                    }
                }
                item { SectionTitle("5 · Hallazgos") }
                if (selectedAnalysis != null && findings.isEmpty()) item { Text("No hay hallazgos disponibles todavía. Si el análisis está en cola, vuelve a seleccionar el registro para actualizar.", color = Muted, fontSize = 13.sp) }
                items(findings, key = { it.optString("id") }) { finding ->
                    Column(Modifier.fillMaxWidth().background(Panel, RoundedCornerShape(14.dp)).padding(14.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(finding.optString("severity", "UNKNOWN"), color = severityColor(finding.optString("severity")), fontWeight = FontWeight.Bold, fontSize = 11.sp)
                            Spacer(Modifier.width(8.dp)); Text("· ${finding.optString("priority")}", color = Muted, fontSize = 11.sp)
                        }
                        Text(finding.optString("title", "Hallazgo"), color = Ink, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 5.dp))
                        Text(finding.optString("description"), color = Color.DarkGray, fontSize = 13.sp, modifier = Modifier.padding(top = 4.dp))
                        Text("Categoría: ${finding.optString("category")} · Revisión: ${finding.optString("review_state")}", color = Muted, fontSize = 11.sp, modifier = Modifier.padding(top = 8.dp))
                    }
                }
                item {
                    SectionTitle("6 · Informes")
                    if (selectedAnalysis != null) {
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                            listOf("JSON", "HTML", "PDF").forEach { format ->
                                Button(onClick = {
                                    val selected = selectedAnalysis
                                    val selectedOrg = org
                                    if (selected != null && selectedOrg != null) runAction {
                                        api.createReport(selectedOrg.getString("id"), selected.getString("id"), format)
                                        reports = api.reports(selectedOrg.getString("id"), selected.getString("id"))
                                        info = "Informe $format generado."
                                    }
                                }, enabled = !busy, colors = ButtonDefaults.buttonColors(containerColor = Green), modifier = Modifier.weight(1f)) { Text(format) }
                            }
                        }
                        if (reports.isEmpty()) Text("No hay informes generados para este análisis.", color = Muted, fontSize = 12.sp)
                        reports.forEach { report ->
                            SelectableCard("${report.optString("format")} · ${report.optString("status")}", "${report.optString("filename")} · ${report.optLong("size_bytes")} bytes", false) { info = "SHA-256: ${report.optString("sha256")}" }
                        }
                    } else Text("Selecciona un análisis para generar informes.", color = Muted, fontSize = 12.sp)
                }
                item { Text("La clasificación es una ayuda técnica. La decisión final de riesgo corresponde a la persona analista.", color = Muted, fontSize = 12.sp, modifier = Modifier.padding(vertical = 8.dp)) }
            }
        }
    }
}

@Composable private fun SectionTitle(text: String) { Text(text, color = Ink, fontSize = 17.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 4.dp, bottom = 2.dp)) }
@Composable private fun Field(label: String, value: String, onChange: (String) -> Unit, keyboard: KeyboardType = KeyboardType.Text) {
    OutlinedTextField(value = value, onValueChange = onChange, label = { Text(label) }, modifier = Modifier.fillMaxWidth().padding(vertical = 5.dp), singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = keyboard))
}
@Composable private fun ActionButton(label: String, action: () -> Unit) { Button(onClick = action, modifier = Modifier.fillMaxWidth().padding(top = 8.dp), colors = ButtonDefaults.buttonColors(containerColor = Green)) { Text(label) } }
@Composable private fun SelectableCard(title: String, subtitle: String, selected: Boolean, action: () -> Unit) {
    Card(onClick = action, modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp), colors = CardDefaults.cardColors(containerColor = if (selected) Color(0xFF102A3A) else Panel), shape = RoundedCornerShape(14.dp)) {
        Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) { Text(title, color = Ink, fontWeight = FontWeight.SemiBold); Text(subtitle, color = Muted, fontSize = 12.sp) }
            if (selected) Text("SELECCIONADO", color = Green, fontSize = 9.sp, fontWeight = FontWeight.Bold)
        }
    }
}
@Composable private fun ErrorText(text: String) { Text(text, color = Color(0xFFFF7C9B), modifier = Modifier.fillMaxWidth().background(Color(0xFF321225), RoundedCornerShape(10.dp)).padding(12.dp), fontSize = 13.sp) }
@Composable private fun InfoCard(text: String) { Text(text, color = Color(0xFF00FF9C), modifier = Modifier.fillMaxWidth().background(Color(0xFF0B2927), RoundedCornerShape(10.dp)).padding(12.dp), fontSize = 13.sp) }
private fun severityColor(severity: String): Color = when (severity.uppercase(Locale.ROOT)) { "CRITICAL" -> Color(0xFFB42318); "HIGH" -> Color(0xFFDC6803); "MEDIUM" -> Color(0xFFB54708); "LOW" -> Color(0xFF027A48); else -> Color.Gray }
