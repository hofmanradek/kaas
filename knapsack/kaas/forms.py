from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import json


class LoginForm(forms.Form):
    """
    User login form
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    """
    New user registration form
    """
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class KnapsakTextArea(forms.Form):
    """
    Text area where user can copy paste JSON with knapsack task definition
    """
    knapsack_json = forms.CharField(widget=forms.Textarea, label='')
    #custom validation of out knapsack json
    def clean_knapsack_json(self):
        data = self.cleaned_data['knapsack_json']
        #now we validate some attributes
        #can the content by parsed to json?
        try:
            jdata = json.loads(data)
        except:
            raise ValidationError("This is not a valid json")

        #mandatory keys are level 0
        mandatory_keys = ("solver_type", "knapsack_data")
        for k in mandatory_keys:
            if not k in jdata.keys():
                raise ValidationError("Key '{}' not found in knapsack json!".format(k))

        #mandatory keys of items
        knapsack_data = jdata['knapsack_data']
        mandatory_keys = ("num_items", "capacity", "items")
        for k in mandatory_keys:
            if not k in knapsack_data.keys():
                raise ValidationError("Key '{}' not found in knapsack json 'knapsack_data' section!".format(k))

        #we test various contidions of knapsack json consistency
        if (not type(knapsack_data['num_items']) is int) or knapsack_data['num_items'] <= 0:
            raise ValidationError("'num_item' value must be an integer > 0!")

        if knapsack_data['capacity'] < 0:
            raise ValidationError("'capacity' value must be >= 0")

        if not type(knapsack_data['items']) is list:
            raise ValidationError("'capacity' value must be a list of items!")

        if len(knapsack_data['items']) != knapsack_data['num_items']:
            raise ValidationError("'num_items' != the actual number of items in item list!")

        items = knapsack_data['items']
        for i, item in enumerate(items):
            mandatory_keys = ("index", "value", "weight")
            for k in mandatory_keys:
                if not k in item.keys():
                    raise ValidationError("Key '{}' not found in item {}!".format(k, i))
                if not type(item[k]) in (int, float):
                    raise ValidationError("Key '{}' of item {} not type int or float!".format(k, i))
                if item[k] < 0:
                    raise ValidationError("Key '{}' of item {} cannot be <0!".format(k, i))

        return data
