from extensions import db

class Leito(db.Model):
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

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        """READ: retorna todos os leitos."""
        return Leito.query.order_by(Leito.id.asc()).all()

    @staticmethod
    def buscar_por_id(id):
        """READ: busca um leito pelo id."""
        return Leito.query.get(id)

    def atualizar(self, status=None, ala=None, numero=None, andar=None, bloco=None):
        if status is not None:
            self.status = status
        if ala is not None:
            self.ala = ala
        if numero is not None:
            self.numero = numero
        if andar is not None:
            self.andar = andar
        if bloco is not None:
            self.bloco = bloco
        db.session.commit()
