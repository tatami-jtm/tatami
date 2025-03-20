import pdfkit
import re
import json
import os
from . import pdftool

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

        elif op == "fscore" or op == "fpoints":
            fighter = self.list.meta._evaluate_fighter_ref(self.list, query)
            scope = query['scope'] if 'scope' in query else 'all'

            if scope not in self.list._score_deductions['calced']:
                return ''
            
            base = self.list._score_deductions['calced'][scope]['base']

            if fighter not in base:
                return ''

            fighter_total = base[fighter]
            if op == 'fscore':
                return str(fighter_total[1])
            else:
                return str(fighter_total[0])

        elif op == "fplacement":
            fighter = self.list.meta._evaluate_fighter_ref(self.list, query)
            if 'scope' not in query:
                if fighter in self.list._score_deductions['results']['first']:
                    return '1.'
                elif fighter in self.list._score_deductions['results']['second']:
                    return '2.'
                elif fighter in self.list._score_deductions['results']['third']:
                    return '3.'
                elif fighter in self.list._score_deductions['results']['fifth']:
                    return '5.'
                else:
                    return ''
            else:
                scope = query['scope']
                order_map = [i[0] for i in self.list._score_deductions['calced'][scope]['order']]
                if fighter in order_map:
                    return str(order_map.index(fighter) + 1) + '.'
                else:   
                    return ''

        elif op == "mscore":
            match = self.list.get_match_by_id(query['match'])
            match_result = match.get_result()

            if not match_result:
                return "-"
            elif query['for'] == 'white':
                return str(match_result.get_score_white())
            elif query['for'] == 'blue':
                return str(match_result.get_score_blue())
        else:
            return f"[invalid operation: {op}]"
        
        return f"[invalid value]"
    
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
    
    def render_image(self, page=1):
        return pdftool.make_image(self.render_pdf(), page - 1)