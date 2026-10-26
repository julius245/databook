"""Países y zonas horarias para el registro global de bibliotecas."""

COUNTRIES = [
    "Colombia", "Argentina", "Bolivia", "Brasil", "Chile", "Costa Rica", "Cuba",
    "Ecuador", "El Salvador", "España", "Estados Unidos", "Guatemala", "Honduras",
    "México", "Nicaragua", "Panamá", "Paraguay", "Perú", "Puerto Rico",
    "República Dominicana", "Uruguay", "Venezuela", "Alemania", "Canadá",
    "Francia", "Italia", "Portugal", "Reino Unido", "Otro",
]

TIMEZONES = [
    ("America/Bogota", "Bogotá, Lima, Quito (UTC−5)"),
    ("America/Mexico_City", "Ciudad de México (UTC−6)"),
    ("America/Cancun", "Cancún (UTC−5)"),
    ("America/Tijuana", "Tijuana (UTC−8)"),
    ("America/Guatemala", "Guatemala, San Salvador (UTC−6)"),
    ("America/Panama", "Panamá (UTC−5)"),
    ("America/Caracas", "Caracas (UTC−4)"),
    ("America/Santo_Domingo", "Santo Domingo (UTC−4)"),
    ("America/La_Paz", "La Paz (UTC−4)"),
    ("America/Santiago", "Santiago (UTC−4/−3)"),
    ("America/Argentina/Buenos_Aires", "Buenos Aires (UTC−3)"),
    ("America/Montevideo", "Montevideo (UTC−3)"),
    ("America/Sao_Paulo", "São Paulo (UTC−3)"),
    ("America/Asuncion", "Asunción (UTC−4/−3)"),
    ("America/New_York", "Nueva York (UTC−5/−4)"),
    ("America/Chicago", "Chicago (UTC−6/−5)"),
    ("America/Denver", "Denver (UTC−7/−6)"),
    ("America/Los_Angeles", "Los Ángeles (UTC−8/−7)"),
    ("America/Puerto_Rico", "Puerto Rico (UTC−4)"),
    ("Atlantic/Canary", "Islas Canarias (UTC+0/+1)"),
    ("Europe/Madrid", "Madrid (UTC+1/+2)"),
    ("Europe/Lisbon", "Lisboa (UTC+0/+1)"),
    ("Europe/London", "Londres (UTC+0/+1)"),
    ("UTC", "UTC"),
]

TIMEZONE_VALUES = {value for value, _label in TIMEZONES}
