# -*- coding: utf-8 -*-
{
    "name": "Gestión Documental",
    "summary": "Módulo para la Gestión de documentos en Feibo Servicios Industriales, C.A.",
    "description": "Este módulo de Gestión de documentos esta en fase de desarrollo, con una versión estable 1.0 donde se permiten requerimientos en relación uno a uno",
    "author": "Haldrim Molina",
    "category": "Gestion Documental",
    "website": "https://github.com/jav1212/odoo_settings.git",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "version": "1.0",
    # any module necessary for this one to work correctly
    "depends": ["base", "web", "mail", "hr", "board"],
    "application": "True",
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
        "views/pages/archivos.xml",
        "views/pages/logger_download.xml",
        "views/pages/logger_acess.xml",
        "views/templates.xml",
        "reports/report_solicitud_detail.xml",
        "reports/report_lista_maestra.xml",
        "reports/report_lista_cambio.xml",
        "mail/mail_solicitud_template.xml",
        "mail/mail_revisado_template.xml",
        "mail/mail_aprobado_template.xml",
        "mail/mail_publicado_template.xml",
        "mail/mail_no_procede_template.xml",
        "mail/mail_no_aprobado_template.xml",
        "mail/mail_no_conforme_template.xml",
        "mail/mail_elaboracion_template.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
