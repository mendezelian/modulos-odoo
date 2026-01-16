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
        'views/res_partner_view.xml'
    ],
    'installable':True,
    'application':True,
    'auto_install':False,
}
