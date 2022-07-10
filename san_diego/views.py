from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from .forms import ClientForm, CarForm, ContactForm, SearchForm, CarPartFormSet, ServiceFormSet
from .models import Car, CarModel, CarPart, Client, Service
from account.models import Profile
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.postgres.search import SearchVector
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def fetch_resources(uri, rel):
    path = os.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, "bootstrap.css"))
    return path


def load_car_models(request):
    car_make_id = request.GET.get('car_make')
    models = CarModel.objects.filter(make_id=car_make_id).order_by('model_name')
    return render(request, 'san_diego/car_models_dropdown.html', {'models': models})


def home_view(request, *args, **kwargs):
    template = 'san_diego/home.html'
    if request.method == 'POST':
        try:
        # try:
        #     message = request.POST['contact_message']
        #     client_mail = request.POST['client_mail']
        #     send_mail(subject='Wycena dla: ' + client_mail,
        #         message=message,
        #         from_email=client_mail,
        #         recipient_list=[settings.EMAIL_HOST_USER],
        #         fail_silently=False)
        #     return HttpResponseRedirect('/')
        # except:
        #     context = {'error': error}
        #     return render(request, template, context)
            form = ContactForm(request.POST)
            if form.is_valid():
                client_email = form.cleaned_data['client_email']
                message = form.cleaned_data['contact_message']
                send_mail(subject='Wycena dla: ' + client_email,
                    message=message,
                    from_email=client_email,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False)
                messages.success(request, _('Your mail has been sent successfully. I will reply as soon as I can.'))
                return HttpResponseRedirect('/')
            else:
                messages.error(request, _('Something went wrong. We will try to fix it as fast as we can. You can call me instead: 669 393 761.'))
                messages.error(request, form.errors)
        except:
            messages.error(request, _('Server side problem occured, please write to us: sandiegogarage@gmail.com or call us: 669 393 761.'))
            messages.error(request, form.errors)
    else:
        form = ContactForm()
    return render(request, template, {'form':  form})


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
    template_name = 'san_diego/service_add.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        car = Car.objects.get(uuid=self.kwargs.get('uuid'))
        service_formset = ServiceFormSet(queryset=Service.objects.none(), prefix='service_formset')
        formset = CarPartFormSet(queryset=CarPart.objects.none(), prefix='carpart_formset')
        return self.render_to_response(
            self.get_context_data(form=service_formset, formset=formset, car=car))

    def post(self, request, *args, **kwargs):
        self.object = None
        car = Car.objects.get(uuid=self.kwargs.get('uuid'))
        service_formset = ServiceFormSet(self.request.POST, prefix='service_formset')
        formset = CarPartFormSet(self.request.POST, prefix='carpart_formset')
        if service_formset.is_valid() and formset.is_valid():
            return self.form_valid(service_formset, formset)
        else:
            return self.form_invalid(service_formset, formset, car)

    def form_valid(self, service_formset, formset):
        form = service_formset.save(commit=False)
        formset = formset.save(commit=False)
        for f in form:
            f.car = Car.objects.get(uuid=self.kwargs.get('uuid'))
            f.user = self.request.user
            f.save()
        for f in formset:
            f.car = Car.objects.get(uuid=self.kwargs.get('uuid'))
            f.user = self.request.user
            f.save()
        return redirect(self.get_success_url())

    def form_invalid(self, service_formset, formset, car):
        return self.render_to_response(self.get_context_data(form=service_formset, formset=formset, car=car))

    def get_success_url(self):
        """If statement is adding funcionality to SAVE AND ADD ANOTHER button."""
        car = get_object_or_404(Car, uuid=self.kwargs.get('uuid'), user=self.request.user)
        if "another" in self.request.POST:
            return reverse_lazy('service_add', kwargs={'uuid': car.uuid})
        return reverse_lazy('service_history', kwargs={'uuid': car.uuid})


@method_decorator(login_required, name='dispatch')
class ServiceEditView(UpdateView):
    model = Service
    template_name = 'san_diego/service_add.html'

    def get_object(self):
        """Pass UUID"""
        return Car.objects.get(uuid=self.kwargs.get("uuid"))

    def get(self, request, *args, **kwargs):
        self.object =self.get_object()
        service_formset = ServiceFormSet(queryset=Service.objects.filter(
            car=self.get_object(), user=self.request.user, date_added=self.kwargs.get('date')), prefix='service_formset')
        formset = CarPartFormSet(queryset=CarPart.objects.filter(
            car=self.get_object(), user=self.request.user, pdate_added=self.kwargs.get('date')), prefix='carpart_formset')
        return self.render_to_response(
            self.get_context_data(form=service_formset, formset=formset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        service_formset = ServiceFormSet(self.request.POST, prefix='service_formset')
        formset = CarPartFormSet(self.request.POST, prefix='carpart_formset')
        if service_formset.is_valid() and formset.is_valid():
            return self.form_valid(service_formset, formset)
        else:
            return self.form_invalid(service_formset, formset)

    def form_valid(self, service_formset, formset, **kwargs):
        form = service_formset.save(commit=False)
        parts_form = formset.save(commit=False)
        for f in form:
            f.car = self.get_object()
            f.user = self.request.user
            f.date_added = self.kwargs.get('date')
            f.save()
        for f in parts_form:
            f.car = self.get_object()
            f.user = self.request.user
            f.pdate_added = self.kwargs.get('date')
            f.save()
        """Loop for deleting objects with can_delete=True checkbox to actually delete them"""
        for obj in service_formset.deleted_objects:
            obj.delete()
        for obj in formset.deleted_objects:
            obj.delete()
        return redirect(self.get_success_url())

    def form_invalid(self, service_formset, formset):
        return self.render_to_response(self.get_context_data(form=service_formset, formset=formset))
    
    def get_success_url(self):
        car = get_object_or_404(Car, uuid=self.kwargs.get('uuid'), user=self.request.user)
        return reverse_lazy('service_history', kwargs={'uuid': car.uuid})


@method_decorator(login_required, name='dispatch')
class ServiceHistoryView(ListView):
    model = Service
    template_name = 'san_diego/service_history.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(ServiceHistoryView, self).get_context_data(**kwargs)
        car = get_object_or_404(Car, uuid=self.kwargs.get('uuid'))
        services = self.get_queryset()
        services_total_price_perday = self.get_queryset().filter().values('date_added').order_by(
            '-date_added').annotate(sum=Sum('service_price'))
        carparts = CarPart.objects.filter(car=car, user=self.request.user).order_by('-pdate_added')
        parts_total_price_perday = carparts.filter().values('pdate_added').annotate(sum=Sum('part_price'))
        total = []
        for item in services_total_price_perday:
            for i in parts_total_price_perday:
                if item['date_added'] == i['pdate_added']:
                    tp = item['sum'] + i['sum']
                    td = {
                        'total': tp,
                        'date': item['date_added']
                    }
                    total.append(td)

        context['car'] = car
        context['services'] = services
        context['carparts'] = carparts
        context['services_total_price_perday'] = services_total_price_perday
        context['parts_total_price_perday'] = parts_total_price_perday
        context['total'] = total

        page = self.request.GET.get('page')
        paginator = Paginator(services, self.paginate_by)

        try:
            services = paginator.page(page)
        except PageNotAnInteger:
            services = paginator.page(1)
        except EmptyPage:
            services = paginator.page(paginator.num_pages)
        context['services'] = services
        return context

    def get_queryset(self, *args):
        self.car = get_object_or_404(Car, uuid=self.kwargs['uuid'], user=self.request.user)
        services = Service.objects.filter(car=self.car).order_by('-date_added')
        return services


def services_parts_delete(request, **kwargs):
    car = get_object_or_404(Car, uuid=kwargs.get('uuid'))
    services = Service.objects.filter(car=car, user=request.user, date_added=kwargs.get('date'))
    carparts = CarPart.objects.filter(car=car, user=request.user, pdate_added=kwargs.get('date'))
    context = {
        'car': car,
        'services': services,
        'carparts': carparts,
        'date': kwargs.get('date'),
    }
    if request.method == 'POST':
        services.delete()
        carparts.delete()
        return redirect('service_history', uuid=car.uuid)
    return render(request, 'san_diego/service_delete.html', context)


def generate_invoice_pdf(request, uuid, *args, **kwargs):
    template_path = 'san_diego/invoice.html'
    date = kwargs.get('date')
    car = get_object_or_404(Car, uuid=uuid)
    profile = get_object_or_404(Profile, user=request.user)
    services = Service.objects.filter(car=car, user=request.user, date_added=kwargs.get('date'))
    carparts = CarPart.objects.filter(car=car, user=request.user, pdate_added=kwargs.get('date'))
    services_total_price_perday = services.filter().values('date_added').order_by(
            '-date_added').annotate(sum=Sum('service_price'))
    parts_total_price_perday = carparts.filter().values('pdate_added').annotate(sum=Sum('part_price'))
    total = []
    for item in services_total_price_perday:
        for i in parts_total_price_perday:
            if item['date_added'] == i['pdate_added']:
                tp = item['sum'] + i['sum']
                td = {
                    'total': tp,
                    'date': item['date_added']
                }
                total.append(td)
    static_root = settings.STATIC_ROOT

    context = {
        'car': car,
        'profile': profile,
        'services': services,
        'carparts': carparts,
        'stpp': services_total_price_perday,
        'ptpp': parts_total_price_perday,
        'total': total,
        'static_root': static_root,
        'date': date,
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="{}_{}.pdf"'.format(car, date)
    # response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(car)
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html.encode('utf-8'), dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
