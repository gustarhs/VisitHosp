from extensions import db

class Triagem(db.Model):
    __tablename__ = 'triagem'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    resultado = db.Column(db.Boolean, nullable=False)
    perguntas = db.Column(db.Text, nullable=False)  # LONGTEXT mapeia para Text no SQLAlchemy
    respostas = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "data_hora": self.data_hora.isoformat(),
            "resultado": self.resultado,
            "perguntas": self.perguntas,
            "respostas": self.respostas
        }

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        """READ: retorna todas as triagens."""
        return Triagem.query.order_by(Triagem.id.asc()).all()

    @staticmethod
    def buscar_por_id(id):
        """READ: busca uma triagem pelo id."""
        return Triagem.query.get(id)

    def atualizar(self, data_hora=None, resultado=None, perguntas=None, respostas=None):
        if data_hora is not None:
            self.data_hora = data_hora
        if resultado is not None:
            self.resultado = resultado
        if perguntas is not None:
            self.perguntas = perguntas
        if respostas is not None:
            self.respostas = respostas
        db.session.commit()
