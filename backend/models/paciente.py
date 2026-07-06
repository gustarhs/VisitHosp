from database import db

class PacienteModel(db.Model):
    __tablename__ = 'paciente'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_nascimento = db.Column(db.DateTime, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(20), nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "data_nascimento": self.data_nascimento.isoformat(),
            "tipo": self.tipo,
            "status": self.status,
            "nome": self.nome,
            "cpf": self.cpf
        }
