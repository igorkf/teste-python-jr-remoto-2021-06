from rest_framework import status, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import requests

from .models import Project
from .serializers import ProjectSerializer


def check_packages_at_pypi(project: dict):
    '''
    Faz requisições na API do PyPi para verificar se cada pacote do projeto é valido.   
    Caso a versão do pacote não seja especificada no projeto, então é capturada a versão
    mais recente disponível na API do PyPi.  
    É possível que projeto não use nenhum pacote (ou seja, "packages": []), então
    neste caso não é necessário fazer requisições na API do PyPi.

    Exemplo de um projeto:
        data = {
            'name': 'titan',
            'packages': [
                {'name': 'Django'},
                {'name': 'pypypypypypy', 'version': '2.0'},
                {'name': 'graphene', 'version': '2.0'}
            ]
        }
    '''

    STATUS_CODE = status.HTTP_200_OK

    for package in project['packages']:
        project_name = package.get('name', ' ')
        url = f'https://pypi.org/pypi/{project_name}/json'
        response = requests.get(url)

        try:
            response.raise_for_status()
            pypi_data = response.json()['info']
            package['name'] = pypi_data['name']
            package['version'] = package.get('version', pypi_data['version'])
        except requests.exceptions.HTTPError:
            STATUS_CODE = status.HTTP_404_NOT_FOUND
            break

    return STATUS_CODE, project


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = 'name'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        PYPI_STATUS_CODE, checked_project_data = check_packages_at_pypi(
            project=request.data
        )

        if PYPI_STATUS_CODE == status.HTTP_200_OK:
            serializer.save(**checked_project_data)
            headers = self.get_success_headers(serializer.data)
            return Response(
                data=checked_project_data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            return Response(
                data={'error': 'One or more packages do not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )
