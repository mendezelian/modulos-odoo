from odoo import models, fields, api
import requests
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class GameSession(models.Model):
    _name = 'game.session'
    _description = 'Sesión de Juego'
    
    spring_id = fields.Integer(string='ID Spring', readonly=True, index=True)
    _sql_constraints = [
        ('spring_player_uniq', 'unique(spring_id, player_id)', 'Ya existe una sesión para este jugador y partida.')
    ]

    name = fields.Char(
        string='Referencia', 
        required=True, 
        copy=False, 
        readonly=True, 
        default='Nueva Partida'
    )
    
    player_id = fields.Many2one(
        'res.partner', 
        string='Jugador', 
        required=True, 
        domain=[('is_player', '=', True)]
    )
    
    game_id = fields.Many2one(
        'product.product', 
        string='Juego', 
        required=True
    )
    
    date_start = fields.Datetime(
        string='Fecha de Inicio', 
        default=fields.Datetime.now
    )
    
    duration = fields.Float(
        string='Duración (minutos)'
    )
    
    score = fields.Integer(
        string='Puntuación'
    )
    
    state = fields.Selection([
        ('in_progress', 'En Progreso'),
        ('finished', 'Finalizada'),
        ('abandoned', 'Abandonada'),
    ], string='Estado', default='in_progress')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nueva Partida') == 'Nueva Partida':
            # Generar nombre descriptivo si no se proporciona
            # Nota: Esto es básico, se podría usar ir.sequence
            pass 
        return super(GameSession, self).create(vals)

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.player_id.name} - {record.game_id.name}"
            result.append((record.id, name))
        return result

    @api.model
    def action_sync_sessions(self):
        url = "http://3.233.57.10:8080/api/v1/partidas"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            matches = response.json()
        except Exception as e:
            _logger.error(f"Error syncing sessions: {e}")
            return

        # Ensure default product exists
        product = self.env['product.product'].search([('name', '=', 'Spring Game')], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': 'Spring Game',
                'type': 'service',
                'detailed_type': 'service',
            })

        count_created = 0
        for match_data in matches:
            partida = match_data.get('partida', {})
            jugadores = match_data.get('jugadores', [])
            
            spring_match_id = partida.get('id')
            if not spring_match_id:
                continue

            date_str = partida.get('fecha')
            duration_str = partida.get('duracion')
            
            # Helper to parse duration "HH:MM:SS" -> minutes
            duration_minutes = 0.0
            if duration_str:
                try:
                    h, m, s = map(int, duration_str.split(':'))
                    duration_minutes = h * 60 + m + s / 60.0
                except:
                    pass

            for jug in jugadores:
                spring_player_id = jug.get('id')
                score = jug.get('score', 0)
                
                # Find player
                player = self.env['res.partner'].search([('spring_id', '=', spring_player_id), ('is_player', '=', True)], limit=1)
                
                if not player:
                    continue
                    
                # Check if session already exists
                existing = self.search([('spring_id', '=', spring_match_id), ('player_id', '=', player.id)], limit=1)
                if existing:
                    continue
                
                # Create session
                self.create({
                    'name': f"Partida {spring_match_id}",
                    'player_id': player.id,
                    'game_id': product.id,
                    'date_start': date_str, # Odoo handles 'YYYY-MM-DD' usually fine for datetime fields if it's just date
                    'duration': duration_minutes,
                    'score': score,
                    'spring_id': spring_match_id,
                    'state': 'finished'
                })
                count_created += 1
                
        _logger.info(f"Sync complete. Created {count_created} new sessions.")
