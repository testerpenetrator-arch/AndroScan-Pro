# Preparación de entrega final y firma Android

## Estado del artefacto

El repositorio contiene el código fuente del cliente Android. En el entorno donde se preparó este paquete no se dispone de Gradle ni Android SDK, por lo que **no se incluye ni se afirma que exista un APK compilado**. El workflow de CI intenta compilarlo y, si tiene éxito, publicar el APK de depuración como artefacto de la ejecución.

## Compilación local

Requisitos: JDK 17, Gradle 8.9 y Android SDK Platform 35 / Build Tools 35.0.0.

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin"
./scripts/build-android-apk.sh
```

El script comprueba requisitos, compila el APK debug y calcula su SHA-256. No firma una versión de producción.

## Instalación de prueba

Con un dispositivo autorizado y depuración USB activada:

```bash
adb install -r android-client/app/build/outputs/apk/debug/app-debug.apk
```

En el primer inicio, configura la URL HTTPS del servidor de ensayo. No uses HTTP en redes remotas ni credenciales reales contra un servidor no confiable.

## Firma de producción

La clave privada de firma debe generarse y custodiarse fuera del repositorio, idealmente en un almacén de secretos del CI o en un equipo de release controlado. Nunca añadas keystore, contraseñas ni tokens al ZIP, al Git ni a los logs. La firma de release, las pruebas de instalación y la verificación de conectividad contra el backend deben completarse antes de declarar una versión de producción.

## Checklist de liberación

- [ ] Compilar el APK debug en un entorno con Android SDK.
- [ ] Instalar y abrir el APK en un dispositivo físico/emulador compatible.
- [ ] Probar login, selección de organización, carga de APK, estado del análisis, hallazgos y generación de informes.
- [ ] Probar certificado TLS válido, token expirado, errores HTTP y conectividad interrumpida.
- [ ] Ejecutar pruebas integrales con PostgreSQL, Redis, MinIO y workers aislados.
- [ ] Revisar aislamiento multi-tenant y límites de carga/sandbox.
- [ ] Firmar release con clave externa al repositorio y guardar el SHA-256.
- [ ] Adjuntar evidencia de pruebas y limitaciones conocidas.
