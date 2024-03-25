# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class Gestion(http.Controller):
    @http.route("/gestion/gestion", auth="public")
    def index(self, **kw):
        return "Hello, world"

    @http.route("/gestion/gestion/objects", auth="public")
    def list(self, **kw):
        return http.request.render(
            "gestion.listing",
            {
                "root": "/gestion/gestion",
                "objects": http.request.env["gestion.gestion"].search([]),
            },
        )

    @http.route(
        '/gestion/gestion/objects/<model("gestion.gestion"):obj>', auth="public"
    )
    def object(self, obj, **kw):
        return http.request.render("gestion.object", {"object": obj})

    @http.route("/download/<model>/<id>/<field>", type="http", auth="user")
    def download(self, model, id, field, **kw):
        record = request.env[model].sudo().browse(int(id))

        if not record or field not in record:
            return request.not_found()

        field_data = record[field]
        if not isinstance(field_data, bytes):
            raise ValueError(
                "The field '%s' does not contain byte stream data." % field
            )

        filename = record.name or "download.bin"

        return request.make_response(
            field_data,
            headers=[
                ("Content-Type", "application/octet-stream"),
                ("Content-Disposition", f'attachment; filename="{filename}"'),
            ],
        )
