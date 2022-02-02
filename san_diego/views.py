from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from .forms import ClientForm, CarForm, SearchForm, ServiceForm, CarPartsFormSet
from .models import Car, CarModel, Client, Service
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from django.contrib.postgres.search import SearchVector
from django.db.models import Sum
from django.db.models import F


def load_car_models(request):
    car_make_id = request.GET.get('car_make')
    models = CarModel.objects.filter(make_id=car_make_id).order_by('model_name')
    return render(request, 'san_diego/car_models_dropdown.html', {'models': models})

def home_view(request, *args, **kwargs):
    template = 'san_diego/home.html'
    context = {}
    return render(request, template, context)

def car_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Car.objects.annotate(search=SearchVector('client', 'car_make', 'car_model'),).filter(search=query)
        return render(request, 'san_diego/car_library.html', {'form': form, 'query': query, 'results': results}) # przypisac to do pola w car_library.html

### CLASS BASED VIEWS ###

@method_decorator(login_required, name='dispatch')
class CarListView(ListView):
    context_object_name = 'cars'
    paginate_by = 20
    template_name = 'san_diego/car_library.html'
    model = Car

    def get_context_data(self, **kwargs):
        context = super(CarListView, self).get_context_data(**kwargs)
        cars = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(cars, self.paginate_by)

        try:
            cars = paginator.page(page)
        except PageNotAnInteger:
            cars = paginator.page(1)
        except EmptyPage:
            cars = paginator.page(paginator.num_pages)
        context['cars'] = cars
        return context

    def get_queryset(self):
        """Returns objects created by the logged in user."""
        query = self.request.GET.get('q')
        if query:
            object_list = Car.objects.annotate(search=SearchVector('client__client_name', 'car_make__car_make', 'car_model__model_name'),
            ).filter(user=self.request.user, search=query)
        else:
            object_list = Car.objects.filter(user=self.request.user)
        return object_list


@method_decorator(login_required, name='dispatch')
class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'san_diego/car_add.html'
    success_url = reverse_lazy('car_library')

    def get_context_data(self, **kwargs):
        context = super(CarCreateView,self).get_context_data(**kwargs)
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
        self.object.user = self.request.user # assign object to the user.author
        self.object.save()
        return redirect('car_library')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to display only clients that belong to a given user"""
        kwargs = super(CarCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


@method_decorator(login_required, name='dispatch')
class CarDetailView(DetailView):
    model = Car
    template_name = 'san_diego/car_detail.html'
    context_object_name = 'car'

    def dispatch(self, request, *args, **kwargs):
        """Check if the user is the author, if not - raise the error"""
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("You are not allowed to see this")
        return super(CarDetailView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        """Pass UUID"""
        return Car.objects.get(uuid=self.kwargs.get("uuid"))


@method_decorator(login_required, name='dispatch')
class CarUpdateView(UpdateView):
    model = Car
    template_name = 'san_diego/car_edit.html'
    context_object_name = 'car'
    form_class = CarForm

    def get_success_url(self):
        return reverse_lazy('car_library')

    # def get(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     return self.render_to_response(
    #         self.get_context_data(form=form))

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
        # car = form.save(commit=False)
        # car.user = self.request.user
        # car.save()
        return redirect('car_library')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        """Check if the user is the author, if not - raise the error"""
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("You are not allowed to edit this")
        return super(CarUpdateView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        """Pass UUID"""
        return Car.objects.get(uuid=self.kwargs.get("uuid"))

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display clients that belong to a given user"""
        kwargs = super(CarUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


@method_decorator(login_required, name='dispatch')
class CarDeleteView(DeleteView):
    model = Car
    template_name = 'san_diego/car_delete.html'
    context_object_name = 'car'
    success_url = reverse_lazy('car_library')

    def dispatch(self, request, *args, **kwargs):
        """Check if the user is the author, if not - raise the error"""
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("You are not allowed to delete this")
        return super(CarDeleteView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        """Pass UUID"""
        return Car.objects.get(uuid=self.kwargs.get("uuid"))


@method_decorator(login_required, name='dispatch')
class ClientListView(ListView):
    context_object_name = 'clients'
    paginate_by = 20
    template_name = 'san_diego/client_library.html'
    model = Client

    def get_context_data(self, **kwargs):
        context = super(ClientListView, self).get_context_data(**kwargs)
        clients = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(clients, self.paginate_by)
        try:
            clients = paginator.page(page)
        except PageNotAnInteger:
            clients = paginator.page(1)
        except EmptyPage:
            clients = paginator.page(paginator.num_pages)
        context['clients'] = clients
        return context

    def get_queryset(self):
        """Returns objects created by the logged in user."""
        query = self.request.GET.get('q')
        if query:
            object_list = Client.objects.annotate(search=SearchVector('client_name',),
            ).filter(user=self.request.user, search=query)
        else:
            object_list = Client.objects.filter(user=self.request.user)
        return object_list


@method_decorator(login_required, name='dispatch')
class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'san_diego/client_add.html'
    success_url = reverse_lazy('client_library')

    def form_valid(self, form):
        """Assign user to object created"""
        client = form.save(commit=False)
        client.user = self.request.user
        client.save()
        return redirect('client_library')


@method_decorator(login_required, name='dispatch')
class ClientEditView(UpdateView):
    model = Client
    template_name = 'san_diego/client_edit.html'
    context_object_name = 'client'
    form_class = ClientForm

    def get_success_url(self):
        return reverse_lazy('client_library')

    def dispatch(self, request, *args, **kwargs):
        """Check if the user is the author, if not - raise the error"""
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("You are not allowed to edit this")
        return super(ClientEditView, self).dispatch(request, *args, **kwargs)
    
    def get_object(self):
        """Pass UUID"""
        return Client.objects.get(uuid=self.kwargs.get("uuid"))


@method_decorator(login_required, name='dispatch')
class ClientDetailView(DetailView):
    model = Client
    template_name = 'san_diego/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, *args, **kwargs):
        context = super(ClientDetailView, self).get_context_data(**kwargs)
        context['cars'] = self.get_queryset()
        return context

    def dispatch(self, request, *args, **kwargs):
        """Check if the user is the author, if not - raise the error"""
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("You are not allowed to see this")
        return super(ClientDetailView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        """Pass UUID"""
        return Client.objects.get(uuid=self.kwargs.get("uuid"))

    def get_queryset(self):
        client = Client.objects.get(uuid=self.kwargs.get("uuid"))
        cars = Car.objects.filter(client=client)
        return cars


@method_decorator(login_required, name='dispatch')
class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'san_diego/client_delete.html'
    context_object_name= 'client'
    success_url = reverse_lazy('client_library')

    def dispatch(self, request, *args, **kwargs):
        """Check if the user is the author, if not - raise the error"""
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("You are not allowed to delete this")
        return super(ClientDeleteView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        """Pass UUID"""
        return Client.objects.get(uuid=self.kwargs.get("uuid"), user=self.request.user)


@method_decorator(login_required, name='dispatch')
class ServiceAddView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'san_diego/service_add.html'
    success_url = reverse_lazy('car_library') 

    def get(self, request, *args, **kwargs):
        self.object = None
        car = Car.objects.get(uuid=self.kwargs.get('uuid'))
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = CarPartsFormSet()
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset, car=car))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = CarPartsFormSet(self.request.POST, instance=self.object)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save(commit=False)
        form.instance.car = Car.objects.get(uuid=self.kwargs.get('uuid'))
        self.object.user = self.request.user
        self.object.save()
        formset.instance = self.object
        formset.save()
        return redirect('car_library')

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

@method_decorator(login_required, name='dispatch')
class ServiceHistoryView(ListView):
    model = Service
    template_name = 'san_diego/service_history.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(ServiceHistoryView, self).get_context_data(**kwargs)
        car = get_object_or_404(Car, uuid=self.kwargs.get('uuid'))
        service = self.get_queryset().annotate(total=Sum(F('carparts__part_price')) + F('service_price'))
        context['car'] = car
        # context['service'] = service

        page = self.request.GET.get('page')
        paginator = Paginator(service, self.paginate_by)

        try:
            service = paginator.page(page)
        except PageNotAnInteger:
            service = paginator.page(1)
        except EmptyPage:
            service = paginator.page(paginator.num_pages)
        context['service'] = service
        return context

    def get_queryset(self, *args):
        self.car = get_object_or_404(Car, uuid=self.kwargs['uuid'], user=self.request.user)
        service = Service.objects.filter(car=self.car).order_by('-date_added')
        return service


@method_decorator(login_required, name='dispatch')
class ServiceDeleteView(DeleteView):
    model = Service
    template = 'san_diego/service_delete.html'
    context_object_name= 'service'

    def get_success_url(self):
        car = get_object_or_404(Car, uuid=self.kwargs.get('uuid'))
        return reverse_lazy('service_history', kwargs={'uuid': car.uuid})

    def get_context_data(self, **kwargs):
        context = super(ServiceDeleteView, self).get_context_data(**kwargs)
        car = get_object_or_404(Car, uuid=self.kwargs.get('uuid'))
        context['car'] = car
        return context
        

    def get_object(self, queryset=None):
        sid = self.kwargs.get('id')
        service = get_object_or_404(Service, id=sid, user=self.request.user)
        return service


@method_decorator(login_required, name='dispatch')
class ServiceEditView(UpdateView):
    model = Service
    template_name = 'san_diego/service_add.html'
    context_object_name = 'service'
    form_class = ServiceForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        car = Car.objects.get(uuid=self.kwargs.get('uuid'))
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = CarPartsFormSet(instance=self.object)
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset, car=car))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = CarPartsFormSet(self.request.POST, instance=self.object)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def get_object(self, **kwargs):
        sid = self.kwargs.get('id')
        service = get_object_or_404(Service, id=sid, user=self.request.user)
        return service

    def form_valid(self, form, formset):
        self.object = form.save(commit=False)
        form.instance.car = Car.objects.get(uuid=self.kwargs.get('uuid'))
        self.object.user = self.request.user
        self.object.save()
        formset.instance = self.object
        formset.save()
        return redirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_success_url(self):
        car = get_object_or_404(Car, uuid=self.kwargs.get('uuid'), user=self.request.user)
        return reverse_lazy('service_history', kwargs={'uuid': car.uuid})