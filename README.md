# House Construcción - Sistema de Gestión

Sistema web para gestión de proyectos de construcción con módulos de gastos, libro de obras y estadísticas.

## 🚀 Características

- **Rendición de gastos**: Control de gastos por categorías y proveedores
- **Libro de Obras**: Gestión de proyectos y registros diarios de obra
- **Estadísticas**: Dashboards interactivos y reportes
- **Administración**: Gestión de usuarios y permisos
- **Interfaz responsive**: Optimizada para móviles (350px+)

## 📋 Requisitos

- Python 3.12+
- pip
- Git

## 🔧 Instalación

1. **Clonar el repositorio:**
\\\ash
git clone https://github.com/tu-usuario/HouseConstruccion.git
cd HouseConstruccion/Admin
\\\

2. **Crear entorno virtual:**
\\\ash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
\\\

3. **Instalar dependencias:**
\\\ash
pip install -r requirements.txt
\\\

4. **Configurar variables de entorno:**
Crea un archivo \.env\ en la carpeta Admin con:
\\\
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
\\\

5. **Aplicar migraciones:**
\\\ash
python manage.py migrate
\\\

6. **Crear superusuario:**
\\\ash
python manage.py createsuperuser
\\\

7. **Ejecutar servidor:**
\\\ash
python manage.py runserver
\\\

8. **Abrir en navegador:** http://127.0.0.1:8000/

## 🎨 Branding

**Colores corporativos:**
- Naranja: #FF6B02
- Azul marino: #001F3F
- Amarillo: #FDB913

**Logos:** Ubicados en \static/assets/images/\

## 🛠️ Tecnologías

- Django 4.2
- Django REST Framework
- Bootstrap 5
- Rosetta (i18n)
- Webpack Loader

## 📱 Soporte

- ✅ Desktop (1920px+)
- ✅ Tablet (768px+)
- ✅ Mobile (350px+)

## 📝 Licencia

Proyecto privado - House Construcción © 2025
