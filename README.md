# 🏛️ Proyecto: Automatización de Reportes Regulatorios y Procesos de Cumplimiento

**Repositorio:** `FinNovaBank-SAS/Proyecto`

## 🎯 Requisitos Arquitectónicos

Este prototipo funcional (30% de la evaluación) aborda la automatización de reportes regulatorios conforme a normativas (UIAF, SARLAFT, Basilea III, Habeas Data) mediante una arquitectura moderna, contenerizada y con despliegue continuo.

| Requisito del Prototipo | Cumplimiento | Evidencia en el Repositorio |
| :--- | :--- | :--- |
| Uso de repositorios (Monorepo) | ✅ Satisfecho | Estructura de código unificada en una sola raíz. |
| Uso de Dockerfile y Docker-Compose | ✅ Satisfecho | Archivos `Dockerfile` y `docker-compose.yml` en la raíz. |
| Uso de GitHub Actions | ✅ Satisfecho | Flujo de CI/CD en `.github/workflows/deploy.yml`. |
| Funcionalidad en local con contenedor | ✅ Satisfecho | Ver **1. Pruebas Locales**. |
| Evidencia de despliegue y actualización | ✅ Satisfecho | Flujo `deploy.yml` que etiqueta con `latest` y `github.sha`. |

## 🚀 Tecnologías Utilizadas

| Categoría | Tecnología | Uso Específico |
| :--- | :--- | :--- |
| **Aplicación** | Python (Flask) | Servidor web que simula la lógica de **generación y envío** de reportes SARLAFT. |
| **Monorepo** | GitHub | Plataforma para el control de versiones y hosting del monorepositorio. |
| **Contenerización** | Docker | Empaquetado inmutable de la aplicación para garantizar la **funcionalidad en local y nube**. |
| **Orquestación Local** | Docker Compose | Facilita la ejecución y prueba en entorno de desarrollo. |
| **CI/CD** | GitHub Actions | Automatiza los pasos de **Build, Push y Despliegue**. |
| **Nube de Despliegue** | [***TU NUBE AQUÍ***] | Servicio de Contenedores (ej. Azure Container Apps, Google Cloud Run, AWS ECS). |

---

## 🛠️ 1. Implementación Local (Prototipo Funcional Obligatorio)

Este proceso permite la **funcionalidad en local con contenedor** (obligatorio).

### 1.1. Prerrequisitos

* Docker y Docker Compose instalados.
* Código clonado localmente.

### 1.2. Pasos de Implementación (Evidencia Dockerfile y Docker-Compose)

1.  **Construir la Imagen:** Utiliza el `Dockerfile` para construir la imagen de la aplicación.
    ```bash
    docker-compose build
    ```
2.  **Ejecutar el Contenedor:** Utiliza `docker-compose.yml` para levantar el servicio.
    ```bash
    docker-compose up -d
    ```
3.  **Verificar el Prototipo Funcional:**
    * **Estado:** Accede a `http://localhost:8080/`. Deberías ver un mensaje de éxito.
    * **Generar Reporte:** Accede a `http://localhost:8080/generate-sarlaft-report`. Esto simula el flujo automático de generación, retornando un archivo JSON con los datos de cumplimiento.

4.  **Detener:**
    ```bash
    docker-compose down
    ```

---

## ☁️ 2. Despliegue en la Nube (Evidencia CI/CD)

Este proceso se gestiona automáticamente mediante GitHub Actions.

### 2.1. Configuración de la Nube (Ejemplo con un Registro de Contenedores)

1.  Crear una cuenta en el **Registro de Contenedores** (Docker Hub, ACR, etc.).
2.  Configurar las variables de autenticación (`DOCKER_USERNAME`, `DOCKER_PASSWORD`, `REGISTRY_URL`) como **Secrets** en GitHub (ver la sección de *Pre-requisitos*).
3.  Configurar un servicio de contenedores en la nube para que consuma la imagen del registro.

### 2.2. Flujo de Despliegue (Evidencia GitHub Actions)

El archivo `.github/workflows/deploy.yml` automatiza el siguiente flujo al hacer `git push`:

1.  **Login:** Inicia sesión en el Registro de Contenedores usando los Secrets de GitHub.
2.  **Build & Tag:** La imagen se construye. Se etiqueta con dos versiones:
    * `[REGISTRY_URL]/regulatory-report-app:latest`
    * `[REGISTRY_URL]/regulatory-report-app:[COMMIT_SHA]` (Para trazabilidad).
3.  **Push:** Ambas imágenes son subidas al registro.
4.  **Despliegue/Actualización (Evidencia de Despliegue):** El paso final notifica al servicio de contenedores en la nube ([***TU NUBE AQUÍ***]) que debe actualizarse para usar la imagen `:latest`. La actualización del tag `COMMIT_SHA` sirve como **Evidencia de Actualización de Imagen**.

### 2.3. Funcionalidad en Nube (URL Opcional)

Una vez completado el flujo de CI/CD, la funcionalidad debe estar disponible en la URL pública del servicio de contenedores:

**URL de la Aplicación en Nube:** `[PEGA AQUÍ LA URL PÚBLICA DE TU SERVICIO DE CONTENEDORES]`

**Endpoint de Prueba:** `https://www.spanishdict.com/translate/p%C3%BAblica/generate-sarlaft-report`