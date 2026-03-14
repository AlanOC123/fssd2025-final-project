from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet


class ApexReadOnlyModelViewSet(ReadOnlyModelViewSet):
    ordering_fields = ["created_at", "updated_at", "id"]
    ordering = ["id"]


class NormalisedLookupViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["code", "label", "description"]
    ordering_fields = ["order_index", "label", "code"]
    ordering = ["order_index", "label"]
