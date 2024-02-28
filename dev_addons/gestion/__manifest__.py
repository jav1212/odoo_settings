# -*- coding: utf-8 -*-
{
    "name": "Gestion",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "description": """
        Long description of module's purpose
    """,
    "author": "My Company",
    "category": "Gestion Documental",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "web", "mail", "hr"],
    # always loaded
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/pages/directorios.xml",
        "views/pages/coordinadores.xml",
        "views/pages/gerentes_jefes.xml",
        "views/pages/documentos.xml",
        "views/pages/solicitud.xml",
        "views/pages/departamentos.xml",
        "views/pages/empleados.xml",
        "views/pages/respuestas.xml",
        "views/pages/revisiones.xml",
        "views/templates.xml",
        "mail/mail_solicitud_template.xml",
        "mail/mail_revisado_template.xml",
        "mail/mail_aprobado_template.xml",
        "mail/mail_publicado_template.xml",
        "mail/mail_no_procede_template.xml",
        "reports/report.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
