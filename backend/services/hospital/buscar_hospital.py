from models.hospital import Hospital

def buscar_hospital(id):
    return Hospital.buscar_por_id(id)