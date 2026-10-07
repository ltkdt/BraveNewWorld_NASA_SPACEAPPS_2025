from django import forms
from datetime import date
# Create custom widget in your forms.py file.
class DateInput(forms.DateInput):
    input_type = 'date'

default_start_date = date(2007,1,1)
default_end_date = date.today()

class LastActiveForm(forms.Form):
    """
    Last Active Date Form
    """
    start_active = forms.DateField(widget=DateInput, label="Start Date", initial=default_start_date)
    end_active = forms.DateField(widget=DateInput, label="End Date", initial=default_end_date)