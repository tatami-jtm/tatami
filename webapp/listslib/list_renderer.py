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
                elif item['type'] == 'score':
                    self._write_score(new, item)
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
            
            elif item.tag == 'write-score':
                match_id = item.attrib['match-id']
                match = self.lo.get_match_by_id(match_id, informational_only=True)
                if not match:
                    continue

                result = match.get_result()
                if not result:
                    continue

                if item.attrib['for'] == 'white':
                    if result.is_white_winner():
                        score = result.get_score_white()
                    else:
                        score = 0
                elif item.attrib['for'] == 'blue':
                    if result.is_blue_winner():
                        score = result.get_score_blue()
                    else:
                        score = 0
                else:
                    continue

                contents.append({'type': 'score',
                                 'x': float(item.attrib['x']), 'y': float(item.attrib['y']),
                                 'score': score})

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

                if not fighter: continue  # no result yet, ignore

                contents.append({'type': fighter_type,
                                 'x': float(item.attrib['x']), 'y': float(item.attrib['y']),
                                 'fighter': fighter})
        
        return contents
    
    def _write_header(self, pdf, item):
        pdf.set_font("helvetica", "", 9)

        if 'title' in self.params:
            pdf.set_xy(item['x'], item['y'])
            pdf.cell(53, 5.5, self.params['title'], align='L')

        pdf.set_font("helvetica", "B", 13)

        if 'event_class' in self.params:
            pdf.set_xy(item['x'], item['y'] + 6.0)
            pdf.cell(17.25, 12.75, self.params['event_class'], align='L')

        if 'group' in self.params:
            pdf.set_xy(item['x'] + 18, item['y'] + 6.0)
            pdf.cell(35, 12.75, self.params['group'], align='L')
    
    def _write_score(self, pdf, item):
        pdf.set_font("helvetica", "", 10)
        pdf.set_xy(item['x'], item['y'])
        pdf.cell(6.5, 5.5, f"{item['score']}", align='C')

    def _write_fighter(self, pdf, item):  # TODO: cell-ify
        pdf.set_font("helvetica", "", 8.5)
        pdf.text(item['x'], item['y'], item['fighter'].get_name())
    
    def _write_full_fighter(self, pdf, item):
        pdf.set_font("helvetica", "B", 8.5)
        pdf.set_xy(item['x'], item['y'])
        pdf.cell(37, 3.5, item['fighter'].get_name(), align='L')

        pdf.set_font("helvetica", "", 5.5)
        pdf.set_xy(item['x'], item['y']+3.25)
        pdf.cell(37, 2, item['fighter'].get_affil(), align='L')

    def make_pdf(self, params):
        self.params = params
        return pdftool.make_writer(self._make_obj())

    def write_pdf(self, filename, params):
        self.params = params
        return pdftool.write_file(self._make_obj(), filename)

    def make_image(self, params):
        self.params = params
        return pdftool.make_image(self._make_obj())