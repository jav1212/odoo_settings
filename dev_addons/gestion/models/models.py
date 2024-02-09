# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
    documentos = fields.One2many("gestion.documento", "directorio")


class documento(models.Model):
    _name = "gestion.documento"
    _description = "gestion.documento"

    name = fields.Char(
        string="Nombre",
        required=True,
        help="Introduzca el nombre del documento",
    )  # Nombre del documento
    descripcion = fields.Text()  # Descripcion del documento
    directorio = fields.Many2one("gestion.directorio")
    solicitud = fields.One2many("gestion.solicitud", "documento")
    fileref = fields.Binary(string="Archivo")
    is_editable = fields.Boolean(string="Editable", default=False)

    def emitir_solicitud_edicion(self):
        return True


class solicitud(models.Model):
    _name = "gestion.solicitud"
    _description = "gestion.solicitud"

    fecha_emision = fields.Datetime()
    descripcion = fields.Text()
    estado = fields.Char()
    fileref = fields.Binary(string="Archivo")
    documento = fields.Many2one("gestion.documento", readonly=True)


# TODO: this class can be abstract from database model User or Partner
class empleado(models.Model):
    _name = "res.users"
    _inherit = "res.users"

    departamento = fields.Many2one(
        "gestion.departamento", string="Departamento"
    )  # Departamento al que pertenece
    es_coordinador_sgc = fields.Boolean()
    es_gerente = fields.Boolean()
    es_jefe_de_area = fields.Boolean()
    es_director_de_operaciones = fields.Boolean()

    # primer_nombre = fields.Char()  # Primer nombre del empleado
    # primer_apellido = fields.Char()  # Primer apellido del empleado
    # segundo_nombre = fields.Char()  # Segundo nombre del empleado
    # segudo_apellido = fields.Char()  # Segundo apellido del empleado
    # departamento = fields.Char()
    # correo = fields.Char()  # Correo electronico del empleado


# TODO: ask if they want to add more departament
class departamento(models.Model):
    _name = "gestion.departamento"
    _description = "gestion.departamento"

    name = fields.Char(
        string="Nombre",
        required=True,
        help="Introduzca el nombre del departamento",
    )  # Nombre del departamento
    descripcion = fields.Text()  # Descripcion del documento


# TODO: is just to have some nice charts
class gestion(models.Model):
    _name = "gestion.gestion"
    _description = "gestion.gestion"

    name = fields.Char()


class bandeja(models.Model):
    _name = "gestion.bandeja"
    _description = "gestion.bandeja"

    name = fields.Char()


class respuesta(models.Model):
    _name = "gestion.respuesta"
    _description = "gestion.respuesta"

    # TODO: generate a code id for this model

    fecha_emision = fields.Datetime()
    descripcion = fields.Text()
