from os import path as osp
from . import pdftool
from .fighter import BlankFighter

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
                elif item['type'] == 'total':
                    self._write_total(new, item)
                elif item['type'] == 'fighter':
                    self._write_fighter(new, item)
                elif item['type'] == 'short_fighter':
                    self._write_short_fighter(new, item)
                elif item['type'] == 'full_fighter':
                    self._write_full_fighter(new, item)                

            if 'draft' in self.params:
                self._write_draft(new)
            elif 'mat' in self.params:
                self._write_mat(new)

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

                if result.get_absolute_winner():
                    score = 'X'

                contents.append({'type': 'score',
                                 'x': float(item.attrib['x']), 'y': float(item.attrib['y']),
                                 'score': score})
            
            elif item.tag == 'write-total':
                if 'scope' not in item.attrib:
                    if not self.lo.completed(): continue
                    if not self.lo.score(): continue
                else:
                    self.lo.score()
                    if not self.lo._score_deductions['calced']: continue

                fighter_id = item.attrib['fighter-id']
                fighter_ref = {'fighter': int(fighter_id)}
                fighter = self.lo.meta._evaluate_fighter_ref(self.lo, fighter_ref)

                if item.attrib['option'] == 'placement':
                    if 'scope' not in item.attrib:
                        if fighter in self.lo._score_deductions['results']['first']:
                            fighter_total = '1.'
                        elif fighter in self.lo._score_deductions['results']['second']:
                            fighter_total = '2.'
                        elif fighter in self.lo._score_deductions['results']['third']:
                            fighter_total = '3.'
                        elif fighter in self.lo._score_deductions['results']['fifth']:
                            fighter_total = '5.'
                        else:
                            continue
                    else:
                        scope = item.attrib['scope']
                        order_map = [i[0] for i in self.lo._score_deductions['calced'][scope]['order']]
                        if fighter in order_map:
                            fighter_total = str(order_map.index(fighter) + 1) + '.'
                        else:   
                            continue
                else:
                    if 'scope' in item.attrib:
                        scope = item.attrib['scope']
                    else:
                        scope = 'all'

                    if scope not in self.lo._score_deductions['calced']:
                        continue

                    base = self.lo._score_deductions['calced'][scope]['base']

                    if fighter not in base:
                        continue

                    fighter_total = base[fighter]
                    if item.attrib['option'] == 'score':
                        fighter_total = fighter_total[1]
                    else:
                        fighter_total = fighter_total[0]

                contents.append({'type': 'total',
                                'x': float(item.attrib['x']), 'y': float(item.attrib['y']),
                                'score': fighter_total})

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
                    if 'among' not in reference.attrib:
                        if not self.lo.completed(): continue
                        if not self.lo.score(): continue

                        fighter_ref = {'placed': int(reference.attrib['on'])}
                    else:
                        self.lo.score()
                        if not self.lo._score_deductions['calced']: continue

                        fighter_ref = {'placed': int(reference.attrib['on']), 'among': reference.attrib['among']}

                fighter = self.lo.meta._evaluate_fighter_ref(self.lo, fighter_ref)

                if item.attrib['type'] == 'full':
                    fighter_type = 'full_fighter'
                elif item.attrib['type'] == 'short':
                    fighter_type = 'short_fighter'
                else:
                    fighter_type = 'fighter'

                if not fighter: continue  # no result yet, ignore

                contents.append({'type': fighter_type,
                                 'x': float(item.attrib['x']), 'y': float(item.attrib['y']),
                                 'fighter': fighter})
        
        return contents
    
    def _write_header(self, pdf, item):
        pdf.set_font("helvetica", "", 9)

        if 'title' in self.params:
            pdf.set_xy(item['x'], item['y'])
            pdf.cell(53, 5.5, self.params['title'], align='L', fill=('debug' in self.params))

        pdf.set_font("helvetica", "B", 13)

        if 'event_class' in self.params:
            pdf.set_xy(item['x'], item['y'] + 6.0)
            pdf.cell(17.25, 12.75, self.params['event_class'], align='L', fill=('debug' in self.params))

        if 'group' in self.params:
            pdf.set_xy(item['x'] + 18, item['y'] + 6.0)
            pdf.cell(35, 12.75, self.params['group'], align='L', fill=('debug' in self.params))
    
    def _write_score(self, pdf, item):
        pdf.set_font("helvetica", "", 10)
        pdf.set_xy(item['x'], item['y'])
        pdf.cell(6.5, 5.5, f"{item['score']}", align='C', fill=('debug' in self.params))
    
    def _write_total(self, pdf, item):
        pdf.set_font("helvetica", "", 10)
        pdf.set_xy(item['x'], item['y'])
        pdf.cell(8.25, 5.5, f"{item['score']}", align='C', fill=('debug' in self.params))

    def _write_short_fighter(self, pdf, item):
        pdf.set_font("helvetica", "", 8)
        pdf.set_xy(item['x'], item['y'])
        pdf.cell(31, 5, item['fighter'].get_name(), align='L', fill=('debug' in self.params))

    def _write_fighter(self, pdf, item):
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_xy(item['x'], item['y'])

        pdf.cell(37, 5, item['fighter'].get_name(), align='L', fill=('debug' in self.params))
    
    def _write_full_fighter(self, pdf, item):
        if item['fighter'].is_disqualified() and not item['fighter'] == BlankFighter:
            pdf.set_text_color(255, 0, 0)

        pdf.set_font("helvetica", "B", 8.5)
        pdf.set_xy(item['x'], item['y'])
        pdf.cell(37, 3.5, self._limit(item['fighter'].get_name(), 21), align='L', fill=('debug' in self.params))

        pdf.set_font("helvetica", "", 5.5)
        pdf.set_xy(item['x'], item['y']+3.25)
        pdf.cell(37, 2, item['fighter'].get_affil(), align='L', fill=('debug' in self.params))

        if item['fighter'].is_disqualified() and not item['fighter'] == BlankFighter:
            pdf.set_font("helvetica", "B", 14)
            pdf.set_xy(item['x'] + 33, item['y'])
            pdf.cell(4.25, 5.5, 'H', align='C', fill=('debug' in self.params))

            pdf.set_text_color(0, 0, 0)

    def _write_qrcode(self, pdf):
        pass

    def _write_mat(self, pdf):
        pdf.set_font("helvetica", "", 10)
        pdf.set_xy(18, 5)
        pdf.cell(174, 10, self.params['mat'], align='C')

    def _write_draft(self, pdf):
        pdf.set_text_color(255, 0, 0)
        pdf.set_font("helvetica", "B", 50)
        with pdf.local_context(fill_opacity=0.25):
            i = 0
            for y in range(0, 400, 40):
                pdf.set_xy(10, 15 + y)
                pdf.cell(190, 20, "Entwurf", align=['L', 'R', 'C'][i])
                i += 1
                i %= 3

        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(0, 0)

    def _limit(self, text, length):
        if len(text) <= length:
            return text
        
        return text[:length - 3].strip() + '...'

    def make_pdf(self, params):
        self.params = params
        return pdftool.make_writer(self._make_obj())

    def write_pdf(self, filename, params):
        self.params = params
        return pdftool.write_file(self._make_obj(), filename)

    def make_image(self, params):
        self.params = params
        page = 1
        if 'page' in params:
            page = params['page']
        return pdftool.make_image(self._make_obj(), page - 1)