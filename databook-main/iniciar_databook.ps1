
# ==========================================
# INICIO DE DATABOOK - ENTORNO LOCAL
# ==========================================

$env:APP_ENV = "development"

# Correo inicial del superadministrador
$env:SUPERADMIN_EMAIL = "admin@databook.local"

# IMPORTANTE:
# Usa la contraseña real del superadministrador.
# No compartas este archivo con otras personas.
$env:SUPERADMIN_PASSWORD = "angel123"

# Ir a la carpeta donde está este script
Set-Location $PSScriptRoot

# Iniciar DataBook
python main.py
