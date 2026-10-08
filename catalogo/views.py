from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DetailView, FormView,
                                  ListView, TemplateView, UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import (BuscarPorCodigoForm, FiltroPropiedadForm,
                    PropiedadCrearForm, PropiedadEditarForm)
from .models import Propiedad

MSG_VENDIDA = 'Esta propiedad ya fue vendida y su información no puede ser modificada'

class HomeView(TemplateView):
    template_name = 'catalogo/home.html'

class PropiedadListView(ListView):
    model = Propiedad
    template_name = 'catalogo/lista.html'
    context_object_name = 'propiedades'

    def get_queryset(self):
        qs = Propiedad.objects.all()
        self.filtro = FiltroPropiedadForm(self.request.GET or None)
        if self.filtro.is_valid():
            d = self.filtro.cleaned_data
            if d['fecha_desde']:
                qs = qs.filter(fecha_creacion__date__gte=d['fecha_desde'])
            if d['fecha_hasta']:
                qs = qs.filter(fecha_creacion__date__lte=d['fecha_hasta'])
            if d['precio_min'] is not None:
                qs = qs.filter(precio_venta__gte=d['precio_min'])
            if d['precio_max'] is not None:
                qs = qs.filter(precio_venta__lte=d['precio_max'])
            if d['estado']:
                qs = qs.filter(estado_venta=d['estado'])
            else:
                qs = qs.exclude(estado_venta=Propiedad.EstadoVenta.INACTIVA)
        else:
            qs = qs.exclude(estado_venta=Propiedad.EstadoVenta.INACTIVA)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtro'] = self.filtro
        return ctx

class PropiedadDetailView(DetailView):
    model = Propiedad
    template_name = 'catalogo/detalle.html'

class PropiedadCreateView(LoginRequiredMixin, CreateView):
    model = Propiedad
    form_class = PropiedadCrearForm
    template_name = 'catalogo/crear.html'
    success_url = reverse_lazy('catalogo:lista')

    def form_valid(self, form):
        form.instance.agente = self.request.user
        messages.success(self.request, 'Propiedad publicada correctamente.')
        return super().form_valid(form)

class PropiedadUpdateView(LoginRequiredMixin, UpdateView):
    model = Propiedad
    form_class = PropiedadEditarForm
    template_name = 'catalogo/editar.html'
    success_url = reverse_lazy('catalogo:lista')

    def dispatch(self, request, *args, **kwargs):
        propiedad = get_object_or_404(Propiedad, pk=kwargs['pk'])
        
        # Validación de autoría
        if propiedad.agente and propiedad.agente != request.user:
            messages.error(request, 'No tienes permiso para modificar una propiedad publicada por otro agente.')
            return redirect('catalogo:lista')
            
        if propiedad.esta_vendida:
            messages.error(request, MSG_VENDIDA)
            return redirect('catalogo:lista')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.cleaned_data.get('eliminar_fotografia'):
            messages.success(self.request, 'Propiedad actualizada y fotografía eliminada.')
        else:
            messages.success(self.request, 'Propiedad actualizada correctamente.')
        return super().form_valid(form)

class BuscarPropiedadView(LoginRequiredMixin, FormView):
    template_name = 'catalogo/buscar.html'
    form_class = BuscarPorCodigoForm

    def form_valid(self, form):
        codigo = form.cleaned_data['codigo_referencia']
        propiedad = Propiedad.objects.filter(codigo_referencia__iexact=codigo).first()
        if not propiedad:
            form.add_error('codigo_referencia', f'No existe una propiedad con código {codigo}.')
            return self.form_invalid(form)
        return redirect('catalogo:editar', pk=propiedad.pk)

class PropiedadDarDeBajaView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        propiedad = get_object_or_404(Propiedad, pk=pk)
        
        if propiedad.agente and propiedad.agente != request.user:
            messages.error(request, 'No tienes permiso para dar de baja una propiedad publicada por otro agente.')
            return redirect('catalogo:lista')

        if propiedad.esta_vendida:
            messages.error(request, MSG_VENDIDA)
        else:
            propiedad.dar_de_baja()
            messages.success(request, f'La propiedad {propiedad.codigo_referencia} fue dada de baja.')
        return redirect('catalogo:lista')
