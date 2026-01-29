import requests
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

LOGROS = [
    ('iniciado','Recluta de Campo'),          # 50
    ('rastreador','Rastreador de Sombras'),   # 200
    ('acechador','Acechador Silvestre'),      # 300
    ('cazador_pistas','Cazador de Pistas'),   # 400
    ('capturador','Capturador Veloz'),        # 500
    ('guerrero','Guerrero de Élite'),          # 600
    ('depredador','Depredador de Bases'),     # 700
    ('maestro_caza','Maestro de la Caza'),    # 800
    ('leyenda_flag','Leyenda de la bandera'), # 900
    ('debora_mundos','El Debora Mundos'),     # 1000
]

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_player = fields.Boolean(
        string="Es Jugador",
        default=False,
        store=True
    )

    nickname = fields.Char(
        string="Nickname",
        store=True
    )

    avatar = fields.Image(
        string="Avatar",
        max_width=512,
        max_height=512,
        store=True
    )

    spring_id = fields.Integer(
        string="ID de SPRING",
        store=True,
        readonly=True
    )

    puntos_acumulados = fields.Integer(
        string="Puntos Acumulados",
        compute="_compute_puntos_actualizados",
        store=True
    )

    nivel = fields.Integer(
        string="Nivel del jugador",
        compute="_compute_nivel",
        store=True
    )

    logros = fields.Selection(
        selection=LOGROS,
        string="Logros desbloqueados",
        compute="_compute_logro",
        store=True
    )

    # OVERRIDES

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if vals.get("is_player"):
            record._send_player_to_api()
        return record

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if "is_player" in vals:
                if record.is_player:
                    record._send_player_to_api()
                record._change_player_state()
        return res

    # SPRING API

    def _send_player_to_api(self):
        if not self.is_player or self.spring_id:
            return

        url = "http://3.233.57.10:8080/api/v1/jugadores"

        payload = {
            "email": self.email,
            "nombre": self.nickname
        }

        try:
            if self.nickname and self.email:
                response = requests.post(url, json=payload, timeout=5)
                response.raise_for_status()

                data = response.json()
                spring_id = data.get("id")

                if spring_id:
                    self.write({"spring_id": spring_id})
                    _logger.info(f"Jugador creado en Spring con ID {spring_id}")
        except Exception as e:
            _logger.error(f"Error enviando jugador a API: {e}")

    def _change_player_state(self):
        if not self.spring_id:
            return

        url = "http://3.233.57.10:8080/api/v1/jugadores"
        payload = {
            "is_active": self.is_player
        }

        try:
            response = requests.patch(
                f"{url}/{self.spring_id}",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            _logger.info(f"Estado del jugador actualizado en Spring")
        except Exception as e:
            _logger.error(f"Error al cambiar estado del jugador: {e}")

    def _get_puntos_acumulados_to_api(self):
        url = "http://3.233.57.10:8000/api/v1/jugadores"

        try:
            response = requests.get(
                f"{url}/{self.spring_id}/score",
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            puntos_acumulados = data.get("puntosAcumulados", 0)

            _logger.info(f"Puntos acumulados obtenidos: {puntos_acumulados}")
            return puntos_acumulados
        except Exception as e:
            _logger.error(f"Error al consultar puntos en la API: {e}")
            return 0


    # COMPUTES

    @api.depends("is_player", "spring_id")
    def _compute_puntos_actualizados(self):
        for record in self:
            record.puntos_acumulados = 0
            if record.is_player and record.spring_id:
                record.puntos_acumulados = record._get_puntos_acumulados_to_api()

    @api.depends("puntos_acumulados")
    def _compute_nivel(self):
        for record in self:
            pts = record.puntos_acumulados or 0
            if pts >= 1000:
                record.nivel = 100
            elif pts > 0:
                record.nivel = pts // 10
            else:
                record.nivel = 0

    @api.depends("puntos_acumulados")
    def _compute_logro(self):
        for record in self:
            pts = record.puntos_acumulados or 0

            if pts >= 1000: record.logros = 'debora_mundos'
            elif pts >= 900: record.logros = 'leyenda_flag'
            elif pts >= 800: record.logros = 'maestro_caza'
            elif pts >= 700: record.logros = 'depredador'
            elif pts >= 600: record.logros = 'guerrero'
            elif pts >= 500: record.logros = 'capturador'
            elif pts >= 400: record.logros = 'cazador_pistas'
            elif pts >= 300: record.logros = 'acechador'
            elif pts >= 200: record.logros = 'rastreador'
            elif pts >= 50:  record.logros = 'iniciado'
            else:            record.logros = False

    def action_sync_puntos(self):
        for record in self:
            if record.is_player and record.spring_id:
                record.puntos_acumulados = record._get_puntos_acumulados_to_api()

