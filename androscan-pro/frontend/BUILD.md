# Construcción del frontend F9.8

## Requisitos
- Node.js 20+ recomendado.
- npm 10+.

## Instalación

```bash
cd frontend
npm install
```

## Validación TypeScript y build

```bash
npm run build
```

## Configuración de API

Crear `.env` a partir de `.env.example` y definir:

```text
VITE_API_URL=http://localhost:8000/api/v1
```

La variable se incorpora durante el build de Vite; no colocar secretos en variables `VITE_*`.

> Nota de validación del paquete: el entorno de construcción usado para esta entrega no pudo completar `npm install` por timeout de resolución de dependencias. Por eso no se declara como ejecutado un build React dentro de este entorno. El proyecto incluye las tipificaciones React/ReactDOM necesarias para `tsc -b`.
