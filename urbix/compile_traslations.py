#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para compilar traducciones sin necesidad de gettext
"""

try:
    import polib
except ImportError:
    print("❌ Error: polib no está instalado")
    print("Ejecuta: pip install polib")
    exit(1)

import os

# Ruta al archivo .po
po_file = 'locale/es/LC_MESSAGES/django.po'
mo_file = 'locale/es/LC_MESSAGES/django.mo'

# Verificar que el archivo .po existe
if not os.path.exists(po_file):
    print(f"❌ Error: No se encuentra el archivo {po_file}")
    exit(1)

try:
    # Compilar el archivo .po a .mo
    po = polib.pofile(po_file)
    po.save_as_mofile(mo_file)
    print("✅ ¡Traducciones compiladas exitosamente!")
    print(f"📄 Archivo generado: {mo_file}")
except Exception as e:
    print(f"❌ Error al compilar: {e}")
    exit(1)
