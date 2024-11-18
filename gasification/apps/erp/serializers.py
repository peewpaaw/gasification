from rest_framework import serializers

from .models import Counterparty, ConstructionObject


class CounterpartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = "__all__"


class CounterpartySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = ('id', 'inn', 'name', 'guid')


class ConstructionObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionObject
        fields = "__all__"


class ConstructionObjectSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionObject
        fields = ('id', 'code')
