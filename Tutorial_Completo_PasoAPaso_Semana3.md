# Tutorial Completo Paso a Paso — Semana 3: Roles, Permisos y Carrito
### Desde el proyecto de la Semana 2 hasta control de acceso y carrito funcionando

**Punto de partida:** ya tienes el proyecto de la Semana 2 corriendo — CRUD completo de productos y sistema de login con contraseñas encriptadas. Este documento asume eso exactamente.

---

## Índice

1. [Verificar que la Semana 2 sigue funcionando](#1-verificar-la-semana-2)
2. [Ver el problema con tus propios ojos](#2-ver-el-problema)
3. [Crear el módulo auth.py](#3-crear-el-módulo-authpy)
4. [El decorador login_requerido](#4-el-decorador-login_requerido)
5. [El decorador rol_requerido](#5-el-decorador-rol_requerido)
6. [Proteger las rutas de gestión de productos](#6-proteger-las-rutas)
7. [Actualizar el navbar según el rol](#7-actualizar-el-navbar)
8. [Construir el carrito de compras](#8-construir-el-carrito)
9. [Ejecutar y probar todo el flujo](#9-ejecutar-y-probar)
10. [Solución de problemas](#10-solución-de-problemas)

---

## 1. Verificar la Semana 2

```bash
cd tienda_online
source venv/bin/activate      # Windows: venv\Scripts\activate
python app.py
```

Confirma que puedes registrarte, iniciar sesión, y crear/editar/desactivar productos. Si algo de esto no funciona, resuélvelo antes de continuar (revisa el tutorial de la Semana 2).

Detén el servidor con `Ctrl + C`.

---

## 2. Ver el problema

Antes de escribir la solución, vamos a confirmar que existe un problema real. Con el servidor corriendo (`python app.py`), abre una terminal **nueva** (deja la del servidor corriendo) y ejecuta:

```bash
curl -X POST http://127.0.0.1:5000/productos/nuevo/fisico \
  -d "codigo=HACK001" \
  -d "nombre=Producto Sin Login" \
  -d "precio_base=10.00" \
  -d "stock=5" \
  -d "peso_kg=1" \
  -d "costo_envio_por_kg=1"
```

Ahora recarga `http://127.0.0.1:5000` en tu navegador — **sin haber iniciado sesión en ningún lado**, deberías ver "Producto Sin Login" en el catálogo.

**Esto confirma el problema:** aunque el botón "+ Agregar producto" solo aparece cuando hay sesión iniciada, la URL sigue existiendo y sigue aceptando peticiones de cualquiera. Esconder un botón en el HTML no es seguridad — es solo una decisión de interfaz.

Elimina ese producto de prueba antes de continuar (opcional, pero mantiene tu base de datos limpia):

```bash
psql -U postgres -d tienda_online -c "DELETE FROM productos WHERE codigo = 'HACK001';"
```

---

## 3. Crear el módulo auth.py

Vamos a crear un archivo nuevo, separado de `app.py`, para los decoradores de seguridad. Esto conecta directamente con lo que aprendiste en la clase de Módulos: código relacionado va junto, en su propio archivo.

Crea `auth.py` dentro de `tienda_online/`:

```python
"""
auth.py
───────
Decoradores de autenticación y autorización.
"""

from functools import wraps
from flask import session, redirect, url_for, flash
```

Por ahora solo los imports — vamos a construir el contenido paso a paso en las siguientes secciones.

---

## 4. El decorador login_requerido

Agrega esto a `auth.py`:

```python
def login_requerido(f):
    """
    Decorador que exige una sesión activa (sin importar el rol).
    """
    @wraps(f)
    def decorada(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para acceder a esa página.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorada
```

**Explicación línea por línea — este es el concepto más importante de la clase:**

- **`def login_requerido(f):`** — recibe una función `f`. Esa `f` es la ruta que queremos proteger (por ejemplo, `ver_carrito`).

- **`@wraps(f)`** — esto preserva el nombre y la documentación original de `f` dentro de la función `decorada`. Sin esto, Flask puede confundirse con nombres de funciones internas cuando registra varias rutas decoradas.

- **`def decorada(*args, **kwargs):`** — esta es la función que REALMENTE se ejecuta cuando alguien visita la ruta protegida. `*args, **kwargs` acepta cualquier cantidad de argumentos — necesario porque no todas las rutas reciben los mismos parámetros.

- **`if "usuario_id" not in session:`** — verifica si hay una sesión activa. Recuerda que `session["usuario_id"]` se estableció en el login de la Semana 2.

- **`return f(*args, **kwargs)`** — si sí hay sesión, ejecuta la función ORIGINAL (la ruta real), pasándole los mismos argumentos que recibió `decorada`.

- **`return decorada`** — el decorador retorna la nueva función. Esta es la pieza que Python realmente usa cuando escribes `@login_requerido` encima de una ruta.

**Cómo se usa (todavía no lo apliques en ningún lado, solo para entender la sintaxis):**

```python
@app.route("/carrito")
@login_requerido
def ver_carrito():
    ...
```

Cuando Flask recibe una petición a `/carrito`, en realidad ejecuta `decorada()`, NO `ver_carrito()` directamente. `decorada()` decide si deja pasar hacia `ver_carrito()` o no.

---

## 5. El decorador rol_requerido

`login_requerido` verifica que haya sesión, pero no distingue QUÉ rol tiene esa sesión. Agrega esto a `auth.py`, después de `login_requerido`:

```python
def rol_requerido(rol):
    """
    Fábrica de decoradores: retorna un decorador que exige un rol
    específico. Se usa así: @rol_requerido("admin")
    """
    def decorador(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            if "usuario_id" not in session:
                flash("Debes iniciar sesión para acceder a esa página.", "danger")
                return redirect(url_for("login"))
            if session.get("usuario_rol") != rol:
                flash("No tienes permisos para acceder a esa página.", "danger")
                return redirect(url_for("inicio"))
            return f(*args, **kwargs)
        return decorada
    return decorador
```

**Esta es la parte conceptualmente más difícil de todo el proyecto — tómate tu tiempo con esta sección.**

`login_requerido` tenía UN nivel de función. `rol_requerido` tiene TRES niveles, porque necesita "recordar" el argumento `"admin"` que le pasas:

```
rol_requerido("admin")
    ↓ retorna
decorador          (esta función recuerda que rol="admin" gracias a que "rol" quedó
                     capturado del nivel de afuera — esto se llama "closure" en Python)
    ↓ se aplica sobre f (la ruta que queremos proteger)
decorada           (la función que se ejecuta de verdad en cada petición)
```

**Sigue la cadena de llamadas paso a paso:**

1. Escribes `@rol_requerido("admin")` encima de una ruta.
2. Python ejecuta `rol_requerido("admin")` inmediatamente. Esto retorna la función `decorador`.
3. Ese `decorador` se aplica automáticamente sobre la función de la ruta (`f`), retornando `decorada`.
4. Cada vez que alguien visita esa URL, se ejecuta `decorada`, que compara `session.get("usuario_rol")` contra el `rol` que quedó guardado desde el paso 2.

**Por qué el orden de los `if` importa:**

Primero se verifica si hay sesión. Solo si eso pasa, se verifica el rol. Si invirtiéramos el orden, alguien sin sesión recibiría un mensaje confuso ("no tienes permisos" en vez de "debes iniciar sesión"), porque `session.get("usuario_rol")` retornaría `None`, y `None != "admin"` también es verdadero.

---

## 6. Proteger las rutas de gestión de productos

Abre `app.py`.

### 6.1 — Importa los decoradores

Al inicio de `app.py`, agrega:

```python
from auth import login_requerido, rol_requerido
```

### 6.2 — Protege las 3 rutas de crear productos

Agrega `@rol_requerido("admin")` **entre** `@app.route(...)` y `def`:

```python
@app.route("/productos/nuevo/fisico", methods=["GET", "POST"])
@rol_requerido("admin")
def nuevo_producto_fisico():
    # ... el resto del código queda exactamente igual
```

Repite lo mismo para `nuevo_producto_digital` y `nuevo_producto_perecible`.

**El orden de los decoradores importa:** `@app.route` siempre va primero (más "afuera"), y `@rol_requerido` va después (más cerca de la función).

### 6.3 — Protege editar y eliminar

```python
@app.route("/productos/<int:producto_id>/editar", methods=["GET", "POST"])
@rol_requerido("admin")
def editar_producto(producto_id):
    # ... sin cambios en el resto

@app.route("/productos/<int:producto_id>/eliminar", methods=["POST"])
@rol_requerido("admin")
def eliminar_producto(producto_id):
    # ... sin cambios en el resto
```

### 6.4 — Verifica que la vulnerabilidad quedó cerrada

Reinicia el servidor y repite la prueba de la sección 2:

```bash
curl -X POST http://127.0.0.1:5000/productos/nuevo/fisico \
  -d "codigo=HACK002" -d "nombre=Otro Intento" \
  -d "precio_base=10" -d "stock=5" -d "peso_kg=1" -d "costo_envio_por_kg=1"
```

Recarga el catálogo — **esta vez el producto NO debe aparecer.**

---

## 7. Actualizar el navbar

Modifica `templates/base.html`. Busca el bloque del menú "+ Agregar producto" y reemplázalo por:

```html
{% if session.get('usuario_rol') == 'admin' %}
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
        ⚙️ Panel Admin
    </a>
    <ul class="dropdown-menu">
        <li><a class="dropdown-item" href="{{ url_for('nuevo_producto_fisico') }}">+ Producto Físico</a></li>
        <li><a class="dropdown-item" href="{{ url_for('nuevo_producto_digital') }}">+ Producto Digital</a></li>
        <li><a class="dropdown-item" href="{{ url_for('nuevo_producto_perecible') }}">+ Producto Perecible</a></li>
    </ul>
</li>
{% endif %}
```

**El cambio clave:** antes comprobábamos `session.get('usuario_id')` (cualquier sesión). Ahora comprobamos específicamente `session.get('usuario_rol') == 'admin'`.

También agrega el link al carrito (solo para clientes):

```html
{% if session.get('usuario_rol') == 'cliente' %}
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('ver_carrito') }}">🛍️ Mi carrito</a>
</li>
{% endif %}
```

---

## 8. Construir el carrito de compras

### 8.1 — Ruta para agregar productos al carrito

Agrega a `app.py`:

```python
@app.route("/carrito/agregar/<int:producto_id>", methods=["POST"])
@login_requerido
def agregar_carrito(producto_id):
    producto = Producto.query.get_or_404(producto_id)

    carrito = session.get("carrito", {})
    clave = str(producto_id)
    carrito[clave] = carrito.get(clave, 0) + 1
    session["carrito"] = carrito

    flash(f"'{producto.nombre}' agregado al carrito.", "success")
    return redirect(request.referrer or url_for("inicio"))
```

**Explicación detallada:**

- **`@login_requerido`** (no `@rol_requerido("admin")`) — cualquier usuario CON sesión puede usar el carrito, sin importar el rol.

- **`session.get("carrito", {})`** — recupera el carrito actual de la sesión. Si todavía no existe, usa un diccionario vacío `{}` por defecto.

- **`clave = str(producto_id)`** — convertimos el ID a texto porque `session` se serializa a JSON internamente, y JSON no permite claves numéricas en los objetos.

- **`carrito.get(clave, 0) + 1`** — si el producto ya estaba, le suma 1. Si no, `get(clave, 0)` retorna `0`, y el resultado es `1`.

- **`session["carrito"] = carrito`** — **obligatorio, no opcional.** Flask solo detecta automáticamente que la sesión cambió cuando le asignas directamente una clave. Si solo modificas el diccionario interno sin reasignar, el cambio puede no guardarse.

- **`request.referrer`** — la URL desde la que vino la petición. Permite regresar al usuario a donde estaba (catálogo o detalle).

### 8.2 — Ruta para ver el carrito

```python
@app.route("/carrito")
@login_requerido
def ver_carrito():
    carrito = session.get("carrito", {})
    items = []
    total = 0.0

    for clave, cantidad in carrito.items():
        producto = Producto.query.get(int(clave))
        if producto:
            subtotal = producto.precio_final() * cantidad
            total += subtotal
            items.append({"producto": producto, "cantidad": cantidad, "subtotal": subtotal})

    return render_template("carrito.html", items=items, total=total)
```

**Explicación detallada:**

- **`Producto.query.get(int(clave))`** — a diferencia de `get_or_404()`, retorna `None` si el producto no existe, en vez de lanzar un error. Correcto aquí porque un producto pudo haber sido desactivado después de que el cliente lo agregó al carrito.

- **`if producto:`** — si ya no existe, lo saltamos silenciosamente.

- **`producto.precio_final() * cantidad`** — el polimorfismo de la Semana 1 vuelve a aparecer: no importa el tipo real del producto, `precio_final()` calcula correctamente.

### 8.3 — Ruta para eliminar del carrito

```python
@app.route("/carrito/eliminar/<int:producto_id>", methods=["POST"])
@login_requerido
def eliminar_carrito(producto_id):
    carrito = session.get("carrito", {})
    clave = str(producto_id)

    if clave in carrito:
        del carrito[clave]
        session["carrito"] = carrito
        flash("Producto quitado del carrito.", "success")

    return redirect(url_for("ver_carrito"))
```

### 8.4 — La plantilla del carrito

Crea `templates/carrito.html`:

```html
{% extends "base.html" %}

{% block titulo %}Mi Carrito{% endblock %}

{% block content %}
    <a href="{{ url_for('inicio') }}" class="btn btn-outline-secondary mb-3">← Seguir comprando</a>

    <h1 class="mb-4">🛍️ Mi Carrito</h1>

    {% if items %}
        <table class="table">
            <thead>
                <tr>
                    <th>Producto</th>
                    <th>Precio unitario</th>
                    <th>Cantidad</th>
                    <th>Subtotal</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td>
                        {{ item.producto.nombre }}
                        <span class="badge bg-secondary">{{ item.producto.tipo }}</span>
                    </td>
                    <td>${{ "%.2f"|format(item.producto.precio_final()) }}</td>
                    <td>{{ item.cantidad }}</td>
                    <td class="fw-bold">${{ "%.2f"|format(item.subtotal) }}</td>
                    <td>
                        <form action="{{ url_for('eliminar_carrito', producto_id=item.producto.id) }}" method="POST">
                            <button type="submit" class="btn btn-sm btn-outline-danger">Quitar</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="d-flex justify-content-end">
            <div class="card" style="width: 20rem;">
                <div class="card-body">
                    <h4 class="d-flex justify-content-between">
                        <span>Total:</span>
                        <span>${{ "%.2f"|format(total) }}</span>
                    </h4>
                </div>
            </div>
        </div>
    {% else %}
        <p class="text-muted">Tu carrito está vacío. Ve al catálogo y agrega algún producto.</p>
    {% endif %}
{% endblock %}
```

### 8.5 — Agrega el botón "Agregar al carrito"

En `templates/index.html`, dentro de la tarjeta de cada producto:

```html
{% if session.get('usuario_rol') == 'cliente' %}
<form action="{{ url_for('agregar_carrito', producto_id=producto.id) }}" method="POST">
    <button type="submit" class="btn btn-primary">🛍️</button>
</form>
{% endif %}
```

Y en `templates/detalle.html`, después de la información del producto:

```html
{% if session.get('usuario_rol') == 'cliente' %}
<form action="{{ url_for('agregar_carrito', producto_id=producto.id) }}" method="POST">
    <button type="submit" class="btn btn-primary">🛍️ Agregar al carrito</button>
</form>
{% endif %}
```

**Nota:** en `detalle.html`, cambia también la condición de "Editar" y "Desactivar" de `session.get('usuario_id')` a `session.get('usuario_rol') == 'admin'`.

---

## 9. Ejecutar y probar

### Paso 1 — Reinicia el servidor

```bash
python app.py
```

### Paso 2 — Prueba como visitante sin sesión

Visita el catálogo — no debes ver "Panel Admin" ni "Mi carrito".

### Paso 3 — Prueba como cliente

1. Inicia sesión con `cliente@tienda.com` / `cliente123`
2. Confirma que ves "🛍️ Mi carrito", pero NO "⚙️ Panel Admin"
3. Agrega 2-3 productos al carrito
4. Visita "Mi carrito" — verifica cantidades y total
5. Intenta visitar directamente `/productos/nuevo/fisico` — debes ser redirigido con "No tienes permisos"

### Paso 4 — Prueba como administrador

1. Cierra sesión, inicia con `admin@tienda.com` / `admin123`
2. Confirma que ves "⚙️ Panel Admin", pero NO "🛍️ Mi carrito"
3. Crea, edita y desactiva un producto normalmente

### Paso 5 — Verificación final de seguridad

Sin sesión, repite la prueba con `curl` de la sección 2 — debe fallar correctamente.

---

## 10. Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| La ruta sigue sin protegerse pese al decorador | El decorador está antes de `@app.route`, o falta el paréntesis en `@rol_requerido("admin")` | El orden correcto es `@app.route` primero, `@rol_requerido(...)` después |
| `NameError: name 'login_requerido' is not defined` | Falta el import en `app.py` | Verifica `from auth import login_requerido, rol_requerido` |
| El carrito se vacía al recargar la página | Falta `session["carrito"] = carrito` después de modificar el diccionario | Revisa que esa línea esté presente en las 3 rutas del carrito |
| Error al acceder al carrito si un producto fue desactivado | No se está verificando `if producto:` antes de usarlo | Revisa el `for` en `ver_carrito()` |
| El cliente ve el "Panel Admin" | La condición del navbar compara `usuario_id` en vez de `usuario_rol == 'admin'` | Revisa el bloque `{% if %}` en `base.html` |
| El admin ve el botón de carrito | Falta la condición específica `usuario_rol == 'cliente'` en las plantillas | Revisa `index.html`, `detalle.html` y `base.html` |
| Mensaje de error confuso | El orden de los `if` dentro de `rol_requerido` está invertido | Verifica sesión primero, rol después |

---

## Checklist final — proyecto completo (3 semanas)

- [ ] Sin sesión, no se puede crear/editar/desactivar productos ni por la interfaz ni por URL directa
- [ ] Un cliente logueado tampoco puede gestionar productos
- [ ] Un admin logueado sí puede gestionar productos normalmente
- [ ] El navbar muestra "Panel Admin" solo a administradores
- [ ] El navbar muestra "Mi carrito" solo a clientes
- [ ] El carrito acumula cantidades correctamente
- [ ] El total del carrito se calcula usando `precio_final()` (polimorfismo funcionando)
- [ ] Se puede quitar un producto del carrito
- [ ] Entiendo la diferencia entre `login_requerido` y `rol_requerido("admin")`
- [ ] Entiendo por qué `session["carrito"] = carrito` es obligatorio después de modificar el diccionario
