from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, ReviewAssignment


class CustomUserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'affiliation', 'orcid_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            ('AUTHOR', 'Author (Submit Research Papers)'),
            ('REVIEWER', 'Peer Reviewer'),
        ]
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ArticleSubmissionForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'authors_list', 'abstract', 'keywords', 'manuscript_pdf']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full title of the research paper'
            }),
            'authors_list': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Lakhan Prajapati, Dr. R. K. Sharma'
            }),
            'abstract': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Paste your complete research abstract here...'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Machine Learning, IoT, Django, Renewable Energy'
            }),
            'manuscript_pdf': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewAssignment
        fields = ['recommendation', 'comments']
        widgets = {
            'recommendation': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Provide constructive peer-review feedback for the authors and editor...'
            }),
        }