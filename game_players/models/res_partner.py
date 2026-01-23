import requests
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
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
    spring_id = fields.Integer("ID de SPRING", readonly = True)
    

    #Override create
    @api.model
    def create(self,vals):
        record = super().create(vals)
        if vals.get("is_player"):
            record._send_player_to_api()
        return record

    #Override write
    def write(self,vals):
        res = super().write(vals)
        for record in self:
            if vals.get("is_player") or record.is_player:
                record._send_player_to_api()
        return res
    
    #metodo para enviar datos
    def _send_player_to_api(self):
        url = "http://3.233.57.10:8080/api/v1/jugadores"

        payload = {
                "email": self.email,
                "nombre":self.nickname
        }

        try:
            if not self.spring_id:
                response = requests.post(url, json = payload, timeout=5)
                response.raise_for_status()
                
                data = response.json()
                spring_id = data.get("id")

                if spring_id:
                    self.write({"spring_id":spring_id})
                    _logger.info(f"Jugador creado en spring con ID {spring_id}")
        except Exception as e:
            _logger.error(f"Error enviando jugador a API: {e}")


    #Trigger para actualizar el nivel según el puntaje acumulado
    @api.depends('puntos_acumulados')
    def _compute_nivel(self):
        for record in self:
            pts = record.puntos_acumulados 
            #lógica para calcular el nivel
            if pts >= 1000: record.nivel = 100
            elif pts > 0 : record.nivel = pts // 10
            else: record.nivel = 0

    #Trigger para actualizar los logros según el puntaje acumulado
    @api.depends('puntos_acumulados')
    def _compute_logro(self):
        for record in self:
            pts = record.puntos_acumulados or 0
            #lógica de rango de puntos para los logros
            if pts >= 1000 : record.logros = 'debora_mundos'
            elif pts >= 900 : record.logros = 'leyenda_flag'
            elif pts >= 800 : record.logros = 'maestro_caza'
            elif pts >= 700 : record.logros = 'depredador'
            elif pts >= 600 : record.logros = 'guerrero'
            elif pts >= 500 : record.logros = 'capturador'
            elif pts >= 400 : record.logros = 'cazador_pistas'
            elif pts >= 300 : record.logros = 'acechador'
            elif pts >= 200 : record.logros = 'rastreador'
            elif pts >= 50  : record.logros = 'iniciado'
            else:             record.logros = False
