from database import db

class VisitaModel(db.Model):
    __tablename__ = 'visita'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    qr_code = db.Column(db.String(100), nullable=False, unique=True)
  
    def to_dict(self):
        return {
            "id": self.id,
            "data_hora": self.data_hora.isoformat() if self.data_hora else None,
            "status": self.status,
            "qr_code": self.qr_code,
            "id_visitante": self.id_visitante,
            "id_hospital": self.id_hospital,
            "id_internacao": self.id_internacao,
            "id_triagem": self.id_triagem
        }
