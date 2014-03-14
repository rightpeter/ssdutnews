#!/usr/bin/env python
#-*- coding: utf-8 -*-

import tornado

class Pagination(tornado.web.UIModule):
    def render(self, total_pages, current_page, visible_pages):
        return self.render_string("pagination.html", total_pages=total_pages,
                current_page=current_page, visible_pages=visible_pages)
