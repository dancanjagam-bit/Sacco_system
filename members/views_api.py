from decimal import Decimal
from .permissions import IsAdmin

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import (
    Member,
    Transaction,
    Loan,
    Savings,
    LoanRepayment
)
from .serializers import (
    MemberSerializer,
    TransactionSerializer,
    LoanSerializer,
    SavingsSerializer
)


# =========================
# SAVINGS VIEWSET
# =========================
class SavingsViewSet(viewsets.ModelViewSet):
    queryset = Savings.objects.all()
    serializer_class = SavingsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        saving = serializer.save()

        member = saving.member
        member.balance += saving.amount
        member.save()

        Transaction.objects.create(
            member=member,
            amount=saving.amount,
            type="DEPOSIT"
        )


# =========================
# MEMBER VIEWSET
# =========================
class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]


# =========================
# TRANSACTION VIEWSET
# =========================
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by("-date")
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        loan_id = self.request.query_params.get("loan")
        member_id = self.request.query_params.get("member")

        if loan_id:
            queryset = queryset.filter(loan_id=loan_id)

        if member_id:
            queryset = queryset.filter(member_id=member_id)

        return queryset


# =========================
# LOAN VIEWSET
# =========================

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        loan = self.get_object()

        if loan.status != "PENDING":
            return Response(
                {"error": "Loan already processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        loan.status = "APPROVED"

        # initialize balance if not already set
        if not loan.balance:
            loan.balance = loan.amount

        loan.save()

        return Response({"message": "Loan approved"})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        loan = self.get_object()

        if loan.status != "PENDING":
            return Response(
                {"error": "Loan already processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        loan.status = "REJECTED"
        loan.save()

        return Response({"message": "Loan rejected"})

    @action(detail=True, methods=['post'])
    def repay(self, request, pk=None):

        with transaction.atomic():

            loan = self.get_object()

            try:
                amount = Decimal(request.data.get("amount", "0"))
            except Exception:
                return Response(
                    {"error": "Invalid amount format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if amount <= 0:
                return Response(
                    {"error": "Invalid repayment amount"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if loan.status != "APPROVED":
                return Response(
                    {"error": "Only approved loans can receive repayments"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if amount > loan.balance:
                return Response(
                    {"error": "Repayment amount exceeds loan balance"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                LoanRepayment.objects.create(
                    loan=loan,
                    amount=amount
                )

                repayment = Transaction.objects.create(
                    member=loan.member,
                    loan=loan,
                    amount=amount,
                    type="LOAN_REPAYMENT"
                )

            loan.balance -= amount

            if loan.balance == 0:
                loan.status = "REPAID"

            loan.save()

            return Response(
                {
                    "message": "Repayment recorded successfully",
                    "loan_id": loan.id,
                    "balance": str(loan.balance),
                    "status": loan.status,
                    "repayment": {
                        "id": repayment.id,
                        "amount": str(repayment.amount),
                        "date": repayment.date.strftime("%Y-%m-%d %H:%M:%S")
                    }
                },
                status=status.HTTP_200_OK
            )
    # =========================
    # LOAN REPAYMENT ACTION
    # =========================
    @action(detail=True, methods=['post'])
    def repay(self, request, pk=None):
        loan = self.get_object()
        amount = Decimal(request.data.get("amount", "0"))

        if amount <= 0:
            return Response(
                {"error": "Invalid repayment amount"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # create repayment transaction
        repayment = Transaction.objects.create(
            member=loan.member,
            loan=loan,
            amount=amount,
            type="LOAN_REPAYMENT"
            )

        # update loan balance
        loan.balance -= amount
        if loan.balance <= 0:
            loan.balance = 0
            loan.status = "REPAID"

        loan.save()

        return Response(
            {
                "message": "Repayment recorded successfully",
                "loan_id": loan.id,
                "balance": str(loan.balance),
                "status": loan.status,
                "repayment": {
                    "id": repayment.id,
                    "amount": str(repayment.amount),
                    "date": repayment.date.strftime("%Y-%m-%d %H:%M:%S")
                }
            },
            status=status.HTTP_200_OK
        )
