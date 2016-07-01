import csv
import zipfile

from rest_framework import renderers
from six import StringIO, text_type

# TODO: add in 'How to cite' here
CSV_PREAMBLE = """
Research that uses data from D-PLACE should cite both the original source(s) of 
the data and the paper by Kirby et al. in which D-PLACE was first presented 
(e.g., research using cultural data from the Binford Hunter-Gatherer dataset: "Binford (2001); 
Binford and Johnson (2006); Kirby et al. Submitted)." The reference list should include the date data were 
accessed and URL for D-PLACE (https://d-place.org), in addition to the full references for Binford (2001), 
Binford and Johnson (2006), and Kirby et al. Submitted. 
""".replace("\n", " ").strip().lstrip()


class DPLACECSVResults(object):
    def __init__(self, data):
        self.data = data
        self.field_map = dict()
        self.field_names = [
            'Source',
            'Preferred society name',
            'Society id',
            'Cross-dataset id',
            'Original society name',
            'Revised latitude',
            'Revised longitude',
            'Original latitude',
            'Original longitude',
            'Glottolog language/dialect id',
            'Glottolog language/dialect name',
            'ISO code',
            'Language family',
            ]
        self.rows = []
        self.parse()
        self.encode_field_names()
        self.flatten()

    def field_names_for_cultural_variable(self, variable):
        v = "%s %s" % (variable['label'], variable['name'])
        return {
            'code': "Code: %s" % v,
            'description': "Description: %s" % v,
            'comments': "Comment: %s" % v,
            'subcase': "Subcase: %s" % v,
            'focal_year': "Focal Year: %s" % v,
            'sources': "References: %s" % v,
        }

    def field_names_for_environmental_variable(self, variable):
        return {
            'name': "Variable: %s (%s)" % (variable['name'], variable['units']),
            'comments': "Comment: %s (%s)" % (variable['name'], variable['units'])
        }

    def parse(self):
        if 'geographic_regions' in self.data:
            if len(self.data['geographic_regions']) > 0:
                self.field_names.append('Continent')
                self.field_names.append('Region name')

        if 'variable_descriptions' in self.data:
            self.field_map['variable_descriptions'] = dict()
            for v in self.data['variable_descriptions']:
                field_names = self.field_names_for_cultural_variable(v['variable'])
                self.field_map['variable_descriptions'][v['variable']['id']] = field_names
                self.field_names.append(field_names['focal_year'])
                self.field_names.append(field_names['code'])
                self.field_names.append(field_names['description'])
                self.field_names.append(field_names['comments'])
                self.field_names.append(field_names['subcase'])
                self.field_names.append(field_names['sources'])

        if 'environmental_variables' in self.data:
            self.field_map['environmental_variables'] = dict()
            for v in self.data['environmental_variables']:
                field_names = self.field_names_for_environmental_variable(v)
                self.field_map['environmental_variables'][v['id']] = field_names
                self.field_names.append(field_names['name'])
                self.field_names.append(field_names['comments'])

    def encode_field_names(self):
        # Field names must also be utf-8 encoded
        self.field_names = [
            field.encode("utf-8") for field in self.field_names
        ]

    def flatten(self):
        # data is a dictionary with a list of societies
        for item in self.data.get('societies', []):
            row = dict()
            # Merge in society data
            society = item['society']
            row['Source'] = society['source']['name']
            row['Preferred society name'] = society['name']
            row['Society id'] = society['ext_id']
            row['Cross-dataset id'] = society['xd_id']
            row['Original society name'] = society['original_name']
            row['Revised longitude'] = "" if society['location'] is None \
                else society['location']['coordinates'][0]
            row['Revised latitude'] = "" if society['location'] is None \
                else society['location']['coordinates'][1]
            row['Original longitude'] = "" if society['original_location'] is None \
                else society['original_location']['coordinates'][0]
            row['Original latitude'] = "" if society['original_location'] is None \
                else society['original_location']['coordinates'][1]
            if society['language'] is not None and 'name' in society['language']:
                row['ISO code'] = society['language']['iso_code']
                row['Glottolog language/dialect name'] = society['language']['name']
                row['Glottolog language/dialect id'] = society['language']['glotto_code']
                if 'family' in society['language'] \
                    and 'name' in society['language']['family']:
                        row['Language family'] = society['language']['family']['name']
            else:
                row['Glottolog language/dialect name'] = ""
                row['Glottolog language/dialect id'] = ""
                row['Language family'] = ""
            
            if society['region']:
                row['Continent'] = society['region']['continent']
                row['Region name'] = society['region']['region_nam']

            # cultural
            cultural_trait_values = item['variable_coded_values']
            extra_rows = []  # Binford societies may have multiple values for one variable
            for cultural_trait_value in cultural_trait_values:
                # Figure out the column name
                variable_id = cultural_trait_value['variable']
                field_names = self.field_map['variable_descriptions'][variable_id]
                if field_names['code'] in row:
                    if 'code_description' in cultural_trait_value:
                        try:
                            description = \
                                cultural_trait_value['code_description']['description']
                        except:
                            description = ""
                    else:
                        description = ""
                    extra_rows.append(dict({
                        'Preferred society name': society['name'],
                        'Society id': society['ext_id'],
                        'Cross-dataset id': society['xd_id'],
                        'Original society name': society['original_name'],
                        'Revised longitude': "" if society['location'] is None \
                            else society['location']['coordinates'][0],
                        'Revised latitude': "" if society['location'] is None \
                            else society['location']['coordinates'][1],
                        'Original longitude': "" if society['original_location'] is None \
                            else society['original_location']['coordinates'][0],
                        'Original latitude': "" if society['original_location'] is None \
                            else society['original_location']['coordinates'][0],
                        'Source': society['source']['name'],
                        'ISO code': "" if society['language'] is None \
                            else society['language']['iso_code'],
                        'Glottolog language/dialect name': "" if (society['language'] is None or (society['language'] and 'name' not in society['language'])) \
                            else society['language']['name'],
                        'Glottolog language/dialect id': "" if society['language'] is None \
                            else society['language']['glotto_code'],
                        'Language family': "" if (society['language'] is None or (society['language'] and ('family' not in society['language'] or (society['language']['family'] and 'name' not in society['language']['family'])))) \
                            else society['language']['family']['name'],
                        
                        field_names['code']: cultural_trait_value['coded_value'],
                        field_names['description']: description,
                        field_names['focal_year']: cultural_trait_value['focal_year'],
                        field_names['comments']: cultural_trait_value['comment'],
                        field_names['subcase']: cultural_trait_value['subcase'],
                        field_names['sources']: ''.join(
                            [x['author'] + '(' + x['year'] + '); '
                             for x in cultural_trait_value['references']])
                    }))
                    continue

                row[field_names['code']] = cultural_trait_value['coded_value']
                row[field_names['focal_year']] = cultural_trait_value['focal_year']
                if 'code_description' in cultural_trait_value:
                    try:
                        row[field_names['description']] = \
                            cultural_trait_value['code_description']['description']
                    except:
                        row[field_names['description']] = ''
                row[field_names['comments']] = \
                    cultural_trait_value['comment']
                row [field_names['subcase']] = \
                    cultural_trait_value['subcase']
                row[field_names['sources']] = ''.join([
                    x['author'] + '(' + x['year'] + '); '
                    for x in cultural_trait_value['references']])
            # environmental
            environmental_values = item['environmental_values']
            for environmental_value in environmental_values:
                variable_id = environmental_value['variable']
                field_names = self.field_map['environmental_variables'][variable_id]
                row[field_names['name']] = environmental_value['value']
                row[field_names['comments']] = environmental_value['comment']
            # language - already have
            #
            self.rows.append(row)
            for extra in extra_rows:
                self.rows.append(extra)


def encode_if_text(val):
    return val.encode('utf-8') if isinstance(val, text_type) else val


def encode_rowdict(rowdict):
    encoded = dict()
    for k in rowdict:
        encoded_k = encode_if_text(k)
        elem = rowdict[k]
        encoded[encoded_k] = encode_if_text(elem)
    return encoded


class DPLACECSVRenderer(renderers.BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        "Renders a list of SocietyResultSets to CSV"
        if data is None:
            return ''
        results = DPLACECSVResults(data)
        csv_buffer = StringIO()
        csv_writer = csv.DictWriter(
            csv_buffer, results.field_names, extrasaction='ignore')
        cite_writer = csv.writer(csv_buffer)
        cite_writer.writerow([CSV_PREAMBLE])
        csv_writer.writeheader()
        for row in results.rows:
            csv_writer.writerow(encode_rowdict(row))

        return csv_buffer.getvalue()


class ZipRenderer(renderers.BaseRenderer):
    media_type = 'application/zip'
    format = 'zip'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Renders zip file for phylogeny download"""
        if data is None:
            return ''

        s = StringIO()
        zf = zipfile.ZipFile(s, "w")
        try:
            if 'legends' in data:
                for l in data['legends'] or []:
                    if 'svg' in l:
                        if 'name' in l:
                            zf.writestr(
                                l['name'].encode('utf-8'),
                                l['svg'].encode('utf-8')
                            )
            if 'tree' in data:
                if 'name' in data:
                    zf.writestr(
                        (data['name'] or 'x').encode('utf-8'),
                        (data['tree'] or '').encode('utf-8'))
                else:
                    zf.writestr('tree.svg', (data['tree'] or '').encode('utf-8'))
        finally:
            zf.close()
        return s.getvalue()
