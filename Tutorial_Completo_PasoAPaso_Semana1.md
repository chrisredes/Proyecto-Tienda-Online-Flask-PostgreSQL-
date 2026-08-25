# Tutorial Completo Paso a Paso — Proyecto Flask + PostgreSQL
### Desde cero: instalación, configuración y código explicado línea por línea

**Punto de partida:** ya sabes Python y POO. No sabes nada de PostgreSQL, Flask, ni de cómo se instala y configura un proyecto web. Este documento asume eso exactamente.

---

## Índice

1. [Verificar que tienes Python instalado](#1-verificar-python)
2. [Instalar PostgreSQL](#2-instalar-postgresql)
3. [Crear la base de datos](#3-crear-la-base-de-datos)
4. [Preparar la carpeta del proyecto](#4-preparar-la-carpeta-del-proyecto)
5. [Crear un entorno virtual](#5-crear-un-entorno-virtual)
6. [Instalar las librerías del proyecto](#6-instalar-las-librerías)
7. [Construir el proyecto — código explicado paso a paso](#7-construir-el-proyecto)
8. [Ejecutar y probar](#8-ejecutar-y-probar)
9. [Solución de problemas comunes](#9-solución-de-problemas)

---

## 1. Verificar Python

Abre una terminal (en Windows: `cmd` o PowerShell; en Mac/Linux: Terminal) y escribe:

```bash
python --version
```

Si no reconoce el comando, prueba:

```bash
python3 --version
```

Debes ver algo como `Python 3.10.x` o superior. Si no tienes Python instalado, descárgalo de **python.org** antes de continuar — pero como ya han trabajado con Python en clase, es muy probable que ya lo tengas.

---

## 2. Instalar PostgreSQL

PostgreSQL es el motor de base de datos. Es un programa aparte de Python — se instala independientemente. Las instrucciones cambian según tu sistema operativo.

### Windows

1. Ve a **https://www.postgresql.org/download/windows/**
2. Haz clic en "Download the installer" (te lleva al instalador de EDB)
3. Descarga la versión más reciente (16.x)
4. Ejecuta el instalador descargado
5. Durante la instalación:
   - Deja todos los componentes marcados (incluye **pgAdmin 4**, una herramienta visual que usaremos)
   - Cuando pida una contraseña para el usuario `postgres`, **elige una que puedas recordar** — la vas a necesitar. Anótala en un lugar seguro.
   - Deja el puerto en `5432` (el valor por defecto)
   - Al final, puedes omitir "Stack Builder" (no lo necesitamos)
6. Termina la instalación

### macOS

**Opción recomendada — Postgres.app (la más simple):**

1. Ve a **https://postgresapp.com/**
2. Descarga la aplicación
3. Arrástrala a la carpeta Aplicaciones
4. Ábrela — vas a ver un ícono de elefante en la barra superior
5. Haz clic en "Initialize" para crear tu primer servidor — esto ya deja PostgreSQL corriendo automáticamente

**Opción alternativa — con Homebrew (si ya lo usas):**

```bash
brew install postgresql@16
brew services start postgresql@16
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Verifica que el servicio esté corriendo:

```bash
sudo service postgresql status
```

Si no está activo:

```bash
sudo service postgresql start
```

### Verificar que la instalación funcionó (todos los sistemas operativos)

Abre una terminal nueva y escribe:

```bash
psql --version
```

Debes ver algo como `psql (PostgreSQL) 16.x`. Si ves eso, la instalación fue exitosa.

---

## 3. Crear la base de datos

Vamos a crear la base de datos que usará el proyecto. Hay dos formas — usa la que te resulte más cómoda.

### Opción A — Por terminal (psql)

**En Windows**, abre "SQL Shell (psql)" desde el menú de inicio (se instaló junto con PostgreSQL). Te va a pedir:
- Server: presiona Enter (deja el valor por defecto)
- Database: presiona Enter
- Port: presiona Enter
- Username: presiona Enter (queda como `postgres`)
- Password: escribe la contraseña que configuraste en la instalación

**En macOS/Linux**, en tu terminal normal:

```bash
psql -U postgres
```

Te pedirá la contraseña que configuraste (en macOS con Postgres.app puede que no pida contraseña).

**Una vez dentro de psql** (verás el prompt `postgres=#`), escribe:

```sql
CREATE DATABASE tienda_online;
```

Debes ver el mensaje `CREATE DATABASE`. Eso confirma que se creó correctamente.

Para salir:

```sql
\q
```

### Opción B — Con pgAdmin (interfaz visual, solo si la instalaste)

1. Abre pgAdmin 4
2. Te pedirá una contraseña maestra la primera vez — puedes usar la misma de PostgreSQL
3. En el panel izquierdo, expande "Servers" → clic derecho en tu servidor → conecta con tu contraseña
4. Clic derecho en "Databases" → **Create** → **Database...**
5. En "Database", escribe `tienda_online`
6. Clic en **Save**

### Verificar que la base de datos existe

```bash
psql -U postgres -l
```

Deberías ver `tienda_online` en la lista de bases de datos.

---

## 4. Preparar la carpeta del proyecto

Crea una carpeta para el proyecto en el lugar donde normalmente guardas tus trabajos de la universidad:

```bash
mkdir tienda_online
cd tienda_online
```

Dentro, crea la subcarpeta para las plantillas HTML:

```bash
mkdir templates
```

Tu estructura por ahora:
```
tienda_online/
└── templates/
```

---

## 5. Crear un entorno virtual

**¿Qué es esto y por qué lo necesitas?**

Cuando instalas librerías de Python con `pip`, normalmente se instalan de forma global en tu computadora. Eso funciona mientras tengas un solo proyecto, pero apenas trabajes en dos proyectos distintos que necesiten versiones diferentes de la misma librería, vas a tener conflictos.

Un **entorno virtual** es una "burbuja" aislada donde instalas las librerías SOLO para ese proyecto específico, sin afectar el resto de tu computadora.

**Crear el entorno virtual** (dentro de la carpeta `tienda_online`):

```bash
python -m venv venv
```

Esto crea una carpeta llamada `venv` con una copia aislada de Python.

**Activar el entorno virtual:**

En Windows (cmd):
```bash
venv\Scripts\activate
```

En Windows (PowerShell):
```bash
venv\Scripts\Activate.ps1
```

En macOS/Linux:
```bash
source venv/bin/activate
```

**Cómo saber si funcionó:** tu terminal debe mostrar `(venv)` al inicio de la línea, algo como:

```
(venv) C:\Users\TuNombre\tienda_online>
```

**Importante:** cada vez que abras una terminal nueva para trabajar en este proyecto, tienes que activar el entorno virtual de nuevo con el mismo comando. Si no lo activas, Python no va a encontrar las librerías que instalemos en el siguiente paso.

---

## 6. Instalar las librerías

Con el entorno virtual activado (`(venv)` visible en tu terminal), instala todo con un solo comando:

```bash
pip install Flask Flask-SQLAlchemy psycopg2-binary python-dotenv Werkzeug
```

Vas a ver un montón de líneas de instalación. Al final debe decir algo como `Successfully installed Flask-3.0.3 Flask-SQLAlchemy-3.1.1 ...`

**¿Qué es cada librería?**

| Librería | Para qué sirve |
|---|---|
| `Flask` | El framework que crea el servidor web y maneja las rutas (URLs) |
| `Flask-SQLAlchemy` | El traductor entre tus clases Python y las tablas de PostgreSQL |
| `psycopg2-binary` | El conector técnico que le permite a Python "hablar" con PostgreSQL específicamente |
| `python-dotenv` | Lee variables secretas (como contraseñas) desde un archivo separado |
| `Werkzeug` | Viene incluido con Flask — lo usaremos más adelante para encriptar contraseñas |

**Verificar que todo se instaló:**

```bash
pip list
```

Debes ver las 5 librerías (y algunas dependencias adicionales que se instalan automáticamente) en la lista.

---

## 7. Construir el proyecto

Ahora sí, el código. Vamos a crear cada archivo, explicando qué hace cada parte.

### 7.1 — Archivo `.env` (tus datos secretos de conexión)

Crea un archivo llamado exactamente `.env` (con el punto al inicio, sin extensión) dentro de `tienda_online/`:

```
DB_USER=postgres
DB_PASSWORD=tu_contraseña_real_aqui
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tienda_online
SECRET_KEY=cualquier-texto-largo-y-aleatorio-aqui
```

Reemplaza `tu_contraseña_real_aqui` con la contraseña que configuraste al instalar PostgreSQL.

**Por qué este archivo es importante:** nunca vamos a escribir contraseñas directamente en el código Python. Si en el futuro subes este proyecto a GitHub, quieres que este archivo específico NUNCA se suba (lo normal es agregarlo a un archivo `.gitignore`, pero eso lo veremos cuando lleguemos a control de versiones).

---

### 7.2 — Archivo `config.py`

Crea `config.py` dentro de `tienda_online/`:

```python
"""
config.py
─────────
Configuración central de la aplicación. Lee las variables de entorno
desde el archivo .env para no dejar contraseñas escritas directamente
en el código.
"""

import os
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env al entorno de Python
load_dotenv()


class Config:
    # Datos de conexión a PostgreSQL, tomados del .env
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres123")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "tienda_online")

    # SQLAlchemy necesita esta URI con el formato:
    # postgresql://usuario:contraseña@host:puerto/nombre_basedatos
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Desactiva una función de SQLAlchemy que no usaremos
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clave secreta para sesiones de Flask (login, mensajes, etc.)
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-de-desarrollo-temporal")
```

**Explicación línea por línea de lo nuevo:**

- `os.getenv("DB_USER", "postgres")` — busca la variable `DB_USER` en el archivo `.env`. Si no la encuentra, usa `"postgres"` como valor por defecto.
- La f-string de `SQLALCHEMY_DATABASE_URI` arma automáticamente la "dirección" completa de tu base de datos, combinando usuario, contraseña, host, puerto y nombre.
- `class Config` — es una clase normal de Python, como las que ya conocen. Aquí no hay herencia ni métodos complejos, solo se usa como un "contenedor" organizado de configuración.

---

### 7.3 — Archivo `models.py` (las clases conectadas a la base de datos)

Este es el archivo más importante conceptualmente. Créalo dentro de `tienda_online/`:

```python
"""
models.py
─────────
Aquí viven las clases que representan las tablas de la base de datos.

En lugar de heredar de ABC como en clases anteriores, ahora heredamos
de db.Model (de SQLAlchemy). SQLAlchemy tiene su propio mecanismo de
herencia para tablas — funciona con el MISMO concepto de POO que ya
conocen: una clase Padre, clases Hijas que la extienden, y Python
decidiendo automáticamente cuál usar según el tipo real del objeto.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ══════════════════════════════════════════════════════════════
# USUARIO
# ══════════════════════════════════════════════════════════════

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="cliente")
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password_plano):
        self.password_hash = generate_password_hash(password_plano)

    def check_password(self, password_plano):
        return check_password_hash(self.password_hash, password_plano)

    def es_admin(self):
        return self.rol == "admin"

    def __repr__(self):
        return f"<Usuario {self.email} ({self.rol})>"


# ══════════════════════════════════════════════════════════════
# PRODUCTO — jerarquía con herencia polimórfica
# ══════════════════════════════════════════════════════════════

class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    precio_base = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)

    # Columnas exclusivas de ProductoFisico (quedan NULL en otros tipos)
    peso_kg = db.Column(db.Float, nullable=True)
    costo_envio_por_kg = db.Column(db.Float, nullable=True)

    # Columnas exclusivas de ProductoDigital
    licencia = db.Column(db.String(20), nullable=True)

    # Columnas exclusivas de ProductoPerecible
    dias_para_vencer = db.Column(db.Integer, nullable=True)

    # Columna discriminadora: le dice a SQLAlchemy qué clase usar
    tipo = db.Column(db.String(30))

    __mapper_args__ = {
        "polymorphic_identity": "producto",
        "polymorphic_on": tipo,
    }

    def precio_final(self):
        return self.precio_base

    def ficha(self):
        return (f"[{self.codigo}] {self.nombre} "
                f"| Precio final: ${self.precio_final():.2f} "
                f"| Stock: {self.stock}")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.codigo} - {self.nombre}>"


class ProductoFisico(Producto):
    __mapper_args__ = {"polymorphic_identity": "fisico"}

    def precio_final(self):
        envio = (self.peso_kg or 0) * (self.costo_envio_por_kg or 0)
        return self.precio_base + envio


class ProductoDigital(Producto):
    __mapper_args__ = {"polymorphic_identity": "digital"}

    MULTIPLICADORES = {
        "personal": 1.0,
        "comercial": 2.5,
        "educativa": 0.6,
    }

    def precio_final(self):
        multiplicador = self.MULTIPLICADORES.get(self.licencia, 1.0)
        return self.precio_base * multiplicador


class ProductoPerecible(Producto):
    __mapper_args__ = {"polymorphic_identity": "perecible"}

    def precio_final(self):
        dias = self.dias_para_vencer
        if dias is None:
            return self.precio_base
        if dias <= 3:
            return self.precio_base * 0.50
        elif dias <= 7:
            return self.precio_base * 0.80
        return self.precio_base
```

**Explicación detallada de las piezas nuevas:**

- **`db = SQLAlchemy()`** — crea el "traductor" entre Python y PostgreSQL. Todavía no está conectado a ninguna app específica (eso pasa en `app.py`).

- **`db.Column(db.Integer, primary_key=True)`** — así se define una columna de tabla usando sintaxis de Python. `primary_key=True` significa que ese campo identifica de forma única cada fila (como la cédula en los ejercicios que ya hicieron).

- **`nullable=False`** — significa "este campo es obligatorio, no puede quedar vacío". Es el equivalente en base de datos a las validaciones que hacían con `if valor <= 0: print("error")`.

- **`unique=True`** — no puede haber dos filas con el mismo valor en esa columna (por ejemplo, dos usuarios con el mismo email).

- **`tipo = db.Column(db.String(30))`** + **`polymorphic_on: tipo`** — esta es la pieza clave. Cuando guardas un `ProductoFisico`, SQLAlchemy automáticamente escribe `"fisico"` en esta columna. Cuando lees los datos de vuelta, mira esta columna y sabe que debe reconstruir un objeto `ProductoFisico`, no un `Producto` genérico.

- **`class ProductoFisico(Producto):`** — esto es herencia normal de Python, exactamente igual a `class Circulo(Figura):`. La diferencia es que `Producto` no es una clase abstracta con `ABC` — es una clase conectada a SQLAlchemy, y su mecanismo de herencia guarda todo en la misma tabla física.

- **`precio_final()` sobreescrito en cada subclase** — esto es polimorfismo puro, idéntico a lo que ya practicaron. Lo único nuevo es que los objetos ahora vienen de una base de datos real en lugar de crearse a mano en una lista.

---

### 7.4 — Archivo `app.py` (el corazón de la aplicación)

Crea `app.py` dentro de `tienda_online/`:

```python
"""
app.py
──────
Punto de entrada de la aplicación. Aquí se crea la app de Flask,
se conecta con la base de datos, y se definen las rutas (URLs).
"""

from flask import Flask, render_template
from config import Config
from models import db, Producto

app = Flask(__name__)
app.config.from_object(Config)

# Conecta esta app con la instancia de SQLAlchemy definida en models.py
db.init_app(app)


@app.route("/")
def inicio():
    """Página principal: lista todos los productos activos."""
    productos = Producto.query.filter_by(activo=True).all()
    return render_template("index.html", productos=productos)


@app.route("/producto/<int:producto_id>")
def detalle_producto(producto_id):
    """Muestra el detalle de un producto específico."""
    producto = Producto.query.get_or_404(producto_id)
    return render_template("detalle.html", producto=producto)


if __name__ == "__main__":
    app.run(debug=True)
```

**Explicación detallada:**

- **`app = Flask(__name__)`** — crea la aplicación. `__name__` le dice a Flask en qué archivo está corriendo, para que sepa dónde buscar la carpeta `templates/`.

- **`app.config.from_object(Config)`** — toma toda la configuración que armaste en `config.py` (incluida la conexión a PostgreSQL) y se la aplica a esta app.

- **`db.init_app(app)`** — esta línea es la que finalmente conecta el `db` de `models.py` con esta aplicación específica. Sin esto, SQLAlchemy no sabría a qué base de datos conectarse.

- **`@app.route("/")`** — un decorador (ya conocen los decoradores de `@property` y `@abstractmethod`). Este le dice a Flask: "cuando alguien visite la URL raíz del sitio, ejecuta la función de abajo".

- **`def inicio():`** — la función que se ejecuta. Se llama "vista" en Flask.

- **`Producto.query.filter_by(activo=True).all()`** — esto es SQL escrito como si fuera Python. Es el equivalente a `SELECT * FROM productos WHERE activo = true`. SQLAlchemy traduce esto automáticamente al lenguaje SQL real.

- **`render_template("index.html", productos=productos)`** — busca el archivo `index.html` dentro de `templates/` y le "inyecta" la lista de productos para que la plantilla pueda mostrarla.

- **`<int:producto_id>`** — esto en la URL significa "esta parte de la dirección va a ser un número entero, y quiero que me lo pases como el parámetro `producto_id`". Si alguien visita `/producto/5`, Flask ejecuta `detalle_producto(5)`.

- **`Producto.query.get_or_404(producto_id)`** — busca el producto por su ID. Si no existe, automáticamente muestra una página de error 404 (no encontrado), sin que tengas que escribir ese manejo de error tú mismo.

- **`if __name__ == "__main__":`** — ya lo vieron en la clase de módulos. Esto asegura que el servidor solo se inicie cuando ejecutas este archivo directamente, no si algún día lo importas desde otro lugar.

---

### 7.5 — Archivo `init_db.py` (crear tablas y datos de prueba)

Crea `init_db.py` dentro de `tienda_online/`:

```python
"""
init_db.py
──────────
Script para crear las tablas en PostgreSQL y cargar datos de prueba.
Ejecutar UNA sola vez (o cada vez que quieras reiniciar los datos).
"""

from app import app
from models import db, ProductoFisico, ProductoDigital, ProductoPerecible, Usuario

with app.app_context():
    print("Creando tablas...")
    db.drop_all()   # Borra todo si ya existía (útil mientras desarrollan)
    db.create_all()
    print("✔ Tablas creadas.")

    # ── Usuarios de prueba ────────────────────────────────────
    admin = Usuario(nombre="Admin Principal", email="admin@tienda.com", rol="admin")
    admin.set_password("admin123")

    cliente = Usuario(nombre="Cliente Demo", email="cliente@tienda.com", rol="cliente")
    cliente.set_password("cliente123")

    db.session.add_all([admin, cliente])

    # ── Productos de prueba ─────────────────────────────────────
    p1 = ProductoFisico(
        codigo="FIS001", nombre="Audífonos Bluetooth", precio_base=25.00,
        stock=40, peso_kg=0.3, costo_envio_por_kg=2.50
    )
    p2 = ProductoDigital(
        codigo="DIG001", nombre="Curso de Python Avanzado", precio_base=40.00,
        stock=999, licencia="personal"
    )
    p3 = ProductoPerecible(
        codigo="PER001", nombre="Caja de fresas orgánicas", precio_base=8.00,
        stock=15, dias_para_vencer=2
    )

    db.session.add_all([p1, p2, p3])
    db.session.commit()

    print("✔ Usuarios y productos de prueba insertados.")
    print("\nCredenciales de prueba:")
    print("  Admin   → admin@tienda.com   / admin123")
    print("  Cliente → cliente@tienda.com / cliente123")
```

**Explicación detallada:**

- **`with app.app_context():`** — SQLAlchemy necesita saber "en qué aplicación Flask estoy trabajando" para poder hablar con la base de datos correcta. Este bloque se lo garantiza. Es obligatorio siempre que uses `db` fuera de una ruta normal de Flask.

- **`db.drop_all()`** — borra todas las tablas si ya existían. Últil mientras están desarrollando y quieren "empezar de cero" varias veces. **Cuidado:** en un proyecto real ya en producción, jamás usarías esto — borraría todos los datos reales.

- **`db.create_all()`** — lee todas las clases que heredan de `db.Model` en tu proyecto, y crea automáticamente las tablas correspondientes en PostgreSQL con sus columnas exactas.

- **`admin.set_password("admin123")`** — nunca guardamos la contraseña tal cual. Este método (que definiste en `models.py`) la convierte en un hash irreversible antes de guardarla.

- **`db.session.add_all([...])`** — prepara varios objetos para guardarse (todavía no los guarda).

- **`db.session.commit()`** — esta es la línea que realmente escribe todo en PostgreSQL. Sin este `commit()`, nada de lo anterior se guarda de verdad — se queda solo "en memoria".

---

### 7.6 — Plantilla `templates/base.html`

Crea la carpeta `templates/` (si no la creaste antes) y dentro el archivo `base.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block titulo %}Tienda Online{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>

    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('inicio') }}">🛒 Tienda Online</a>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

**Explicación detallada:**

- **`{% block titulo %}...{% endblock %}`** — define una "zona editable" que cada página hija puede sobreescribir. Si una página hija no define su propio título, usa "Tienda Online" por defecto.

- **`{{ url_for('inicio') }}`** — en lugar de escribir la URL a mano (`href="/"`), Flask genera la dirección automáticamente basándose en el nombre de la función de la ruta (`def inicio():`). Esto es una buena práctica: si algún día cambias la URL en `app.py`, el link se actualiza solo, sin que tengas que buscar y reemplazar en cada plantilla.

- **`{% block content %}{% endblock %}`** — la zona principal donde cada página específica (`index.html`, `detalle.html`) va a insertar su propio contenido.

---

### 7.7 — Plantilla `templates/index.html`

```html
{% extends "base.html" %}

{% block titulo %}Catálogo — Tienda Online{% endblock %}

{% block content %}
    <h1 class="mb-4">Catálogo de Productos</h1>

    <div class="row">
        {% for producto in productos %}
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <span class="badge bg-secondary mb-2">{{ producto.tipo }}</span>
                    <h5 class="card-title">{{ producto.nombre }}</h5>
                    <p class="card-text text-muted">Código: {{ producto.codigo }}</p>
                    <p class="card-text fs-4 fw-bold">
                        ${{ "%.2f"|format(producto.precio_final()) }}
                    </p>
                    <a href="{{ url_for('detalle_producto', producto_id=producto.id) }}"
                       class="btn btn-primary">
                        Ver detalle
                    </a>
                </div>
            </div>
        </div>
        {% else %}
        <p class="text-center text-muted">No hay productos disponibles todavía.</p>
        {% endfor %}
    </div>
{% endblock %}
```

**Explicación detallada:**

- **`{% extends "base.html" %}`** — esta línea le dice a Jinja2 "esta página es hija de base.html". Es exactamente el mismo concepto que `class Hijo(Padre):` en Python.

- **`{% for producto in productos %}`** — un bucle `for` normal, escrito con la sintaxis especial de Jinja2 (con `{% %}` en vez de dos puntos e indentación). Recorre la lista `productos` que le pasamos desde `app.py`.

- **`{{ producto.nombre }}`** — acceso a un atributo del objeto, igual que en Python (`producto.nombre`), pero con dobles llaves `{{ }}` para indicar "aquí va un valor a mostrar".

- **`{{ "%.2f"|format(producto.precio_final()) }}`** — llama al método `precio_final()` del objeto (polimorfismo funcionando aquí mismo, en la plantilla), y le aplica formato de 2 decimales.

- **`{% else %}`** dentro de un `{% for %}`** — esto es específico de Jinja2 (no existe en Python normal): si la lista está vacía, muestra ese contenido alternativo.

---

### 7.8 — Plantilla `templates/detalle.html`

```html
{% extends "base.html" %}

{% block titulo %}{{ producto.nombre }} — Tienda Online{% endblock %}

{% block content %}
    <a href="{{ url_for('inicio') }}" class="btn btn-outline-secondary mb-3">← Volver al catálogo</a>

    <div class="card">
        <div class="card-body">
            <span class="badge bg-secondary mb-2">{{ producto.tipo }}</span>
            <h1>{{ producto.nombre }}</h1>
            <p class="text-muted">Código: {{ producto.codigo }}</p>
            <p class="fs-3 fw-bold">${{ "%.2f"|format(producto.precio_final()) }}</p>
            <p>Stock disponible: {{ producto.stock }}</p>

            {% if producto.tipo == "fisico" %}
                <hr>
                <h5>Detalles de envío</h5>
                <p>Peso: {{ producto.peso_kg }} kg</p>
            {% elif producto.tipo == "digital" %}
                <hr>
                <h5>Detalles de licencia</h5>
                <p>Tipo de licencia: {{ producto.licencia|capitalize }}</p>
            {% elif producto.tipo == "perecible" %}
                <hr>
                <h5>Detalles de vencimiento</h5>
                <p>Días para vencer: {{ producto.dias_para_vencer }}</p>
            {% endif %}
        </div>
    </div>
{% endblock %}
```

**Explicación detallada:**

- **`{% if producto.tipo == "fisico" %}` ... `{% elif %}` ... `{% endif %}`** — condicional de Jinja2, igual que un `if/elif` de Python pero con esta sintaxis especial de plantillas.

- **`{{ producto.licencia|capitalize }}`** — el símbolo `|` aplica un "filtro" al valor. `capitalize` pone la primera letra en mayúscula. Es parecido a encadenar métodos en Python (`.capitalize()`), pero con sintaxis propia de Jinja2.

---

## 8. Ejecutar y probar

Tu estructura final de carpetas debe verse así:

```
tienda_online/
├── venv/                    (creado automáticamente, no lo tocas)
├── .env
├── app.py
├── config.py
├── init_db.py
├── models.py
└── templates/
    ├── base.html
    ├── index.html
    └── detalle.html
```

### Paso 1 — Verifica que el entorno virtual esté activo

Tu terminal debe mostrar `(venv)` al inicio. Si no, actívalo de nuevo (paso 5 de este documento).

### Paso 2 — Crea las tablas y los datos de prueba

```bash
python init_db.py
```

Debes ver:
```
Creando tablas...
✔ Tablas creadas.
✔ Usuarios y productos de prueba insertados.
```

### Paso 3 — Verifica en PostgreSQL que las tablas se crearon (opcional pero recomendado)

```bash
psql -U postgres -d tienda_online -c "SELECT codigo, nombre, tipo FROM productos;"
```

Debes ver una tabla con tus 3 productos y su columna `tipo` correctamente llenada.

### Paso 4 — Ejecuta la aplicación

```bash
python app.py
```

Debes ver:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Paso 5 — Ábrelo en el navegador

Ve a **http://127.0.0.1:5000** — debes ver el catálogo con tus productos, cada uno con su precio ya calculado según su tipo.

Haz clic en "Ver detalle" de cualquier producto — debes ver la página de detalle con la información específica de ese tipo (envío, licencia, o vencimiento).

### Paso 6 — Detener el servidor

En la terminal donde está corriendo, presiona `Ctrl + C`.

---

## 9. Solución de problemas

| Problema | Causa más probable | Solución |
|---|---|---|
| `python: command not found` | Python no está en el PATH, o se llama `python3` en tu sistema | Prueba `python3` en lugar de `python` en todos los comandos |
| `ModuleNotFoundError: No module named 'flask'` | El entorno virtual no está activado, o las librerías no se instalaron | Verifica que veas `(venv)` en tu terminal; si no, actívalo y vuelve a instalar |
| `psycopg2.OperationalError: could not connect to server` | PostgreSQL no está corriendo | Windows: revisa "Servicios" → PostgreSQL debe estar "En ejecución". Mac: abre Postgres.app. Linux: `sudo service postgresql start` |
| `psycopg2.OperationalError: password authentication failed` | La contraseña en tu `.env` no coincide con la real de PostgreSQL | Verifica que `DB_PASSWORD` en `.env` sea exactamente la que configuraste al instalar |
| `sqlalchemy.exc.OperationalError: database "tienda_online" does not exist` | Olvidaste crear la base de datos, o el nombre no coincide | Repite el paso 3 de este documento, verifica el nombre exacto |
| La página carga pero sin estilos (se ve "fea") | No hay conexión a internet para cargar Bootstrap desde el CDN | Bootstrap se carga desde internet — revisa tu conexión |
| `TemplateNotFound: index.html` | El archivo no está dentro de la carpeta `templates/`, o el nombre no coincide exactamente | Flask busca plantillas SOLO en una carpeta llamada exactamente `templates` |
| Los precios no cambian según el tipo de producto | Olvidaste sobreescribir `precio_final()` en alguna subclase, o hay un error de indentación | Revisa que el método esté DENTRO de la clase hija, con la indentación correcta |
| `(venv)` desapareció de mi terminal | Cerraste la terminal o abriste una nueva | Vuelve a activar el entorno virtual (paso 5) cada vez que abras una terminal nueva |

---

## Checklist final — antes de la próxima clase

- [ ] PostgreSQL instalado y corriendo
- [ ] Base de datos `tienda_online` creada
- [ ] Entorno virtual creado y se activa correctamente
- [ ] Las 5 librerías instaladas dentro del entorno virtual
- [ ] Los 5 archivos Python creados (`config.py`, `models.py`, `app.py`, `init_db.py`) y las 3 plantillas HTML
- [ ] `python init_db.py` corre sin errores
- [ ] `python app.py` levanta el servidor sin errores
- [ ] Puedes ver el catálogo en `http://127.0.0.1:5000` con los 3 productos y sus precios correctos
- [ ] Puedes hacer clic en "Ver detalle" y ver la información específica de cada tipo de producto
