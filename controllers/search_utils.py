"""Helpers compartidos para búsquedas por ISBN e ID personal.

Los ISBN e IDs se escriben de muchas maneras ("978-958-04-1234-5", "1.234.567.890"),
por eso tanto el término digitado como el valor guardado se comparan sin separadores.
"""

import re


def compact_term(term):
    """'978-958 04' -> '97895804'. Si no queda nada, vuelve al término original."""
    return re.sub(r"[\s.\-]", "", term) or term


def isbn_matches(column):
    """Condición SQL (un placeholder `?`) que coincide con una columna ISBN ignorando guiones y espacios."""
    return f"REPLACE(REPLACE({column}, '-', ''), ' ', '') LIKE ?"


def id_matches(column):
    """Condición SQL (un placeholder `?`) que coincide con una columna de ID personal ignorando puntos, guiones y espacios."""
    return f"REPLACE(REPLACE(REPLACE({column}, '.', ''), '-', ''), ' ', '') LIKE ?"
