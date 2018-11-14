from rest_framework import serializers
from django.apps import apps

REPORT = apps.get_model('report', 'Report')

fields = ('reporter', 'title', 'body',)


class ArticleReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = REPORT
        fields = fields

    def create(self, validated_data):
        instance = REPORT.objects.create(**validated_data)

        return validated_data
