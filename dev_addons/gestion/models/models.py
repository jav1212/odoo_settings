# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
from datetime import timedelta
import base64
from odoo import fields, http
from odoo.http import request


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

    directorio_hijos = fields.One2many(
        string="Directorios hijos",
        comodel_name="gestion.directorio",
        inverse_name="directorio_padre",
    )  # Directorio al que pertenece

    directorio_padre = fields.Many2one(
        "gestion.directorio", string="Directorio padre"
    )  # Directorio al que pertenece

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

    fileref = fields.Binary(
        string="Archivo adjunto",
        help="Adjunta un archivo en formato PDF, WORD, PPT o EXCEL",
    )  # Archivo de formato pdf

    def descargar_archivo(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        download_url = base_url + "/download/binary/file/%s" % self.id
        return {
            "type": "ir.actions.act_url",
            "url": download_url,
            "target": "self",
        }

    descripcion = fields.Text(
        string="Descripción del directorio",
        help="Introduzca una breve descripción del documento",
    )
    # Descripcion del documento

    directorio = fields.Many2one(
        "gestion.directorio", string="Directorio padre"
    )  # Directorio al que pertenece

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

    # DETALLES DEL FLUJO DE BORRADO DE LA SOLICITUD
    doc_name_auxiliar = fields.Char()
    doc_code_auxiliar = fields.Char()
    doc_revision_auxiliar = fields.Char()
    doc_fecha_revision_auxiliar = fields.Datetime()

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

    # ^ CAMPOS BASICOS DE LA SOLICITUD
    # & STATE = CAMPO DE SELECCION QUE REPRESENTA EL ESTADO ACTUAL DE LA SOLICITUD
    # & GERENCIA_SOLICITANTE = REFERENCIA A LA GERENCIA QUE ESTA QUE ESTA SOLICITANTE
    # & NAME = CAMPO COMPUTADO QUE DENOTA EL NOMBRE DE LA SOLICITUD CON EL ID DE LA MISMA

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
    gerencia_solicitante = fields.Many2one(
        "hr.department",
        readonly=True,
        default=lambda self: self.env.user.department_id,
        string="Gerencia Solicitante",
    )
    name = fields.Char(compute="_compute_name", default="SOL-NUEVA", string="Codigo")

    @api.depends()
    def _compute_name(self):
        for solicitud in self:
            solicitud.name = f"SOL-{solicitud.id}"

    # ^ REFERENCIA AL MODELS ARCHIVO DE LA SIGUIENTE MANERA
    # & REQUERIMIENTO_SELECTION = CAMPO DE SELECCION DEL FORMULARIO DE LA SOLICITUD QUE SE REFIERE AL TIPO DE REQUERIMIENTO
    # & OTROS DOCUMENTOS_DESCRIPTION = CAMPO DE TEXTO EN CASO DE QUE SE SELECCIONE "OTROS" EN EL SELECTOR DEL REQUERIMIENTO_SELECTION
    # & ORIGEN = CAMPO DE SELECCION DE FORMULARIO DE LA SOLICITUD QUE SE REFIERE AL ORIGEN DE LA SOLICITUD
    # & REQUERIMIENTO = DESCRIPCION BASICA DEL REQUERIMIENTO EN GENERAL

    requerimiento_selection = fields.Selection(
        [
            ("Documento nuevo", "Documento nuevo"),
            ("Actualización", "Actualización"),
            ("Modificación", "Modificación"),
            ("Eliminación", "Eliminación"),
            ("Procedimiento", "Procedimiento"),
            ("Instructivo", "Instructivo"),
            ("Formulario", "Formulario"),
            ("Manual", "Manual"),
            ("Políticas", "Políticas"),
            ("Otros", "Otros"),
        ],
        string="Requerimiento de la solicitud",
    )
    otros_documentos_description = fields.Text(string="Descripción de otros")
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
            ("revision por la direccion", "Revisión por la dirección"),
        ],
        string="Origen de la solicitud",
    )
    requerimiento = fields.Text(string="Descripción del requerimiento")

    # ^ REFERENCIA AL MODELS ARCHIVO DE LA SIGUIENTE MANERA
    # & DOCUMENTOS_ASOCIADOS = REFERENCIA A DOCUMENTOS YA PREVIAMENTE CREADOS
    # & DOCUMENTOS_NUEVOS_ASOCIADOS = REFERENCIA A NUEVOS DOCUMENTOS
    # & DOCUMENTOS_MERGED = UNION DE LAS REFERENCIAS ANTERIORES

    documentos_asociados = fields.Many2many(
        comodel_name="gestion.documento",
        relation="solicitud_documento_rel",
        column1="solicitud_id",
        column2="documento_id",
        string="Documentos",
    )

    documentos_nuevos_asociados = fields.Many2many(
        comodel_name="gestion.documento",
        relation="solicitud_documento_nuevo_rel",
        column1="solicitud_nuevo_id",
        column2="documento_nuevo_id",
        string="Documentos",
    )

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

    # ^ REFERENCIA AL MODELS ARCHIVO DE LA SIGUIENTE MANERA
    # & ARCHIVOS = ADJUNTOS VARIOS AL MOMENTO DE CREAR LA SOLICITUD
    # & ARCHIVOS_ELABORACION = ADJUNTOS VARIOS AL MOMENTO DE ELABORAR EL DOCUMENTO DE LA SOLICITUD
    # & ARCHIVOS_REVISION = ADJUNTOS VARIOS AL MOMENTO DE LA REVISION NO CONFORME DE LA SOLICITUD

    archivos = fields.One2many(
        string="Archivos",
        comodel_name="gestion.archivo",
        inverse_name="solicitud_borrador",
    )

    archivos_elaboracion = fields.One2many(
        string="Archivos",
        comodel_name="gestion.archivo",
        inverse_name="solicitud_elaboracion",
    )

    archivos_revision = fields.One2many(
        string="Archivos",
        comodel_name="gestion.archivo",
        inverse_name="solicitud_revision",
    )

    # ^ REFERENCIA AL MODELS RES.USERS DE LA SIGUIENTE MANERA
    # & CREATE_UID = USUARIO CREADOR DE LA SOLICITUD
    # & REVIEWED_UID = USUARIO REVISOR DE LA SOLICITUD
    # & APPROVED_UID = USUARIO APROBADOR DE LA SOLICITUD
    # & PUBLISHED_UID = USUARIO PUBLICADOR DE LA SOLICITUD

    create_uid = fields.Many2one("res.users", string="Creado por", readonly=True)
    reviewed_uid = fields.Many2one("res.users", string="Revisado por", readonly=True)
    approved_uid = fields.Many2one("res.users", string="Aprobado por", readonly=True)
    published_uid = fields.Many2one("res.users", string="Publicado por", readonly=True)

    # TODO: aca tenemos que verificar que si selecciona revisor y aprobador no se seleccione revisor individuales o aprobador individuales y viceversa

    # ^ REFERENCIA AL MODELS RES.USERS DE LA SIGUIENTE MANERA
    # & REVISOR = USUARIO DESIGNADO PARA REVISAR LA SOLICITUD CREADA POR EL COORDINADOR
    # & APROBADOR = USUARIO DESIGNAOD PARA APROBAR LA SOLICITUD CREADA POR EL COORDINADOR
    # & REVISOR_Y_APROBADOR = USUARIO DESIGANDOR PARA REVISAR Y APROBAR LA SOLICITUD POR EL DIRECTOR
    # & COORDINADOR = USUARIO PUBLICADOR DE LA SOLICITUD

    revisor = fields.Many2one(
        "res.users",
        string="Revisor",
    )
    aprobador = fields.Many2one(
        "res.users",
        string="Aprobador",
    )
    revisor_y_aprobador = fields.Many2one(
        "res.users",
        string="Revisor y Aprobador",
    )
    coordinador = fields.Many2one(
        "res.users",
        string="Coordinador asignado",
    )

    # ^ CAMPOS DE DESCRIPCION DESGLOSADOS DE LA SIGUIENTE MANERA
    # & DESCRIPCION_NO_PROCEDE = DESCRIPCION BASICA DE PORQUE NO PROCEDE LA SOLICITUD
    # & DESCRIPCION_NO_CONFORME_REVISION = DESCRIPCION BASICA DE LAS RAZONES POR LAS CUALES NO ESTA CONFORME LA REVISION
    # & DESCRIPCION_NO_CONFORME_APROBACION = DESCRIPCION BASICA DE LAS RAZONES POR LAS CUALES NO ESTA CONFORE LA APROBACION
    # & DESCRIPCION_PUBLICACION = DESCRIPCION BASICA LOS CAMBIOS REALIZADO PARA LAS NOTIFICACIONES POR CORREO

    descripcion_no_procede = fields.Text(string="Razones de la no procedencia")
    descripcion_no_conforme_revision = fields.Text(
        string="Razones de la no conformidad de revisión"
    )
    descripcion_no_conforme_aprobacion = fields.Text(
        string="Razones de la no conformidad de aprobación"
    )
    descripcion_publicacion = fields.Text(
        string="Explique los cambios a publicar por correo"
    )

    # ^ CAMPOS DE FECHA DESGLOSADOS DE LA SIGUIENTE MANERA
    # & FECHA_EMISION = CAPTURA LA FECHA EXACTA DE CUANDO LA SOLICITUD SE MANDA A LA EVALUACION DE PROCEDENCIA
    # & FECHA_REVISION = CAPTURA LA FECHA EXACTA DE CUANDO LA SOLICITUD SE REVISA CONFORME
    # & FECHA_APROBACION = CAPTURA LA FECHA EXACTA DE CUANDO LA SOLICITUD SE APRUEBA CONFORME
    # & FECHA_PUBLICACION = CAPTURA LA FECHA EXACTA DE CUANDO LA SOLICITUD SE PUBLICA

    fecha_emision = fields.Datetime(string="Fecha de emisión")
    fecha_revision = fields.Datetime(string="Fecha de revisión")
    fecha_aprobacion = fields.Datetime(string="Fecha de aprobación")
    fecha_publicacion = fields.Datetime(string="Fecha de publicación")

    # ^ CAMPOS DE FECHA DESGLOSADOS DE LA SIGUIENTE MANERA
    # & DESCRIPCION_CAMBIOS = DESCRIPCION BASICA DE LOS CAMBIOS PARA EL REPORTE DE CAMBIOS
    # & NUMERO_CAMBIO = CAPTURA LA FECHA EXACTA DE CUANDO LA SOLICITUD SE REVISA CONFORME
    # & NUMERO_CAMBIO_TEXT = CAPTURA LA FECHA EXACTA DE CUANDO LA SOLICITUD SE APRUEBA CONFORME

    descripcion_cambios = fields.Text(
        string="Descripción de los cambios para el reporte"
    )
    numero_cambio = fields.Integer()
    numero_cambio_text = fields.Char()

    # ^ CAMPOS DE FECHA DESGLOSADOS DE LA SIGUIENTE MANERA
    # & PROGRESS = CAMPO ADICIONAL PARA MOSTRAR UN PROGRESO DE LA SOLICITUD

    progress = fields.Integer(default=lambda self: 0, compute="_compute_progress")

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

    # ^ CAMPOS DE FECHA DESGLOSADOS DE LA SIGUIENTE MANERA
    # & IS_CREATOR = CAMPO BOOLEANO QUE VERIFICA SI EL USUARIO ACTUAL ES EL CREADOR DE LA SOLICITUD
    # & IS_ASSIGNED_COORDINATOR = CAMPO BOOLEANO QUE VERIFICA SI EL USUARIO ACTUAL ES EL COORDINADOR ASIGANDO PARA LA SOLICITUD

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

    # ^ FUNCIONES LIGADAS A BOTONES EN LA VISTA DE SOLICITUD

    def send_email(self):
        self.state = "solicitado"
        self.fecha_emision = fields.Datetime.now()
        self.create_uid = self.env.user
        template = self.env.ref("gestion.mail_solicitud_template")
        massive_attachment = []
        for rec in self:
            # & SE UNIFICAN TODOS LOS ARCHIVOS ADJUNTOS EN LA CREACION DE LA SOLICITUD
            if rec.archivos:
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

            # & SE UNIFICAN TODOS LOS DOCUMENTOS ASOCIADOS EN LA CREACION DE LA SOLICITUD
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

            # & SE REFERENCIAN AL MAIL TEMPLATE Y SE ENVIAN POSTERIORMENTE
            template.attachment_ids = [
                (6, 0, [attach.id for attach in massive_attachment])
            ]
            template.send_mail(rec.id, force_send=True)

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

    def procedente(self):
        if self.is_assigned_coordinator:
            self.state = "elaboracion"
        else:
            raise ValidationError(
                _(
                    "No eres el coordinador asignado de la solicitud, por lo tanto no puedes evaluar su estado de procedencia"
                )
            )

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

    def mandar_a_aprobacion(self):
        if self.is_assigned_coordinator:
            self.state = "aprobacion"
        else:
            raise ValidationError(
                _(
                    "No eres el coordinador asignado de la solicitud, por lo tanto no puedes mandar la solicitud al estado de aprobacion"
                )
            )

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

    def mandar_a_publicacion(self):
        if self.is_assigned_coordinator:
            self.state = "publicacion"
        else:
            raise ValidationError(
                _(
                    "No eres el coordinador asignado de la solicitud, por lo tanto no puedes mandar la solicitud al estado de publicacion"
                )
            )

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
    _description = "gestion.cambios"

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


class AccessLog(models.Model):
    _name = "gestion.accesslog"
    _description = "gestion.accesslog"


class DownloadLog(models.Model):
    _name = "gestion.downloadlog"
    _description = "gestion.downloadlog"

    downloaded_by = fields.Many2one(
        "res.users", string="Descargado por", readonly=True
    )  # Indica quien esta descargando

    last_update = fields.Datetime(
        default=lambda self: fields.Datetime.now(), string="Fecha de creación"
    )  # Fecha de la descarga
