# Proyecto: Automatización de Reportes Regulatorios y Procesos de Cumplimiento

**Repositorio:** `FinNovaBank-SAS/Proyecto`

## Requisitos Arquitectónicos

Este prototipo funcional aborda la automatización de reportes regulatorios conforme a normativas (UIAF, SARLAFT, Basilea III, Habeas Data) mediante una arquitectura moderna, contenerizada y con despliegue continuo.

| Requisito del Prototipo | Cumplimiento | Evidencia en el Repositorio |
| :--- | :--- | :--- |
| Uso de repositorios (Monorepo) | ✅ Satisfecho | Estructura de código unificada en una sola raíz. |
| Uso de Dockerfile y Docker-Compose | ✅ Satisfecho | Archivos `Dockerfile` y `docker-compose.yml` en la raíz. |
| Uso de GitHub Actions | ✅ Satisfecho | Flujo de CI/CD en `.github/workflows/deploy.yml`. |
| Funcionalidad en local con contenedor | ✅ Satisfecho | Ver **1. Pruebas Locales**. |
| Evidencia de despliegue y actualización | ✅ Satisfecho | Flujo `deploy.yml` que etiqueta con `latest` y `github.sha`. |

## Tecnologías Utilizadas

| Categoría | Tecnología | Uso Específico |
| :--- | :--- | :--- |
| **Aplicación** | Python (Flask) | Servidor web que simula la lógica de **generación y envío** de reportes SARLAFT. |
| **Monorepo** | GitHub | Plataforma para el control de versiones y hosting del monorepositorio. |
| **Contenerización** | Docker | Empaquetado inmutable de la aplicación para garantizar la **funcionalidad en local y nube**. |
| **Orquestación Local** | Docker Compose | Facilita la ejecución y prueba en entorno de desarrollo. |
| **CI/CD** | GitHub Actions | Automatiza los pasos de **Build, Push y Despliegue**. |
| **Registro** | **Docker Hub** | **Registro de Contenedores** que almacena la imagen final. |
| **Nube de Despliegue** | **Render (Web Service)** | Servicio de Contenedores **Serverless** que ejecuta la imagen final. |

---

##  1. Implementación Local 

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
    * **Generar Reporte:** Accede a `http://localhost:5000/generate-sarlaft-report`. Esto simula el flujo automático de generación, retornando un archivo JSON con los datos de cumplimiento.


4.  **Detener:**
    ```bash
    docker-compose down
    ```

---

##  2. Despliegue en la Nube (Evidencia CI/CD y Despliegue Final)

Este proceso se gestiona automáticamente mediante **GitHub Actions** y utiliza **Docker Hub** y **Render**.

### 2.1. Configuración del Flujo

1.  La imagen final se construye y sube al **Registro de Contenedores Docker Hub** bajo el usuario `dxvxd12`.
2.  **Render** consume esta imagen para mantener el servicio activo.

### 2.2. Flujo de Despliegue (Evidencia GitHub Actions)

El archivo `.github/workflows/deploy.yml` automatiza el siguiente flujo al hacer `git push`:

1.  **Login:** Inicia sesión en Docker Hub usando los Secrets de GitHub.
2.  **Build & Tag:** La imagen se construye y se etiqueta: `dxvxd12/regulatory-report-app:latest`
3.  **Push:** La imagen es subida a Docker Hub.
4.  **Despliegue/Actualización:** El servicio en **Render** descarga y despliega la nueva imagen `:latest`.

### 2.3. Funcionalidad en Nube (URL Pública)

Una vez completado el flujo de CI/CD, la funcionalidad está disponible en la URL pública del servicio de contenedores de Render:

| Evidencia | Descripción | URL |
| :--- | :--- | :--- |
| **CI/CD Exitoso** | Log de la acción de GitHub que construye y sube la imagen. | **https://docs.github.com/es/repositories/creating-and-managing-repositories/quickstart-for-repositories/actions** |
| **Imagen Final** | Dirección completa de la imagen en Docker Hub. | `docker.io/dxvxd12/regulatory-report-app:latest` |
| **URL Base de Render** | URL principal del servicio web. | `https://finnova-reports-api.onrender.com` |
| **FUNCIONALIDAD EN NUBE** | **Prueba final de la API que retorna el reporte JSON (Evidencia final).** | **`https://finnova-reports-api.onrender.com/generate-sarlaft-report`** |