from decimal import Decimal
from datetime import date
from django.db import transaction
from .models import Loan
from .models import LoanRepayment, Transaction


def apply_daily_interest():
    loans = Loan.objects.filter(status="APPROVED")

    today = date.today()

    for loan in loans:
        if not loan.last_interest_date:
            loan.last_interest_date = today
            loan.save()
            continue

        days = (today - loan.last_interest_date).days
        if days <= 0:
            continue

        daily_rate = Decimal(loan.interest_rate) / Decimal("100") / Decimal("365")

        with transaction.atomic():
            interest = loan.balance * daily_rate * days
            loan.balance += interest
            loan.last_interest_date = today
            loan.save()


def repay_loan(loan, amount):
    amount = Decimal(amount)

    with transaction.atomic():

        # 1. Apply interest-first repayment logic
        interest_portion = min(amount, loan.balance - loan.amount)
        principal_portion = amount - interest_portion

        loan.balance -= amount
        if loan.balance <= 0:
            loan.balance = 0
            loan.status = "REPAID"

        loan.save()

        # 2. Save repayment
        LoanRepayment.objects.create(
            loan=loan,
            amount=amount
        )

        # 3. Ledger entry
        Transaction.objects.create(
            member=loan.member,
            loan=loan,
            amount=amount,
            type="LOAN_REPAYMENT"
        )
