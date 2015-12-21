from rest_framework import renderers
import csv
from six import StringIO, text_type
from models import *

class DPLACECSVResults(object):
    def __init__(self,data):
        self.data = data
        self.field_map = dict()
        self.field_names = ['Society name', 'Society source', 'Longitude', 'Latitude',
                            'ISO code', 'Language name']
        self.rows = []
        self.parse()
        self.encode_field_names()
        self.flatten()

    def field_names_for_cultural_variable(self, variable):
        return {'code' : "Code: %s %s" % (variable['label'], variable['name']),
                'description': "Description: %s %s" % (variable['label'], variable['name']),
                'comments': "Comment: %s %s" % (variable['label'], variable['name']),
                'focal_year': "Focal Year: %s %s" % (variable['label'], variable['name']),
                'sources': "References: %s %s" % (variable['label'], variable['name'])}
    def field_names_for_environmental_variable(self, variable):
        return {'name' : "%s (%s)" % (variable['name'], variable['units']) }

    def parse(self):
        # get IDs for variable descriptions
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
                self.field_names.append(field_names['sources'])
        if 'environmental_variables' in self.data:
            self.field_map['environmental_variables'] = dict()
            for v in self.data['environmental_variables']:
                field_names = self.field_names_for_environmental_variable(v)
                self.field_map['environmental_variables'][v['id']] = field_names
                self.field_names.append(field_names['name'])

    def encode_field_names(self):
        # Field names must also be utf-8 encoded
        self.field_names = [field.encode("utf-8") for field in self.field_names]

    def flatten(self):
    # data is a dictionary with a list of societies
        for item in self.data['societies']:
            row = dict()
            # Merge in society data
            society = item['society']
            row['Society name'] = society['name']
            row ['Society source'] = society['source']['name']
            row['Longitude'] = "" if society['location'] is None else society['location']['coordinates'][0]
            row['Latitude'] = "" if society['location'] is None else society['location']['coordinates'][1]
            if society['language'] is not None and 'name' in society['language']:
                row['ISO code'] = society['language']['iso_code']
                row['Language name'] = society['language']['name']
            else:
                row['Language name'] = ""
            # geographic - only one
            geographic_regions = item['geographic_regions']
            if len(geographic_regions) == 1:
                geographic_region = geographic_regions[0]
                row['Continent'] = geographic_region['continent']
                row['Region name'] = geographic_region['region_nam']
            # cultural
            cultural_trait_values = item['variable_coded_values']
            for cultural_trait_value in cultural_trait_values:
                # Figure out the column name
                variable_id = cultural_trait_value['variable']
                field_names = self.field_map['variable_descriptions'][variable_id]
                row[field_names['code']] = cultural_trait_value['coded_value']
                row[field_names['focal_year']] = cultural_trait_value['focal_year']
                if 'code_description' in cultural_trait_value:
                    try:
                        row[field_names['description']] = cultural_trait_value['code_description']['description']
                    except:
                        break
                row[field_names['comments']] = cultural_trait_value['comment']
                row[field_names['sources']] = ''.join([x['author']+'('+x['year']+'); ' for x in cultural_trait_value['references']])
            # environmental
            environmental_values = item['environmental_values']
            for environmental_value in environmental_values:
                variable_id = environmental_value['variable']
                field_names = self.field_map['environmental_variables'][variable_id]
                row[field_names['name']] = environmental_value['value']
            # language - already have
            #
            self.rows.append(row)

def encode_if_text(val):
    return val.encode('utf-8') if isinstance(val, text_type) else val

def encode_rowdict(rowdict):
    encoded = dict()
    for k in rowdict:
        encoded_k = encode_if_text(k)
        elem = rowdict[k]
        encoded[encoded_k] = encode_if_text(elem)
    return encoded

class DPLACECsvRenderer(renderers.BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        '''
        Renders a list of SocietyResultSets to CSV
        '''
        if data is None:
            return ''
        results = DPLACECSVResults(data)

        csv_buffer = StringIO()
        csv_writer = csv.DictWriter(csv_buffer, results.field_names)
        cite_writer = csv.writer(csv_buffer)
        cite_writer.writerow(['To cite D-PLACE: Research that uses data from D-PLACE should cite both the original source of the coded data and this paper (e.g., for anthropological data from the Ethnographic Atlas: "Murdock (1962-1971); Kirby et al n.d.)." In the reference list, the D-PLACE URL (www.d-place.org) and the date the data were downloaded should be given.']) #add in 'How to cite' here
        csv_writer.writeheader()
        for row in results.rows:
            csv_writer.writerow(encode_rowdict(row))

        return csv_buffer.getvalue()
        
class ZipRenderer(renderers.BaseRenderer):

    media_type = 'application/zip'
    format = 'zip'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        '''
        Renders zip file for phylogeny download
        '''
        import zipfile
        if data is None:
            return ''
        
        s = StringIO()
        try:
            zf = zipfile.ZipFile(s, "w") 
            if 'legends' in data:
                for l in data['legends']:
                    if 'svg' in l:
                        if 'name' in l:
                            zf.writestr(str(l['name']), str(l['svg']))
            if 'tree' in data:
                if 'name' in data:
                    zf.writestr(str(data['name']), str(data['tree']))
                else:
                    zf.writestr('tree.svg', str(data['tree']))
        finally:
            zf.close()
        return s.getvalue()
