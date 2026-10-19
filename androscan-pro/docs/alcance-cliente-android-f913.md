# F9.13 — Actualización de alcance: cliente Android + plataforma servidor

- Estado: especificación aprobada por el usuario; implementación Android todavía no iniciada.
- Enfoque: Spec-Driven Development (SDD). No generar código móvil hasta aprobar la especificación técnica y los criterios de aceptación.
- Fecha de actualización: 2026-10-13.

## 1. Entregable final

AndroScan tendrá dos componentes que se entregan y validan por separado:

1. **Plataforma de servidor**: API, base de datos, cola de trabajos, almacenamiento, motores estáticos aislados y panel web administrativo.
2. **Cliente Android instalable**: aplicación nativa distribuible como APK, que se conecta al servidor mediante HTTPS y API REST.

El cliente Android no analizará ni ejecutará el APK seleccionado localmente. La plataforma de servidor será responsable de validar el archivo, calcular SHA-256, almacenarlo y programar el análisis en entornos aislados.

## 2. Arquitectura propuesta

| Componente | Tecnología propuesta | Estado |
|---|---|---|
| Cliente Android | Kotlin + Jetpack Compose | Propuesta; aprobación técnica específica pendiente |
| API | FastAPI + REST + OpenAPI 3.1 | Decisión previa aprobada |
| Panel web | React + TypeScript + Vite | Decisión previa aprobada |
| Persistencia | PostgreSQL + SQLAlchemy + Alembic | Decisión previa aprobada |
| Cola | Redis + Celery | Decisión previa aprobada |
| Análisis estático | MobSF, JADX, Apktool en sandbox | Decisión previa aprobada; validar hardening de despliegue |
| Transporte | HTTPS con validación normal de certificados TLS | Requisito obligatorio para despliegue remoto |

La aplicación móvil usará un cliente HTTP con timeout, manejo de errores y almacenamiento seguro de credenciales. No se permitirá desactivar la validación de certificados TLS en compilaciones de producción. No se fijará una URL de servidor inmutable: deberá configurarse de forma segura según el entorno o el mecanismo de distribución acordado.

## 3. Requisitos funcionales del cliente Android

- AND-RF-001: iniciar sesión mediante el endpoint de autenticación existente y cerrar sesión de forma segura.
- AND-RF-002: mostrar únicamente organizaciones a las que la identidad autenticada tenga acceso.
- AND-RF-003: listar aplicaciones, versiones APK y análisis autorizados de la organización activa.
- AND-RF-004: registrar una aplicación cuando el rol y la API lo permitan.
- AND-RF-005: seleccionar un archivo APK mediante el selector de documentos del sistema Android; solicitar solo los permisos necesarios.
- AND-RF-006: mostrar nombre, tamaño y confirmación antes de cargar; permitir cancelar la carga cuando sea técnicamente posible.
- AND-RF-007: enviar el archivo a la API existente y mostrar validaciones, errores y resultado de recepción.
- AND-RF-008: mostrar estado de análisis y refrescarlo sin sondeo excesivo; los detalles del mecanismo de actualización se definirán en diseño.
- AND-RF-009: mostrar hallazgos con categoría, severidad, prioridad, evidencia disponible y estado de revisión humana.
- AND-RF-010: mostrar comparación entre análisis de una misma aplicación cuando la API autorice la consulta.
- AND-RF-011: listar informes y permitir descargar PDF/JSON/HTML con manejo seguro del archivo descargado.
- AND-RF-012: mostrar claramente que la asistencia de IA es orientativa y que el riesgo final lo decide una persona analista.
- AND-RF-013: ofrecer estados de carga, vacío, error, sesión expirada y falta de conectividad.
- AND-RF-014: ocultar funciones no permitidas por rol, sin tratar la interfaz como control de autorización; el servidor siempre revalida los permisos.

## 4. Requisitos de seguridad y privacidad

- AND-SEC-001: todo tráfico remoto en producción debe usar HTTPS y validación de certificados TLS.
- AND-SEC-002: no almacenar contraseñas en texto plano ni escribir tokens, APK, evidencia sensible o informes en logs.
- AND-SEC-003: guardar los tokens usando mecanismos de almacenamiento seguro apropiados para Android; evaluar Android Keystore y una biblioteca de almacenamiento cifrado mantenida.
- AND-SEC-004: minimizar la duración y el alcance de los tokens; la expiración y renovación deben coincidir con la estrategia de identidad del backend.
- AND-SEC-005: evitar exportar información sensible a almacenamiento compartido sin una acción explícita del usuario; advertir antes de compartir informes.
- AND-SEC-006: no incluir claves, credenciales, tokens ni secretos en el código fuente o APK.
- AND-SEC-007: no analizar ni ejecutar localmente el APK seleccionado; se transmite como archivo no confiable al servidor autorizado.
- AND-SEC-008: aplicar autorización multi-tenant en el backend en cada petición; el ID de organización enviado por el cliente no es prueba de pertenencia.
- AND-SEC-009: usar selector de archivos del sistema y permisos mínimos; no pedir acceso general al almacenamiento si no es necesario.
- AND-SEC-010: proteger estados de error y notificaciones para no revelar hallazgos o nombres de APK en pantallas bloqueadas.
- AND-SEC-011: aplicar ofuscación solo como defensa complementaria, nunca como sustituto de la seguridad del servidor.
- AND-SEC-012: definir política de privacidad, retención local y eliminación de sesión antes de la publicación.

## 5. Requisitos no funcionales

- AND-RNF-001: compatibilidad mínima de Android por definir según dispositivos objetivo y herramientas disponibles; no fijar un nivel API sin confirmación.
- AND-RNF-002: diseño adaptable a teléfonos y tabletas, accesible y legible.
- AND-RNF-003: operaciones de red fuera del hilo principal; interfaz receptiva durante cargas y consultas.
- AND-RNF-004: carga con progreso cuando sea compatible con la API; tratar interrupciones y reintentos sin duplicar operaciones.
- AND-RNF-005: soporte de tamaños de archivo coherente con el límite del servidor por organización; el servidor es la autoridad final.
- AND-RNF-006: pruebas unitarias, pruebas de integración del cliente HTTP, pruebas UI y validación en dispositivos/emuladores compatibles.
- AND-RNF-007: compilación reproducible del APK y documentación de firma, instalación y actualización.
- AND-RNF-008: las versiones de release deben firmarse con una clave gestionada fuera del repositorio; nunca usar claves de release de ejemplo.

## 6. Criterios de aceptación

- AND-CA-001: una persona usuaria autorizada puede iniciar sesión y consultar solo sus organizaciones.
- AND-CA-002: la aplicación permite seleccionar y enviar una APK válida al servidor sin ejecutarla localmente.
- AND-CA-003: la aplicación presenta errores del servidor de forma comprensible y no filtra datos sensibles.
- AND-CA-004: el estado del análisis y los hallazgos se consultan a través de la API autenticada.
- AND-CA-005: una petición de otra organización no permite acceder a aplicaciones, análisis, hallazgos ni informes ajenos.
- AND-CA-006: la descarga de informes funciona en los formatos admitidos y requiere autorización.
- AND-CA-007: la sesión y los tokens se eliminan al cerrar sesión según el diseño de identidad aprobado.
- AND-CA-008: el APK de release se instala en dispositivos compatibles y su firma se verifica.
- AND-CA-009: el repositorio contiene instrucciones reproducibles de construcción e instalación, sin secretos.
- AND-CA-010: pruebas automatizadas y pruebas manuales de seguridad se documentan antes de declarar la entrega lista.

## 7. Decisiones pendientes que requieren aclaración antes del código

- AND-D01: versión mínima de Android y dispositivos objetivo.
- AND-D02: nombre de paquete Android (applicationId), por ejemplo un dominio invertido que controle el proyecto.
- AND-D03: distribución privada (instalación directa) o publicación en Google Play; pueden requerir procesos distintos.
- AND-D04: forma de configurar URL del servidor: compilaciones por entorno o pantalla de configuración restringida.
- AND-D05: estrategia definitiva de identidad, duración de token y renovación; actualmente el backend usa JWT local.
- AND-D06: política de guardar informes en el dispositivo y de compartirlos.
- AND-D07: estrategia de firma de release y custodia de la clave.
- AND-D08: pruebas en dispositivos físicos y versiones de Android disponibles.

## 8. Límites explícitos

- La aplicación Android es un cliente de la plataforma, no un motor local de análisis.
- El archivo APK que el usuario analiza es distinto del APK instalable de AndroScan.
- La existencia de código fuente del servidor no implica que ya exista un APK Android compilado.
- La compilación del APK final no se declarará completada hasta construirlo, verificar su firma e instalarlo en un entorno compatible.
- La integración real con un proveedor de IA externo permanece desactivada hasta aprobar privacidad, tratamiento de datos y credenciales.

## 9. Trazabilidad

| Requisito | Origen / relación |
|---|---|
| AND-RF-001..004 | RF de autenticación, organizaciones, aplicaciones e historial |
| AND-RF-005..008 | RF de carga APK, versiones y orquestación de análisis |
| AND-RF-009..012 | RF de hallazgos, revisiones, comparaciones, informes y asistencia IA |
| AND-SEC-001..012 | SEC-001..SEC-020 y RNF de transporte, autenticación, privacidad y aislamiento |
| AND-CA-001..010 | Criterios de aceptación globales CE-001..CE-008 adaptados al cliente móvil |
