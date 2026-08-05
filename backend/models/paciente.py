from extensions import db

class Paciente(db.Model):
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

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        """READ: retorna todos os pacientes."""
        return Paciente.query.order_by(Paciente.id.asc()).all()

    @staticmethod
    def buscar_por_id(id):
        """READ: busca um paciente pelo id."""
        return Paciente.query.get(id)

    def atualizar(self, data_nascimento=None, tipo=None, status=None, nome=None, cpf=None):
        if data_nascimento is not None:
            self.data_nascimento = data_nascimento
        if tipo is not None:
            self.tipo = tipo
        if status is not None:
            self.status = status
        if nome is not None:
            self.nome = nome
        if cpf is not None:
            self.cpf = cpf
        db.session.commit()
