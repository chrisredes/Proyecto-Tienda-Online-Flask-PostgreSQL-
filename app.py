from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash
)
from config import Config
from models import (
    db, Usuario, Categoria, CategoriaMercancia, FormaPago,
    Evento, EventoConcierto, EventoTeatro, EventoDeportivo,
    Mercancia,
    Carrito, CarritoItem, Compra, DetalleCompra,
)
from auth import login_requerido, rol_requerido

app = Flask(__name__)
app.config.from_object(Config)

# Conecta esta app con la instancia de SQLAlchemy definida en models.py
db.init_app(app)

# Mapa de tipos de evento a sus clases Python (polimorfismo)
CLASES_EVENTO = {
    "concierto": EventoConcierto,
    "teatro": EventoTeatro,
    "deportivo": EventoDeportivo,
}


# ===========================================================================
# CONTEXT PROCESSOR
# ===========================================================================
@app.context_processor
def inyectar_utilidades():
    """Hace disponibles variables globales sin repetirlas en cada vista."""
    es_admin_val = bool(session.get("es_admin", False) or session.get("usuario_rol") == "admin")
    return {
        "usuario_en_sesion": session.get("nombre_usuario"),
        "es_admin_sesion": es_admin_val,
        "es_admin": es_admin_val,
    }


# ===========================================================================
# AUTENTICACION: registro, login, logout
# ===========================================================================
@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Registra un nuevo usuario (rol cliente) y le crea su carrito vacío."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not nombre or not email or not password:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("registro"))

        if Usuario.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado.", "error")
            return redirect(url_for("registro"))

        nuevo_usuario = Usuario(nombre=nombre, email=email, rol="cliente")
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.flush()  # obtiene id_usuario antes del commit

        # Cada usuario nuevo recibe un carrito propio vacío
        db.session.add(Carrito(id_usuario=nuevo_usuario.id_usuario))
        db.session.commit()

        flash("Registro exitoso, ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Autentica usuario y establece variables de sesión."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario is None or not usuario.check_password(password):
            flash("Correo o contraseña incorrectos.", "error")
            return redirect(url_for("login"))

        session["id_usuario"] = usuario.id_usuario
        session["nombre_usuario"] = usuario.nombre
        session["usuario_rol"] = usuario.rol  # 'admin' o 'cliente'
        session["es_admin"] = usuario.es_admin()

        flash(f"Bienvenido, {usuario.nombre}.", "success")
        return redirect(url_for("listar_eventos"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Cierra la sesión del usuario."""
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("listar_eventos"))


# ===========================================================================
# EVENTOS
# ===========================================================================
@app.route("/")
@app.route("/eventos")
def listar_eventos():
    """Lista eventos activos con filtro opcional por categoría."""
    id_categoria = request.args.get("categoria", type=int)
    consulta = Evento.query.filter_by(activo=True)
    if id_categoria:
        consulta = consulta.filter_by(id_categoria=id_categoria)
    eventos = consulta.order_by(Evento.fecha_evento.asc()).all()
    categorias = Categoria.query.all()
    return render_template(
        'index.html', eventos=eventos, categorias=categorias,
        id_categoria=id_categoria
    )


@app.route("/eventos/<int:id_evento>")
def detalle_evento(id_evento):
    """Muestra el detalle de un evento específico."""
    evento = Evento.query.get_or_404(id_evento)
    return render_template("detalle_evento.html", evento=evento)


@app.route("/eventos/nuevo", methods=["GET", "POST"])
@rol_requerido("admin")
def nuevo_evento():
    """Crea un nuevo evento simple adaptado al formulario dedicado."""
    categorias = Categoria.query.all()
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre", "").strip()
            lugar = request.form.get("lugar", "").strip()
            fecha_str = request.form.get("fecha")
            precio = float(request.form.get("precio", 0))
            
            if not nombre or not lugar or not fecha_str or precio <= 0:
                flash("Por favor completa todos los campos con valores válidos.", "error")
                return redirect(url_for("nuevo_evento"))

            fecha_evento = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M")
            cat_defecto = categorias[0].id_categoria if categorias else 1

            nuevo = Evento(
                codigo=f"EVT-{int(datetime.now().timestamp())}",
                nombre=nombre,
                lugar=lugar,
                fecha_evento=fecha_evento,
                precio_base=precio,
                capacidad=100,
                id_categoria=cat_defecto
            )
            db.session.add(nuevo)
            db.session.commit()
            
            flash(f"¡Evento '{nuevo.nombre}' creado con éxito!", "success")
            return redirect(url_for("listar_eventos"))
            
        except ValueError:
            flash("Formato de fecha o precio inválido.", "error")
            return redirect(url_for("nuevo_evento"))
        except Exception as e:
            db.session.rollback()
            flash(f"Ocurrió un error al guardar el evento: {str(e)}", "error")
            return redirect(url_for("nuevo_evento"))

    return render_template("nuevo_evento.html", categorias=categorias)


@app.route("/eventos/crear_avanzado", methods=["GET", "POST"])
@rol_requerido("admin")
def crear_evento():
    """Crea un nuevo evento avanzado (solo administrador)."""
    categorias = Categoria.query.all()
    if request.method == "POST":
        tipo = request.form.get("tipo")
        ClaseEvento = CLASES_EVENTO.get(tipo)
        if ClaseEvento is None:
            flash("Tipo de evento inválido.", "error")
            return redirect(url_for("crear_evento"))

        try:
            evento = ClaseEvento(
                codigo=request.form["codigo"].strip(),
                nombre=request.form["nombre"].strip(),
                descripcion=request.form.get("descripcion", "").strip(),
                lugar=request.form["lugar"].strip(),
                fecha_evento=datetime.strptime(
                    request.form["fecha_evento"], "%Y-%m-%dT%H:%M"
                ),
                precio_base=float(request.form["precio_base"]),
                capacidad=int(request.form["capacidad"]),
                id_categoria=int(request.form["id_categoria"]),
            )

            if tipo == "concierto":
                evento.artista = request.form.get("artista", "").strip()
                evento.cargo_servicio_pct = float(
                    request.form.get("cargo_servicio_pct", 0.10)
                )
            elif tipo == "teatro":
                evento.elenco = request.form.get("elenco", "").strip()
                evento.es_matinee = bool(request.form.get("es_matinee"))
            elif tipo == "deportivo":
                evento.equipo_local = request.form.get("equipo_local", "").strip()
                evento.equipo_visitante = request.form.get(
                    "equipo_visitante", "").strip()
                evento.recargo_fijo = float(request.form.get("recargo_fijo", 2.50))

            db.session.add(evento)
            db.session.commit()
            flash(f"Evento '{evento.nombre}' creado correctamente.", "success")
            return redirect(url_for("listar_eventos"))

        except (ValueError, KeyError) as error:
            flash(f"Datos inválidos: {error}", "error")
            return redirect(url_for("crear_evento"))

    return render_template("form_evento.html", categorias=categorias, evento=None)


@app.route("/eventos/<int:id_evento>/editar", methods=["GET", "POST"])
@rol_requerido("admin")
def editar_evento(id_evento):
    """Edita un evento existente."""
    evento = Evento.query.get_or_404(id_evento)
    categorias = Categoria.query.all()

    if request.method == "POST":
        try:
            evento.nombre = request.form.get("nombre", request.form.get("titulo", "")).strip()
            evento.descripcion = request.form.get("descripcion", "").strip()
            evento.lugar = request.form.get("lugar", "").strip()
            
            if "fecha_evento" in request.form and request.form["fecha_evento"]:
                evento.fecha_evento = datetime.strptime(
                    request.form["fecha_evento"], "%Y-%m-%dT%H:%M"
                )
            
            evento.precio_base = float(request.form.get("precio_base", evento.precio_base))
            if "capacidad" in request.form:
                evento.capacidad = int(request.form["capacidad"])
            elif "aforo" in request.form:
                evento.capacidad = int(request.form["aforo"])
                
            if "id_categoria" in request.form:
                evento.id_categoria = int(request.form["id_categoria"])
            if "activo" in request.form:
                evento.activo = bool(request.form.get("activo"))

            db.session.commit()
            flash(f"Evento '{evento.nombre}' actualizado correctamente.", "success")
            return redirect(url_for("detalle_evento", id_evento=evento.id_evento))
        except Exception as error:
            db.session.rollback()
            flash(f"Error al actualizar el evento: {error}", "error")
            return redirect(url_for("editar_evento", id_evento=id_evento))

    return render_template("form_evento.html", categorias=categorias, evento=evento)


@app.route("/eventos/<int:id_evento>/eliminar", methods=["POST"])
@rol_requerido("admin")
def eliminar_evento(id_evento):
    """Eliminación lógica de evento."""
    evento = Evento.query.get_or_404(id_evento)
    evento.activo = False
    db.session.commit()
    flash(f"Evento '{evento.nombre}' eliminado (dado de baja).", "success")
    return redirect(url_for("listar_eventos"))


# ===========================================================================
# MERCANCIAS
# ===========================================================================
@app.route("/mercancias")
def listar_mercancias():
    """Lista mercancías activas con filtro opcional por categoría."""
    id_categoria = request.args.get("categoria", type=int)
    consulta = Mercancia.query.filter_by(activo=True)
    if id_categoria:
        consulta = consulta.filter_by(id_categoria_mercancia=id_categoria)
    mercancias = consulta.order_by(Mercancia.nombre.asc()).all()
    categorias = CategoriaMercancia.query.all()
    return render_template(
        "mercancias.html", mercancias=mercancias,
        categorias=categorias, id_categoria=id_categoria
    )


@app.route("/mercancias/<int:id_mercancia>")
def detalle_mercancia(id_mercancia):
    """Muestra el detalle de una mercancía específica."""
    mercancia = Mercancia.query.get_or_404(id_mercancia)
    return render_template("detalle_mercancia.html", mercancia=mercancia)


@app.route("/mercancia/nueva", methods=["GET", "POST"])
@rol_requerido("admin")
def nueva_mercancia():
    """Guarda mercancía registrada en la plantilla nuevo_mercancia.html."""
    categorias = CategoriaMercancia.query.all()
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            precio = float(request.form.get("precio", 0))
            stock = int(request.form.get("stock", 0))
            
            if not nombre or precio <= 0 or stock < 0:
                flash("Verifique los campos requeridos.", "error")
                return redirect(url_for("nueva_mercancia"))

            cat_defecto = categorias[0].id_categoria_mercancia if categorias else 1

            nueva = Mercancia(
                codigo=f"MER-{int(datetime.now().timestamp())}",
                nombre=nombre,
                descripcion=descripcion,
                precio_base=precio,
                stock=stock,
                id_categoria_mercancia=cat_defecto
            )
            db.session.add(nueva)
            db.session.commit()
            
            flash(f"¡Mercancía '{nueva.nombre}' creada con éxito!", "success")
            return redirect(url_for("listar_mercancias"))

        except ValueError:
            flash("El precio y stock deben ser numéricos.", "error")
            return redirect(url_for("nueva_mercancia"))
        except Exception as e:
            db.session.rollback()
            flash(f"Ocurrió un error: {str(e)}", "error")
            return redirect(url_for("nueva_mercancia"))
        
    return render_template("nuevo_mercancia.html", categorias=categorias)


@app.route("/mercancias/<int:id_mercancia>/editar", methods=["GET", "POST"])
@rol_requerido("admin")
def editar_mercancia(id_mercancia):
    """Edita los datos básicos de una mercancía existente."""
    mercancia = Mercancia.query.get_or_404(id_mercancia)
    categorias = CategoriaMercancia.query.all()

    if request.method == "POST":
        try:
            mercancia.nombre = request.form.get("nombre", "").strip()
            mercancia.descripcion = request.form.get("descripcion", "").strip()
            mercancia.precio_base = float(request.form.get("precio_base", 0))
            mercancia.stock = int(request.form.get("stock", 0))

            if "id_categoria_mercancia" in request.form:
                mercancia.id_categoria_mercancia = int(request.form["id_categoria_mercancia"])
            if "activo" in request.form:
                mercancia.activo = bool(request.form.get("activo"))

            db.session.commit()
            flash(f"Mercancía '{mercancia.nombre}' actualizada correctamente.", "success")
            return redirect(url_for("detalle_mercancia", id_mercancia=mercancia.id_mercancia))

        except (ValueError, KeyError):
            db.session.rollback()
            flash("Revisa los campos numéricos.", "error")
            return redirect(url_for("editar_mercancia", id_mercancia=id_mercancia))

    return render_template("editar_mercancia.html", mercancia=mercancia, categorias=categorias)


@app.route("/mercancias/<int:id_mercancia>/eliminar", methods=["POST"])
@rol_requerido("admin")
def eliminar_mercancia(id_mercancia):
    """Eliminación lógica de mercancía."""
    mercancia = Mercancia.query.get_or_404(id_mercancia)
    mercancia.activo = False
    db.session.commit()
    flash(f"Mercancía '{mercancia.nombre}' eliminada.", "success")
    return redirect(url_for("listar_mercancias"))


# ===========================================================================
# CARRITO DE COMPRAS
# ===========================================================================
@app.route("/carrito/agregar/<int:id_evento>", methods=["POST"])
@login_requerido
def agregar_carrito(id_evento):
    """Agrega un evento (o producto) al carrito basado en sesión."""
    evento = Evento.query.get_or_404(id_evento)

    carrito = session.get("carrito", {})
    clave = str(id_evento)
    carrito[clave] = carrito.get(clave, 0) + 1
    session["carrito"] = carrito

    flash(f"'{evento.nombre}' agregado al carrito.", "success")
    return redirect(request.referrer or url_for("listar_eventos"))


@app.route("/carrito")
@login_requerido
def ver_carrito():
    """Muestra el contenido actual del carrito del usuario."""
    carrito = session.get("carrito", {})
    items = []
    total = 0.0

    for clave, cantidad in carrito.items():
        evento = Evento.query.get(int(clave))
        if evento:
            subtotal = evento.precio_base * cantidad
            total += subtotal
            items.append({"producto": evento, "cantidad": cantidad, "subtotal": subtotal})

    return render_template("carrito.html", items=items, total=total)


@app.route("/carrito/eliminar/<int:id_evento>", methods=["POST"])
@login_requerido
def eliminar_carrito(id_evento):
    """Quita un elemento del carrito de compras."""
    carrito = session.get("carrito", {})
    clave = str(id_evento)

    if clave in carrito:
        del carrito[clave]
        session["carrito"] = carrito
        flash("Elemento quitado del carrito.", "success")

    return redirect(url_for("ver_carrito"))


if __name__ == "__main__":
    app.run(debug=True)