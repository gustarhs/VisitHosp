from extensions import db

class Hospital(db.Model):
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

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        """READ: retorna todos os hospitais."""
        return Hospital.query.order_by(Hospital.id.asc()).all()

    @staticmethod
    def buscar_por_id(id):
        """READ: busca um hospital pelo id."""
        return Hospital.query.get(id)

    def atualizar(self, nome=None, horario_visita=None, rua=None, numero=None, cidade=None, estado=None):
        if nome is not None:
            self.nome = nome
        if horario_visita is not None:
            self.horario_visita = horario_visita
        if rua is not None:
            self.rua = rua
        if numero is not None:
            self.numero = numero
        if cidade is not None:
            self.cidade = cidade
        if estado is not None:
            self.estado = estado
        db.session.commit()
