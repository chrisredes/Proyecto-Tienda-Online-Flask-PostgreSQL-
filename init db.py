"""
init_db.py
==========


Uso:
    python init_db.py
"""

from datetime import datetime, timedelta
from app import app
from models import (
    db, Usuario, Categoria, CategoriaMercancia, FormaPago, Carrito,
    EventoConcierto, EventoTeatro, EventoDeportivo,
    Mercancia,
)


def inicializar_base_datos():
    """Orquesta la creacion de esquema y la carga de datos semilla."""
    with app.app_context():
        print("=" * 60)
        print("INICIALIZANDO BASE DE DATOS")
        print("=" * 60)

        # Reinicio completo (util durante desarrollo)
        print("\n[1/4] Eliminando tablas existentes...")
        db.drop_all()
        print("      ✔ Tablas eliminadas.")

        print("\n[2/4] Creando tablas nuevas...")
        db.create_all()
        print("      ✔ Tablas creadas.")

        # ------------------------------------------------------------------
        # CATEGORIAS DE EVENTOS
        # ------------------------------------------------------------------
        print("\n[3/4] Insertando datos de prueba...")
        cat_conciertos = Categoria(nombre_categoria="Conciertos")
        cat_teatro = Categoria(nombre_categoria="Teatro")
        cat_deportivo = Categoria(nombre_categoria="Deportivo")
        db.session.add_all([cat_conciertos, cat_teatro, cat_deportivo])
        db.session.flush()

        # ------------------------------------------------------------------
        # CATEGORIAS DE MERCANCIA
        # ------------------------------------------------------------------
        cat_ropa = CategoriaMercancia(nombre_categoria="Ropa")
        cat_coleccionables = CategoriaMercancia(nombre_categoria="Coleccionables")
        cat_accesorios = CategoriaMercancia(nombre_categoria="Accesorios")
        db.session.add_all([cat_ropa, cat_coleccionables, cat_accesorios])
        db.session.flush()

        # ------------------------------------------------------------------
        # FORMAS DE PAGO
        # ------------------------------------------------------------------
        db.session.add_all([
            FormaPago(nombre_pago="tarjeta credito"),
            FormaPago(nombre_pago="tarjeta debito"),
            FormaPago(nombre_pago="payPal"),
        ])

        # ------------------------------------------------------------------
        # USUARIOS DE PRUEBA
        # ------------------------------------------------------------------
        admin = Usuario(
            nombre="Admin Principal",
            email="admin@eventos.com",
            rol="admin"
        )
        admin.set_password("admin123")

        cliente = Usuario(
            nombre="Cliente Demo",
            email="cliente@eventos.com",
            rol="cliente"
        )
        cliente.set_password("cliente123")

        db.session.add_all([admin, cliente])
        db.session.flush()

        # Crear carritos vacios para cada usuario
        db.session.add_all([
            Carrito(id_usuario=admin.id_usuario),
            Carrito(id_usuario=cliente.id_usuario),
        ])

        # ------------------------------------------------------------------
        # EVENTOS DE PRUEBA (demuestra polimorfismo STI)
        # ------------------------------------------------------------------
        e1 = EventoConcierto(
            codigo="CON001", nombre="Noche de Rock Nacional",
            descripcion="Festival con las mejores bandas de rock del pais.",
            lugar="Coliseo Rumiñahui",
            fecha_evento=datetime.now() + timedelta(days=20),
            precio_base=25.00, capacidad=500,
            id_categoria=cat_conciertos.id_categoria,
            artista="Varios artistas", cargo_servicio_pct=0.12,
        )
        e2 = EventoConcierto(
            codigo="CON002", nombre="Tour Sinfonico",
            descripcion="Orquesta sinfonica interpretando clasicos del pop.",
            lugar="Teatro Nacional Sucre",
            fecha_evento=datetime.now() + timedelta(days=35),
            precio_base=40.00, capacidad=300,
            id_categoria=cat_conciertos.id_categoria,
            artista="Orquesta Sinfonica Nacional", cargo_servicio_pct=0.10,
        )
        e3 = EventoTeatro(
            codigo="TEA001", nombre="Hamlet",
            descripcion="Clasico de Shakespeare puesto en escena.",
            lugar="Teatro Bolivar",
            fecha_evento=datetime.now() + timedelta(days=15),
            precio_base=18.00, capacidad=150,
            id_categoria=cat_teatro.id_categoria,
            elenco="Compania Nacional de Teatro", es_matinee=True,
        )
        e4 = EventoTeatro(
            codigo="TEA002", nombre="La Casa de Bernarda Alba",
            descripcion="Drama de Federico Garcia Lorca.",
            lugar="Teatro Bolivar",
            fecha_evento=datetime.now() + timedelta(days=18),
            precio_base=18.00, capacidad=150,
            id_categoria=cat_teatro.id_categoria,
            elenco="Compania Nacional de Teatro", es_matinee=False,
        )
        e5 = EventoDeportivo(
            codigo="DEP001", nombre="Clasico Nacional",
            descripcion="Partido de futbol de la liga local.",
            lugar="Estadio Olimpico Atahualpa",
            fecha_evento=datetime.now() + timedelta(days=10),
            precio_base=15.00, capacidad=1000,
            id_categoria=cat_deportivo.id_categoria,
            equipo_local="Equipo A", equipo_visitante="Equipo B",
            recargo_fijo=3.00,
        )
        db.session.add_all([e1, e2, e3, e4, e5])

        # ------------------------------------------------------------------
        # MERCANCIAS DE PRUEBA
        # ------------------------------------------------------------------
        m1 = Mercancia(
            codigo="MER001", nombre="Camiseta Rock Nacional",
            descripcion="Camiseta oficial del festival de rock. 100% algodon.",
            precio_base=25.00, stock=100,
            id_categoria_mercancia=cat_ropa.id_categoria_mercancia,
            imagen_url="/static/img/mercancia/camiseta_rock.jpg",
        )
        m2 = Mercancia(
            codigo="MER002", nombre="Gorra Clasico Nacional",
            descripcion="Gorra edicion limitada del partido. Ajustable.",
            precio_base=15.00, stock=50,
            id_categoria_mercancia=cat_accesorios.id_categoria_mercancia,
            imagen_url="/static/img/mercancia/gorra_clasico.jpg",
        )
        m3 = Mercancia(
            codigo="MER003", nombre="Poster Hamlet Firmado",
            descripcion="Poster autografiado por todo el elenco de la obra.",
            precio_base=35.00, stock=20,
            id_categoria_mercancia=cat_coleccionables.id_categoria_mercancia,
            imagen_url="/static/img/mercancia/poster_hamlet.jpg",
        )
        m4 = Mercancia(
            codigo="MER004", nombre="Taza Sinfonica",
            descripcion="Taza ceramica edicion especial del tour sinfonico.",
            precio_base=12.00, stock=200,
            id_categoria_mercancia=cat_accesorios.id_categoria_mercancia,
            imagen_url="/static/img/mercancia/taza_sinfonica.jpg",
        )
        m5 = Mercancia(
            codigo="MER005", nombre="Pin Coleccionable",
            descripcion="Pin metalico serie limitada. Varios modelos.",
            precio_base=8.00, stock=500,
            id_categoria_mercancia=cat_coleccionables.id_categoria_mercancia,
            imagen_url="/static/img/mercancia/pin_coleccionable.jpg",
        )
        db.session.add_all([m1, m2, m3, m4, m5])

        db.session.commit()
        print("      ✔ Datos insertados correctamente.")

        # ------------------------------------------------------------------
        # RESUMEN
        # ------------------------------------------------------------------
        print("\n" + "=" * 60)
        print("BASE DE DATOS INICIALIZADA CON EXITO")
        print("=" * 60)
        print("\nCredenciales de prueba:")
        print("  Admin   → admin@eventos.com   / admin123")
        print("  Cliente → cliente@eventos.com / cliente123")
        print("\nCategorias de mercancia creadas:")
        print("  - Ropa")
        print("  - Coleccionables")
        print("  - Accesorios")
        print("\nMercancias de prueba: 5 items")
        print("Eventos de prueba: 5 items")
        print("=" * 60)


if __name__ == "__main__":
    inicializar_base_datos() 