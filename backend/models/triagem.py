from database import db

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
