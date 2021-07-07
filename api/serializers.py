from rest_framework import serializers

from .models import PackageRelease, Project


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
