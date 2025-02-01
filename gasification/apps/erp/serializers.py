from rest_framework import serializers

from .models import Counterparty, ConstructionObject


############################
# COUNTERPARTY SERIALIZERS #
############################

class CounterpartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = "__all__"


class CounterpartySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = ('id', 'inn', 'name', 'guid')


class CounterpartyUploadSerializer(serializers.Serializer):
    inn = serializers.CharField(max_length=12)
    name = serializers.CharField(max_length=255)
    guid = serializers.CharField(max_length=36)


####################################
# CONSTRUCTION OBJECTS SERIALIZERS #
####################################

class WorkPackageSerializer(serializers.Serializer):
    pass

class ConstructionObjectUploadSerializer(serializers.Serializer):
    counterparty = serializers.CharField(max_length=36, help_text="GUID 1С контрагента")
    code = serializers.CharField(max_length=255, help_text="Код объекта ПиС")
    guid = serializers.CharField(max_length=36, help_text="Код объекта ПиС")
    address = serializers.CharField(max_length=255, help_text="Адрес объета ПиС")
    work_packages = serializers.ListSerializer(child=serializers.IntegerField(), help_text="Комплекс работ (в массиве)")

    def validate_work_packages(self, value):
        valid_values = {item[0] for item in ConstructionObject.WORK_PACKAGES}
        for item in value:
            if item not in valid_values:
                raise serializers.ValidationError(f"Work packages must be in {valid_values}")
        return value

    def validate_counterparty(self, value):
        counterparty = Counterparty.objects.filter(guid=value)
        if counterparty.exists():
            return counterparty.first()
        raise serializers.ValidationError(f"Counterparty with guid `{value}` does not exist")


class ConstructionObjectSerializer(serializers.ModelSerializer):
    work_packages = serializers.SerializerMethodField()

    def get_work_packages(self, obj):
        return obj.get_work_packages_display_list()

    class Meta:
        model = ConstructionObject
        fields = "__all__"


class ConstructionObjectSimpleSerializer(ConstructionObjectSerializer):
    class Meta:
        model = ConstructionObject
        fields = ('id', 'code', 'address', 'work_packages')
