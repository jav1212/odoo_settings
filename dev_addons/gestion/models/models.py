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

    descripcion = fields.Text(
        string="Descripción del directorio",
        help="Introduzca una breve descripción del directorio",
    )  # Descripcion del directorio

    documentos = fields.One2many(
        string="Documentos", comodel_name="gestion.documento", inverse_name="directorio"
    )  # Documentos del directorio

    suma_tamaños = fields.Integer(
        string="Suma de Tamaños de Archivos", compute="_calcular_suma_tamaños"
    )

    @api.depends("documentos.tamaño_archivo")
    def _calcular_suma_tamaños(self):
        for record in self:
            record.suma_tamaños = sum(doc.tamaño_archivo for doc in record.documentos)
            record.suma_tamaños = record.suma_tamaños / (1024 * 1024)

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
    )  # Fecha de emisión

    create_uid = fields.Many2one(
        "res.users", string="Creado por", readonly=True
    )  # Indica el creador del directorio

    is_admin = fields.Boolean(
        compute="_compute_admin", default=True
    )  # Verifica si el usuario actual es administrador

    def _compute_admin(self):
        for directorio in self:
            directorio.is_admin = self.env.user.has_group(
                "gestion.group_gestion_administrador"
            )

    is_visible = fields.Boolean(
        compute="_compute_visible", default=True
    )  # Verifica si el documento es visible para el usuario actual

    @api.depends("departamentos", "is_admin")
    def _compute_visible(self):
        for directorio in self:
            directorio.is_visible = (
                self.env.user.department_id.id in directorio.departamentos.ids
            ) or directorio.is_admin

    def action_name(self):
        pass


class documento(models.Model):
    _name = "gestion.documento"
    _description = "gestion.documento"

    name = fields.Char(
        string="Nombre",
        required=True,
        help="Introduzca el nombre del documento",
    )  # Nombre del documento

    descripcion = fields.Text(
        string="Descripción del directorio",
        help="Introduzca una breve descripción del documento",
    )
    # Descripcion del documento

    directorio = fields.Many2one(
        "gestion.directorio", required=True, string="Directorio padre"
    )  # Directorio al que pertenece

    fileref = fields.Binary(
        string="Archivo adjunto",
        help="Adjunta un archivo en formato PDF, WORD, PPT o EXCEL",
    )  # Archivo de formato pdf

    tamaño_archivo = fields.Integer(
        string="Tamaño del Archivo", compute="_calcular_tamaño_archivo"
    )

    @api.depends("fileref")
    def _calcular_tamaño_archivo(self):
        for record in self:
            if record.fileref:
                # Calcular el tamaño del archivo en bytes
                record.tamaño_archivo = len(record.fileref)
            else:
                record.tamaño_archivo = 0

    departamento_padre = fields.Many2one(
        "hr.department",
        string="Departamento padre",
        required=True,
    )  # Departamento padre del archivo

    tipo_documento = fields.Selection(
        [
            ("P", "Procedimiento"),
            ("I", "Instructivo"),
            ("F", "Formulario"),
            ("D", "Documento del SGC"),
        ],
        required=True,
        default="D",
        string="Tipo de Documento",
    )  # Tipo del documento

    code = fields.Char(
        compute="_compute_code", default="XXX-YNNN", string="Código del documento"
    )  # Codigo del documento

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
    )  # Departamentos para los cuales es visible

    # PERSONAL PARA LA LISTA MAESTRA
    create_uid = fields.Many2one(
        "res.users", string="Creado por", readonly=True
    )  # Creador del documento

    reviewed_uid = fields.Many2one(
        "res.users", string="Revisado por", readonly=True
    )  # Revisor del documento

    approved_uid = fields.Many2one(
        "res.users", string="Aprobado por", readonly=True
    )  # Aprobador del documento

    # FECHAS PARA LA LISTA MAESTRA
    fecha_elaboracion = fields.Datetime(
        default=lambda self: fields.Datetime.now(), string="Fecha de elaboración"
    )  # Fecha de elaboración del documento

    fecha_revision = fields.Datetime(
        string="Fecha de revisión"
    )  # Fecha de revision del documento

    fecha_aprobacion = fields.Datetime(
        string="Fecha de aprobación"
    )  # Fecha de aprobacion del documento

    fecha_publicacion = fields.Datetime(
        string="Fecha de publicación y distribución"
    )  # Fecha de publicación y distribución del documento

    #  PARA LA LISTA MAESTRA
    frecuencia_revision = fields.Integer(
        string="Frecuencia de la revisiones (años)"
    )  # Frecuencia en la que se realiza la revisión en años

    fecha_prox_revision = fields.Datetime(
        string="Fecha de la próxima revisión"
    )  # Fecha de la próxima revisión programada con el atributo frecuencia revisión

    revision = fields.Integer(
        readonly=True, string="Número de revisión vigente"
    )  # Numero de revision vigente

    revision_text = fields.Char()  # Campo de apoyo para los reportes

    forma_distribucion = fields.Selection(
        [
            ("Electrónica", "Electrónica"),
            ("Física", "Física"),
            ("Electrónica y Física", "Electrónica y Física"),
        ],
        required=True,
        string="Forma de distribución del documento",
    )  # Forma de distribucion del documento

    # PARA LA LISTA DE CAMBIOS
    numero_cambio = fields.Integer()  # Numero de cambios totales

    is_admin = fields.Boolean(
        compute="_compute_admin", default=True
    )  # Verifica si el usuario tiene permisos administrativos

    def _compute_admin(self):
        for documento in self:
            documento.is_admin = self.env.user.has_group(
                "gestion.group_gestion_administrador"
            )

    is_visible = fields.Boolean(
        compute="_compute_visible", default=True
    )  # Verifica si es documento es visible para el usuario actual

    @api.depends("departamentos", "is_admin")
    def _compute_visible(self):
        for documento in self:
            documento.is_visible = (
                self.env.user.department_id.id in documento.departamentos.ids
            ) or documento.is_admin


# TODO: agregar documento para agregar en la solicitud nueva CHECKKK
# TODO: agregar la condicion de nuevo cuando crea un nuevo documento por solicitud
# TODO: agregar pestaña de cancelados al workflow de la solicitud CHECKKK
# TODO: agregar validacion de que no esta procedente, revisado, aprobado y dar los comentarios de porque no CHECKKK
# TODO: cambiar el flujo de la negacion de aprobacion de borrador a en elaboracion CHECKK NOT TESTED
# TODO: agregar el codigo al nombre al inicio y agregar la revision al final
# TODO: eliminar el numero de cambios en el formulario de publicacion CHECKKK
# TODO: agregar el nombre al reporte de solicitud
# TODO: cambiar las solicitud publicadas a la pantalla de cambios CHECKKK
# TODO: revisar el nombre de la busqueda


class Archivo(models.Model):
    _name = "gestion.archivo"
    _description = "gestion.archivo"

    name = fields.Char()
    fileref = fields.Binary(string="Archivo adjunto")
    solicitud_borrador = fields.Many2one(
        "gestion.solicitud", required=True, string="Solicitud", ondelete="cascade"
    )

    solicitud_elaboracion = fields.Many2one(
        "gestion.solicitud", required=True, string="Solicitud", ondelete="cascade"
    )

    solicitud_revision = fields.Many2one(
        "gestion.solicitud", required=True, string="Solicitud", ondelete="cascade"
    )


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
            ("cancelado", "Cancelado"),
        ],
        default="borrador",
        string="Estatus de la solicitud",
    )
    state_color = fields.Char(compute="_compute_state_color", default="red")

    @api.depends("state")
    def _compute_state_color(self):
        for record in self:
            if record.state == "borrador":
                record.state_color = "color:blue"
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
            elif record.state == "cancelado":
                record.state_color = "color:red"

    gerencia_solicitante = fields.Many2one(
        "hr.department",
        readonly=True,
        default=lambda self: self.env.user.department_id,
        string="Gerencia Solicitante",
    )

    name = fields.Char(compute="_compute_code", default="SOL-NUEVA", string="Codigo")

    @api.depends()
    def _compute_code(self):
        for solicitud in self:
            solicitud.name = f"SOL-{solicitud.id}"

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
        string="Requerimiento de la solicitud",
    )
    # Descripcion del requerimiento
    otros_documentos_description = fields.Text(string="Descripción de otros")

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
    requerimiento = fields.Text(string="Descripción del requerimiento")

    # ARCHIVOS
    archivos = fields.One2many(
        string="Archivos",
        comodel_name="gestion.archivo",
        inverse_name="solicitud_borrador",
    )  # Archivos adjuntos de la solicitud

    documentos_asociados = fields.Many2many(
        comodel_name="gestion.documento",
        relation="solicitud_documento_rel",
        column1="solicitud_id",
        column2="documento_id",
        string="Documentos",
    )  # Documentos masivos asociados a una solicitud

    documentos_nuevos_asociados = fields.Many2many(
        comodel_name="gestion.documento",
        relation="solicitud_documento_nuevo_rel",
        column1="solicitud_nuevo_id",
        column2="documento_nuevo_id",
        string="Documentos",
    )  # Documentos masivos asociados a una solicitud

    archivos_elaboracion = fields.One2many(
        string="Archivos",
        comodel_name="gestion.archivo",
        inverse_name="solicitud_elaboracion",
    )  # Archivos adjuntos de la solicitud

    archivos_revision = fields.One2many(
        string="Archivos",
        comodel_name="gestion.archivo",
        inverse_name="solicitud_revision",
    )  # Archivos adjuntos de la solicitud

    documentos_merged = fields.Many2many(
        comodel_name="gestion.documento",
        compute="_compute_documentos_merged",
        string="Documentos Merged",
    )

    @api.depends("documentos_nuevos_asociados", "documentos_asociados")
    def _compute_documentos_merged(self):
        for record in self:
            record.documentos_merged = (
                record.documentos_nuevos_asociados | record.documentos_asociados
            )

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
    descripcion_no_procede = fields.Text(string="Razones de la no procedencia")

    # fields para cuando no esta conforme con los cambios
    descripcion_no_conforme_revision = fields.Text(
        string="Razones de la no conformidad de revisión"
    )

    # fields para cuando no esta conforme la aprobacion
    descripcion_no_conforme_aprobacion = fields.Text(
        string="Razones de la no conformidad de aprobación"
    )

    # fields para cuando se va a publicar
    descripcion_publicacion = fields.Text(
        string="Explique los cambios a publicar por correo"
    )

    # FECHAS
    fecha_emision = fields.Datetime(string="Fecha de emisión")
    fecha_revision = fields.Datetime(string="Fecha de revisión")
    fecha_aprobacion = fields.Datetime(string="Fecha de aprobación")
    fecha_publicacion = fields.Datetime(string="Fecha de publicación")

    # CAMBIOS
    descripcion_cambios = fields.Text(
        string="Descripción de los cambios para el reporte"
    )
    numero_cambio = fields.Integer()
    numero_cambio_text = fields.Char()
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
            if solicitud.state == "borrador" or solicitud.state == "cancelado":
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
        massive_attachment = []
        for rec in self:
            if rec.archivos:
                # Para cada archivo masivo no creado como un archivo
                for archivo in rec.archivos:
                    attachment = self.env["ir.attachment"].create(
                        {
                            "name": f"Adjunto-{archivo.name}",
                            "datas": archivo.fileref,
                            "type": "binary",
                            "res_id": rec.id,
                        }
                    )
                    massive_attachment.append(attachment)

            # Assuming you want to create a PDF attachment for each record
            for doc in rec.documentos_asociados:
                attachment = self.env["ir.attachment"].create(
                    {
                        "name": f"{rec.name}-{doc.name}.pdf",
                        "datas": doc.fileref,
                        "type": "binary",
                        "res_id": rec.id,
                    }
                )
                massive_attachment.append(attachment)

            # Assuming `template` is defined elsewhere in your code
            template.attachment_ids = [
                (6, 0, [attach.id for attach in massive_attachment])
            ]
            template.send_mail(rec.id, force_send=True)

    # DESDE ADMINISTRADORES EN ADELANTE
    def no_procedente(self):
        if self.is_assigned_coordinator:
            if self.descripcion_no_procede != False:
                self.state = "cancelado"
                template = self.env.ref("gestion.mail_no_procede_template")
                for rec in self:
                    template.send_mail(rec.id, force_send=True)
            else:
                raise ValidationError(
                    _("Se debe dar una descripción de por qué no procede la solicitud")
                )
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
            massive_attachment = []
            for rec in self:
                if rec.archivos_elaboracion:
                    # Para cada archivo masivo no creado como un archivo
                    for archivo in rec.archivos_elaboracion:
                        attachment = self.env["ir.attachment"].create(
                            {
                                "name": f"Adjunto-{archivo.name}",
                                "datas": archivo.fileref,
                                "type": "binary",
                                "res_id": rec.id,
                            }
                        )
                        massive_attachment.append(attachment)
                template.attachment_ids = [
                    (6, 0, [attach.id for attach in massive_attachment])
                ]
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
            if self.descripcion_no_conforme_revision != False:
                self.state = "elaboracion"
                template = self.env.ref("gestion.mail_no_conforme_template")
                massive_attachment = []
                for rec in self:
                    if rec.archivos_revision:
                        # Para cada archivo masivo no creado como un archivo
                        for archivo in rec.archivos_revision:
                            attachment = self.env["ir.attachment"].create(
                                {
                                    "name": f"Adjunto-{archivo.name}",
                                    "datas": archivo.fileref,
                                    "type": "binary",
                                    "res_id": rec.id,
                                }
                            )
                            massive_attachment.append(attachment)
                    template.attachment_ids = [
                        (6, 0, [attach.id for attach in massive_attachment])
                    ]
                    template.send_mail(rec.id, force_send=True)
            else:
                raise ValidationError(
                    _(
                        "Se debe dar una descripción de por qué no está conforme con la elaboración de la solicitud"
                    )
                )
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
            massive_attachment = []
            for rec in self:
                # TODO: fix the use case when the user cant create the document, thats a if CHECCCCCK
                for doc in rec.documentos_asociados:
                    attachment = self.env["ir.attachment"].create(
                        {
                            "name": f"{rec.name}-{doc.name}.pdf",
                            "datas": doc.fileref,
                            "type": "binary",
                            "res_id": rec.id,
                        }
                    )
                    massive_attachment.append(attachment)

                # Assuming `template` is defined elsewhere in your code
                template.attachment_ids = [
                    (6, 0, [attach.id for attach in massive_attachment])
                ]
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
        if self.descripcion_no_conforme_aprobacion != False:
            self.state = "elaboracion"
            self.fecha_revision = False
            self.approved_uid = False
            self.reviewed_uid = False
            self.descripcion_no_procede = False
            self.descripcion_no_conforme_revision = False
            template = self.env.ref("gestion.mail_no_aprobado_template")
            for rec in self:
                template.send_mail(rec.id, force_send=True)
        else:
            raise ValidationError(
                _(
                    "Se debe dar una descripción de por qué no está conforme con la aprobación de la solicitud"
                )
            )

    # DESDE DIRECTORES EN ADELANTE
    def aprobado(self):
        self.state = "aprobado"
        self.fecha_aprobacion = fields.Datetime.now()
        self.approved_uid = self.env.user
        template = self.env.ref("gestion.mail_aprobado_template")
        massive_attachment = []
        for rec in self:
            for doc in rec.documentos_asociados:
                attachment = self.env["ir.attachment"].create(
                    {
                        "name": f"{rec.name}-{doc.name}.pdf",
                        "datas": doc.fileref,
                        "type": "binary",
                        "res_id": rec.id,
                    }
                )
                massive_attachment.append(attachment)
            # Assuming `template` is defined elsewhere in your code
            template.attachment_ids = [
                (6, 0, [attach.id for attach in massive_attachment])
            ]
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
                for documento_nuevo in self.documentos_nuevos_asociados:
                    documento_nuevo.create_uid = self.env.user
                    documento_nuevo.reviewed_uid = self.reviewed_uid
                    documento_nuevo.approved_uid = self.approved_uid
                    documento_nuevo.fecha_elaboracion = self.fecha_publicacion
                    documento_nuevo.fecha_revision = self.fecha_revision
                    documento_nuevo.fecha_prox_revision = (
                        self.fecha_aprobacion
                        + timedelta(documento_nuevo.frecuencia_revision * 365)
                    )
                    documento_nuevo.fecha_aprobacion = self.fecha_aprobacion
                    documento_nuevo.fecha_publicacion = self.fecha_publicacion
                    documento_nuevo.revision = 0
                    documento_nuevo.revision_text = f"0{documento_nuevo.revision}"
                    # NOTE: cuando se crea el documento el cambio es 0
                    documento_nuevo.numero_cambio = 0
                self.numero_cambio = 0
                self.numero_cambio_text = f"0{self.numero_cambio}"
            else:
                for documento in self.documentos_asociados:
                    documento.reviewed_uid = self.reviewed_uid
                    documento.approved_uid = self.approved_uid
                    documento.fecha_revision = self.fecha_revision
                    documento.fecha_prox_revision = self.fecha_aprobacion + timedelta(
                        days=documento.frecuencia_revision * 365
                    )
                    documento.fecha_aprobacion = self.fecha_aprobacion
                    documento.fecha_publicacion = self.fecha_publicacion
                    documento.revision = documento.revision + 1
                    documento.revision_text = f"0{documento.revision}"
                    documento.numero_cambio = documento.numero_cambio + 1
                    # NOTE: cuando no se crea el documento se tiene que aumentar el cambio en 1
                    self.numero_cambio = documento.numero_cambio
                    self.numero_cambio_text = f"0{self.numero_cambio}"
            template = self.env.ref("gestion.mail_publicado_template")
            massive_attachment = []
            for rec in self:
                for doc in rec.documentos_merged:
                    attachment = self.env["ir.attachment"].create(
                        {
                            "name": f"{rec.name}-{doc.name}.pdf",
                            "datas": doc.fileref,
                            "type": "binary",
                            "res_id": rec.id,
                        }
                    )
                    massive_attachment.append(attachment)

                # Assuming `template` is defined elsewhere in your code
                template.attachment_ids = [
                    (6, 0, [attach.id for attach in massive_attachment])
                ]
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


class Cambios(models.Model):
    _name = "gestion.cambios"
    _descrition = "gestion.cambios"

    fecha_revision = fields.Datetime()
    descripcion = fields.Text()
    revision = fields.Integer()


class Departamentos(models.Model):
    _name = "hr.department"
    _inherit = "hr.department"

    code = fields.Char(string="Codigo")


class Tablero(models.Model):
    _name = "gestion.tablero"
    _description = "gestion.tablero"

    def actualizar_lista_maestra(self):
        pass
