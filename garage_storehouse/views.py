from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from san_diego.models import Car
from .models import CarPart
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector
from .forms import CarPartForm
from django.urls import reverse_lazy
from django.http import Http404, HttpResponse

# Create your views here.

@method_decorator(login_required, name='dispatch')
class StorehouseView(ListView):
    template_name = 'garage_storehouse/storehouse.html'
    model_name = CarPart
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super(StorehouseView, self).get_context_data(**kwargs)
        storehouse_parts = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(storehouse_parts, self.paginate_by)

        try:
            storehouse_parts = paginator.page(page)
        except PageNotAnInteger:
            storehouse_parts = paginator.page(1)
        except EmptyPage:
            storehouse_parts = paginator.page(paginator.num_pages)
        context['storehouse_parts'] = storehouse_parts
        return context

    def get_queryset(self):
        """Returns objects created by the logged in user."""
        query = self.request.GET.get('q')
        if query:
            object_list = CarPart.objects.annotate(search=SearchVector('part_name', 'car_make__car_make', 'car_model__model_name', 'part_id_number'),
            ).filter(user=self.request.user, search=query)
        else:
            object_list = CarPart.objects.filter(user=self.request.user)
        return object_list


@method_decorator(login_required, name='dispatch')
class StorehouseAddPartView(CreateView):
    form_class = CarPartForm
    template_name = 'garage_storehouse/add_part.html'
    model = CarPart

    def get_context_data(self, **kwargs):
        context = super(StorehouseAddPartView,self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(
            self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user # assign object to the user
        self.object.save()
        if 'another' in self.request.POST:
            id = self.kwargs.get('id')
            return redirect('storehouse_add_part')
        else:
            return redirect('storehouse')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(login_required, name='dispatch')
class StorehouseEditPartView(UpdateView):
    model = CarPart
    template_name = 'garage_storehouse/add_part.html'
    form_class = CarPartForm

    def get_success_url(self):
        return reverse_lazy('storehouse')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def form_valid(self, form):
        """Assign user to object created and save the form"""
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        if 'another' in self.request.POST:
            id = self.kwargs.get('id')
            return redirect('storehouse_add_part')
        else:
            return redirect('storehouse')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        """Check if the user is the author, if not - raise the error"""
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("You are not allowed to edit this")
        return super(StorehouseEditPartView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return CarPart.objects.get(id=self.kwargs.get("id"))


@method_decorator(login_required, name='dispatch')
class StorehouseDeletePartView(DeleteView):
    model = CarPart
    template_name = 'garage_storehouse/delete_part.html'
    success_url = reverse_lazy('storehouse')
    context_object_name = 'carpart'

    def dispatch(self, request, *args, **kwargs):
        """Check if the user is the author, if not - raise the error"""
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("You are not allowed to delete this")
        return super(StorehouseDeletePartView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return CarPart.objects.get(id=self.kwargs.get("id"), user=self.request.user)