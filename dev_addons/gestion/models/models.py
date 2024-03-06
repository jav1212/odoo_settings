# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
from datetime import timedelta

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

    version = fields.Integer(default=1)
    comentarios_version = fields.Text()
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
    fileref = fields.Binary()  # Archivo de formato pdf
    departamento_padre = fields.Many2one(
        "hr.department",
        string="Departamento padre",
        required=True,
    )
    tipo_documento = fields.Selection(
        [
            ("P", "Procedimiento"),
            ("I", "Instructivo"),
            ("F", "Formulario"),
            ("D", "Documento del SGC"),
        ],
        required=True,
        default="D",
    )
    code = fields.Char(compute="_compute_code", default="XXX-YNNN")

    def _compute_code(self):
        for rec in self:
            if rec.id < 10:
                rec.code = (
                    f"{rec.departamento_padre.code}-{rec.tipo_documento}00{rec.id}"
                )
            elif rec.id < 100:
                rec.code = (
                    f"{rec.departamento_padre.code}-{rec.tipo_documento}0{rec.id}"
                )
            else:
                rec.code = f"{rec.departamento_padre.code}-{rec.tipo_documento}{rec.id}"

    departamentos = fields.Many2many(
        comodel_name="hr.department",
        relation="documento_departamento_rel",
        column1="directorio_id",
        column2="departamento_id",
        string="Visible para los departamentos",
        # compute="_compute_departments",
    )

    # PERSONAL PARA LA LISTA MAESTRA

    create_uid = fields.Many2one("res.users", string="Creado por", readonly=True)
    reviewed_uid = fields.Many2one("res.users", string="Revisado por", readonly=True)
    approved_uid = fields.Many2one("res.users", string="Aprobado por", readonly=True)

    # FECHAS PARA LA LISTA MAESTRA

    fecha_elaboracion = fields.Datetime(
        default=lambda self: fields.Datetime.now(), string="Fecha de elaboración"
    )
    fecha_revision = fields.Datetime()
    fecha_aprobacion = fields.Datetime()
    fecha_publicacion = fields.Datetime()

    #  PARA LA LISTA MAESTRA
    frecuencia_revision = fields.Integer(default=0)
    fecha_prox_revision = fields.Datetime()
    # TODO: ELIMINAR ESTE CAMPO
    cantidad_ultima_revision = fields.Integer()
    revision = fields.Integer(readonly=True)
    forma_distribucion = fields.Selection(
        [
            ("Electrónica", "Electrónica"),
            ("Física", "Física"),
            ("Electrónica y Física", "Electrónica y Física"),
        ],
        required=True,
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

    def generate_lista_maestra(self):
        p


# TODO arreglar las direcciones de los correos CHECKKKKK
# TODO hacer los caminos fallidos del workflow de la solicitud SEMI-CHECKKK
# TODO preguntar lo del many2many del empleado NOT CHECKK
# TODO pautar la reunion de control SEMI-CHECKKK
# TODO preguntar el codigo de los departamentos, en las lista maestra CHECKK
# TODO adjuntar un los archivos al correo CHECKKKK

# TODO arregla cuando el correo no tiene archivo adjunto checkkkk
# TODO hacer el flujo complejo de la solicitud semi-checkkk
# TODO arreglar los formularios semi-checkkk
# TODO generar los reportes de la solicitud semi-checkkk
# TODO arreglar lo del many2many del empleado not checkkk
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
    state_color = fields.Char(compute="_compute_state_color", default="red")

    @api.depends("state")
    def _compute_state_color(self):
        for record in self:
            if record.state == "borrador":
                record.state_color = "color:red"
            elif record.state == "solicitado":
                record.state_color = "color:orange"
            elif record.state == "elaboracion":
                record.state_color = "color:orange"
            elif record.state == "revision":
                record.state_color = "color:orange"
            elif record.state == "revisado":
                record.state_color = "color:yellow"
            elif record.state == "aprobacion":
                record.state_color = "color:yellow"
            elif record.state == "aprobado":
                record.state_color = "color:green"
            elif record.state == "publicacion":
                record.state_color = "color:green"
            elif record.state == "publicado":
                record.state_color = "color:green"

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
            ("Documento nuevo", "Documento nuevo"),
            ("Actualización", "Actualización"),
            ("Modificación", "Modificación"),
            ("Procedimiento", "Procedimiento"),
            ("Instructivo", "Instructivo"),
            ("Formulario", "Formulario"),
            ("Manual", "Manual"),
            ("Políticas", "Políticas"),
            ("Otros", "Otros"),
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
    documento_nuevo = fields.Many2one(
        "gestion.documento", string="Documento nuevo asociado"
    )
    documento_elaboracion = fields.Binary()
    documento_revision = fields.Binary()

    # PERSONAL
    create_uid = fields.Many2one("res.users", string="Creado por", readonly=True)
    reviewed_uid = fields.Many2one("res.users", string="Revisado por", readonly=True)
    approved_uid = fields.Many2one("res.users", string="Aprobado por", readonly=True)
    published_uid = fields.Many2one("res.users", string="Publicado por", readonly=True)
    coordinador = fields.Many2one(
        "res.users",
        string="Coordinador asignado",
    )

    # fields para cuando no procede
    descripcion_no_procede = fields.Text()

    # fields para cuando no esta conforme con los cambios
    descripcion_no_conforme_revision = fields.Text()

    # fields para cuando no esta conforme la aprobacion
    descripcion_no_conforme_aprobacion = fields.Text()

    # fields para cuando se va a publicar
    descripcion_publicacion = fields.Text()

    # FECHAS
    fecha_revision = fields.Datetime()
    fecha_aprobacion = fields.Datetime()
    fecha_publicacion = fields.Datetime()

    # CAMBIOS
    origen = fields.Selection(
        [
            ("Auditoría Interna", "Auditoría Interna"),
            ("Auditoría Externa", "Auditoría Externa"),
        ],
        string="Origen del documento",
    )
    descripcion_cambios = fields.Text()
    numero_cambio = fields.Integer()
    fecha_cambio = fields.Datetime(default=lambda self: self.fecha_publicacion)

    # SMART BUTTONS
    progress = fields.Integer(default=lambda self: 0, compute="_compute_progress")

    # VERIFICACIONES SOBRE EL USUARIO ACTUAL

    is_creator = fields.Boolean(compute="_compute_is_creator", default=True)

    @api.depends("create_uid")
    def _compute_is_creator(self):
        for rec in self:
            if rec.create_uid != False:
                if rec.create_uid.name == self.env.user.name:
                    rec.is_creator = True
                else:
                    rec.is_creator = False

    is_assigned_coordinator = fields.Boolean(compute="_compute_is_assigned_coordinator")

    @api.depends("coordinador")
    def _compute_is_assigned_coordinator(self):
        for rec in self:
            if rec.coordinador != False:
                if rec.coordinador.name == self.env.user.name:
                    rec.is_assigned_coordinator = True
                else:
                    rec.is_assigned_coordinator = False

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

    # DESDE GERENTES EN ADELANTE
    def send_email(self):
        self.state = "solicitado"
        self.fecha_emision = fields.Datetime.now()
        self.create_uid = self.env.user
        template = self.env.ref("gestion.mail_solicitud_template")
        for rec in self:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"Documento-{rec.name}.pdf",
                    "datas": rec.documento.fileref,
                    "type": "binary",
                    "res_id": rec.id,
                }
            )
            template.attachment_ids = [(6, 0, [attachment.id])]
            template.send_mail(rec.id, force_send=True)

    # DESDE ADMINISTRADORES EN ADELANTE
    def no_procedente(self):
        if self.is_assigned_coordinator:
            self.state = "borrador"
            self.fecha_emision = False
            template = self.env.ref("gestion.mail_no_procede_template")
            for rec in self:
                template.send_mail(rec.id, force_send=True)
        else:
            raise ValidationError(
                _(
                    "No eres el coordinador asignado de la solicitud, por lo tanto no puedes evaluar su estado de procedencia"
                )
            )

    # DESDE ADMINISTRADORES EN ADELANTE
    def procedente(self):
        if self.is_assigned_coordinator:
            self.state = "elaboracion"
        else:
            raise ValidationError(
                _(
                    "No eres el coordinador asignado de la solicitud, por lo tanto no puedes evaluar su estado de procedencia"
                )
            )

    # DESDE ADMINISTRADORES EN ADELANTE
    def mandar_a_revision(self):
        if self.is_assigned_coordinator:
            self.state = "revision"
            template = self.env.ref("gestion.mail_elaboracion_template")
            for rec in self:
                attachment = self.env["ir.attachment"].create(
                    {
                        "name": f"Elaborado-{rec.name}.pdf",
                        "datas": rec.documento_elaboracion,
                        "type": "binary",
                        "res_model": "gestion.solicitud",
                        "res_id": rec.id,
                    }
                )
                template.attachment_ids = [(6, 0, [attachment.id])]
                template.send_mail(rec.id, force_send=True)
        else:
            raise ValidationError(
                _(
                    "No eres el coordinador asignado de la solicitud, por lo tanto no puedes mandar la solicitud al estado de revision"
                )
            )

    # DESDE GERENTES EN ADELANTE
    def no_revisado(self):
        if self.is_creator:
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
        else:
            raise ValidationError(
                _(
                    "No eres el creador de la solicitud, por lo tanto no puedes revisarla"
                )
            )

    # DESDE GERENTES EN ADELANTE
    def revisado(self):
        if self.is_creator == True:
            self.state = "revisado"
            self.fecha_revision = fields.Datetime.now()
            self.reviewed_uid = self.env.user
            template = self.env.ref("gestion.mail_revisado_template")
            for rec in self:
                # TODO: fix the use case when the user cant create the document, thats a if CHECCCCCK
                attachment = self.env["ir.attachment"].create(
                    {
                        "name": f"Documento-{rec.name}.pdf",
                        "datas": rec.documento.fileref,
                        "type": "binary",
                        "res_id": rec.id,
                    }
                )
                template.attachment_ids = [(6, 0, [attachment.id])]
                template.send_mail(rec.id, force_send=True)
        else:
            raise ValidationError(
                _(
                    "No eres el creador de la solicitud, por lo tanto no puedes revisarla"
                )
            )

    # DESDE ADMINISTRADORES EN ADELANTE
    def mandar_a_aprobacion(self):
        if self.is_assigned_coordinator:
            self.state = "aprobacion"
        else:
            raise ValidationError(
                _(
                    "No eres el coordinador asignado de la solicitud, por lo tanto no puedes mandar la solicitud al estado de aprobacion"
                )
            )

    # DESDE DIRECTORES EN ADELANTE
    def no_aprobado(self):
        self.state = "borrador"
        self.fecha_emision = False
        self.fecha_revision = False
        self.approved_uid = False
        self.reviewed_uid = False
        self.descripcion_no_procede = False
        self.descripcion_no_conforme_revision = False
        self.descripcion_no_conforme_aprobacion = False
        self.documento_elaboracion = False
        self.documento_revision = False
        template = self.env.ref("gestion.mail_no_aprobado_template")
        for rec in self:
            template.send_mail(rec.id, force_send=True)

    # DESDE DIRECTORES EN ADELANTE
    def aprobado(self):
        self.state = "aprobado"
        self.fecha_aprobacion = fields.Datetime.now()
        self.approved_uid = self.env.user
        template = self.env.ref("gestion.mail_aprobado_template")
        for rec in self:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"Documento-{rec.name}.pdf",
                    "datas": rec.documento.fileref,
                    "type": "binary",
                    "res_model": "gestion.documento",
                    "res_id": rec.id,
                }
            )
            template.attachment_ids = [(6, 0, [attachment.id])]
            template.send_mail(rec.id, force_send=True)

    # DESDE ADMINISTRADORES EN ADELANTE
    def mandar_a_publicacion(self):
        if self.is_assigned_coordinator:
            self.state = "publicacion"
        else:
            raise ValidationError(
                _(
                    "No eres el coordinador asignado de la solicitud, por lo tanto no puedes mandar la solicitud al estado de publicacion"
                )
            )

    # DESDE ADMINISTRADORES EN ADELANTE
    def publicado(self):
        if self.is_assigned_coordinator:
            self.state = "publicado"
            self.fecha_publicacion = fields.Datetime.now()
            self.published_uid = self.env.user
            if self.requerimiento_selection == "Documento nuevo":
                self.documento_nuevo.create_uid = self.env.user
                self.documento_nuevo.reviewed_uid = self.reviewed_uid
                self.documento_nuevo.approved_uid = self.approved_uid
                self.documento_nuevo.fecha_elaboracion = self.fecha_publicacion
                self.documento_nuevo.fecha_revision = self.fecha_revision
                self.documento_nuevo.fecha_prox_revision = self.fecha_revision + timedelta(
                    days=self.documento_nuevo.frecuencia_revision * 345
                )
                self.documento_nuevo.fecha_aprobacion = self.fecha_aprobacion
                self.documento_nuevo.fecha_publicacion = self.fecha_publicacion
                # TODO: FIX THE NUMERO CAMBIO
                self.documento_nuevo.revision = 1
                self.numero_cambio = 0
            else:
                self.documento.reviewed_uid = self.reviewed_uid
                self.documento.approved_uid = self.approved_uid
                self.documento.fecha_revision = self.fecha_revision
                self.documento.fecha_prox_revision = self.fecha_revision + timedelta(
                    days=self.documento.frecuencia_revision * 345
                )
                self.documento.fecha_aprobacion = self.fecha_aprobacion
                self.documento.fecha_publicacion = self.fecha_publicacion
                self.documento.revision = self.documento.revision + 1
                # TODO: FIX THE NUMERO CAMBIO
                self.numero_cambio = self.numero_cambio + 1
            template = self.env.ref("gestion.mail_publicado_template")
            for rec in self:
                attachment = self.env["ir.attachment"].create(
                    {
                        "name": f"Documento-{rec.name}.pdf",
                        "datas": rec.documento.fileref,
                        "type": "binary",
                        "res_model": "gestion.documento",
                        "res_id": rec.id,
                    }
                )
                template.attachment_ids = [(6, 0, [attachment.id])]
                template.send_mail(rec.id, force_send=True)
        else:
            raise ValidationError(
                _(
                    "No eres el coordinador asignado de la solicitud, por lo tanto no puedes publicar la solicitud"
                )
            )

    # TODO: preguntar hasta que punto se puede cancelar la solicitud hoy en la prueba
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


class Tablero(models.Model):
    _name = "gestion.tablero"
    _description = "gestion.tablero"

    def actualizar_lista_maestra(self):
        pass
