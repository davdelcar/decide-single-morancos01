from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from base.perms import UserIsStaff
from .models import Census
from django.http import HttpResponse

from import_export import resources
from django.utils.translation import gettext_lazy as _



def export_csv(request):

    census_resource = resources.modelresource_factory(model=Census)()

    dataset = census_resource.export()

    response= HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="census.csv"'

    return response

from django.contrib import messages
import openpyxl
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView

class CensusList(TemplateView):
    template_name = "census/census.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["census"] = Census.objects.all()
        return context

class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response(_('Error try to create census'), status=ST_409)
        return Response(_('Census created'), status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response(_('Voters deleted from census'), status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response(_('Invalid voter'), status=ST_401)
        return Response(_('Valid voter'))


class CensusImportView(TemplateView):
    template_name = "census/import.html"

    def post(self, request, *args, **kwargs):
        
        if request.method == "POST":
        
            if "census_file" not in request.FILES:

                messages.error(request, "Por favor, seleccione un archivo para importar.")
                return HttpResponseRedirect("/census/import/")
                        
            census_file = request.FILES["census_file"]
            workbook = openpyxl.load_workbook(census_file)
            sheet = workbook.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                voting_id = row[0]
                voter_id = row[1]

                # Comprobar si ya existe un objeto con la misma pareja de voting_id y voter_id
                existing_census = Census.objects.filter(
                    voting_id=voting_id, voter_id=voter_id
                ).first()

                if not existing_census:
                    # Si no existe, crear uno nuevo
                    Census.objects.create(voting_id=voting_id, voter_id=voter_id)
                else:
                    # Si ya existe, puedes manejar esto según tus requisitos, por ejemplo, mostrar un mensaje de error
                    messages.error(
                        request,
                        f"Ya existe un registro para la pareja de voting_id={voting_id} y voter_id={voter_id}",
                    )

            messages.success(request, _("Importación finalizada"))
            return HttpResponseRedirect("/census/import/")