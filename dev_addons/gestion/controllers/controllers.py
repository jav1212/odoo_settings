# -*- coding: utf-8 -*-
from odoo.http import request, content_disposition
import datetime
from odoo import http
from odoo.http import request
from werkzeug.wrappers import Response
import base64


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

    @http.route(
        '/download/binary/file/<model("gestion.documento"):record>',
        type="http",
        auth="public",
    )
    def saveas(self, record):
        file_content = base64.b64decode(record.fileref)
        headers = [
            ("Content-Type", "application/octet-stream"),
            ("Content-Disposition", "attachment; filename=%s" % record.name),
        ]
        return request.make_response(file_content, headers=headers)
