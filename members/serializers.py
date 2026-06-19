from rest_framework import serializers
from .models import Member, Transaction, Loan
from .models import Savings

class SavingsSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(
        source="member.name",
        read_only=True
    )

    class Meta:
        model = Savings
        fields = "__all__"

class MemberSerializer(serializers.ModelSerializer):
    total_savings = serializers.ReadOnlyField()

    class Meta:
        model = Member
        fields = "__all__"

class TransactionSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.name", read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.name", read_only=True)

    class Meta:
        model = Loan
        fields = '__all__'

    def validate_status(self, value):
        allowed_statuses = ["PENDING", "APPROVED", "REJECTED", "REPAID"]
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of {allowed_statuses}."
            )
        return value

