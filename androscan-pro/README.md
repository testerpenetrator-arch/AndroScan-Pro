<p class="ds-markdown-paragraph"><span class="">La presente guía describe el montaje de AndroScan paso a paso, utilizando el paquete acumulativo </span><code>AndroScan_1.0.0.zip</code><span class="">.</span></p><p class="ds-markdown-paragraph"><span class="">El objetivo es que el lector finalice con los tres componentes instalados y conectados:</span></p><ol start="1"><li><p class="ds-markdown-paragraph"><strong><span class="">Backend y servicios</span></strong></p><p class="ds-markdown-paragraph"><span class="">FastAPI, PostgreSQL, Redis, Celery y MinIO. Recibe los APK y administra los análisis.</span></p></li><li><p class="ds-markdown-paragraph"><strong><span class="">Cliente web</span></strong></p><p class="ds-markdown-paragraph"><span class="">React, TypeScript y Vite. Se abre desde el navegador y consume la API.</span></p></li><li><p class="ds-markdown-paragraph"><strong><span class="">Cliente Android</span></strong></p><p class="ds-markdown-paragraph"><span class="">Proyecto Kotlin + Jetpack Compose. Se compila desde Android Studio para obtener el APK instalable de AndroScan.</span></p></li></ol><p class="ds-markdown-paragraph"><span class="">Antes de comenzar, conviene aclarar que el ZIP contiene código fuente, no un APK Android ya compilado. Las instrucciones que siguen permiten preparar el entorno, ejecutar los servicios y comprobar qué componentes compilan correctamente. El análisis real con MobSF, JADX y Apktool también requiere configurar y probar la imagen del sandbox; no basta con que el backend arranque.</span></p><h2><span class="">1. Preparación del equipo</span></h2><p class="ds-markdown-paragraph"><span class="">Se recomienda realizar el primer montaje en un equipo con Linux o en un servidor Linux. Si se trabaja desde Arch Linux, la terminal es suficiente para casi todo; para Android será necesario Android Studio.</span></p><h3><span class="">Requisitos</span></h3><div class="ds-scroll-area ds-scroll-area--show-on-focus-within ds-scroll-area--enabled _1210dd7 c03cafe9" style="--container-height: 344px;"><div class="ds-scroll-area__gutters" style="--container-height: 344px; position: sticky; top: 0px; left: 0px; right: 0px; width: 100%; height: 0px;"><div class="ds-scroll-area__horizontal-gutter" style="left: 0px; right: 0px; display: block; top: calc(var(--container-height) - 14px); height: 8px;"></div><div class="ds-scroll-area__vertical-gutter" style="right: 3px; top: 3px; bottom: calc(0px - var(--container-height) + 3px); width: 8px;"></div></div>
Herramienta | Para qué sirve
-- | --
Docker Engine + Docker Compose | Ejecutar el backend y sus servicios
Git, unzip, curl y OpenSSL | Gestionar el código, archivos y secretos
Python 3.12 o superior | Ejecutar pruebas y herramientas auxiliares
Node.js 20+ y npm | Compilar el cliente web
Android Studio + JDK 17 | Compilar el cliente Android
Android SDK Platform 35 | Construir el APK

</div><p class="ds-markdown-paragraph"><span class="">En Arch Linux, las herramientas base pueden instalarse con:</span></p>
<div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">sudo</span> pacman <span class="token parameter variable">-Syu</span></span>
<span><span class="token function">sudo</span> pacman <span class="token parameter variable">-S</span> <span class="token function">docker</span> <span class="token function">docker-compose</span> <span class="token punctuation">\</span></span>
<span>  <span class="token function">git</span> <span class="token function">unzip</span> <span class="token function">curl</span> openssl python nodejs <span class="token function">npm</span> jdk17-openjdk</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Después, se habilita Docker:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">sudo</span> systemctl <span class="token builtin class-name">enable</span> <span class="token parameter variable">--now</span> <span class="token function">docker</span></span>
<span><span class="token function">sudo</span> systemctl status <span class="token function">docker</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Se comprueba que responde:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">docker</span> <span class="token parameter variable">--version</span></span>
<span><span class="token function">docker</span> compose version</span>
<span>python <span class="token parameter variable">--version</span></span>
<span><span class="token function">node</span> <span class="token parameter variable">--version</span></span>
<span><span class="token function">npm</span> <span class="token parameter variable">--version</span></span>
<span><span class="token function">java</span> <span class="token parameter variable">-version</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Si Docker no permite ejecutar comandos sin </span><code>sudo</code><span class="">, inicialmente pueden utilizarse con </span><code>sudo docker compose ...</code><span class="">. Agregar el usuario al grupo </span><code>docker</code><span class=""> facilita el uso, pero ese grupo concede privilegios equivalentes a root; conviene hacerlo solo si se comprende ese riesgo.</span></p><p class="ds-markdown-paragraph"><strong><span class="">Android Studio:</span></strong><span class=""> se instala desde el sitio oficial de Android Developers: </span><a href="https://developer.android.com/studio" target="_blank" rel="noreferrer"><span class="">Descargar Android Studio</span></a><span class="">. En el SDK Manager se instala Android SDK Platform 35 y las herramientas de compilación correspondientes.</span></p><h2><span class="">2. Extracción del proyecto</span></h2><p class="ds-markdown-paragraph"><span class="">Se descarga el paquete desde el enlace anterior y se abre una terminal en la carpeta donde quedó el archivo.</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">mkdir</span> <span class="token parameter variable">-p</span> ~/proyectos/androscan</span>
<span><span class="token function">unzip</span> ~/Descargas/AndroScan_1.0.0.zip <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">-d</span> ~/proyectos/androscan</span>
<span><span class="token builtin class-name">cd</span> ~/proyectos/androscan/androscan-pro</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Si el navegador guardó el archivo en otra carpeta, debe modificarse la ruta de </span><code>unzip</code><span class="">.</span></p><p class="ds-markdown-paragraph"><span class="">Se comprueba que se está en la raíz correcta:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">ls</span> <span class="token parameter variable">-la</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Deberían encontrarse, entre otros:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">text</span></div></div></div></div><pre><span>backend/</span>
<span>frontend/</span>
<span>android-client/</span>
<span>scripts/</span>
<span>docker-compose.yml</span>
<span>docker-compose.prod.yml</span>
<span>.env.example</span>
<span>README.md</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Si no aparecen esos archivos, no deben ejecutarse los comandos siguientes hasta ubicar la carpeta correcta.</span></p><h2><span class="">3. Configuración de los secretos</span></h2><p class="ds-markdown-paragraph"><span class="">El proyecto dispone de un script que crea un archivo </span><code>.env</code><span class=""> con contraseñas aleatorias.</span></p><p class="ds-markdown-paragraph"><span class="">Se ejecuta:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">chmod</span> +x scripts/*.sh</span>
<span>./scripts/init-secrets.sh</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Después:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span>./scripts/validate-env.sh</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Si la validación es correcta, se revisa que el archivo exista:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">ls</span> <span class="token parameter variable">-l</span> .env</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Debe tener permisos restringidos al propietario, normalmente </span><code>-rw-------</code><span class="">.</span></p><p class="ds-markdown-paragraph"><span class="">No deben publicarse ni compartirse </span><code>.env</code><span class="">. Contiene contraseñas de PostgreSQL, MinIO y la clave usada para firmar los tokens de autenticación.</span></p><p class="ds-markdown-paragraph"><span class="">La configuración inicial utiliza el modo de desarrollo. No deben publicarse directamente estos servicios en Internet: para producción debe configurarse HTTPS, proxy inverso, firewall y gestión segura de secretos.</span></p><h2><span class="">4. Levantamiento del backend y los servicios</span></h2><p class="ds-markdown-paragraph"><span class="">Desde la raíz </span><code>androscan-pro</code><span class="">, se ejecuta:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">sudo</span> <span class="token function">docker</span> compose config <span class="token parameter variable">-q</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Esto permite revisar si Compose puede interpretar la configuración y resolver las variables. Si falla porque falta una variable, debe revisarse el paso anterior.</span></p><p class="ds-markdown-paragraph"><span class="">Luego se descargan las imágenes y se construye la API:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">sudo</span> <span class="token function">docker</span> compose pull</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">sudo</span> <span class="token function">docker</span> compose build</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Y se levantan los servicios:</span></p><blockquote><p class="ds-markdown-paragraph"><strong><span class="">Nota:</span></strong><span class=""> si </span><code>docker pull quay.io/minio/minio:latest</code><span class=""> devuelve </span><code>401 Unauthorized</code><span class="">, significa que el registro requiere autenticación o que se ha alcanzado un límite. En ese caso puede iniciarse sesión con </span><code>docker login quay.io</code><span class=""> o utilizar una imagen espejo de MinIO accesible públicamente. Este aviso debe resolverse antes de continuar.</span></p></blockquote><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">sudo</span> <span class="token function">docker</span> compose up <span class="token parameter variable">--build</span> <span class="token parameter variable">-d</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Se comprueba su estado:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">docker</span> compose <span class="token function">ps</span> <span class="token parameter variable">-a</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Los servicios previstos son:</span></p><ul><li><p class="ds-markdown-paragraph"><code>api</code><span class="">: API FastAPI.</span></p></li><li><p class="ds-markdown-paragraph"><code>postgres</code><span class="">: base de datos.</span></p></li><li><p class="ds-markdown-paragraph"><code>redis</code><span class="">: cola de tareas.</span></p></li><li><p class="ds-markdown-paragraph"><code>worker</code><span class="">: procesamiento asíncrono.</span></p></li><li><p class="ds-markdown-paragraph"><code>minio</code><span class="">: almacenamiento de archivos.</span></p></li><li><p class="ds-markdown-paragraph"><code>frontend</code><span class="">: servidor de desarrollo web.</span></p></li></ul><p class="ds-markdown-paragraph"><span class="">Se consultan los registros si alguno aparece detenido:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">docker</span> compose logs <span class="token parameter variable">--tail</span><span class="token operator">=</span><span class="token number">100</span> api</span>
<span><span class="token function">docker</span> compose logs <span class="token parameter variable">--tail</span><span class="token operator">=</span><span class="token number">100</span> postgres</span>
<span><span class="token function">docker</span> compose logs <span class="token parameter variable">--tail</span><span class="token operator">=</span><span class="token number">100</span> worker</span>
<span><span class="token function">docker</span> compose logs <span class="token parameter variable">--tail</span><span class="token operator">=</span><span class="token number">100</span> minio</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Para ver los registros de forma continua:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">docker</span> compose logs <span class="token parameter variable">-f</span> api worker</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">La vista de registros se abandona con </span><code>Ctrl+C</code><span class="">; eso no detiene los contenedores.</span></p><h3><span class="">Ejecución de las migraciones de la base de datos</span></h3><p class="ds-markdown-paragraph"><span class="">Con los servicios levantados, se ejecutan las migraciones de Alembic:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">docker</span> compose <span class="token builtin class-name">exec</span> api alembic upgrade <span class="token function">head</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Esto crea o actualiza el esquema de PostgreSQL conforme a las migraciones incluidas en el proyecto.</span></p><p class="ds-markdown-paragraph"><span class="">Se comprueba qué versión quedó aplicada:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">docker</span> compose <span class="token builtin class-name">exec</span> api alembic current</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Si el comando </span><code>exec</code><span class=""> indica que el contenedor de API no está activo, deben consultarse primero sus registros. No debe intentarse crear el administrador hasta que las migraciones hayan terminado correctamente.</span></p><h3><span class="">Comprobación de la API</span></h3><p class="ds-markdown-paragraph"><span class="">Se abren en el navegador:</span></p><ul><li><p class="ds-markdown-paragraph"><span class="">Documentación interactiva: </span><a href="http://localhost:8000/docs" target="_blank" rel="noreferrer"><span class="">http://localhost:8000/docs</span></a></p></li><li><p class="ds-markdown-paragraph"><span class="">Estado del proceso: </span><a href="http://localhost:8000/api/v1/health/live" target="_blank" rel="noreferrer"><span class="">http://localhost:8000/api/v1/health/live</span></a></p></li><li><p class="ds-markdown-paragraph"><span class="">Disponibilidad de la base de datos: </span><a href="http://localhost:8000/api/v1/health/ready" target="_blank" rel="noreferrer"><span class="">http://localhost:8000/api/v1/health/ready</span></a></p></li></ul><p class="ds-markdown-paragraph"><span class="">También pueden utilizarse:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">curl</span> <span class="token parameter variable">-i</span> http://localhost:8000/api/v1/health/live</span>
<span><span class="token function">curl</span> <span class="token parameter variable">-i</span> http://localhost:8000/api/v1/health/ready</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">El primer endpoint comprueba que la API responde; el segundo verifica la conexión a la base de datos.</span></p><p class="ds-markdown-paragraph"><span class="">Si se recibe un error, no debe avanzarse a la creación del usuario hasta resolverlo.</span></p><h2><span class="">5. Creación del primer administrador</span></h2><p class="ds-markdown-paragraph"><span class="">El proyecto incluye un script para crear el usuario administrador inicial y su organización.</span></p><p class="ds-markdown-paragraph"><span class="">Se ejecuta el siguiente comando, reemplazando el correo, nombre y contraseña por valores propios:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">docker</span> compose <span class="token builtin class-name">exec</span> api python <span class="token parameter variable">-m</span> app.scripts.create_admin <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--email</span> admin@tu-dominio.local <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--name</span> <span class="token string">"Administrador AndroScan"</span> <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--organization</span> <span class="token string">"Mi Organización"</span> <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--slug</span> mi-organizacion <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--password</span> <span class="token string">'CAMBIA_ESTA_CONTRASENA'</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><strong><span class="">Nota:</span></strong><span class=""> en el ZIP, el script se encuentra en </span><code>backend/scripts/create_admin.py</code><span class="">. Por tanto, si el módulo anterior no existe en la copia, debe utilizarse el método que apunta directamente al archivo:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">docker</span> compose <span class="token builtin class-name">exec</span> api python /app/scripts/create_admin.py <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--email</span> admin@tu-dominio.local <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--name</span> <span class="token string">"Administrador AndroScan"</span> <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--organization</span> <span class="token string">"Mi Organización"</span> <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--slug</span> mi-organizacion <span class="token punctuation">\</span></span>
<span>  <span class="token parameter variable">--password</span> <span class="token string">'CAMBIA_ESTA_CONTRASENA'</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Debe usarse una contraseña larga y única. Conviene tener presente que escribirla en la línea de comandos puede dejarla en el historial de la terminal. Para un entorno compartido, es preferible adaptar el script para solicitarla de forma interactiva o mediante un mecanismo seguro.</span></p><p class="ds-markdown-paragraph"><span class="">Después, se abre </span><code>http://localhost:8000/docs</code><span class=""> y se localiza </span><code>POST /api/v1/auth/login</code><span class="">. Se usa el correo y la contraseña configurados para comprobar la autenticación.</span></p><p class="ds-markdown-paragraph"><span class="">Si el script no encuentra el rol </span><code>ADMIN</code><span class="">, debe revisarse de nuevo que las migraciones hayan finalizado correctamente.</span></p><h2><span class="">6. Compilación y ejecución del cliente web</span></h2><p class="ds-markdown-paragraph"><span class="">Se abre una segunda terminal:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token builtin class-name">cd</span> ~/proyectos/androscan/androscan-pro/frontend</span>
<span><span class="token function">npm</span> <span class="token function">install</span></span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Cuando termine la instalación:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">npm</span> run build</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Este comando realiza la comprobación de TypeScript y construye los archivos de producción de Vite. Si falla, conviene guardar el mensaje completo del error; no significa necesariamente que el backend esté fallando.</span></p><p class="ds-markdown-paragraph"><span class="">Para levantar el servidor web de desarrollo:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">npm</span> run dev -- <span class="token parameter variable">--host</span> <span class="token number">127.0</span>.0.1</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Se abre la URL que indique Vite, normalmente:</span></p><p class="ds-markdown-paragraph"><a href="http://localhost:5173/" target="_blank" rel="noreferrer"><span class="">http://localhost:5173</span></a></p><h3><span class="">Configuración de la URL de la API</span></h3><p class="ds-markdown-paragraph"><span class="">El frontend utiliza </span><code>VITE_API_URL</code><span class="">. Para un montaje local, se crea el archivo </span><code>frontend/.env.local</code><span class="">:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token builtin class-name">cd</span> ~/proyectos/androscan/androscan-pro/frontend</span>
<span><span class="token builtin class-name">printf</span> <span class="token string">'%s\n'</span> <span class="token string">'VITE_API_URL=http://localhost:8000/api/v1'</span> <span class="token operator">&gt;</span> .env.local</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Se reinicia Vite si ya estaba ejecutándose.</span></p><p class="ds-markdown-paragraph"><strong><span class="">Posible ajuste necesario:</span></strong><span class=""> la API y el frontend usan puertos distintos, por lo que el navegador puede bloquear las solicitudes si el backend no tiene configurado CORS para </span><code>http://localhost:5173</code><span class="">. Si aparecen errores CORS en la consola del navegador, debe añadirse una política explícita en FastAPI que permita ese origen de desarrollo. No debe habilitarse cualquier origen en producción.</span></p><p class="ds-markdown-paragraph"><span class="">Una vez resuelto esto, se inicia sesión con el administrador creado anteriormente.</span></p><h2><span class="">7. Compilación del APK de AndroScan con Android Studio</span></h2><p class="ds-markdown-paragraph"><span class="">Este paso genera la aplicación AndroScan que se instalará en el teléfono, no el APK que se desea analizar.</span></p><h3><span class="">A. Apertura del proyecto</span></h3><ol start="1"><li><p class="ds-markdown-paragraph"><span class="">Se inicia Android Studio.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se selecciona </span><strong><span class="">Open</span></strong><span class="">.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se abre la carpeta:</span></p></li></ol><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span>~/proyectos/androscan/androscan-pro/android-client</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><ol start="4"><li><p class="ds-markdown-paragraph"><span class="">Se acepta la sincronización de Gradle.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Si se solicita instalar SDK Platform 35 o Build Tools, se acepta la instalación.</span></p></li></ol><p class="ds-markdown-paragraph"><span class="">Es importante abrir </span><code>android-client</code><span class="">, no la raíz del servidor ni la carpeta </span><code>backend</code><span class="">.</span></p><h3><span class="">B. Configuración de la dirección del servidor</span></h3><p class="ds-markdown-paragraph"><span class="">En la pantalla de inicio de sesión de la aplicación Android puede configurarse la URL base del servidor.</span></p><p class="ds-markdown-paragraph"><span class="">Si el backend corre en el propio equipo y se utiliza el emulador Android estándar, normalmente la dirección es:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">text</span></div></div></div></div><pre><span>http://10.0.2.2:8000</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">El emulador utiliza </span><code>10.0.2.2</code><span class=""> para acceder al host. La API móvil añade automáticamente </span><code>/api/v1</code><span class=""> a esa dirección.</span></p><p class="ds-markdown-paragraph"><span class="">Si la aplicación se instala en un teléfono físico, </span><code>10.0.2.2</code><span class=""> no es la dirección correcta. Debe utilizarse la IP local del equipo y, para una conexión segura, lo recomendable es configurar HTTPS con un certificado confiable.</span></p><p class="ds-markdown-paragraph"><span class="">El cliente actual admite HTTP solamente para pruebas locales con </span><code>localhost</code><span class=""> o </span><code>10.0.2.2</code><span class="">. Para un servidor remoto exige HTTPS.</span></p><h3><span class="">C. Generación del APK</span></h3><p class="ds-markdown-paragraph"><span class="">En Android Studio:</span></p><ol start="1"><li><p class="ds-markdown-paragraph"><span class="">Se espera a que finalice la sincronización de Gradle.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se abre el menú </span><strong><span class="">Build</span></strong><span class="">.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se selecciona </span><strong><span class="">Build Bundle(s) / APK(s)</span></strong><span class="">.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se pulsa </span><strong><span class="">Build APK(s)</span></strong><span class="">.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se espera el resultado de compilación.</span></p></li></ol><p class="ds-markdown-paragraph"><span class="">Si se genera correctamente, Android Studio mostrará un enlace para localizar el archivo.</span></p><p class="ds-markdown-paragraph"><span class="">La ruta habitual de salida será:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">text</span></div></div></div></div><pre><span>android-client/app/build/outputs/apk/debug/app-debug.apk</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Puede verificarse con:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token function">ls</span> <span class="token parameter variable">-lh</span> app/build/outputs/apk/debug/app-debug.apk</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Si no aparece, la compilación no terminó correctamente. Debe revisarse la ventana </span><strong><span class="">Build</span></strong><span class=""> de Android Studio y corregirse el primer error real antes de volver a intentarlo.</span></p><h3><span class="">D. Compilación desde terminal (alternativa)</span></h3><p class="ds-markdown-paragraph"><span class="">Si se tienen Gradle y Android SDK configurados, puede ejecutarse:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span><span class="token builtin class-name">cd</span> ~/proyectos/androscan/androscan-pro/android-client</span>
<span>gradle assembleDebug</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Este proyecto no incluye actualmente el wrapper </span><code>gradlew</code><span class="">; por eso el comando requiere una instalación de Gradle compatible. Android Studio suele ser la ruta más sencilla para el primer build.</span></p><h2><span class="">8. Instalación del APK en el teléfono</span></h2><p class="ds-markdown-paragraph"><span class="">Se activan las opciones de desarrollador y la depuración USB en el teléfono Android. Se conecta al equipo y se comprueba que ADB lo detecte:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span>adb devices</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Si aparece como autorizado, se instala el APK:</span></p><div class="md-code-block md-code-block-dark"><div class="md-code-block-banner-wrap"><div class="md-code-block-banner md-code-block-banner-lite"><div class="_121d384"><div class="d2a24f03"><span class="d813de27">bash</span></div></div></div></div><pre><span>adb <span class="token function">install</span> <span class="token parameter variable">-r</span> app/build/outputs/apk/debug/app-debug.apk</span></pre><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _33882ae"></svg><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" class="_9bc997d _28d7e84"></svg></div><p class="ds-markdown-paragraph"><span class="">Se abre AndroScan desde el teléfono. En la pantalla inicial:</span></p><ol start="1"><li><p class="ds-markdown-paragraph"><span class="">Se introduce la URL base del servidor.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se introduce el correo del administrador.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se introduce la contraseña.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se inicia sesión.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se selecciona la organización.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se registra o selecciona una aplicación.</span></p></li><li><p class="ds-markdown-paragraph"><span class="">Se selecciona un APK autorizado para probar la carga.</span></p></li></ol><p class="ds-markdown-paragraph"><span class="">En un teléfono físico, el servidor debe ser accesible desde la red del teléfono y la URL remota debe utilizar HTTPS. No debe exponerse el puerto 8000 directamente a Internet para evitar este requisito.</span></p><h2><span class="">9. Verificación del flujo de análisis</span></h2><p class="ds-markdown-paragraph"><span class="">Cuando el backend y los clientes funcionen, el flujo esperado es:</span></p><p class="ds-markdown-paragraph"><strong><span class="">Android o navegador</span></strong></p><p class="ds-markdown-paragraph"><span class="">El usuario inicia sesión y selecciona un APK.</span></p><p class="ds-markdown-paragraph"><strong><span class="">FastAPI</span></strong></p><p class="ds-markdown-paragraph"><span class="">Valida la solicitud y registra la aplicación y su versión.</span></p><p class="ds-markdown-paragraph"><strong><span class="">PostgreSQL + MinIO</span></strong></p><p class="ds-markdown-paragraph"><span class="">Guardan los metadatos y el archivo APK.</span></p><p class="ds-markdown-paragraph"><strong><span class="">Redis + worker</span></strong></p><p class="ds-markdown-paragraph"><span class="">Gestionan el trabajo asíncrono de análisis.</span></p><p class="ds-markdown-paragraph"><strong><span class="">Sandbox de análisis</span></strong></p><p class="ds-markdown-paragraph"><span class="">Ejecuta las herramientas de seguridad en un entorno aislado.</span></p><p class="ds-markdown-paragraph"><span class="">Hay un punto importante: el </span><code>docker-compose.yml</code><span class=""> actual no publica ni configura por sí solo todo el entorno del sandbox de análisis. Antes de dar por válida la detección real de amenazas, debe construirse y conectarse la imagen de herramientas, revisarse el acceso del worker a Docker y comprobarse el aislamiento. No deben probarse APK desconocidos en un host de producción.</span></p><h2><span class="">10. Problemas frecuentes</span></h2><div class="ds-scroll-area ds-scroll-area--show-on-focus-within ds-scroll-area--enabled _1210dd7 c03cafe9" style="--container-height: 606px;"><div class="ds-scroll-area__gutters" style="--container-height: 606px; position: sticky; top: 0px; left: 0px; right: 0px; width: 100%; height: 0px;"><div class="ds-scroll-area__horizontal-gutter" style="left: 0px; right: 0px; display: block; top: calc(var(--container-height) - 14px); height: 8px;"></div><div class="ds-scroll-area__vertical-gutter" style="right: 3px; top: 3px; bottom: calc(0px - var(--container-height) + 3px); width: 8px;"></div></div>
Síntoma | Qué revisar
-- | --
API no inicia | docker compose logs api
PostgreSQL no está listo | docker compose logs postgres y .env
Error de autenticación | Migraciones, usuario creado y credenciales
Web no inicia | npm install, npm run build y versión de Node
Error CORS en navegador | Configuración CORS de FastAPI
Android no conecta en emulador | URL 10.0.2.2:8000, estado del backend y registros
Android no conecta desde teléfono | IP del servidor, firewall, HTTPS y certificado
APK no aparece | Revisar el resultado de Gradle/Android Studio
Análisis se queda pendiente | Logs del worker, Redis y configuración del sandbox

</div><p class="ds-markdown-paragraph"><span class=""></span></p>bash

sudo pacman -Syu
sudo pacman -S docker docker-compose \
  git unzip curl openssl python nodejs npm jdk17-openjdk

Después, se habilita Docker:
bash

sudo systemctl enable --now docker
sudo systemctl status docker

Se comprueba que responde:
bash

docker --version
docker compose version
python --version
node --version
npm --version
java -version

Si Docker no permite ejecutar comandos sin sudo, inicialmente pueden utilizarse con sudo docker compose .... Agregar el usuario al grupo docker facilita el uso, pero ese grupo concede privilegios equivalentes a root; conviene hacerlo solo si se comprende ese riesgo.

Android Studio: se instala desde el sitio oficial de Android Developers: [Descargar Android Studio](https://developer.android.com/studio). En el SDK Manager se instala Android SDK Platform 35 y las herramientas de compilación correspondientes.
2. Extracción del proyecto

Se descarga el paquete desde el enlace anterior y se abre una terminal en la carpeta donde quedó el archivo.
bash

mkdir -p ~/proyectos/androscan
unzip ~/Descargas/AndroScan_1.0.0.zip \
  -d ~/proyectos/androscan
cd ~/proyectos/androscan/androscan-pro

Si el navegador guardó el archivo en otra carpeta, debe modificarse la ruta de unzip.

Se comprueba que se está en la raíz correcta:
bash

ls -la

Deberían encontrarse, entre otros:
text

backend/
frontend/
android-client/
scripts/
docker-compose.yml
docker-compose.prod.yml
.env.example
README.md

Si no aparecen esos archivos, no deben ejecutarse los comandos siguientes hasta ubicar la carpeta correcta.
3. Configuración de los secretos

El proyecto dispone de un script que crea un archivo .env con contraseñas aleatorias.

Se ejecuta:
bash

chmod +x scripts/*.sh
./scripts/init-secrets.sh

Después:
bash

./scripts/validate-env.sh

Si la validación es correcta, se revisa que el archivo exista:
bash

ls -l .env

Debe tener permisos restringidos al propietario, normalmente -rw-------.

No deben publicarse ni compartirse .env. Contiene contraseñas de PostgreSQL, MinIO y la clave usada para firmar los tokens de autenticación.

La configuración inicial utiliza el modo de desarrollo. No deben publicarse directamente estos servicios en Internet: para producción debe configurarse HTTPS, proxy inverso, firewall y gestión segura de secretos.
4. Levantamiento del backend y los servicios

Desde la raíz androscan-pro, se ejecuta:
bash

sudo docker compose config -q

Esto permite revisar si Compose puede interpretar la configuración y resolver las variables. Si falla porque falta una variable, debe revisarse el paso anterior.

Luego se descargan las imágenes y se construye la API:
bash

sudo docker compose pull

bash

sudo docker compose build

Y se levantan los servicios:

    Nota: si docker pull quay.io/minio/minio:latest devuelve 401 Unauthorized, significa que el registro requiere autenticación o que se ha alcanzado un límite. En ese caso puede iniciarse sesión con docker login quay.io o utilizar una imagen espejo de MinIO accesible públicamente. Este aviso debe resolverse antes de continuar.

bash

sudo docker compose up --build -d

Se comprueba su estado:
bash

docker compose ps -a

Los servicios previstos son:

    api: API FastAPI.

    postgres: base de datos.

    redis: cola de tareas.

    worker: procesamiento asíncrono.

    minio: almacenamiento de archivos.

    frontend: servidor de desarrollo web.

Se consultan los registros si alguno aparece detenido:
bash

docker compose logs --tail=100 api
docker compose logs --tail=100 postgres
docker compose logs --tail=100 worker
docker compose logs --tail=100 minio

Para ver los registros de forma continua:
bash

docker compose logs -f api worker

La vista de registros se abandona con Ctrl+C; eso no detiene los contenedores.
Ejecución de las migraciones de la base de datos

Con los servicios levantados, se ejecutan las migraciones de Alembic:
bash

docker compose exec api alembic upgrade head

Esto crea o actualiza el esquema de PostgreSQL conforme a las migraciones incluidas en el proyecto.

Se comprueba qué versión quedó aplicada:
bash

docker compose exec api alembic current

Si el comando exec indica que el contenedor de API no está activo, deben consultarse primero sus registros. No debe intentarse crear el administrador hasta que las migraciones hayan terminado correctamente.
Comprobación de la API

Se abren en el navegador:

    Documentación interactiva: http://localhost:8000/docs

    Estado del proceso: http://localhost:8000/api/v1/health/live

    Disponibilidad de la base de datos: http://localhost:8000/api/v1/health/ready

También pueden utilizarse:
bash

curl -i http://localhost:8000/api/v1/health/live
curl -i http://localhost:8000/api/v1/health/ready

El primer endpoint comprueba que la API responde; el segundo verifica la conexión a la base de datos.

Si se recibe un error, no debe avanzarse a la creación del usuario hasta resolverlo.
5. Creación del primer administrador

El proyecto incluye un script para crear el usuario administrador inicial y su organización.

Se ejecuta el siguiente comando, reemplazando el correo, nombre y contraseña por valores propios:
bash

docker compose exec api python -m app.scripts.create_admin \
  --email admin@tu-dominio.local \
  --name "Administrador AndroScan" \
  --organization "Mi Organización" \
  --slug mi-organizacion \
  --password 'CAMBIA_ESTA_CONTRASENA'

Nota: en el ZIP, el script se encuentra en backend/scripts/create_admin.py. Por tanto, si el módulo anterior no existe en la copia, debe utilizarse el método que apunta directamente al archivo:
bash

docker compose exec api python /app/scripts/create_admin.py \
  --email admin@tu-dominio.local \
  --name "Administrador AndroScan" \
  --organization "Mi Organización" \
  --slug mi-organizacion \
  --password 'CAMBIA_ESTA_CONTRASENA'

Debe usarse una contraseña larga y única. Conviene tener presente que escribirla en la línea de comandos puede dejarla en el historial de la terminal. Para un entorno compartido, es preferible adaptar el script para solicitarla de forma interactiva o mediante un mecanismo seguro.

Después, se abre http://localhost:8000/docs y se localiza POST /api/v1/auth/login. Se usa el correo y la contraseña configurados para comprobar la autenticación.

Si el script no encuentra el rol ADMIN, debe revisarse de nuevo que las migraciones hayan finalizado correctamente.
6. Compilación y ejecución del cliente web

Se abre una segunda terminal:
bash

cd ~/proyectos/androscan/androscan-pro/frontend
npm install

Cuando termine la instalación:
bash

npm run build

Este comando realiza la comprobación de TypeScript y construye los archivos de producción de Vite. Si falla, conviene guardar el mensaje completo del error; no significa necesariamente que el backend esté fallando.

Para levantar el servidor web de desarrollo:
bash

npm run dev -- --host 127.0.0.1

Se abre la URL que indique Vite, normalmente:

http://localhost:5173/
Configuración de la URL de la API

El frontend utiliza VITE_API_URL. Para un montaje local, se crea el archivo frontend/.env.local:
bash

cd ~/proyectos/androscan/androscan-pro/frontend
printf '%s\n' 'VITE_API_URL=http://localhost:8000/api/v1' > .env.local

Se reinicia Vite si ya estaba ejecutándose.

Posible ajuste necesario: la API y el frontend usan puertos distintos, por lo que el navegador puede bloquear las solicitudes si el backend no tiene configurado CORS para http://localhost:5173. Si aparecen errores CORS en la consola del navegador, debe añadirse una política explícita en FastAPI que permita ese origen de desarrollo. No debe habilitarse cualquier origen en producción.

Una vez resuelto esto, se inicia sesión con el administrador creado anteriormente.
7. Compilación del APK de AndroScan con Android Studio

Este paso genera la aplicación AndroScan que se instalará en el teléfono, no el APK que se desea analizar.
A. Apertura del proyecto

    Se inicia Android Studio.

    Se selecciona Open.

    Se abre la carpeta:

bash

~/proyectos/androscan/androscan-pro/android-client

    Se acepta la sincronización de Gradle.

    Si se solicita instalar SDK Platform 35 o Build Tools, se acepta la instalación.

Es importante abrir android-client, no la raíz del servidor ni la carpeta backend.
B. Configuración de la dirección del servidor

En la pantalla de inicio de sesión de la aplicación Android puede configurarse la URL base del servidor.

Si el backend corre en el propio equipo y se utiliza el emulador Android estándar, normalmente la dirección es:
text

http://10.0.2.2:8000

El emulador utiliza 10.0.2.2 para acceder al host. La API móvil añade automáticamente /api/v1 a esa dirección.

Si la aplicación se instala en un teléfono físico, 10.0.2.2 no es la dirección correcta. Debe utilizarse la IP local del equipo y, para una conexión segura, lo recomendable es configurar HTTPS con un certificado confiable.

El cliente actual admite HTTP solamente para pruebas locales con localhost o 10.0.2.2. Para un servidor remoto exige HTTPS.
C. Generación del APK

En Android Studio:

    Se espera a que finalice la sincronización de Gradle.

    Se abre el menú Build.

    Se selecciona Build Bundle(s) / APK(s).

    Se pulsa Build APK(s).

    Se espera el resultado de compilación.

Si se genera correctamente, Android Studio mostrará un enlace para localizar el archivo.

La ruta habitual de salida será:
text

android-client/app/build/outputs/apk/debug/app-debug.apk

Puede verificarse con:
bash

ls -lh app/build/outputs/apk/debug/app-debug.apk

Si no aparece, la compilación no terminó correctamente. Debe revisarse la ventana Build de Android Studio y corregirse el primer error real antes de volver a intentarlo.
D. Compilación desde terminal (alternativa)

Si se tienen Gradle y Android SDK configurados, puede ejecutarse:
bash

cd ~/proyectos/androscan/androscan-pro/android-client
gradle assembleDebug

Este proyecto no incluye actualmente el wrapper gradlew; por eso el comando requiere una instalación de Gradle compatible. Android Studio suele ser la ruta más sencilla para el primer build.
8. Instalación del APK en el teléfono

Se activan las opciones de desarrollador y la depuración USB en el teléfono Android. Se conecta al equipo y se comprueba que ADB lo detecte:
bash

adb devices

Si aparece como autorizado, se instala el APK:
bash

adb install -r app/build/outputs/apk/debug/app-debug.apk

Se abre AndroScan desde el teléfono. En la pantalla inicial:

    Se introduce la URL base del servidor.

    Se introduce el correo del administrador.

    Se introduce la contraseña.

    Se inicia sesión.

    Se selecciona la organización.

    Se registra o selecciona una aplicación.

    Se selecciona un APK autorizado para probar la carga.

En un teléfono físico, el servidor debe ser accesible desde la red del teléfono y la URL remota debe utilizar HTTPS. No debe exponerse el puerto 8000 directamente a Internet para evitar este requisito.
9. Verificación del flujo de análisis

Cuando el backend y los clientes funcionen, el flujo esperado es:

Android o navegador

El usuario inicia sesión y selecciona un APK.

FastAPI

Valida la solicitud y registra la aplicación y su versión.

PostgreSQL + MinIO

Guardan los metadatos y el archivo APK.

Redis + worker

Gestionan el trabajo asíncrono de análisis.

Sandbox de análisis

Ejecuta las herramientas de seguridad en un entorno aislado.

Hay un punto importante: el docker-compose.yml actual no publica ni configura por sí solo todo el entorno del sandbox de análisis. Antes de dar por válida la detección real de amenazas, debe construirse y conectarse la imagen de herramientas, revisarse el acceso del worker a Docker y comprobarse el aislamiento. No deben probarse APK desconocidos en un host de producción.
10. Problemas frecuentes
Síntoma	Qué revisar
API no inicia	docker compose logs api
PostgreSQL no está listo	docker compose logs postgres y .env
Error de autenticación	Migraciones, usuario creado y credenciales
Web no inicia	npm install, npm run build y versión de Node
Error CORS en navegador	Configuración CORS de FastAPI
Android no conecta en emulador	URL 10.0.2.2:8000, estado del backend y registros
Android no conecta desde teléfono	IP del servidor, firewall, HTTPS y certificado
APK no aparece	Revisar el resultado de Gradle/Android Studio
Análisis se queda pendiente	Logs del worker, Redis y configuración del sandbox

Para detener los servicios del entorno local sin borrar los datos persistentes:
bash

docker compose down

No debe agregarse -v si se desea conservar la base de datos y los archivos almacenados.
11. Orden recomendado para la primera instalación

Se recomienda completar los pasos en este orden:

    Instalar Docker y las herramientas base.

    Extraer el ZIP y generar .env.

    Levantar los servicios.

    Ejecutar migraciones y crear el administrador.

    Verificar los endpoints de salud y la autenticación.

    Compilar y abrir el cliente web.

    Abrir Android Studio, sincronizar Gradle y compilar el APK.

    Instalar el APK en un emulador o teléfono de prueba.

    Probar el flujo de carga y comprobar los logs.

    Configurar y verificar el sandbox antes de confiar en los resultados de análisis.
