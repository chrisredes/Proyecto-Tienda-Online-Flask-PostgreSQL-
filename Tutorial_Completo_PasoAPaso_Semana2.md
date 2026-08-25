# Tutorial Completo Paso a Paso — Semana 2: CRUD + Usuarios + Login
### Desde el proyecto de la Semana 1 hasta formularios y autenticación funcionando

**Punto de partida:** ya tienes el proyecto de la Semana 1 corriendo — catálogo de productos leyendo desde PostgreSQL, con la jerarquía `Producto` → `ProductoFisico`/`ProductoDigital`/`ProductoPerecible`. Este documento asume eso exactamente.

---

## Índice

1. [Verificar que la Semana 1 sigue funcionando](#1-verificar-la-semana-1)
2. [Concepto: GET vs POST](#2-concepto-get-vs-post)
3. [Actualizar base.html — navbar dinámico y mensajes flash](#3-actualizar-basehtml)
4. [CRUD — Crear productos (los 3 tipos)](#4-crud-crear-productos)
5. [CRUD — Editar productos](#5-crud-editar-productos)
6. [CRUD — Desactivar productos (eliminación suave)](#6-crud-desactivar-productos)
7. [Registro de usuarios](#7-registro-de-usuarios)
8. [Login y sesiones](#8-login-y-sesiones)
9. [Logout](#9-logout)
10. [Ejecutar y probar todo el flujo](#10-ejecutar-y-probar)
11. [Solución de problemas](#11-solución-de-problemas)

---

## 1. Verificar la Semana 1

Antes de escribir una sola línea nueva, confirma que lo anterior funciona:

```bash
cd tienda_online
source venv/bin/activate      # Windows: venv\Scripts\activate
python app.py
```

Abre `http://127.0.0.1:5000` — debes ver el catálogo con tus productos. Si esto no funciona, resuelve eso primero (revisa la tabla de solución de problemas del tutorial de la Semana 1) antes de continuar.

Detén el servidor con `Ctrl + C` antes de seguir editando archivos.

---

## 2. Concepto: GET vs POST

Antes del código, un concepto que vas a usar constantemente hoy.

**GET** es lo que pasa cuando visitas una URL normalmente — le estás pidiendo al servidor "muéstrame algo". Cuando entras a `/productos/nuevo/fisico` por primera vez, tu navegador hace una petición GET, y lo que esperas ver es el formulario **vacío**.

**POST** es lo que pasa cuando envías un formulario con el atributo `method="POST"`. Le estás diciendo al servidor "aquí tienes datos, guárdalos". Cuando llenas el formulario y presionas "Crear producto", el navegador hace una petición POST con toda la información que escribiste.

**La misma URL puede manejar ambos casos** — así es como vamos a escribir nuestras rutas hoy:

```python
@app.route("/productos/nuevo/fisico", methods=["GET", "POST"])
def nuevo_producto_fisico():
    if request.method == "POST":
        # Aquí llegan los datos del formulario — los procesamos
        ...
    # Si no es POST (es decir, es GET), mostramos el formulario vacío
    return render_template("nuevo_fisico.html")
```

---

## 3. Actualizar base.html

Vamos a modificar el `base.html` de la Semana 1 para que:
- Muestre mensajes de confirmación o error (los llamados "mensajes flash")
- Cambie el menú de navegación según haya una sesión activa o no

Reemplaza el contenido completo de `templates/base.html`:

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
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('inicio') }}">Catálogo</a>
                    </li>
                    {% if session.get('usuario_id') %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            + Agregar producto
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('nuevo_producto_fisico') }}">Producto Físico</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('nuevo_producto_digital') }}">Producto Digital</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('nuevo_producto_perecible') }}">Producto Perecible</a></li>
                        </ul>
                    </li>
                    {% endif %}
                </ul>
                <ul class="navbar-nav ms-auto">
                    {% if session.get('usuario_id') %}
                        <li class="nav-item">
                            <span class="nav-link text-light">
                                👤 {{ session.get('usuario_nombre') }}
                                <span class="badge bg-secondary">{{ session.get('usuario_rol') }}</span>
                            </span>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">Cerrar sesión</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('login') }}">Iniciar sesión</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('registro') }}">Registrarse</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">

        {% with mensajes = get_flashed_messages(with_categories=true) %}
            {% if mensajes %}
                {% for categoria, texto in mensajes %}
                    <div class="alert alert-{{ categoria }} alert-dismissible fade show" role="alert">
                        {{ texto }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

**Explicación detallada de lo nuevo:**

- **`{% if session.get('usuario_id') %}`** — `session` está disponible automáticamente en cualquier plantilla, sin que tengas que pasarla manualmente desde `app.py`. Aquí preguntamos: "¿hay alguien con sesión iniciada?"

- **El menú desplegable "+ Agregar producto"** — solo se muestra si hay sesión activa. Usa clases de Bootstrap (`dropdown`, `dropdown-menu`, `dropdown-item`) que ya viste en el cheatsheet.

- **`{% with mensajes = get_flashed_messages(with_categories=true) %}`** — recupera los mensajes que hayamos enviado con `flash()` desde Python. `with_categories=true` significa que cada mensaje viene acompañado de una categoría (como `"success"` o `"danger"`), que usamos para pintar la alerta del color correcto (`alert-success`, `alert-danger`).

- **`{% endwith %}`** — cierra el bloque `with`. Es una forma de crear una variable temporal (`mensajes`) que solo existe dentro de ese bloque.

---

## 4. CRUD — Crear productos

Vamos a agregar 3 rutas nuevas a `app.py` — una por cada tipo de producto. Empecemos por `ProductoFisico`.

### 4.1 — Actualiza los imports en app.py

Al principio de `app.py`, asegúrate de tener:

```python
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import db, Producto, ProductoFisico, ProductoDigital, ProductoPerecible, Usuario
```

**Qué es nuevo aquí:**
- `request` — para leer los datos que llegan del formulario
- `redirect` — para enviar al usuario a otra página después de una acción
- `session` — para manejar la sesión del usuario logueado
- `flash` — para mostrar mensajes de confirmación o error

### 4.2 — La ruta de creación de ProductoFisico

Agrega esto en `app.py`, después de las rutas de la Semana 1:

```python
@app.route("/productos/nuevo/fisico", methods=["GET", "POST"])
def nuevo_producto_fisico():
    if request.method == "POST":
        try:
            producto = ProductoFisico(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                precio_base=float(request.form["precio_base"]),
                stock=int(request.form["stock"]),
                peso_kg=float(request.form["peso_kg"]),
                costo_envio_por_kg=float(request.form["costo_envio_por_kg"]),
            )
            db.session.add(producto)
            db.session.commit()
            flash(f"Producto físico '{producto.nombre}' creado correctamente.", "success")
            return redirect(url_for("inicio"))
        except ValueError:
            flash("Revisa que los campos numéricos tengan valores válidos.", "danger")
        except Exception:
            db.session.rollback()
            flash("Ocurrió un error. Verifica que el código no esté repetido.", "danger")

    return render_template("nuevo_fisico.html")
```

**Explicación detallada, línea por línea:**

- **`methods=["GET", "POST"]`** — esta única ruta maneja los dos casos que vimos en la sección 2.

- **`request.form["codigo"]`** — recupera el valor del campo del formulario llamado `codigo`. Esto SIEMPRE llega como texto (string), sin importar qué tipo de dato sea en realidad.

- **`float(request.form["precio_base"])`** — como todo llega como texto, hay que convertir explícitamente los números. Si el usuario escribió algo que no es un número válido, esto lanza un `ValueError` — por eso está dentro de un `try`.

- **`db.session.add(producto)`** — le dice a SQLAlchemy "voy a querer guardar este objeto nuevo". Todavía no lo escribe en PostgreSQL.

- **`db.session.commit()`** — esta es la línea que realmente ejecuta el `INSERT` en la base de datos.

- **`flash(mensaje, categoria)`** — guarda un mensaje temporal que se va a mostrar en la próxima página que se cargue (gracias al bloque que agregamos en `base.html`). La categoría (`"success"`, `"danger"`) determina el color de la alerta.

- **`redirect(url_for("inicio"))`** — después de crear el producto, redirige al catálogo. `url_for("inicio")` genera la URL automáticamente a partir del nombre de la función `inicio()`, en vez de escribir `"/"` a mano.

- **`except ValueError:`** — captura errores de conversión de números (si alguien escribió texto donde se esperaba un número).

- **`except Exception:` + `db.session.rollback()`** — captura cualquier otro error (por ejemplo, un código de producto repetido, que viola la restricción `unique=True`). `rollback()` deshace cualquier cambio a medias para que la sesión de base de datos quede en un estado limpio.

### 4.3 — La plantilla del formulario

Crea `templates/nuevo_fisico.html`:

```html
{% extends "base.html" %}

{% block titulo %}Nuevo Producto Físico{% endblock %}

{% block content %}
    <a href="{{ url_for('inicio') }}" class="btn btn-outline-secondary mb-3">← Volver al catálogo</a>

    <div class="card">
        <div class="card-body">
            <h2 class="mb-4">📦 Nuevo Producto Físico</h2>

            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Código</label>
                    <input type="text" class="form-control" name="codigo" required>
                </div>

                <div class="mb-3">
                    <label class="form-label">Nombre</label>
                    <input type="text" class="form-control" name="nombre" required>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Precio base ($)</label>
                        <input type="number" step="0.01" class="form-control" name="precio_base" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Stock inicial</label>
                        <input type="number" class="form-control" name="stock" required>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Peso (kg)</label>
                        <input type="number" step="0.01" class="form-control" name="peso_kg" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Costo de envío por kg ($)</label>
                        <input type="number" step="0.01" class="form-control" name="costo_envio_por_kg" required>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary">Crear producto</button>
            </form>
        </div>
    </div>
{% endblock %}
```

**Los dos detalles más importantes de este formulario:**

- **`<form method="POST">`** — sin esto, el formulario haría una petición GET al enviarse, y `request.form` estaría vacío en Python.

- **`name="codigo"`, `name="nombre"`, etc.** — cada `name` debe coincidir EXACTAMENTE con la clave que usas en `request.form["..."]` del lado de Python. Si te equivocas en la ortografía de uno solo, Python lanzará un `KeyError`.

- **`type="number" step="0.01"`** — el navegador ya valida que solo se puedan escribir números, y `step="0.01"` permite decimales.

### 4.4 — Réplica para ProductoDigital y ProductoPerecible

Ahora repite exactamente el mismo patrón. Agrega a `app.py`:

```python
@app.route("/productos/nuevo/digital", methods=["GET", "POST"])
def nuevo_producto_digital():
    if request.method == "POST":
        try:
            producto = ProductoDigital(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                precio_base=float(request.form["precio_base"]),
                stock=int(request.form["stock"]),
                licencia=request.form["licencia"],
            )
            db.session.add(producto)
            db.session.commit()
            flash(f"Producto digital '{producto.nombre}' creado correctamente.", "success")
            return redirect(url_for("inicio"))
        except ValueError:
            flash("Revisa que los campos numéricos tengan valores válidos.", "danger")
        except Exception:
            db.session.rollback()
            flash("Ocurrió un error. Verifica que el código no esté repetido.", "danger")

    return render_template("nuevo_digital.html")


@app.route("/productos/nuevo/perecible", methods=["GET", "POST"])
def nuevo_producto_perecible():
    if request.method == "POST":
        try:
            producto = ProductoPerecible(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                precio_base=float(request.form["precio_base"]),
                stock=int(request.form["stock"]),
                dias_para_vencer=int(request.form["dias_para_vencer"]),
            )
            db.session.add(producto)
            db.session.commit()
            flash(f"Producto perecible '{producto.nombre}' creado correctamente.", "success")
            return redirect(url_for("inicio"))
        except ValueError:
            flash("Revisa que los campos numéricos tengan valores válidos.", "danger")
        except Exception:
            db.session.rollback()
            flash("Ocurrió un error. Verifica que el código no esté repetido.", "danger")

    return render_template("nuevo_perecible.html")
```

Crea `templates/nuevo_digital.html`:

```html
{% extends "base.html" %}
{% block titulo %}Nuevo Producto Digital{% endblock %}
{% block content %}
    <a href="{{ url_for('inicio') }}" class="btn btn-outline-secondary mb-3">← Volver al catálogo</a>
    <div class="card">
        <div class="card-body">
            <h2 class="mb-4">💾 Nuevo Producto Digital</h2>
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Código</label>
                    <input type="text" class="form-control" name="codigo" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Nombre</label>
                    <input type="text" class="form-control" name="nombre" required>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Precio base ($)</label>
                        <input type="number" step="0.01" class="form-control" name="precio_base" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Stock inicial</label>
                        <input type="number" class="form-control" name="stock" required>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Tipo de licencia</label>
                    <select class="form-control" name="licencia" required>
                        <option value="personal">Personal</option>
                        <option value="comercial">Comercial</option>
                        <option value="educativa">Educativa</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Crear producto</button>
            </form>
        </div>
    </div>
{% endblock %}
```

**Nota sobre `<select>`:** a diferencia de un `<input>`, aquí el valor que llega a `request.form["licencia"]` es el contenido del atributo `value` de la opción seleccionada (`"personal"`, `"comercial"` o `"educativa"`), no el texto visible.

Crea `templates/nuevo_perecible.html`:

```html
{% extends "base.html" %}
{% block titulo %}Nuevo Producto Perecible{% endblock %}
{% block content %}
    <a href="{{ url_for('inicio') }}" class="btn btn-outline-secondary mb-3">← Volver al catálogo</a>
    <div class="card">
        <div class="card-body">
            <h2 class="mb-4">🍓 Nuevo Producto Perecible</h2>
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Código</label>
                    <input type="text" class="form-control" name="codigo" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Nombre</label>
                    <input type="text" class="form-control" name="nombre" required>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Precio base ($)</label>
                        <input type="number" step="0.01" class="form-control" name="precio_base" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Stock inicial</label>
                        <input type="number" class="form-control" name="stock" required>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Días para vencer</label>
                    <input type="number" class="form-control" name="dias_para_vencer" required>
                    <small class="text-muted">3 días o menos = 50% descuento · 7 días o menos = 20% descuento</small>
                </div>
                <button type="submit" class="btn btn-primary">Crear producto</button>
            </form>
        </div>
    </div>
{% endblock %}
```

---

## 5. CRUD — Editar productos

Agrega esta ruta a `app.py`:

```python
@app.route("/productos/<int:producto_id>/editar", methods=["GET", "POST"])
def editar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)

    if request.method == "POST":
        try:
            producto.nombre = request.form["nombre"]
            producto.precio_base = float(request.form["precio_base"])
            producto.stock = int(request.form["stock"])
            db.session.commit()
            flash(f"Producto '{producto.nombre}' actualizado correctamente.", "success")
            return redirect(url_for("detalle_producto", producto_id=producto.id))
        except ValueError:
            flash("Revisa que los campos numéricos tengan valores válidos.", "danger")

    return render_template("editar.html", producto=producto)
```

**El detalle más importante de esta ruta — compáralo con la de "crear":**

Fíjate que aquí **NO** usamos `db.session.add(producto)`. La razón: `producto` ya existía en la base de datos — lo obtuvimos con `Producto.query.get_or_404(producto_id)`. SQLAlchemy ya está "vigilando" ese objeto. Cuando modificas sus atributos (`producto.nombre = ...`), SQLAlchemy detecta el cambio automáticamente. Solo necesitas `db.session.commit()` para que se guarde de verdad.

Crea `templates/editar.html`:

```html
{% extends "base.html" %}

{% block titulo %}Editar {{ producto.nombre }}{% endblock %}

{% block content %}
    <a href="{{ url_for('detalle_producto', producto_id=producto.id) }}" class="btn btn-outline-secondary mb-3">← Cancelar</a>

    <div class="card">
        <div class="card-body">
            <h2 class="mb-1">✏️ Editar Producto</h2>
            <p class="text-muted mb-4">
                <span class="badge bg-secondary">{{ producto.tipo }}</span>
                Código: {{ producto.codigo }} (no editable)
            </p>

            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Nombre</label>
                    <input type="text" class="form-control" name="nombre" value="{{ producto.nombre }}" required>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Precio base ($)</label>
                        <input type="number" step="0.01" class="form-control"
                               name="precio_base" value="{{ producto.precio_base }}" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Stock</label>
                        <input type="number" class="form-control"
                               name="stock" value="{{ producto.stock }}" required>
                    </div>
                </div>

                <div class="alert alert-info">
                    Nota: los campos específicos del tipo de producto (peso, licencia, días de vencimiento)
                    no se editan aquí en esta versión — solo los datos generales.
                </div>

                <button type="submit" class="btn btn-primary">Guardar cambios</button>
            </form>
        </div>
    </div>
{% endblock %}
```

**Detalle clave: `value="{{ producto.nombre }}"`**

A diferencia del formulario de "crear" (que empieza vacío), el formulario de "editar" debe **precargar** los datos actuales del producto. Por eso cada `<input>` tiene un atributo `value` con el dato ya existente — así el usuario ve lo que hay antes de cambiarlo.

---

## 6. CRUD — Desactivar productos

Agrega esta ruta a `app.py`:

```python
@app.route("/productos/<int:producto_id>/eliminar", methods=["POST"])
def eliminar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    producto.activo = False
    db.session.commit()
    flash(f"Producto '{producto.nombre}' desactivado del catálogo.", "success")
    return redirect(url_for("inicio"))
```

**¿Por qué "desactivar" y no "borrar de verdad"?**

Si alguna vez ese producto fue parte de una venta, borrarlo físicamente de la tabla `productos` rompería el historial de ventas — cualquier reporte futuro que intente mostrar "qué se vendió" fallaría al no encontrar el producto. La práctica estándar en sistemas reales es marcar el registro como inactivo (`activo = False`) en vez de eliminarlo. Como ya filtramos `Producto.query.filter_by(activo=True)` en la ruta `/` desde la Semana 1, el producto desaparece del catálogo visible sin perder el dato.

**Nota sobre `methods=["POST"]` (sin `"GET"`):** esta ruta NO tiene una versión "GET" porque no hay ningún formulario que mostrar — es una acción directa. Por eso se activa únicamente a través de un botón dentro de un `<form>`, nunca visitando la URL directamente desde la barra de direcciones.

Agrega el botón correspondiente en `templates/detalle.html`, dentro del `{% block content %}`, después de la información del producto:

```html
{% if session.get('usuario_id') %}
<hr>
<div class="d-flex gap-2">
    <a href="{{ url_for('editar_producto', producto_id=producto.id) }}"
       class="btn btn-outline-primary">
        ✏️ Editar
    </a>
    <form action="{{ url_for('eliminar_producto', producto_id=producto.id) }}"
          method="POST"
          onsubmit="return confirm('¿Seguro que quieres desactivar este producto?');">
        <button type="submit" class="btn btn-outline-danger">
            🗑️ Desactivar
        </button>
    </form>
</div>
{% endif %}
```

**`onsubmit="return confirm(...)"`** — esto es JavaScript mínimo (no necesitas entenderlo a fondo todavía): muestra una ventana de confirmación del navegador antes de enviar el formulario. Si el usuario presiona "Cancelar", el formulario no se envía.

---

## 7. Registro de usuarios

Agrega esta ruta a `app.py`:

```python
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form["email"].strip().lower()

        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese correo.", "danger")
            return render_template("registro.html")

        usuario = Usuario(
            nombre=request.form["nombre"],
            email=email,
            rol="cliente",
        )
        usuario.set_password(request.form["password"])
        db.session.add(usuario)
        db.session.commit()

        flash("Cuenta creada correctamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")
```

**Explicación detallada:**

- **`.strip().lower()`** — quita espacios accidentales al inicio/final y convierte todo a minúsculas. Así `"Ana@Correo.com "` y `"ana@correo.com"` se tratan como el mismo correo — evita duplicados por diferencias de mayúsculas.

- **`Usuario.query.filter_by(email=email).first()`** — busca si ya existe un usuario con ese correo. `.first()` retorna el primer resultado encontrado, o `None` si no hay ninguno. Como `None` es "falsy" en Python, el `if` funciona directamente.

- **`rol="cliente"`** — este valor está fijo en el código, nunca viene de `request.form`. Es una decisión de seguridad deliberada: si dejáramos que el formulario definiera el rol, cualquier persona podría escribir `rol=admin` manualmente y registrarse como administrador.

- **`usuario.set_password(request.form["password"])`** — este método ya lo definiste en `models.py` desde la Semana 1. Internamente usa `generate_password_hash()` de Werkzeug para convertir la contraseña en un hash. **Nunca vas a ver ni guardar la contraseña real.**

Crea `templates/registro.html`:

```html
{% extends "base.html" %}

{% block titulo %}Crear Cuenta{% endblock %}

{% block content %}
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h2 class="mb-4">Crear Cuenta</h2>

                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Nombre completo</label>
                            <input type="text" class="form-control" name="nombre" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Correo electrónico</label>
                            <input type="email" class="form-control" name="email" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Contraseña</label>
                            <input type="password" class="form-control" name="password"
                                   minlength="6" required>
                        </div>

                        <button type="submit" class="btn btn-primary w-100">Registrarme</button>
                    </form>

                    <p class="text-center mt-3 mb-0">
                        ¿Ya tienes cuenta?
                        <a href="{{ url_for('login') }}">Inicia sesión</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

**`type="password"`** — el navegador oculta automáticamente lo que se escribe (mostrando puntos o asteriscos). **`minlength="6"`** — validación básica del lado del navegador; no es suficiente por sí sola (se puede evadir), pero ayuda a la experiencia normal de uso.

---

## 8. Login y sesiones

Agrega esta ruta a `app.py`:

```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre
            session["usuario_rol"] = usuario.rol
            flash(f"¡Bienvenido, {usuario.nombre}!", "success")
            return redirect(url_for("inicio"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html")
```

**Explicación detallada:**

- **`usuario and usuario.check_password(password)`** — Python evalúa esto de izquierda a derecha. Si `usuario` es `None` (no existe ese correo), Python ni siquiera intenta llamar a `.check_password()` — evita un error, porque `None` no tiene ese método.

- **`usuario.check_password(password)`** — compara la contraseña que el usuario escribió AHORA contra el hash guardado en la base de datos. Nunca se "desencripta" el hash — matemáticamente es imposible. Lo que se hace es aplicar el mismo proceso de hash a la contraseña nueva y comparar los resultados.

- **`session["usuario_id"] = usuario.id`** — esto es lo que técnicamente "inicia sesión". Flask guarda esta información en una cookie firmada digitalmente (usando tu `SECRET_KEY`) que el navegador va a enviar automáticamente en cada petición futura.

- **El mensaje de error genérico** — fíjate que decimos "Correo o contraseña incorrectos" sin importar cuál de los dos falló. Esto es intencional: si dijéramos específicamente "ese correo no existe", le estaríamos dando información útil a alguien que intenta adivinar qué cuentas son válidas en el sistema.

Crea `templates/login.html`:

```html
{% extends "base.html" %}

{% block titulo %}Iniciar Sesión{% endblock %}

{% block content %}
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h2 class="mb-4">Iniciar Sesión</h2>

                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Correo electrónico</label>
                            <input type="email" class="form-control" name="email" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Contraseña</label>
                            <input type="password" class="form-control" name="password" required>
                        </div>

                        <button type="submit" class="btn btn-primary w-100">Ingresar</button>
                    </form>

                    <p class="text-center mt-3 mb-0">
                        ¿No tienes cuenta?
                        <a href="{{ url_for('registro') }}">Regístrate</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

---

## 9. Logout

Agrega esta ruta — la más corta de toda la clase:

```python
@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("inicio"))
```

**`session.clear()`** — borra toda la información de la sesión actual (el `usuario_id`, `usuario_nombre`, `usuario_rol` que guardamos en el login). A partir de este punto, `session.get('usuario_id')` vuelve a ser `None`, y el navbar vuelve a mostrar "Iniciar sesión" / "Registrarse".

Esta ruta no necesita plantilla propia — solo redirige.

---

## 10. Ejecutar y probar

### Paso 1 — Reinicia la base de datos con datos frescos (opcional pero recomendado)

```bash
python init_db.py
```

### Paso 2 — Levanta el servidor

```bash
python app.py
```

### Paso 3 — Prueba el flujo completo en el navegador

1. Visita `http://127.0.0.1:5000` — sin sesión, debes ver "Iniciar sesión" y "Registrarse" en el navbar.
2. Haz clic en "Registrarse", crea una cuenta de prueba.
3. Inicia sesión con esa cuenta — el navbar debe mostrar tu nombre.
4. Debe aparecer el menú "+ Agregar producto".
5. Crea un producto de cualquier tipo — verifica que aparece en el catálogo con el precio correcto.
6. Entra al detalle de ese producto, haz clic en "Editar", cambia el precio, guarda.
7. Vuelve al detalle, haz clic en "Desactivar" — confirma, y verifica que el producto ya no aparece en el catálogo.
8. Cierra sesión — el menú de agregar productos debe desaparecer.

### Paso 4 — Verificar en PostgreSQL que las contraseñas están encriptadas

```bash
psql -U postgres -d tienda_online -c "SELECT email, password_hash FROM usuarios;"
```

Debes ver algo como `scrypt:32768:8:1$...` en la columna `password_hash` — nunca la contraseña en texto legible.

---

## 11. Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| `KeyError: 'codigo'` | El `name` del `<input>` no coincide con `request.form["codigo"]` | Revisa que el HTML tenga exactamente `name="codigo"`, sin errores de tipeo |
| El formulario no hace nada al enviar | Falta `method="POST"` en la etiqueta `<form>` | Verifica `<form method="POST">` |
| `sqlalchemy.exc.IntegrityError` al crear un producto | El código ya existe (columna `unique=True`) | Es el comportamiento esperado — debe mostrarse el mensaje de error, no un error de servidor. Revisa que el `try/except` esté bien colocado |
| La sesión no persiste al navegar entre páginas | Falta `SECRET_KEY` en la configuración | Verifica que `.env` tenga `SECRET_KEY` definida y que `config.py` la esté leyendo |
| El botón "+ Agregar producto" nunca aparece | La condición `session.get('usuario_id')` nunca es verdadera | Revisa que el login realmente haga `session["usuario_id"] = usuario.id` |
| `AttributeError: 'NoneType' object has no attribute 'check_password'` | Intentaste llamar a `check_password()` sin verificar antes que `usuario` no sea `None` | Usa `if usuario and usuario.check_password(...)`, en ese orden exacto |
| Los mensajes flash no se muestran | Falta el bloque `{% with mensajes = get_flashed_messages(...) %}` en `base.html` | Verifica que copiaste ese bloque completo en la plantilla base |
| El precio no se actualiza después de editar | Olvidaste `db.session.commit()` después de cambiar los atributos | El `commit()` es obligatorio siempre — sin él, los cambios solo existen en memoria |

---

## Checklist final — antes de la Semana 3

- [ ] Puedo registrarme con una cuenta nueva
- [ ] Puedo iniciar sesión y el navbar muestra mi nombre
- [ ] El menú "+ Agregar producto" aparece solo con sesión activa
- [ ] Puedo crear un producto de cada uno de los 3 tipos
- [ ] Puedo editar un producto y ver el cambio reflejado
- [ ] Puedo desactivar un producto y desaparece del catálogo
- [ ] Al cerrar sesión, el navbar vuelve a mostrar "Iniciar sesión" / "Registrarse"
- [ ] Verifiqué en PostgreSQL que las contraseñas están encriptadas, no en texto plano
- [ ] Entiendo por qué `rol="cliente"` está fijo en el código de registro y no viene del formulario
