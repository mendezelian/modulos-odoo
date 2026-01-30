from odoo import models, fields

class GameRank(models.Model):
    _name = 'game.rank'
    _description = 'Rango de Jugador'
    _order = 'min_points desc'

    name = fields.Char(string='Nombre del Rango', required=True)
    min_points = fields.Integer(string='Puntos Mínimos', required=True)
    image = fields.Image(string='Insignia', max_width=128, max_height=128)
    description = fields.Text(string='Descripción')
