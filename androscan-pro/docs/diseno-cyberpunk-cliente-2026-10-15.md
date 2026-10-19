# AndroScan — actualización visual Cyberpunk (15/10/2026)

## Alcance
Se aplicó una identidad visual coherente al cliente web React/Vite y al cliente Android Kotlin/Jetpack Compose, inspirada en los cinco mockups aprobados (dashboard, selección de APK, escaneo en proceso, resultados y reporte) y en la pantalla de inicio de sesión añadida.

## Tokens visuales
- Fondo: `#030611`.
- Superficie/panel: `#081426`.
- Cian neón: `#00F5FF`.
- Magenta: `#FF2BD6`.
- Púrpura: `#9B5CFF`.
- Verde de estado: `#00FF9C`.
- Texto secundario: `#8CA7C3`.
- Riesgo crítico: tonos rojos `#FF3864`.

## Criterios
- Paneles oscuros con bordes cian y detalles magenta/púrpura.
- Indicadores de riesgo y estado con colores diferenciados.
- Diseño adaptable a pantallas pequeñas en web.
- Interfaz Android con tema oscuro Material 3.
- La UI no presenta datos ficticios de análisis como si fueran reales: los datos provienen de la API.
- El APK analizado se procesa en el servidor; el cliente móvil no ejecuta el archivo seleccionado.

## Validación
La suite del backend se ejecutó en esta actualización: 48 pruebas aprobadas. `npm install` no terminó dentro del tiempo disponible; por ello, la compilación del frontend no se considera validada. No se pudo ejecutar una compilación Android/Gradle en este entorno. La revisión visual debe completarse con una ejecución real en navegador y emulador Android.
