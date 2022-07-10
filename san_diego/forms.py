
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
from .models import Car, CarMake, CarPart, Service, Client, CarModel
from django.utils.translation import gettext_lazy as _


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('user', 'uuid')

        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Name, up to 40 chars.')}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control'})
        }


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        exclude = ('user', 'uuid')

        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'car_make': forms.Select(attrs={'class': 'form-control'}),
            'car_model': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Year')}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'engine': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Engine capacity')}),
            'vin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter VIN number')}),
            'extra_info': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Additional informations')}),
        }
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request') # Grants access to the request object
        super().__init__(*args, **kwargs)
        # returns no value till "Make" field is populated
        self.fields['car_model'].queryset = CarModel.objects.none()
        self.fields['car_make'].queryset = CarMake.objects.order_by('car_make')
        # returns the queryset made by currently logged in user for the client field
        self.fields['client'].queryset = Client.objects.filter(user=self.request.user)

        if 'car_make' in self.data:     # validation for if model is in certain make
            try:
                car_make_id = int(self.data.get('car_make'))
                self.fields['car_model'].queryset = CarModel.objects.filter(make_id=car_make_id).order_by('model_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # this is for edit function to return previously saved model
            self.fields['car_model'].queryset = self.instance.car_make.carmodel_set.order_by('model_name')



class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'service_price']
        widgets = {
            'service_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Service name')}),
            'service_price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Service price')}),
        }


class CarPartForm(forms.ModelForm):
    class Meta:
        model = CarPart
        fields = ['car_part', 'part_price']


ServiceFormSet = modelformset_factory(Service, form=ServiceForm, extra=0, fields=['service_name', 'service_price'], can_delete=True, widgets={
    'service_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Service name')}),
    'service_price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Service price')}),
    'DELETE': forms.CheckboxInput(attrs={'class': 'form-check-input', 'label': _('Delete')}),
})


CarPartFormSet = modelformset_factory(CarPart, form=CarPartForm, fields=['car_part', 'part_price'], can_delete=True, extra=0, widgets={
    'car_part': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Part')}),
    'part_price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Part price')}),
    'DELETE': forms.CheckboxInput(attrs={'class': 'form-check'}),
})


class SearchForm(forms.Form):
    query = forms.CharField()


class ContactForm(forms.Form):
    client_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'text-input'}))
    contact_message = forms.CharField(required=True, min_length=30, widget=forms.Textarea(attrs={'class': 'textarea-input'}))