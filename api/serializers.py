from rest_framework import serializers
import requests

from .models import PackageRelease, Project


def validate_packages_at_pypi(project: dict):
    '''
    Faz requisições na API do PyPi para verificar se cada pacote do projeto é valido.   
    Caso a versão do pacote não seja especificada no projeto, então é capturada a versão
    mais recente disponível na API do PyPi.  
    É possível que projeto não use nenhum pacote (ou seja, "packages": []), então
    neste caso não é necessário fazer requisições na API do PyPi.

    Exemplo:
    >>> project = {
        'name': 'titan',
        'packages': [
            {'name': 'Django'},
            {'name': 'pypypypypypy', 'version': '2.0'},
            {'name': 'graphene', 'version': '2.0'},
        ]
    }
    >>> validate_packages_at_pypi(project)
    >>> ({'error': 'One or more packages do not exist.'}, 400)
    '''

    STATUS_CODE = 201

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
            project = {'error': 'One or more packages do not exist.'}
            STATUS_CODE = 400
            break

    return project, STATUS_CODE


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageRelease
        fields = ['name', 'version']
        extra_kwargs = {'version': {'required': False}}


class ProjectSerializer(serializers.ModelSerializer):
    packages = PackageSerializer(many=True)

    class Meta:
        model = Project
        fields = ['name', 'packages']

    def create(self, validated_data):
        project_data = validated_data['name']
        project = Project.objects.create(name=project_data)

        packages_data = validated_data['packages']
        for package in packages_data:
            PackageRelease.objects.create(
                # TODO: verificar se pacote existe no PyPi
                name=package['name'],
                # TODO: pegar versão mais atual no PyPi se nenhuma versão foi escolhida
                version=package.get('version', '?'),
                project=project
            )
        return project
