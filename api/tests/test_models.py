from django.test import TestCase

from ..models import Project, PackageRelease


release_data = [
    {'name': 'django-rest-swagger'},
    {'name': 'Django', 'version': '2.2.24'},
    {'name': 'psycopg2-binary', 'version': '2.9.1'}
]


class ProjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(name='titan')
        for data in release_data:
            PackageRelease.objects.create(project=cls.project, **data)

    def test_if_project_has_three_packages(self):
        self.assertEqual(self.project.packages.count(), 3)

    def test_if_project_string_representation_is_the_project_name(self):
        name = self.project.name
        self.assertEqual(str(self.project), name)


class PackageReleaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(name='titan')
        cls.packages = []
        for data in release_data:
            package = PackageRelease.objects.create(
                project=cls.project,
                **data
            )
            cls.packages.append(package)

    def test_if_package_release_string_representation_is_the_package_with_version(self):
        for package in self.packages:
            name_version = f'{package.name} {package.version}'
            self.assertEqual(str(package), name_version)
