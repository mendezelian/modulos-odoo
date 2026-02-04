import requests
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)



class ResPartner(models.Model):
    _inherit = "res.partner"

    is_player = fields.Boolean(
        string="Es Jugador",
        default=False,
        store=True
    )

    # Sync avatar to image_1920 for standard Odoo views
    @api.onchange('avatar')
    def _onchange_avatar(self):
        if self.avatar:
            self.image_1920 = self.avatar

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
        store=False,
        readonly=True
    )

    nivel = fields.Integer(
        string="Nivel del jugador",
        compute="_compute_nivel",
        store=False
    )

    level_progress = fields.Integer(
        string="Progreso del Nivel",
        compute="_compute_nivel",
        store=False,
        help="Porcentaje de progreso para alcanzar el siguiente nivel"
    )

    @api.depends("puntos_acumulados")
    def _compute_nivel(self):
        for record in self:
            pts = record.puntos_acumulados or 0
            # Lógica: 1 nivel cada 10 puntos (ajustable)
            # Nivel = Parte entera de puntos / 10
            # Progreso = El resto (puntos % 10) * 10 (para hacerlo %)
            
            if pts >= 1000:
                record.nivel = 100
                record.level_progress = 100
            else:
                record.nivel = pts // 10
                # Cálculo de progreso: (Puntos en el nivel actual) / (Puntos necesarios por nivel) * 100
                # Puntos necesarios por nivel = 10
                start_level_pts = record.nivel * 10
                progress_pts = pts - start_level_pts
                record.level_progress = int((progress_pts / 10) * 100)

    rank_id = fields.Many2one(
        'game.rank',
        string="Rango",
        compute="_compute_rank_id",
        store=False
    )
    
    rank_image = fields.Image(
        related='rank_id.image_128',
        string="Insignia"
    )

    session_count = fields.Integer(
        string="Partidas Jugadas",
        compute="_compute_session_count"
    )

    def _compute_session_count(self):
        for record in self:
            record.session_count = self.env['game.session'].search_count([('player_id', '=', record.id)])

    def action_view_sessions(self):
        self.ensure_one()
        return {
            'name': 'Sesiones de Juego',
            'type': 'ir.actions.act_window',
            'res_model': 'game.session',
            'view_mode': 'list,form',
            'domain': [('player_id', '=', self.id)],
            'context': {'default_player_id': self.id}
        }

    # OVERRIDES

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if vals.get("is_player"):
            record._send_player_to_api()
        if vals.get("avatar"):
             record.image_1920 = vals.get("avatar")
        return record

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if "is_player" in vals:
                if record.is_player:
                    record._send_player_to_api()
                record._change_player_state()
            if "avatar" in vals:
                record.image_1920 = record.avatar
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
        url = "http://3.233.57.10:8080/api/v1/jugadores"

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
            pass
        return 0

    @api.model
    def cron_update_player_scores(self):
        players = self.search([('is_player', '=', True), ('spring_id', '!=', False)])
        for player in players:
            player.action_sync_puntos() # Reuse existing logic


    # COMPUTES

    @api.depends("is_player", "spring_id")
    def _compute_puntos_actualizados(self):
        for record in self:
            record.puntos_acumulados = 0
            if record.is_player and record.spring_id:
                record.puntos_acumulados = record._get_puntos_acumulados_to_api()



    @api.depends("puntos_acumulados")
    def _compute_rank_id(self):
        for record in self:
            pts = record.puntos_acumulados or 0
            # Busca el rango más alto que tenga min_points <= pts
            # Usamos sudo() por si el usuario no tiene permisos de lectura sobre game.rank (aunque debería)
            rank = self.env['game.rank'].search([('min_points', '<=', pts)], order='min_points desc', limit=1)
            record.rank_id = rank

    def action_sync_puntos(self):
        for record in self:
            if record.is_player and record.spring_id:
                record.puntos_acumulados = record._get_puntos_acumulados_to_api()

    @api.model
    def action_sync_players_from_api(self):
        url = "http://3.233.57.10:8080/api/v1/jugadores"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            players_data = response.json()
        except Exception as e:
             _logger.error(f"Error syncing players: {e}")
             return

        count_created = 0
        count_updated = 0
        
        for p_data in players_data:
            spring_id = p_data.get('id')
            email = p_data.get('email')
            name = p_data.get('nombre')
            
            if not spring_id:
                continue

            # Search by spring_id first (most reliable)
            domain = [('spring_id', '=', spring_id), ('is_player', '=', True)]
            player = self.search(domain, limit=1)
            
            # Fallback: Search by email if valid generic partner exists
            if not player and email:
                 player = self.search([('email', '=', email)], limit=1)

            vals = {
                'spring_id': spring_id,
                'nickname': name,
                'is_player': True,
            }
            if name: 
                 vals['name'] = name 

            if email:
                vals['email'] = email

            if player:
                player.write(vals)
                count_updated += 1
            else:
                vals['name'] = name or "Unknown Player"
                self.create(vals)
                count_created += 1

        _logger.info(f"Player Sync: Created {count_created}, Updated {count_updated}")

