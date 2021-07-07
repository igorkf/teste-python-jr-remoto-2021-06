from django.test import TestCase, Client
from rest_framework import status

from ..models import Project, PackageRelease
from ..serializers import ProjectSerializer


client = Client()


class ProjectViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_name = 'titan'
        cls.project = Project.objects.create(name=cls.project_name)
        cls.package_release_1 = PackageRelease.objects.create(
            name='django-rest-swagger',
            project=cls.project
        )
        cls.package_release_2 = PackageRelease.objects.create(
            name='Django',
            version='2.2.24',
            project=cls.project
        )
        cls.package_release_3 = PackageRelease.objects.create(
            name='psycopg2-binary',
            version='2.9.1',
            project=cls.project
        )

    def test_get_single_project(self):
        response = client.get(f'/api/projects/{self.project_name}/')
        project = Project.objects.get(name=self.project_name)
        serializer = ProjectSerializer(project)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_single_project_is_not_found(self):
        response = client.get(f'/api/projects/foobar/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_if_single_project_has_three_packages(self):
        response = client.get(f'/api/projects/{self.project_name}/')
        self.assertEqual(len(response.data['packages']), 3)

    def test_if_single_project_is_deleted(self):
        response = client.delete(f'/api/projects/{self.project_name}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_all_projects(self):
        response = client.get('/api/projects/')
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
