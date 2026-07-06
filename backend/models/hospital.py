from database import db

class HospitalModel(db.Model):
    __tablename__ = 'hospital'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    horario_visita = db.Column(db.DateTime, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    rua = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "horario_visita": self.horario_visita.isoformat(),
            "nome": self.nome,
            "rua": self.rua,
            "numero": self.numero,
            "cidade": self.cidade,
            "estado": self.estado
        }
