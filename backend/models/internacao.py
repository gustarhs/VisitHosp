from database import db

class InternacaoModel(db.Model):
    __tablename__ = 'internacao'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_entrada = db.Column(db.DateTime, nullable=False)
    data_saida = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    token_acesso = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "data_entrada": self.data_entrada.isoformat() if self.data_entrada else None,
            "data_saida": self.data_saida.isoformat() if self.data_saida else None,
            "status": self.status,
            "token_acesso": self.token_acesso,
            "id_paciente": self.id_paciente,
            "id_leito": self.id_leito
        }
