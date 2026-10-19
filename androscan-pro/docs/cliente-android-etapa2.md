# Etapa 2 — Cliente Android nativo (primer incremento)

## Resultado

Se incorpora el proyecto fuente Android `android-client/`, construido con Kotlin y Jetpack Compose. Integra las rutas existentes de autenticación, organizaciones, aplicaciones, carga de APK, inicio/consulta de análisis y hallazgos.

## Validaciones de este entorno

- La suite backend se ejecutó de nuevo: 44 pruebas aprobadas.
- Se verificó que el proyecto móvil contiene configuración Gradle, manifiesto, actividad, cliente HTTP y documentación.
- Se comprobó la sintaxis XML del manifiesto y los recursos.
- No hay Android SDK (`ANDROID_HOME` no está configurado) ni Gradle instalado en el entorno de generación. Por eso no se puede declarar compilación Kotlin ni generar un APK binario validado aquí.

## Alcance que queda para completar

1. Compilar y corregir cualquier incompatibilidad real con Android Studio/Gradle.
2. Implementar descarga segura de informes y comparación de versiones.
3. Mejorar progreso/reintentos de carga y actualización del estado de análisis.
4. Añadir pruebas unitarias y UI en emulador/dispositivo.
5. Probar el flujo contra un servidor desplegado con TLS válido y usuarios de prueba multi-tenant.
6. Definir y custodiar la clave de firma release fuera del repositorio y comprobar la firma del APK resultante.

## Seguridad

- La selección de APK usa el selector del sistema, no solicita permiso de almacenamiento general.
- El archivo se transmite al servidor; no se ejecuta en el teléfono.
- El token se guarda con AndroidX Security Crypto y se elimina al cerrar sesión.
- Las URL remotas requieren HTTPS; no se desactiva la validación TLS.
- El servidor sigue siendo responsable de autenticar y autorizar cada operación y aislar los datos por organización.

## Actualización de integración — etapa 3 (15 de octubre de 2026)

Se añadieron acciones para generar informes JSON, HTML y PDF desde un análisis seleccionado y consultar los informes existentes de ese análisis. Los informes se solicitan a la ruta real `GET/POST /api/v1/organizations/{organization_id}/reports`, usando `analysis_id` como filtro de consulta. La descarga binaria del informe y su apertura/compartición desde Android quedan para el siguiente incremento de integración.

Se incorporaron pruebas de contrato que comparan las rutas mínimas utilizadas por el cliente con el OpenAPI real del backend. Estas pruebas no sustituyen las pruebas de extremo a extremo en un servidor desplegado.
