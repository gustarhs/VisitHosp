from extensions import db

class Visita(db.Model):
    __tablename__ = 'visita'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    qr_code = db.Column(db.String(100), nullable=False, unique=True)

    id_visitante = db.Column(db.Integer, db.ForeignKey('visitante.id'), nullable=False)
    id_hospital = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    id_internacao = db.Column(db.Integer, db.ForeignKey('internacao.id'), nullable=False)
    id_triagem = db.Column(db.Integer, db.ForeignKey('triagem.id'), nullable=True)
  
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

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        """READ: retorna todas as visitas."""
        return Visita.query.order_by(Visita.id.asc()).all()

    @staticmethod
    def buscar_por_id(id):
        """READ: busca uma visita pelo id."""
        return Visita.query.get(id)

    def atualizar(self, data_hora=None, status=None, qr_code=None):
        if data_hora is not None:
            self.data_hora = data_hora
        if status is not None:
            self.status = status
        if qr_code is not None:
            self.qr_code = qr_code
        db.session.commit()
