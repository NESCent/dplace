from django.contrib.gis import forms
from django.forms.models import ModelChoiceField, ModelForm
from dplace_app.models import EAVariableDescription, Environmental

class EASearchForm(forms.Form):
	variable = ModelChoiceField(queryset=EAVariableDescription.objects.all())
	q = forms.CharField(max_length=20)

class EnvironmentalForm(ModelForm):
	def get_queryset(self):
		return Environmental.objects().select_related('society').select_related('iso_code').all()

	class Meta:
		model = Environmental
		exclude = ['reported_location', 'actual_location']

class GeoForm(forms.Form):
	region = forms.PolygonField(widget=forms.OpenLayersWidget(attrs={'map_width': 500, 'map_height': 500}))
