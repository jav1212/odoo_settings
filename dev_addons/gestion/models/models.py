# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _

# TODO: ask about ids at models fields
# TODO: ask about employes and how they are going to store specially if is User o Partner


class directorio(models.Model):
    _name = "gestion.directorio"
    _description = "gestion.directorio"

    name = fields.Char(
        string="Nombre",
        required=True,
        help="Introduzca el nombre del directorio",
    )  # Nombre del directorio

    descripcion = fields.Text()  # Descripcion del directorio

    documentos = fields.One2many(
        string="Documentos", comodel_name="gestion.documento", inverse_name="directorio"
    )  # Documentos del directorio

    departamentos = fields.Many2many(
        comodel_name="hr.department",
        relation="directorio_departamento_rel",
        column1="directorio_id",
        column2="departamento_id",
        string="Visible para los departamentos",
        required=True,
    )  # Departamentos que pueden acceder al departamento

    last_update = fields.Datetime(
        default=lambda self: fields.Datetime.now(), string="Fecha de creación"
    )  # Fecha de emision

    create_uid = fields.Many2one(
        "res.users", string="Creado por", readonly=True
    )  # Indica el creador del directorio

    is_admin = fields.Boolean(compute="_compute_admin", default=True)

    def _compute_admin(self):
        for directorio in self:
            directorio.is_admin = self.env.user.has_group(
                "gestion.group_gestion_administrador"
            )

    is_visible = fields.Boolean(
        compute="_compute_visible", default=True
    )  # Verifica si es visible

    @api.depends("departamentos", "is_admin")
    def _compute_visible(self):
        for directorio in self:
            directorio.is_visible = (
                self.env.user.department_id.id in directorio.departamentos.ids
            ) or directorio.is_admin


class documento(models.Model):
    _name = "gestion.documento"
    _description = "gestion.documento"

    version = fields.Char()
    comentarios_version = fields.Text()
    code = fields.Char()
    version = fields.Integer(default=1)
    name = fields.Char(
        string="Nombre",
        required=True,
        help="Introduzca el nombre del documento",
    )  # Nombre del documento
    descripcion = fields.Text()  # Descripcion del documento
    directorio = fields.Many2one(
        "gestion.directorio", required=True
    )  # Directorio al que pertenece
    solicitud = fields.One2many(
        string="Solicitudes", comodel_name="gestion.solicitud", inverse_name="documento"
    )  # Requerimientos de cambio para el documento
    fileref = fields.Binary()  # Archivo de formato pdf, word, ppt
    departamentos = fields.Many2many(
        comodel_name="hr.department",
        relation="documento_departamento_rel",
        column1="directorio_id",
        column2="departamento_id",
        string="Departamentos",
        # compute="_compute_departments",
    )

    last_update = fields.Datetime(
        default=lambda self: fields.Datetime.now(), string="Fecha de creación"
    )

    create_uid = fields.Many2one("res.users", string="Creado por", readonly=True)

    is_admin = fields.Boolean(compute="_compute_admin", default=True)

    def _compute_admin(self):
        for documento in self:
            documento.is_admin = self.env.user.has_group(
                "gestion.group_gestion_administrador"
            )

    is_visible = fields.Boolean(
        compute="_compute_visible", default=True
    )  # Verifica si es visible

    @api.depends("departamentos", "is_admin")
    def _compute_visible(self):
        for documento in self:
            documento.is_visible = (
                self.env.user.department_id.id in documento.departamentos.ids
            ) or documento.is_admin


# TODO arreglar las direcciones de los correos CHECKKKKK
# TODO hacer los caminos fallidos del workflow de la solicitud SEMI-CHECKKK
# TODO preguntar lo del many2many del empleado NOT CHECKK
# TODO pautar la reunion de control SEMI-CHECKKK
# TODO preguntar el codigo de los departamentos, en las lista maestra CHECKK
# TODO adjuntar un los archivos al correo CHECKKKK

# TODO arregla cuando el correo no tiene archivo adjunto
# TODO hacer el flujo complejo de la solicitud
# TODO arreglar los formularios
# TODO generar los reportes de la solicitud
# TODO arreglar lo del many2many del empleado
# TODO ver lo de la publicacion


class Solicitud(models.Model):
    _name = "gestion.solicitud"
    _description = "gestion.solicitud"

    state = fields.Selection(
        [
            ("borrador", "Borrador"),
            ("solicitado", "Solicitado"),
            ("elaboracion", "En elaboración"),
            ("revision", "En revisión"),
            ("revisado", "Revisado"),
            ("aprobacion", "En aprobación"),
            ("aprobado", "Aprobado"),
            ("publicacion", "En publicación"),
            ("publicado", "Publicado"),
        ],
        default="borrador",
        string="Estatus de la solicitud",
    )
    state_color = fields.Char(
        compute="_compute_state_color", store=False, default="red"
    )

    @api.depends("state")
    def _compute_state_color(self):
        for record in self:
            if record.state == "borrador":
                record.state_color = "red"
            elif record.state == "solicitado":
                record.state_color = "yellow"
            elif record.state == "elaboracion":
                record.state_color = "blue"
            elif record.state == "revision":
                record.state_color = "orange"
            elif record.state == "revisado":
                record.state_color = "green"
            elif record.state == "aprobacion":
                record.state_color = "purple"
            elif record.state == "aprobado":
                record.state_color = "lime"
            elif record.state == "publicacion":
                record.state_color = "pink"
            elif record.state == "publicado":
                record.state_color = "cyan"

    fecha_emision = fields.Datetime()
    gerencia_solicitante = fields.Many2one(
        "hr.department", readonly=True, default=lambda self: self.env.user.department_id
    )

    name = fields.Char(compute="_compute_code", default="SOL-NUEVA", string="Codigo")

    @api.depends()
    def _compute_code(self):
        for solicitud in self:
            solicitud.name = f"SOL-{solicitud.id}"

    email_from = fields.Char()
    email_to = fields.Char()

    # Requerimiento
    requerimiento_selection = fields.Selection(
        [
            ("documento nuevo", "Documento nuevo"),
            ("actualizacion", "Actualización"),
            ("modificacion", "Modificación"),
            ("procedimiento", "Procedimiento"),
            ("instructivo", "Instructivo"),
            ("formulario", "Formulario"),
            ("manual", "Manual"),
            ("políticas", "Políticas"),
            ("otros", "Otros"),
        ],
        string="Requerimientos",
    )
    # Descripcion del requerimiento
    otros_documentos_description = fields.Text()

    # Origen de las solicitudes
    origen_solicitud = fields.Selection(
        [
            ("auditoria externa", "Auditoria externa"),
            ("auditoria interna", "Auditoria interna"),
            ("modificaciones propias", "Modificaciones propias"),
            (
                "documentos vencidos por lista maestra",
                "Documentos vencidos por Lista Maestra",
            ),
            ("integridad del sgc", "Integridad del SGC"),
            ("cambio organizacionales", "Cambios organizacionales"),
            (
                "requisitos legales y reglamentarios",
                "Requisitos Legales y Reglamentarios",
            ),
        ],
        string="Origen de la solicitud",
    )
    requerimiento = fields.Text()

    # ARCHIVOS
    documento = fields.Many2one("gestion.documento", string="Documento asociado")
    documento_elaboracion = fields.Binary()
    documento_revision = fields.Binary()

    # PERSONAL
    create_uid = fields.Many2one("res.users", string="Creado por", readonly=True)
    reviewed_uid = fields.Many2one("res.users", string="Revisado por", readonly=True)
    approved_uid = fields.Many2one("res.users", string="Aprobado por", readonly=True)
    published_uid = fields.Many2one("res.users", string="Publicado por", readonly=True)
    coordinador = fields.Many2one(
        "res.users",
        string="Coordinadores",
    )

    # fields para cuando no procede
    descripcion_no_procede = fields.Text()

    # fields para cuando no esta conforme con los cambios
    descripcion_no_conforme_revision = fields.Text()

    # fields para cuando no esta conforme la aprobacion
    descripcion_no_conforme_aprobacion = fields.Text()

    # fields para cuando se va a publicar
    descripcion_publicacion = fields.Text()

    fecha_revision = fields.Datetime()
    fecha_aprobacion = fields.Datetime()
    fecha_publicacion = fields.Datetime()

    progress = fields.Integer(default=lambda self: 0, compute="_compute_progress")

    @api.depends("state")
    def _compute_progress(self):
        for solicitud in self:
            if solicitud.state == "borrador":
                solicitud.progress = 0
            elif solicitud.state == "solicitado":
                solicitud.progress = 12.5
            elif solicitud.state == "elaboracion":
                solicitud.progress = 25
            elif solicitud.state == "revision":
                solicitud.progress = 37.5
            elif solicitud.state == "revisado":
                solicitud.progress = 50
            elif solicitud.state == "aprobacion":
                solicitud.progress = 62.5
            elif solicitud.state == "aprobado":
                solicitud.progress = 75
            elif solicitud.state == "publicacion":
                solicitud.progress = 87.5
            elif solicitud.state == "publicado":
                solicitud.progress = 100

    def send_email(self):
        self.state = "solicitado"
        self.fecha_emision = fields.Datetime.now()
        template = self.env.ref("gestion.mail_solicitud_template")
        for rec in self:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": "solicitud.pdf",
                    "datas": rec.documento.fileref,
                    "type": "binary",
                    "res_model": "gestion.documento",
                    "res_id": rec.id,
                }
            )
            template.attachment_ids = [(6, 0, [attachment.id])]
            template.send_mail(rec.id, force_send=True)

    def no_procedente(self):
        self.state = "borrador"
        self.fecha_emision = False
        template = self.env.ref("gestion.mail_no_procede_template")
        for rec in self:
            template.send_mail(rec.id, force_send=True)

    def procedente(self):
        self.state = "elaboracion"

    def mandar_a_revision(self):
        self.state = "revision"
        # template = self.env.ref("gestion.mail_elaboracion_template")
        # for rec in self:
        #    attachment = self.env["ir.attachment"].create(
        #        {
        #            "name": f"Elaborado-{rec.name}.pdf",
        #            "datas": rec.documento_elaboracion,
        #            "type": "binary",
        #            "res_model": "gestion.solicitud",
        #            "res_id": rec.id,
        #        }
        #    )
        #    template.attachment_ids = [(6, 0, [attachment.id])]
        #    template.send_mail(rec.id, force_send=True)

    def no_revisado(self):
        self.state = "elaboracion"
        template = self.env.ref("gestion.mail_no_conforme_template")
        for rec in self:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"Inconformidad-{rec.name}.pdf",
                    "datas": rec.documento_revision,
                    "type": "binary",
                    "res_model": "gestion.solicitud",
                    "res_id": rec.id,
                }
            )
            template.attachment_ids = [(6, 0, [attachment.id])]
            template.send_mail(rec.id, force_send=True)

    def revisado(self):
        self.state = "revisado"
        self.fecha_revision = fields.Datetime.now()
        self.reviewed_uid = self.env.user
        template = self.env.ref("gestion.mail_revisado_template")
        for rec in self:
            template.send_mail(rec.id, force_send=True)

    def mandar_a_aprobacion(self):
        self.state = "aprobacion"

    def no_aprobado(self):
        self.state = "borrador"
        self.fecha_emision = False
        self.fecha_revision = False
        self.approved_uid = False
        self.reviewed_uid = False
        template = self.env.ref("gestion.mail_no_aprobado_template")
        for rec in self:
            template.send_mail(rec.id, force_send=True)

    def aprobado(self):
        self.state = "aprobado"
        self.fecha_aprobacion = fields.Datetime.now()
        self.approved_uid = self.env.user
        template = self.env.ref("gestion.mail_aprobado_template")
        for rec in self:
            template.send_mail(rec.id, force_send=True)

    def mandar_a_publicacion(self):
        self.state = "publicacion"

    def publicado(self):
        self.state = "publicado"
        self.fecha_publicacion = fields.Datetime.now()
        self.published_uid = self.env.user
        template = self.env.ref("gestion.mail_publicado_template")
        for rec in self:
            template.send_mail(rec.id, force_send=True)

    # TODO: preguntar hasta que punto se puede cancelar la solicitud
    def cancelado(self):
        if self.state == "solicitado":
            # se envia un correo indicando pq no procede
            self.state = "borrador"
            self.fecha_emision = False
        elif self.state == "revision":
            # se envia un correo indicando pq no esta conforme con los cambios
            self.state = "elaboracion"
        elif self.state == "aprobacion":
            # se envia un correo indicando pq no esta aprobacion conforme
            self.state = "borrador"
            self.fecha_emision = False
            self.fecha_revision = False

    def action_name(self):
        pass


class Departamentos(models.Model):
    _name = "hr.department"
    _inherit = "hr.department"

    code = fields.Char(string="Codigo")
