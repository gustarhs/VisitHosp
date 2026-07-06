from database import db

class LeitoModel(db.Model):
    __tablename__ = 'leito'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Boolean, nullable=False)
    ala = db.Column(db.String(20), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    andar = db.Column(db.Integer, nullable=False)
    bloco = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "ala": self.ala,
            "numero": self.numero,
            "andar": self.andar,
            "bloco": self.bloco
        }
