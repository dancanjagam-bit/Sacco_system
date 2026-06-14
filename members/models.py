from django.db import models

# Create your models here.
from django.utils import timezone

class Member(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Loan(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("REPAID", "Repaid"),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="loans")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    date_applied = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.member.name} – Loan {self.amount} [{self.status}]"


class Transaction(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="transactions")
    loan = models.ForeignKey("Loan", on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=50, default="Manual")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.loan:
            return f"{self.member.name} – Loan Repayment {self.amount}"
        return f"{self.member.name} – {self.source} {self.amount}"


