from extensions import db

class Internacao(db.Model):
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

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        """READ: retorna todas as internações."""
        return Internacao.query.order_by(Internacao.id.asc()).all()

    @staticmethod
    def buscar_por_id(id):
        """READ: busca uma internação pelo id."""
        return Internacao.query.get(id)

    def atualizar(self, data_entrada=None, data_saida=None, status=None, token_acesso=None):
        if data_entrada is not None:
            self.data_entrada = data_entrada
        if data_saida is not None:
            self.data_saida = data_saida
        if status is not None:
            self.status = status
        if token_acesso is not None:
            self.token_acesso = token_acesso
        db.session.commit()
