"""
models.py
=========

"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------------------------
# Instancia unica de SQLAlchemy (se vincula con la app en app.py)
# ---------------------------------------------------------------------------
db = SQLAlchemy()


# ===========================================================================
# 1. USUARIO
# ===========================================================================
class Usuario(db.Model):
    """Representa un usuario de la plataforma (cliente o administrador)."""
    __tablename__ = "usuarios"
    __table_args__ = (
        db.CheckConstraint("rol IN ('cliente', 'admin')", name="ck_usuario_rol_valido"),
    )

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="cliente")
    fecha_registro = db.Column(db.DateTime, default=datetime.now)

    # Relaciones
    carrito = db.relationship("Carrito", backref="usuario", uselist=False)
    compras = db.relationship("Compra", backref="usuario", lazy=True)

    # --- no ---
    def set_password(self, password: str) -> None:
        """Genera y almacena el hash seguro de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica una contraseña comparando contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def es_admin(self) -> bool:
        """Indica si el usuario tiene rol de administrador."""
        return self.rol == "admin"

    def __repr__(self) -> str:
        return f"<Usuario {self.nombre}>"


# ===========================================================================
# 2. CATEGORIAS (Eventos)
# ===========================================================================
class Categoria(db.Model):
    """Categoría para clasificar eventos (concierto, teatro, deportivo)."""
    __tablename__ = "categorias"

    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre_categoria = db.Column(db.String(50), nullable=False, unique=True)
    eventos = db.relationship("Evento", backref="categoria", lazy=True)

    def __repr__(self) -> str:
        return f"<Categoria {self.nombre_categoria}>"


# ===========================================================================
# 3. CATEGORIAS DE MERCANCIA
# ===========================================================================
class CategoriaMercancia(db.Model):
    """Categoría para clasificar mercancía (ropa, coleccionables, accesorios)."""
    __tablename__ = "categorias_mercancia"

    id_categoria_mercancia = db.Column(db.Integer, primary_key=True)
    nombre_categoria = db.Column(db.String(50), nullable=False, unique=True)
    mercancias = db.relationship("Mercancia", backref="categoria", lazy=True)

    def __repr__(self) -> str:
        return f"<CategoriaMercancia {self.nombre_categoria}>"


# ===========================================================================
# 4. EVENTO 
# ===========================================================================
class Evento(db.Model):
    """Evento base. Las subclases sobreescriben precio_final() via polimorfismo."""
    __tablename__ = "eventos"
    __table_args__ = (
        db.CheckConstraint("precio_base > 0", name="ck_evento_precio_positivo"),
        db.CheckConstraint("capacidad > 0", name="ck_evento_capacidad_positiva"),
        db.CheckConstraint("entradas_vendidas >= 0", name="ck_evento_entradas_no_negativas"),
        db.CheckConstraint(
            "entradas_vendidas <= capacidad",
            name="ck_evento_entradas_no_exceden_capacidad"
        ),
        db.CheckConstraint(
            "cargo_servicio_pct IS NULL OR (cargo_servicio_pct >= 0 AND cargo_servicio_pct <= 1)",
            name="ck_evento_cargo_servicio_valido",
        ),
        db.CheckConstraint(
            "recargo_fijo IS NULL OR recargo_fijo >= 0",
            name="ck_evento_recargo_no_negativo"
        ),
    )

    CARGO_SERVICIO_BASE = 0.0

    id_evento = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    lugar = db.Column(db.String(100), nullable=False)
    fecha_evento = db.Column(db.DateTime, nullable=False, index=True)
    precio_base = db.Column(db.Numeric(10, 2), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Encapsulamiento: entradas vendidas solo se modifica via metodos
    _entradas_vendidas = db.Column("entradas_vendidas", db.Integer, default=0, nullable=False)

    id_categoria = db.Column(
        db.Integer, db.ForeignKey("categorias.id_categoria"), nullable=False, index=True
    )

    # Columnas especificas de subclases (nullable porque no todas aplican)
    artista = db.Column(db.String(100), nullable=True)          # Concierto
    cargo_servicio_pct = db.Column(db.Numeric(4, 2), nullable=True)  # Concierto
    elenco = db.Column(db.String(150), nullable=True)           # Teatro
    es_matinee = db.Column(db.Boolean, nullable=True)           # Teatro
    equipo_local = db.Column(db.String(100), nullable=True)     # Deportivo
    equipo_visitante = db.Column(db.String(100), nullable=True) # Deportivo
    recargo_fijo = db.Column(db.Numeric(6, 2), nullable=True)   # Deportivo

    # 
    tipo = db.Column(db.String(30))
    __mapper_args__ = {
        "polymorphic_identity": "evento",
        "polymorphic_on": tipo,
    }

    # Relaciones
    items_carrito = db.relationship("CarritoItem", backref="evento", lazy=True)
    detalles_compra = db.relationship("DetalleCompra", backref="evento", lazy=True)

    # --- Property: entradas disponibles (calculado) ---
    @property
    def entradas_disponibles(self) -> int:
        return self.capacidad - self._entradas_vendidas

    @entradas_disponibles.setter
    def entradas_disponibles(self, valor: int) -> None:
        if valor < 0 or valor > self.capacidad:
            raise ValueError("Cantidad de entradas disponibles fuera de rango.")
        self._entradas_vendidas = self.capacidad - valor

    def hay_disponibilidad(self, cantidad: int) -> bool:
        """Verifica si existen suficientes entradas para vender."""
        return cantidad > 0 and cantidad <= self.entradas_disponibles

    def vender_entradas(self, cantidad: int) -> None:
        """Descuenta entradas del cupo disponible. Lanza error si no alcanza."""
        if not self.hay_disponibilidad(cantidad):
            raise ValueError(
                f"No hay suficientes entradas disponibles para '{self.nombre}'."
            )
        self._entradas_vendidas += cantidad

    def liberar_entradas(self, cantidad: int) -> None:
        """Devuelve entradas al cupo disponible (ej. al cancelar compra)."""
        self._entradas_vendidas = max(0, self._entradas_vendidas - cantidad)

    # --- Polimorfismo: precio final ---
    def precio_final(self) -> float:
        return float(self.precio_base)

    def ficha(self) -> str:
        return (
            f"[{self.tipo}] {self.nombre} | Lugar: {self.lugar} | "
            f"Fecha: {self.fecha_evento:%d/%m/%Y %H:%M} | "
            f"Precio: ${self.precio_final():.2f} | "
            f"Disponibles: {self.entradas_disponibles}/{self.capacidad}"
        )

    def __repr__(self) -> str:
        return f"<Evento {self.nombre}>"


class EventoConcierto(Evento):
    """Evento concierto: precio final incluye cargo de servicio."""
    __mapper_args__ = {"polymorphic_identity": "concierto"}

    def precio_final(self) -> float:
        cargo = float(self.cargo_servicio_pct or 0.10)
        return float(self.precio_base) * (1 + cargo)


class EventoTeatro(Evento):
    """Evento teatro: funciones matinee tienen descuento del 15%."""
    __mapper_args__ = {"polymorphic_identity": "teatro"}

    def precio_final(self) -> float:
        if self.es_matinee:
            return float(self.precio_base) * 0.85
        return float(self.precio_base)


class EventoDeportivo(Evento):
    """Evento deportivo: precio final suma recargo fijo."""
    __mapper_args__ = {"polymorphic_identity": "deportivo"}

    def precio_final(self) -> float:
        recargo = float(self.recargo_fijo or 2.50)
        return float(self.precio_base) + recargo


# ===========================================================================
# 5. MERCANCIA
# ===========================================================================
class Mercancia(db.Model):
    """Producto fisico disponible para compra (ropa, coleccionables, accesorios)."""
    __tablename__ = "mercancias"
    __table_args__ = (
        db.CheckConstraint("precio_base > 0", name="ck_mercancia_precio_positivo"),
        db.CheckConstraint("stock >= 0", name="ck_mercancia_stock_no_negativo"),
    )

    id_mercancia = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio_base = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True)
    imagen_url = db.Column(db.String(255), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)

    id_categoria_mercancia = db.Column(
        db.Integer,
        db.ForeignKey("categorias_mercancia.id_categoria_mercancia"),
        nullable=False,
        index=True,
    )

    # Relaciones
    items_carrito = db.relationship("CarritoItem", backref="mercancia", lazy=True)
    detalles_compra = db.relationship("DetalleCompra", backref="mercancia", lazy=True)

    def hay_stock(self, cantidad: int) -> bool:
        """Verifica si existe stock suficiente."""
        return cantidad > 0 and cantidad <= self.stock

    def descontar_stock(self, cantidad: int) -> None:
        """Descuenta unidades del stock. Lanza error si no alcanza."""
        if not self.hay_stock(cantidad):
            raise ValueError(f"Stock insuficiente para '{self.nombre}'. Disponible: {self.stock}")
        self.stock -= cantidad

    def reponer_stock(self, cantidad: int) -> None:
        """Reintegra unidades al stock (ej. cancelacion de compra)."""
        self.stock += cantidad

    def precio_final(self) -> float:
        """Precio de venta de la mercancia (sin recargos adicionales por defecto)."""
        return float(self.precio_base)

    def ficha(self) -> str:
        return (
            f"[MER] {self.nombre} | Precio: ${self.precio_final():.2f} | "
            f"Stock: {self.stock} | Categoria: {self.categoria.nombre_categoria}"
        )

    def __repr__(self) -> str:
        return f"<Mercancia {self.nombre}>"


# ===========================================================================
# 6. FORMA DE PAGO
# ===========================================================================
class FormaPago(db.Model):
    """Metodos de pago disponibles para el checkout."""
    __tablename__ = "formas_pago"

    id_pago = db.Column(db.Integer, primary_key=True)
    nombre_pago = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<FormaPago {self.nombre_pago}>"


# ===========================================================================
# 7. CARRITO + ITEMS 
# ===========================================================================
class Carrito(db.Model):
    """Carrito persistente vinculado 1:1 con cada usuario."""
    __tablename__ = "carritos"

    id_carrito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuarios.id_usuario"), unique=True, nullable=False, index=True
    )
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)

    items = db.relationship(
        "CarritoItem", backref="carrito", lazy=True, cascade="all, delete-orphan"
    )

    def total(self) -> float:
        """Suma el subtotal de cada item (evento o mercancia)."""
        return sum(item.subtotal() for item in self.items)

    def cantidad_items(self) -> int:
        return sum(item.cantidad for item in self.items)

    def vaciar(self) -> None:
        """Elimina todos los items del carrito (tras confirmar compra)."""
        self.items.clear()

    def __repr__(self) -> str:
        return f"<Carrito de usuario {self.id_usuario}>"


class CarritoItem(db.Model):
    """
    Item dentro de un carrito.
    Puede referenciar un Evento O una Mercancia (XOR via CHECK constraint).
    """
    __tablename__ = "carrito_items"
    __table_args__ = (
        db.CheckConstraint("cantidad > 0", name="ck_carrito_item_cantidad_positiva"),
        db.CheckConstraint(
            "(id_evento IS NOT NULL AND id_mercancia IS NULL) OR "
            "(id_evento IS NULL AND id_mercancia IS NOT NULL)",
            name="ck_carrito_item_tipo_unico",
        ),
        db.UniqueConstraint("id_carrito", "id_evento", name="uq_carrito_item_evento"),
        db.UniqueConstraint("id_carrito", "id_mercancia", name="uq_carrito_item_mercancia"),
    )

    id_item = db.Column(db.Integer, primary_key=True)
    id_carrito = db.Column(
        db.Integer, db.ForeignKey("carritos.id_carrito"), nullable=False, index=True
    )
    id_evento = db.Column(
        db.Integer, db.ForeignKey("eventos.id_evento"), nullable=True, index=True
    )
    id_mercancia = db.Column(
        db.Integer, db.ForeignKey("mercancias.id_mercancia"), nullable=True, index=True
    )
    cantidad = db.Column(db.Integer, nullable=False, default=1)

    def subtotal(self) -> float:
        """Calcula subtotal segun el tipo de item (evento o mercancia)."""
        if self.id_evento is not None and self.evento is not None:
            return self.evento.precio_final() * self.cantidad
        elif self.id_mercancia is not None and self.mercancia is not None:
            return self.mercancia.precio_final() * self.cantidad
        return 0.0

    def nombre_item(self) -> str:
        """Devuelve el nombre descriptivo del item."""
        if self.id_evento is not None and self.evento is not None:
            return self.evento.nombre
        elif self.id_mercancia is not None and self.mercancia is not None:
            return self.mercancia.nombre
        return "Item desconocido"

    def tipo_item(self) -> str:
        """Devuelve 'evento' o 'mercancia'."""
        if self.id_evento is not None:
            return "evento"
        return "mercancia"

    def __repr__(self) -> str:
        return f"<CarritoItem {self.nombre_item()} cantidad={self.cantidad}>"


# ===========================================================================
# 8. COMPRA + DETALLE
# ===========================================================================
class Compra(db.Model):
    """Orden de compra generada durante el checkout."""
    __tablename__ = "compras"
    __table_args__ = (
        db.CheckConstraint("total >= 0", name="ck_compra_total_no_negativo"),
        db.CheckConstraint(
            "estado IN ('pendiente', 'pagada', 'cancelada')",
            name="ck_compra_estado_valido"
        ),
    )

    id_compra = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False, index=True
    )
    id_pago = db.Column(db.Integer, db.ForeignKey("formas_pago.id_pago"), nullable=False)
    fecha_compra = db.Column(db.DateTime, default=datetime.now, index=True)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")

    forma_pago = db.relationship("FormaPago")
    detalles = db.relationship(
        "DetalleCompra", backref="compra", lazy=True, cascade="all, delete-orphan"
    )

    def calcular_total(self) -> float:
        """Recalcula el total en base a los detalles de la compra."""
        self.total = sum(d.subtotal() for d in self.detalles)
        return self.total

    def confirmar_pago(self) -> None:
        self.estado = "pagada"

    def cancelar(self) -> None:
        """Cancela la compra y devuelve entradas/stock de cada item."""
        for detalle in self.detalles:
            if detalle.id_evento is not None and detalle.evento is not None:
                detalle.evento.liberar_entradas(detalle.cantidad)
            elif detalle.id_mercancia is not None and detalle.mercancia is not None:
                detalle.mercancia.reponer_stock(detalle.cantidad)
        self.estado = "cancelada"

    def ficha(self) -> str:
        return (
            f"Compra #{self.id_compra} | Fecha: {self.fecha_compra:%d/%m/%Y} | "
            f"Total: ${self.total:.2f} | Estado: {self.estado}"
        )

    def __repr__(self) -> str:
        return f"<Compra #{self.id_compra} - {self.estado}>"


class DetalleCompra(db.Model):
    """
    Linea de detalle dentro de una compra.
    Guarda el precio_unitario al momento de la compra (inmutable historico).
    """
    __tablename__ = "detalle_compras"
    __table_args__ = (
        db.CheckConstraint("cantidad > 0", name="ck_detalle_cantidad_positiva"),
        db.CheckConstraint("precio_unitario > 0", name="ck_detalle_precio_positivo"),
        db.CheckConstraint(
            "(id_evento IS NOT NULL AND id_mercancia IS NULL) OR "
            "(id_evento IS NULL AND id_mercancia IS NOT NULL)",
            name="ck_detalle_tipo_unico",
        ),
    )

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_compra = db.Column(
        db.Integer, db.ForeignKey("compras.id_compra"), nullable=False, index=True
    )
    id_evento = db.Column(
        db.Integer, db.ForeignKey("eventos.id_evento"), nullable=True, index=True
    )
    id_mercancia = db.Column(
        db.Integer, db.ForeignKey("mercancias.id_mercancia"), nullable=True, index=True
    )
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    def subtotal(self) -> float:
        return float(self.precio_unitario) * self.cantidad

    def nombre_item(self) -> str:
        if self.id_evento is not None and self.evento is not None:
            return self.evento.nombre
        elif self.id_mercancia is not None and self.mercancia is not None:
            return self.mercancia.nombre
        return "Item desconocido"

    def __repr__(self) -> str:
        return f"<DetalleCompra {self.nombre_item()} cantidad={self.cantidad}>"
