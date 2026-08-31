# AndroScan-Pro
Sistema de Análisis de Seguridad y Generación de Inteligencia para Aplicaciones Android

> Android Security Analysis & Threat Intelligence Generation Tool para Red Team
> Cristian Camilo Calderon

[![Kotlin Version](https://img.shields.io/badge/Kotlin-2.0.0-blue.svg)](https://kotlinlang.org)
[![API](https://img.shields.io/badge/API-26%2B-brightgreen.svg)](https://developer.android.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 Descripción

**AndroScan Pro** es una aplicación Android para análisis de seguridad estático de aplicaciones, diseñada específicamente para  análisis de seguridad estático de aplicaciones, diseñada específicamente para equipos Red Team y profesionales de pentesting móvil. Inspirada en herramientas como APKPeek, NEXAR-MAAS y APK-Permission-Inspector, permite escanear APKs instaladas o subidas, detectar permisos peligrosos, secretos hardcodeados, y enriquecer los hallazgos con inteligencia de amenazas.

## 🚀 Características Principales

- ✅ **Análisis estático de APKs** (metadatos, permisos, componentes) 
- 🔍 **Detección de secretos y credenciales** con reglas de detección 
- 🛡️ **Clasificación de permisos** en categorías *normal*, *dangerous*, *signature*
- 📊 **Motor de puntuación de riesgo** (0-100) con clasificación de LIMPIO a CRÍTICO 
- 🌐 **Integración con VirusTotal** y Koodous para inteligencia de amenazas
- 📤 **Exportación de reportes en JSON y SARIF** 
- 📱 **Escaneo offline** para entornos aislados 
- 🔄 **Código de retorno** para integración en en CI/CD 


## 🏗️ Arquitectura

El proyecto sigue **Clean Architecture** con capas bien definidas y gestión centralizada de dependencias.

app/
├── presentation/                     # UI con Jetpack Compose + MVI (Google, 2025; viamgr, 2022)
│   ├── ui/                           # Pantallas y componentes
│   ├── viewmodel/                    # ViewModels con gestión de estado
│   └── state/                        # Estados UI (sealed classes)
├── domain/                           # Casos de uso y lógica de negocio (segnonna, 2021)
│   ├── usecase/                      # Casos de uso
│   └── model/                        # Modelos de dominio
├── data/                             # Repositorios y fuentes de datos (Google, 2025; Square, 2025)
│   ├── repository/                   # Implementación de repositorios
│   ├── local/                        # Fuentes locales (Room)
│   └── remote/                       # Fuentes remotas (Retrofit)
└── buildSrc/                         # Gestión de dependencias

## 🛠️ Tecnologías

- **Kotlin** + **Corrutinas** + **Flow** (Google, 2025)
- **Jetpack Compose** (UI declarativa) (Google, 2025)
- **Clean Architecture** + **MVI** (Model-View-Intent) (segnonna, 2021; viamgr, 2022)
- **Hilt** (inyección de dependencias) (Google, 2025)
- **Retrofit** (APIs externas: VirusTotal, Koodous) (Square, 2025)
- **Room** (caché local de análisis) (Google, 2025)

## 📦 Instalación

# >  Bash
git clone https://github.com/tu-usuario/androscan-pro.git
cd androscan-pro

# Abrir en Android Studio y ejecutar
📄 Licencia
MIT License
