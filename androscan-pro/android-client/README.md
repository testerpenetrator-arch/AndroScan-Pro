# AndroScan Android — cliente nativo inicial

Cliente Android nativo en Kotlin + Jetpack Compose. Se comunica con la API FastAPI existente; **no analiza ni ejecuta APK localmente**.

## Funcionalidad incluida en este incremento

- Inicio de sesión con `POST /api/v1/auth/login`.
- Almacenamiento cifrado de la sesión mediante AndroidX Security Crypto.
- Consulta y selección de organizaciones accesibles por el usuario autenticado.
- Consulta y registro de aplicaciones.
- Selección de APK mediante el selector de documentos Android y carga multipart al backend.
- Inicio de análisis asíncrono y consulta del historial.
- Consulta de hallazgos con severidad, prioridad y estado de revisión.
- Manejo básico de estados ocupados, errores y confirmaciones.
- HTTPS obligatorio para servidor remoto; no se desactiva validación TLS.

## Herramientas

- Android Studio actualizado con soporte para Android Gradle Plugin 8.7.3.
- JDK 17 o compatible con AGP 8.7.x (JDK 21 también suele ser compatible).
- Android SDK Platform 35 y Build Tools correspondientes.
- Gradle descargado por Android Studio o instalación compatible.

## Compilar en Android Studio

1. Abre la carpeta `android-client` como proyecto Gradle.
2. Espera la sincronización y descarga de dependencias.
3. Configura la URL de la API en el campo de inicio de sesión. Usa la URL HTTPS de tu servidor real.
4. Para generar un APK de depuración, selecciona **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
5. Instala el APK de depuración en un dispositivo compatible y prueba contra un servidor de ensayo.

Desde la terminal, con Gradle instalado y Android SDK configurado:

```bash
gradle assembleDebug
```

Este paquete todavía no incluye el wrapper `gradlew` ni el SDK de Android. La compilación real debe hacerse en Android Studio o en un entorno Android SDK configurado. No se afirma que exista un APK compilado en este incremento.

## Configuración de servidor

El cliente solicita una URL base. Las URL remotas deben usar HTTPS y un certificado confiable. Solo se permiten excepciones HTTP para direcciones locales de desarrollo (`10.0.2.2` o `localhost`). No uses esas excepciones en producción.

El inicio de sesión usa JWT de la API. La sesión se guarda en preferencias cifradas del dispositivo. Cerrar sesión elimina el token local. No se almacenan contraseñas.

## Limitaciones conocidas del primer incremento

- Sin renovación automática de JWT: al expirar la sesión se debe volver a iniciar sesión.
- No se implementa todavía descarga de informes, comparación de versiones, paginación ni sondeo automático del análisis.
- La carga se ejecuta en segundo plano, pero no dispone aún de una barra de progreso por bytes.
- Las respuestas del backend y la seguridad multi-tenant deben validarse mediante pruebas de integración en un entorno desplegado.
- La clave de firma de release no se incluye en el repositorio; debe custodiarse fuera del código fuente.
