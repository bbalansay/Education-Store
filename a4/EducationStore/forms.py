from django import forms

class SearchForm(forms.Form):
    """Form for searching Google for eBooks"""
    keywords = forms.CharField(label="Search", max_length=100, required=True)

class EmailForm(forms.Form):
    '''Form for submitting a message to contact us'''
    sender = forms.CharField(label="Your email address", max_length=100, required=True)
    message = forms.CharField(label="Message", max_length=512, help_text="512 characters maximum.", required=True)