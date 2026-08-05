from extensions import db # Seu arquivo de configuração do SQLAlchemy

class Visitante(db.Model):
    __tablename__ = 'visitante'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.DateTime, nullable=False)
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

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def listar_todos():
        """READ: retorna todos os visitantes."""
        return Visitante.query.order_by(Visitante.id.asc()).all()

    @staticmethod
    def buscar_por_id(id):
        """READ: busca um visitante pelo id."""
        return Visitante.query.get(id)

    def atualizar(self, status=None, tipo=None, nome=None, data_nascimento=None, termo_consentimento=None, cpf=None):
        if status is not None:
            self.status = status
        if tipo is not None:
            self.tipo = tipo
        if nome is not None:
            self.nome = nome
        if data_nascimento is not None:
            self.data_nascimento = data_nascimento
        if termo_consentimento is not None:
            self.termo_consentimento = termo_consentimento
        if cpf is not None:
            self.cpf = cpf
        db.session.commit()
