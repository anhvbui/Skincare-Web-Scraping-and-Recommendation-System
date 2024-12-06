from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
from .models import UserInput

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email', 'password1', 'password2']

# Input fields from the skin-quiz.html form
"""
class UserInputForm(forms.ModelForm):
    class Meta:
        model = UserInput
        fields = ['well_aging','acne','blackheads','moistrurising','brightening',
                  'soothing','dullness','visible_pores','scarring','dry','oily',
                  'combination','sensitive','normal','age',]
"""