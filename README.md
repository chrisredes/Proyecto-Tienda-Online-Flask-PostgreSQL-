# 🎫 Proyecto Tienda Online

Plataforma web desarrollada en Python con Flask y PostgreSQL.

---

## 🚀 ¿Qué hace el programa?

Permite a los usuarios interactuar con un catálogo digital de eventos y productos. Sus funciones principales incluyen:

* Visualización de eventos disponibles y productos de mercancía oficial.
* Sistema de carrito de compras interactivo.
*
* Interfaz visual adaptada con iconos y recursos gráficos propios.

---

## 🎯 Objetivos

* Aplicar conceptos de desarrollo web y Programación Orientada a Objetos (POO).
* Completar el desarrollo del proyecto Tienda Online 
* 

---

## 🧰 Dependencias y Tecnologías Usadas

* **Python** (Versión 3.10 o superior recomendada)
* **Flask** (Framework web backend)
* **PostgreSQL & SQLAlchemy** (Base de datos relacional y ORM)
* **HTML5 / Bootstrap 5** (Estructura, diseño responsivo y estilos)

---

## 🔑 Credenciales de Prueba (Para Evaluación)

Utiliza los siguientes usuarios predeterminados para probar los permisos y la autenticación del sistema:

| Rol | Correo / Usuario | Contraseña | Permisos / Alcance |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin@eventos.com` | `admin123` | Control total: crear, editar y eliminar catálogo/eventos. |
| **Cliente** | `cliente@eventos.com` | `cliente123` | Navegar catálogo, agregar al carrito y procesar compras. |

---

## ⚙️ Guía de Instalación y Ejecución

Sigue estos pasos para clonar y poner en marcha el proyecto localmente:

### 1. Clonar el repositorio

Abre tu terminal y ejecuta:

```bash
git clone https://github.com/chrisredes/Proyecto-Tienda-Online-Flask-PostgreSQL-.git
cd Proyecto-Tienda-Online-Flask-PostgreSQL-
```

### 2. Crear y activar un entorno virtual

**En macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**En Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto basándote en la siguiente plantilla:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=clave_secreta_para_evaluacion
DB_USER=postgres
DB_PASSWORD=tu_contrasena_postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tienda_online
```

### 5. Inicializar la Base de Datos

Crea la base de datos en PostgreSQL con el nombre `tienda_online` y ejecuta el script de migración/datos semilla:

```bash
python init_db.py
```

## ▶️ Ejecución de la Aplicación

Para iniciar el servidor de desarrollo, ejecuta:

```bash
python app.py
```

Abre tu navegador e ingresa a:

**`http://127.0.0.1:5000/`**

## 📁 Estructura del Proyecto

```text
├── assets/            # Iconos e imágenes del sistema
├── templates/         # Vistas HTML (Jinja2)
├── app.py             # Rutas principales y lógica de la aplicación
├── config.py          # Configuración del servidor y BD
├── models.py          # Modelos de base de datos (SQLAlchemy)
├── init_db.py         # Script para la creación e inicialización de la BD
├── requirements.txt   # Lista de dependencias del proyecto
├── .gitignore         # Archivos excluidos de Git
└── README.md          # Documentación oficial del proyecto
```

## ✒️ Autor

- **Christian Perez** - [*chrisredes*](https://github.com/chrisredes)
