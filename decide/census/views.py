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
import csv
from django.http import HttpResponse

from import_export import resources

def export_csv(request):

    """queryset = Census.objects.all()

    options = Census._meta

    print(options.fields)

    fields = [field.name for field in options.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="census.csv"'

    writer = csv.writer(response)

    writer.writerow([options.get_field(field).verbose_name for field in fields])

    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])  

    redirect('/census')

    return response"""

    census_resource = resources.modelresource_factory(model=Census)()

    dataset = census_resource.export()

    response= HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="census.csv"'

    return response

def import_csv(request):
    
    censo= []
    with open('census.csv', 'r') as csvfile:
        reader = list(csv.reader(csvfile, delimiter=','))
        for row in reader[1:]:
            censo.append(
                Census(
                    voting_id=row[1],
                    voter_id=row[2]
                )
            )
    if len(censo) > 0:
        Census.objects.bulk_create(censo)

    return HttpResponse('Census imported')

    """
    with open('census.csv', 'r') as csv_file:
        import tablib

        census_resource = resources.modelresource_factory(model=Census)()
        dataset = tablib.Dataset(headers=[field.name for field in Census._meta.fields]).load(csv_file.read())
        result = census_resource.import_data(dataset, dry_run=True)

        if not result.has_errors():
            census_resource.import_data(dataset, dry_run=False)
        
        return HttpResponse('Census imported')
    """   


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
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')
