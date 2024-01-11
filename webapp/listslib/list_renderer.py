from os import path as osp
from . import pdftool

TEMPLATES_FILE = osp.join(osp.dirname(__file__), 'templates.pdf')

class ListRenderer:

    def __init__(self, lo):
        self.lo = lo

    def _make_obj(self):
        old = pdftool.load_file(TEMPLATES_FILE)
        pagetable, new = self._make_render()
        prepared_new = pdftool.prepare_new(new)

        if not pagetable:
            raise ValueError('no PDF rendering possible for this list type')
        else:
            output = pdftool.merge_files(old, prepared_new, *pagetable)
        
        return output

    def _make_render(self):
        new = pdftool.create_new()
        pagetable = []

        for page in self._get_pages():
            if len(pagetable):
                new.add_page()
            
            pagetable.append(page['no'])

            for item in page['contents']:
                if item['type'] == 'header':
                    self._write_header(new, item)
                elif item['type'] == 'fighter':
                    self._write_fighter(new, item)
                elif item['type'] == 'full_fighter':
                    self._write_full_fighter(new, item)

        return pagetable, new # (page index, page obj)
    
    def _get_pages(self):
        pages = []

        for page in self.lo.meta._com.findall('display/template'):
            pages.append({
                'no': int(page.attrib['page']) - 1,
                'contents': self._get_contents(page)
            })

        return pages
    
    def _get_contents(self, page):
        contents = []

        for item in page:
            if item.tag == 'write-header':
                contents.append({'type': 'header',
                                 'x': float(item.attrib['x']), 'y': float(item.attrib['y'])})

            elif item.tag == 'write-fighter':
                reference = item[0]

                if reference.tag == 'fighter':
                    fighter_ref = {'fighter': int(reference.attrib['id'])}
                    if 'playoff' in reference.attrib:
                        fighter_ref['playoff'] = reference.attrib['playoff']
        
                elif reference.tag == 'winner':
                    fighter_ref = {'winner': reference.attrib['match-id']}

                elif reference.tag == 'loser':
                    fighter_ref = {'loser': reference.attrib['match-id']}

                elif reference.tag == 'placed':
                    fighter_ref = {'placed': reference.attrib['on']}
                    if 'group' in reference.attrib:
                        fighter_ref['group'] = reference.attrib['group']

                fighter = self.lo.meta._evaluate_fighter_ref(self.lo, fighter_ref)
                fighter_type = 'fighter' if item.attrib['type'] != 'full' else 'full_fighter'

                contents.append({'type': fighter_type,
                                 'x': float(item.attrib['x']), 'y': float(item.attrib['y']),
                                 'fighter': fighter})
        
        return contents
    
    def _write_header(self, pdf, item):
        pdf.set_font("helvetica", "", 9)

        if 'title' in self.params:
            pdf.text(item['x'], item['y'], self.params['title'])

        pdf.set_font("helvetica", "B", 13)

        if 'event_class' in self.params:
            pdf.text(item['x'], item['y'] + 10.0, self.params['event_class'])

        if 'group' in self.params:
            pdf.text(item['x'] + 19.0, item['y'] + 10.0, self.params['group'])
    
    def _write_fighter(self, pdf, item):
        pdf.set_font("helvetica", "", 8.5)
        pdf.text(item['x'], item['y'], item['fighter'].get_name())
    
    def _write_full_fighter(self, pdf, item):
        pdf.set_font("helvetica", "B", 8.5)
        pdf.text(item['x'], item['y'], item['fighter'].get_name())
        pdf.set_font("helvetica", "", 5.5)
        pdf.text(item['x'], item['y']+2, item['fighter'].get_affil())

    def make_pdf(self, params):
        self.params = params
        return pdftool.make_writer(self._make_obj())

    def write_pdf(self, filename, params):
        self.params = params
        return pdftool.write_file(self._make_obj(), filename)

    def make_image(self, params):
        self.params = params
        return pdftool.make_image(self._make_obj())