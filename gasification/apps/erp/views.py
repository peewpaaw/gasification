from abc import abstractmethod

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Counterparty, ConstructionObject
from .serializers import CounterpartySerializer, ConstructionObjectSerializer
from .serializers import CounterpartyUploadSerializer, ConstructionObjectUploadSerializer


class CounterpartyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Counterparty.objects.all()
    serializer_class = CounterpartySerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'has_related_user',  # Имя параметра
                openapi.IN_QUERY,  # Тип параметра (query параметр)
                description='Для получения зарегистрированных контрагентов',
                type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Counterparty.objects.all()
        has_related_user = self.request.query_params.get('has_related_user')
        has_related_user = str(has_related_user).lower() == 'true'
        if has_related_user:
            queryset = queryset.filter(
                pk__in=get_user_model().objects.all().values_list('counterparty', flat=True)
            )
        return queryset



class ConstructionObjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConstructionObjectSerializer

    def get_queryset(self):
        queryset = ConstructionObject.objects.all()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            queryset = queryset.filter(counterparty=self.request.user.counterparty)
        return queryset


class ERPUploadBaseView(APIView):
    permission_classes = [IsAdminUser]

    @abstractmethod
    def get_serializer_class(self):
        return CounterpartySerializer

    @abstractmethod
    def get_model_class(self):
        return Counterparty

    def post(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        data = request.data if isinstance(request.data, list) else [request.data]
        created, updated = 0, 0

        for item in data:
            serializer = serializer_class(data=item)
            serializer.is_valid(raise_exception=True)

            #existed_qs = self.get_model_class().objects.filter(guid=[item["guid"] for item in data])
            existed_qs = self.get_model_class().objects.filter(guid=item['guid'])
            if existed_qs.exists():
                existed_qs.update(**serializer.validated_data)
                updated += 1
                continue
            self.get_model_class().objects.create(**serializer.validated_data)
            created += 1

        result = {
            'created': created,
            'updated': updated,
        }
        return Response(
            {"success": True, "result": result},
            status=status.HTTP_200_OK
        )


class CounterpartyUploadView(ERPUploadBaseView):
    """
        Контрагенты
    """
    def get_model_class(self):
        return Counterparty

    def get_serializer_class(self):
        return CounterpartyUploadSerializer

    @swagger_auto_schema(request_body=CounterpartyUploadSerializer)
    def post(self, request, *args, **kwargs):
        """
            Выгрузка контрагентов из 1С

            При проходе контрагента, уже имеющегося в системе (по GUID), выполнится обновление.
        """
        return super().post(request, *args, **kwargs)


class ConstructionObjectUploadView(ERPUploadBaseView):
    """
        Объекты проектирования и строительства
    """
    def get_model_class(self):
        return ConstructionObject

    def get_serializer_class(self):
        return ConstructionObjectUploadSerializer

    @swagger_auto_schema(request_body=ConstructionObjectUploadSerializer(many=True))
    def post(self, request, *args, **kwargs):
        """
            Выгрузка объектов проектирования и строительства из 1С

            При проходе объекта, уже имеющегося в системе (по GUID), выполнится обновление.
            Связь с контрагентом по его GUID. Можно выгружать объекты только тех контрагентов,
            которые зарегистрированы в системе (/counterparties?has_related_user=True)
        """
        return super().post(request, *args, **kwargs)
