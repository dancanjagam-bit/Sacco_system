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
    member_name = serializers.CharField(
        source="member.name",
        read_only=True
    )

    class Meta:
        model = Loan
        fields = [
            "id",
            "member",
            "member_name",
            "amount",
            "balance",
            "interest_rate",
            "status",
            "date_applied",
            "date_updated",
            "last_interest_date",
            "disbursed_at",
        ]

        read_only_fields = [
            "balance",
            "status",
            "date_applied",
            "date_updated",
            "last_interest_date",
            "disbursed_at",
        ]
