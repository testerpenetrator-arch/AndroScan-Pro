package com.androscan.mobile.data

import android.content.Context
import android.net.Uri
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.util.concurrent.TimeUnit

class ApiClient(context: Context) {
    private val prefs = EncryptedSharedPreferences.create(
        context,
        "androscan_secure_session",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    private val http = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS).readTimeout(90, TimeUnit.SECONDS)
        .writeTimeout(180, TimeUnit.SECONDS).build()

    var baseUrl: String
        get() = prefs.getString("base_url", "https://your-androscan-server.example") ?: "https://your-androscan-server.example"
        set(value) { prefs.edit().putString("base_url", value.trim().trimEnd('/')).apply() }
    private var token: String?
        get() = prefs.getString("access_token", null)
        set(value) { prefs.edit().putString("access_token", value).apply() }
    fun isSignedIn() = !token.isNullOrBlank()
    fun signOut() { token = null }

    private suspend fun request(path: String, method: String = "GET", body: okhttp3.RequestBody? = null): String = withContext(Dispatchers.IO) {
        val base = baseUrl.trim().trimEnd('/')
        require(base.startsWith("https://", true) || (base.startsWith("http://10.0.2.2") || base.startsWith("http://localhost"))) {
            "Usa HTTPS para servidores remotos. HTTP solo se admite para pruebas locales de desarrollo."
        }
        val builder = Request.Builder().url("$base/api/v1$path").header("Accept", "application/json")
        token?.let { builder.header("Authorization", "Bearer $it") }
        when (method) { "POST" -> builder.post(body ?: ByteArray(0).toRequestBody(null)); "PUT" -> builder.put(body ?: ByteArray(0).toRequestBody(null)); else -> builder.get() }
        http.newCall(builder.build()).execute().use { response ->
            val text = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                val message = try { JSONObject(text).optString("detail", "Error HTTP ${response.code}") } catch (_: Exception) { "Error HTTP ${response.code}" }
                throw IOException(message)
            }
            text
        }
    }

    suspend fun login(email: String, password: String) {
        val json = JSONObject().put("email", email.trim()).put("password", password)
        val result = JSONObject(request("/auth/login", "POST", json.toString().toRequestBody("application/json".toMediaType())))
        token = result.getString("access_token")
    }
    suspend fun organizations(): List<JSONObject> = jsonArray(request("/organizations"))
    suspend fun applications(org: String): List<JSONObject> = jsonArray(request("/organizations/${org.enc()}/applications"))
    suspend fun createApplication(org: String, name: String, packageName: String): JSONObject {
        val json = JSONObject().put("name", name).put("package_name", packageName)
        return JSONObject(request("/organizations/${org.enc()}/applications", "POST", json.toString().toRequestBody("application/json".toMediaType())))
    }
    suspend fun uploadApk(org: String, app: String, file: File): JSONObject = withContext(Dispatchers.IO) {
        val body = MultipartBody.Builder().setType(MultipartBody.FORM)
            .addFormDataPart("file", file.name, file.asRequestBody("application/vnd.android.package-archive".toMediaType())).build()
        JSONObject(request("/organizations/${org.enc()}/applications/${app.enc()}/apk", "POST", body))
    }
    suspend fun startAnalysis(org: String, version: String): JSONObject {
        return JSONObject(request("/organizations/${org.enc()}/versions/${version.enc()}/analyses", "POST", "{}".toRequestBody("application/json".toMediaType())))
    }
    suspend fun analyses(org: String, app: String): List<JSONObject> = jsonArray(request("/organizations/${org.enc()}/applications/${app.enc()}/analyses"))
    suspend fun findings(org: String, analysis: String): List<JSONObject> = jsonArray(request("/organizations/${org.enc()}/analyses/${analysis.enc()}/findings"))
    suspend fun createReport(org: String, analysis: String, format: String = "JSON"): JSONObject {
        require(format in setOf("JSON", "HTML", "PDF")) { "Formato de informe no válido" }
        val json = JSONObject().put("analysis_id", analysis).put("format", format)
        return JSONObject(request("/organizations/${org.enc()}/reports", "POST", json.toString().toRequestBody("application/json".toMediaType())))
    }
    suspend fun reports(org: String, analysis: String): List<JSONObject> =
        jsonArray(request("/organizations/${org.enc()}/reports?analysis_id=${java.net.URLEncoder.encode(analysis, "UTF-8")}"))

    private fun jsonArray(raw: String): List<JSONObject> {
        val array = JSONArray(raw)
        return (0 until array.length()).map { array.getJSONObject(it) }
    }
    private fun String.enc() = java.net.URLEncoder.encode(this, "UTF-8")
}

fun copyUriToCache(context: Context, uri: Uri): File {
    val name = context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
        val index = cursor.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
        if (cursor.moveToFirst() && index >= 0) cursor.getString(index) else null
    } ?: "selected.apk"
    require(name.lowercase().endsWith(".apk")) { "Selecciona un archivo con extensión .apk" }
    val out = File.createTempFile("androscan-upload-", ".apk", context.cacheDir)
    context.contentResolver.openInputStream(uri).use { input ->
        requireNotNull(input) { "No se pudo abrir el archivo" }.use { source -> out.outputStream().use { target -> source.copyTo(target) } }
    }
    return out
}
