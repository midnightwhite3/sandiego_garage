from .models import CarPart
from django import forms
from san_diego.forms import CarForm
from san_diego.models import CarMake, CarModel

class CarPartForm(forms.ModelForm):
    class Meta:
        model = CarPart
        exclude = ('user',)

        widgets = {
            'part_name': forms.TextInput(attrs={'class': 'form-control'}),
            'part_id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'car_make': forms.Select(attrs={'class': 'form-control'}),
            'car_model': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        # self.request = kwargs.pop('request') # Grants access to the request object
        super().__init__(*args, **kwargs)
        # returns no value till "Make" field is populated
        self.fields['car_model'].queryset = CarModel.objects.none()
        self.fields['car_make'].queryset = CarMake.objects.order_by('car_make')

        if 'car_make' in self.data:     # validation for if model is in certain make
            try:
                car_make_id = int(self.data.get('car_make'))
                self.fields['car_model'].queryset = CarModel.objects.filter(make_id=car_make_id).order_by('model_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            try:
                # this is for edit function to return previously saved model
                self.fields['car_model'].queryset = self.instance.car_make.carmodel_set.order_by('model_name')
            except(AttributeError):
                # Since model and make isnt required, this is an exception if model/make = None
                pass