"""
auth.py
───────
Decoradores de autenticación y autorización adaptados a app.py.
"""
from functools import wraps
from flask import session, redirect, url_for, flash

def login_requerido(f):
    """
    Decorador que exige una sesión activa (sin importar el rol).
    """
    @wraps(f)
    def decorada(*args, **kwargs):
        if "id_usuario" not in session:
            flash("Debes iniciar sesión para acceder a esa página.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorada

def rol_requerido(rol):
    """
    Fábrica de decoradores: exige permisos de administrador si rol == "admin".
    """
    def decorador(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            if "id_usuario" not in session:
                flash("Debes iniciar sesión para acceder a esa página.", "danger")
                return redirect(url_for("login"))
            
            # Verificamos si es admin por booleana o por el rol directo en sesión
            es_admin_sesion = session.get("es_admin", False) or session.get("usuario_rol") == "admin"
            
            if rol == "admin" and not es_admin_sesion:
                flash("No tienes permisos para acceder a esa página.", "danger")
                return redirect(url_for("listar_eventos"))
                
            return f(*args, **kwargs)
        return decorada
    return decorador