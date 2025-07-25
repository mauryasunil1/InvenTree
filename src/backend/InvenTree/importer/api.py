"""API endpoints for the importer app."""

from django.shortcuts import get_object_or_404
from django.urls import include, path

from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

import importer.models
import importer.registry
import importer.serializers
import InvenTree.permissions
from InvenTree.api import BulkDeleteMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import (
    CreateAPI,
    ListAPI,
    ListCreateAPI,
    RetrieveUpdateAPI,
    RetrieveUpdateDestroyAPI,
)
from users.permissions import check_user_permission


class DataImporterPermissionMixin:
    """Mixin class for checking permissions on DataImporter objects."""

    # Default permissions: User must be authenticated
    permission_classes = [
        InvenTree.permissions.IsAuthenticatedOrReadScope,
        InvenTree.permissions.DataImporterPermission,
    ]


class DataImporterModelSerializer(serializers.Serializer):
    """Model references to map info that might get imported."""

    serializer = serializers.CharField(read_only=True)
    model_type = serializers.CharField(read_only=True)
    api_url = serializers.URLField(read_only=True, allow_null=True)


class DataImporterModelList(APIView):
    """API endpoint for displaying a list of models available for import."""

    permission_classes = [InvenTree.permissions.IsAuthenticatedOrReadScope]
    serializer_class = DataImporterModelSerializer(many=True)

    def get(self, request):
        """Return a list of models available for import."""
        models = []

        for serializer in importer.registry.get_supported_serializers():
            model = serializer.Meta.model
            url = model.get_api_url() if hasattr(model, 'get_api_url') else None

            models.append({
                'serializer': str(serializer.__name__),
                'model_type': model.__name__.lower(),
                'api_url': url,
            })

        return Response(models)


class DataImportSessionMixin:
    """Mixin class for DataImportSession API views."""

    queryset = importer.models.DataImportSession.objects.all()
    serializer_class = importer.serializers.DataImportSessionSerializer
    permission_classes = [InvenTree.permissions.DataImporterPermission]


class DataImportSessionList(BulkDeleteMixin, DataImportSessionMixin, ListCreateAPI):
    """API endpoint for accessing a list of DataImportSession objects."""

    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['model_type', 'status', 'user']
    ordering_fields = ['timestamp', 'status', 'model_type']


class DataImportSessionDetail(DataImportSessionMixin, RetrieveUpdateDestroyAPI):
    """Detail endpoint for a single DataImportSession object."""


class DataImportSessionAcceptFields(APIView):
    """API endpoint to accept the field mapping for a DataImportSession."""

    permission_classes = [InvenTree.permissions.IsAuthenticatedOrReadScope]
    serializer_class = None

    @extend_schema(
        responses={200: importer.serializers.DataImportSessionSerializer(many=False)}
    )
    def post(self, request, pk):
        """Accept the field mapping for a DataImportSession."""
        session = get_object_or_404(importer.models.DataImportSession, pk=pk)

        # Check that the user has permission to accept the field mapping
        if model_class := session.model_class:
            if not check_user_permission(request.user, model_class, 'change'):
                raise PermissionDenied()

        # Attempt to accept the mapping (may raise an exception if the mapping is invalid)
        session.accept_mapping()

        return Response(importer.serializers.DataImportSessionSerializer(session).data)


class DataImportSessionAcceptRows(DataImporterPermissionMixin, CreateAPI):
    """API endpoint to accept the rows for a DataImportSession."""

    queryset = importer.models.DataImportSession.objects.all()
    serializer_class = importer.serializers.DataImportAcceptRowSerializer

    def get_serializer_context(self):
        """Add the import session object to the serializer context."""
        ctx = super().get_serializer_context()

        try:
            ctx['session'] = importer.models.DataImportSession.objects.get(
                pk=self.kwargs.get('pk', None)
            )
        except Exception:
            pass

        ctx['request'] = self.request
        return ctx


class DataImportColumnMappingList(DataImporterPermissionMixin, ListAPI):
    """API endpoint for accessing a list of DataImportColumnMap objects."""

    queryset = importer.models.DataImportColumnMap.objects.all()
    serializer_class = importer.serializers.DataImportColumnMapSerializer

    filter_backends = SEARCH_ORDER_FILTER

    filterset_fields = ['session']


class DataImportColumnMappingDetail(DataImporterPermissionMixin, RetrieveUpdateAPI):
    """Detail endpoint for a single DataImportColumnMap object."""

    queryset = importer.models.DataImportColumnMap.objects.all()
    serializer_class = importer.serializers.DataImportColumnMapSerializer


class DataImportRowList(DataImporterPermissionMixin, BulkDeleteMixin, ListAPI):
    """API endpoint for accessing a list of DataImportRow objects."""

    queryset = importer.models.DataImportRow.objects.all()
    serializer_class = importer.serializers.DataImportRowSerializer

    filter_backends = SEARCH_ORDER_FILTER

    filterset_fields = ['session', 'valid', 'complete']

    ordering_fields = ['pk', 'row_index', 'valid']

    ordering = 'row_index'


class DataImportRowDetail(DataImporterPermissionMixin, RetrieveUpdateDestroyAPI):
    """Detail endpoint for a single DataImportRow object."""

    queryset = importer.models.DataImportRow.objects.all()
    serializer_class = importer.serializers.DataImportRowSerializer


importer_api_urls = [
    path('models/', DataImporterModelList.as_view(), name='api-importer-model-list'),
    path(
        'session/',
        include([
            path(
                '<int:pk>/',
                include([
                    path(
                        'accept_fields/',
                        DataImportSessionAcceptFields.as_view(),
                        name='api-import-session-accept-fields',
                    ),
                    path(
                        'accept_rows/',
                        DataImportSessionAcceptRows.as_view(),
                        name='api-import-session-accept-rows',
                    ),
                    path(
                        '',
                        DataImportSessionDetail.as_view(),
                        name='api-import-session-detail',
                    ),
                ]),
            ),
            path('', DataImportSessionList.as_view(), name='api-importer-session-list'),
        ]),
    ),
    path(
        'column-mapping/',
        include([
            path(
                '<int:pk>/',
                DataImportColumnMappingDetail.as_view(),
                name='api-importer-mapping-detail',
            ),
            path(
                '',
                DataImportColumnMappingList.as_view(),
                name='api-importer-mapping-list',
            ),
        ]),
    ),
    path(
        'row/',
        include([
            path(
                '<int:pk>/',
                DataImportRowDetail.as_view(),
                name='api-importer-row-detail',
            ),
            path('', DataImportRowList.as_view(), name='api-importer-row-list'),
        ]),
    ),
]
