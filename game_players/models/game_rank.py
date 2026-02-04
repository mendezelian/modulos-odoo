from odoo import models, fields

class GameRank(models.Model):
    _name = 'game.rank'
    _inherit = ['image.mixin']
    _description = 'Rango de Jugador'
    _order = 'min_points desc'

    name = fields.Char(string='Nombre del Rango', required=True)
    min_points = fields.Integer(string='Puntos Mínimos', required=True)
    image = fields.Image("Insignia", related="image_1920", store=True)
    description = fields.Text(string='Descripción')
