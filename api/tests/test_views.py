import json

from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Project, PackageRelease
from ..serializers import ProjectSerializer
from ..views import check_packages_at_pypi


project_data = {
    'name': 'titan',
    'packages': [
        {'name': 'django-rest-swagger'},
        {'name': 'Django', 'version': '2.2.24'},
        {'name': 'psycopg2-binary', 'version': '2.9.1'}
    ]
}

invalid_project_data = {
    'name': 'qazwsxedc',
    'packages': [
        {'name': 'pypypypypypypypypypypy'},
        {"name": "graphene", "version": "1900"}
    ]
}


class ProjectViewTest(APITestCase):
    def setUp(self):
        self.project_name = project_data['name']
        project = Project.objects.create(name=self.project_name)
        for package_data in project_data['packages']:
            PackageRelease.objects.create(project=project, **package_data)

    def test_get_project(self):
        response = self.client.get(f'/api/projects/{self.project_name}/')
        project = Project.objects.get(name=self.project_name)
        serializer = ProjectSerializer(project)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_project_has_three_packages(self):
        response = self.client.get(f'/api/projects/{self.project_name}/')
        self.assertEqual(len(response.data['packages']), 3)

    def test_get_project_that_does_not_exists(self):
        response = self.client.get(f'/api/projects/pypypypypypypypypy/')
        error_msg = str(response.data['detail'])
        self.assertEqual(error_msg, 'Not found.')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_all_projects(self):
        response = self.client.get('/api/projects/')
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_project_that_does_not_exists_yet(self):
        # delete projects before creating a new one
        Project.objects.all().delete()

        PYPI_STATUS_CODE, checked_project_data = check_packages_at_pypi(
            project=project_data
        )
        response = self.client.post(
            '/api/projects/',
            data=checked_project_data,
            format='json'
        )
        self.assertEqual(PYPI_STATUS_CODE, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_project_that_already_exists(self):
        PYPI_STATUS_CODE, checked_project_data = check_packages_at_pypi(
            project=project_data
        )

        response = self.client.post(
            '/api/projects/',
            data=checked_project_data,
            format='json'
        )
        error_msg = str(response.data['name'][0])
        self.assertEqual(error_msg, 'project with this name already exists.')
        self.assertEqual(PYPI_STATUS_CODE, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_project_that_does_not_exists_at_pypi(self):
        PYPI_STATUS_CODE, checked_project_data = check_packages_at_pypi(
            project=invalid_project_data
        )

        response = self.client.post(
            '/api/projects/',
            data=checked_project_data,
            format='json'
        )
        error_msg = response.data['error']
        self.assertEqual(error_msg, 'One or more packages do not exist.')
        self.assertEqual(PYPI_STATUS_CODE, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_project(self):
        response = self.client.delete(f'/api/projects/{self.project_name}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
