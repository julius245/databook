# Modulo de seguridad para cifrar claves de usuario
import hashlib

# Esta funcion recibe una clave en texto claro y la convierte a hash SHA256
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Compara la clave ingresada con la clave encriptada guardada
def check_password(password, hashed):
    return hash_password(password) == hashed
