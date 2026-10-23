from datetime import datetime

from extensions import db


class VisitanteVinculo(db.Model):
    """
    Vinculo entre um visitante, um paciente e o leito/internacao onde o paciente esta.
    E a "autorizacao" do visitante para visitar aquele paciente. Quando o acesso e
    revogado, o vinculo fica com ativo=False (guardando data e motivo da revogacao).
    """
    __tablename__ = 'visitante_vinculo'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_visitante = db.Column(db.Integer, db.ForeignKey('visitante.id', ondelete='CASCADE'), nullable=False)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id', ondelete='CASCADE'), nullable=False)
    id_leito = db.Column(db.Integer, db.ForeignKey('leito.id', ondelete='CASCADE'), nullable=False)
    id_internacao = db.Column(db.Integer, db.ForeignKey('internacao.id', ondelete='CASCADE'), nullable=True)
    parentesco = db.Column(db.String(50), nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)
    revogado_em = db.Column(db.DateTime, nullable=True)
    motivo_revogacao = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "id_visitante": self.id_visitante,
            "id_paciente": self.id_paciente,
            "id_leito": self.id_leito,
            "id_internacao": self.id_internacao,
            "parentesco": self.parentesco,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "revogado_em": self.revogado_em.isoformat() if self.revogado_em else None,
            "motivo_revogacao": self.motivo_revogacao,
        }
