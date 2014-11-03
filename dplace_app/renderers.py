from rest_framework import renderers
import csv
from six import StringIO, text_type

class DPLACECSVResults(object):
    def __init__(self,data):
        self.data = data
        self.field_map = dict()
        self.field_names = ['Society name', 'Society source', 'Longitude', 'Latitude',
                            'ISO code', 'Language name']
        self.rows = []
        self.parse()
        self.flatten()

    def field_names_for_cultural_variable(self, variable):
        return {'code' : "Code: %s %s" % (variable['label'], variable['name']),
                'description': "Description: %s %s" % (variable['label'], variable['name'])}
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
                field_names = self.field_names_for_cultural_variable(v)
                self.field_map['variable_descriptions'][v['id']] = field_names
                self.field_names.append(field_names['code'])
                self.field_names.append(field_names['description'])
        if 'environmental_variables' in self.data:
            self.field_map['environmental_variables'] = dict()
            for v in self.data['environmental_variables']:
                field_names = self.field_names_for_environmental_variable(v)
                self.field_map['environmental_variables'][v['id']] = field_names
                self.field_names.append(field_names['name'])

    def flatten(self):
    # data is a dictionary with a list of societies
        for item in self.data['societies']:
            row = dict()
            # Merge in society data
            society = item['society']
            row['Society name'] = society['name']
            row['Society source'] = society['source']
            row['Longitude'] = society['location']['coordinates'][0]
            row['Latitude'] = society['location']['coordinates'][1]
            row['ISO code'] = society['iso_code']
            if society['language'] is not None and 'name' in society['language']:
                row['Language name'] = society['language']['name']
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
                if 'code_description' in cultural_trait_value:
                    row[field_names['description']] = cultural_trait_value['code_description']['description']
            # environmental
            environmental_values = item['environmental_values']
            for environmental_value in environmental_values:
                variable_id = environmental_value['variable']
                field_names = self.field_map['environmental_variables'][variable_id]
                row[field_names['name']] = environmental_value['value']
            # language - already have
            #
            self.rows.append(row)

def encode_rowdict(rowdict):
    encoded = dict()
    for k in rowdict:
        elem = rowdict[k]
        encoded[k] = elem.encode('utf-8') if isinstance(elem, text_type) else elem
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
        csv_writer.writeheader()
        for row in results.rows:
            csv_writer.writerow(encode_rowdict(row))

        return csv_buffer.getvalue()