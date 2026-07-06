from database import db  # Seu arquivo de configuração do SQLAlchemy

class VisitanteModel(db.Model):
    __tablename__ = 'visitante'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    nome = db.Column(db.String(100), nullable=False))
    data_nascimento = db.Column(db.DateTime, nullable=False))
    termo_consentimento = db.Column(db.Boolean, nullable=False)
    cpf = db.Column(db.String(20), nullable=False, unique=True)

    def to_dict(self):
        """Método auxiliar para converter o modelo em dicionário (JSON)"""
        return {
            "id": self.id,
            "status": self.status,
            "tipo": self.tipo,
            "nome": self.nome,
            # Converte a data para string no formato ISO (Ex: "2026-07-06T13:37:36")
            "data_nascimento": self.data_nascimento.isoformat(),
            "termo_consentimento": self.termo_consentimento,
            "cpf": self.cpf
        }
