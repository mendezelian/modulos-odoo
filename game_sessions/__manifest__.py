{
    'name': 'Gestión de Sesiones de Juego',
    'version': '1.0',
    'summary': 'Gestión de partidas y resultados de juegos',
    'description': 'Módulo para gestionar las sesiones de juego de los jugadores',
    'author': 'GameHub',
    'category': 'Gaming/Sessions',
    'depends': ['base', 'game_players', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/game_session_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
