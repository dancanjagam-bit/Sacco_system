from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import Member, Transaction, Loan
from .serializers import MemberSerializer, TransactionSerializer, LoanSerializer

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    @action(detail=True, methods=['post'])
    def repay(self, request, pk=None):
        loan = self.get_object()
        amount = Decimal(request.data.get("amount", "0"))

        # create a transaction
        Transaction.objects.create(
            member=loan.member,
            loan=loan,
            amount=amount,
            source="Loan Repayment"
        )

        # reduce loan balance
        loan.balance -= amount
        if loan.balance <= 0:
            loan.balance = 0
            loan.status = "REPAID"
        loan.save()

        return Response(
            {"message": "Repayment recorded", "balance": str(loan.balance)},
            status=status.HTTP_200_OK
        )

