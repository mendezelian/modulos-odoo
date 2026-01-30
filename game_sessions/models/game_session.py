from odoo import models, fields, api

class GameSession(models.Model):
    _name = 'game.session'
    _description = 'Sesión de Juego'

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
