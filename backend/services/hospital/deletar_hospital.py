from models.hospital import Hospital

def deletar_hospital(id):
    hospital = Hospital.buscar_por_id(id)

    if hospital is None:
        return False

    hospital.deletar()
    return True