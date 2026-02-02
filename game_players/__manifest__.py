{
    'name':'Gestión de jugadores',
    'version':'1.0',
    'summary':'Módulo para gestionar a los jugadores',
    'description':'Permite gestionar a los jugadores',
    'author':'gamehub',
    'category':'Gaming/Players',
    'depends':[
        'base',
        'contacts'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/game_rank_data.xml',
        'data/server_actions.xml',
        'views/res_partner_view.xml',
        'views/game_rank_view.xml',
        'views/players_menu.xml'
    ],
    'installable':True,
    'application':True,
    'auto_install':False,
}
