import pdfkit
import re
import json
import os

class ListRenderer:

    TOKEN_REGEX = re.compile(r'%%([a-z]+)\:(.+?)%%')

    def __init__(self, list_, event, group, served=False):
        self.list = list_
        self.event = event
        self.group = group
        self.served = served

    def render_html(self):
        result = []

        for template in self.list.get_included_templates():
            with open(f'listslib/templates/{template}.html', 'r') as f:
                template_html = f.read()

            result.append(self.render_partial(template_html))

        return "\n\n".join(result)
    
    def render_partial(self, partial):
        return re.sub(self.TOKEN_REGEX, self._apply_code, partial)
    
    def _apply_code(self, match):
        op, query = match[1], match[2]
        query = json.loads(query)

        if op == "fname":
            return self.list.meta._evaluate_fighter_ref(self.list, query).get_name()
        elif op == "fassoc":
            return self.list.meta._evaluate_fighter_ref(self.list, query).get_affil()
        else:
            return f"[invalid operation: {op}]"
    
    def render_html_template(self):
        with open('listslib/templates/base.html', 'r') as f:
            t = f.read()
        
        t = t.replace("%%listname%%", self.list.get_name())
        t = t.replace("%%event%%", self.event.title)
        if self.group.assigned_to_position is None:
            t = t.replace("%%mat%%", "")
        else:
            t = t.replace("%%mat%%", self.group.assigned_to_position.title)
        t = t.replace("%%eventclass%%", self.group.event_class.short_title)
        t = t.replace("%%group%%", self.group.cut_title())
        t = t.replace("%%body%%", self.render_html())

        if self.served:
            t = t.replace("%%css%%", '<link rel="stylesheet" href="/static/application/lists.css">')
        else:
            with open("./static/application/lists.css") as f:
                css_file = f.read()
            
            css_file = css_file.replace("url('../", "url('file://" + os.path.abspath("./static/") + '/')
            t = t.replace("%%css%%", '<style>' + css_file + '</style>')

        return t
    
    def render_pdf(self):
        return pdfkit.from_string(self.render_html_template(), options={
            "title": "Teilnahmebestätigung",
            'margin-top': '10mm',
            'margin-right': '15mm',
            'margin-bottom': '15mm',
            'margin-left': '15mm',
            'encoding': "UTF-8",
            'quiet': '',
            "enable-local-file-access": "",
        })