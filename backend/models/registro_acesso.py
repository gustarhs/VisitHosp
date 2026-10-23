from datetime import datetime

from extensions import db


class RegistroAcesso(db.Model):
    """Evento de auditoria: check-in (entrada) ou check-out (saida) de uma visita."""
    __tablename__ = 'registro_acesso'

    TIPO_CHECKIN = 'checkin'
    TIPO_CHECKOUT = 'checkout'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_visita = db.Column(db.Integer, db.ForeignKey('visita.id', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, default=datetime.now)
    origem = db.Column(db.String(20), nullable=False, default='recepcao')

    def to_dict(self):
        return {
            "id": self.id,
            "id_visita": self.id_visita,
            "tipo": self.tipo,
            "data_hora": self.data_hora.isoformat() if self.data_hora else None,
            "origem": self.origem,
        }

    def salvar(self):
        db.session.add(self)
        db.session.commit()
