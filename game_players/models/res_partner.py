from odoo import models, fields, api

LOGROS = [
    ('iniciado','Recluta de Campo'), # 3
    ('rastreador','Rastreador de Sombras'), # 10
    ('acechador','Acechador Silvestre'), # 15
    ('cazador_pistas','Cazador de Pistas'), # 20
    ('capturador','Capturador Veloz'), # 25
    ('guerrero','Guerrero de Élite'), # 30
    ('depredador','Depredador de Bases'), # 35
    ('maestro_caza','Maestro de la Caza'), # 40
    ('leyenda_flag','Leyenda de la bandera'), # 45
    ('debora_mundos','El Debora Mundos'), #50
]

class ResPartner(models.Model):
    _inherit = 'res.partner' # Se crea el modelo
    is_player = fields.Boolean(string = "Es Jugador")
    nickname = fields.Char(string = "Nickname")
    avatar = fields.Image(string = "Avatar", max_width = 512, max_height = 512)
    nivel = fields.Integer(
        string = "Nivel del jugador",
        compute = "_compute_nivel",
        store = True
    )
    puntos_acumulados = fields.Integer(string = "Puntos Acumulados")
    logros = fields.Selection(
        selection = LOGROS,
        string = "Logros desbloqueados",
        compute = "_compute_logro",
        store = True
    )
    
    #Trigger para actualizar el nivel según el puntaje acumulado
    @api.depends('puntos_acumulados')
    def _compute_nivel(self):
        for record in self:
            pts = record.puntos_acumulados 
            #lógica para calcular el nivel
            if pts >= 200: record.nivel = 100
            elif pts > 0 : record.nivel = pts // 2
            else: record.nivel = 0

    #Trigger para actualizar los logros según el puntaje acumulado
    @api.depends('puntos_acumulados')
    def _compute_logro(self):
        for record in self:
            pts = record.puntos_acumulados or 0
            #lógica de rango de puntos para los logros
            if pts >= 200 : record.logros = 'debora_mundos'
            elif pts >= 180 : record.logros = 'leyenda_flag'
            elif pts >= 150 : record.logros = 'maestro_caza'
            elif pts >= 130 : record.logros = 'depredador'
            elif pts >= 120 : record.logros = 'guerrero'
            elif pts >= 100 : record.logros = 'capturador'
            elif pts >= 70 : record.logros = 'cazador_pistas'
            elif pts >= 50 : record.logros = 'acechador'
            elif pts >= 20 : record.logros = 'rastreador'
            elif pts >= 3  : record.logros = 'iniciado'
            else:             record.logros = False
