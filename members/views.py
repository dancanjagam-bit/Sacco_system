import json
import base64
import requests

from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .models import Member, Transaction, Loan
from django.db.models import Sum, Count
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Member, Savings, Loan, LoanRepayment

# =========================
# FRONTEND
# =========================
def frontend(request):
    return render(request, "index.html")


def home(request):
    return HttpResponse("Welcome to the SACCO System API")


# =========================
# UTILITY: ACCESS TOKEN
# =========================
def get_access_token():
    consumer_key = "YOUR_CONSUMER_KEY"
    consumer_secret = "YOUR_CONSUMER_SECRET"

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))

    return response.json().get("access_token")


# =========================
# BANK CALLBACK (DEPOSIT)
# =========================
@csrf_exempt
def bank_callback(request):
    data = json.loads(request.body)

    phone = data.get("reference")
    amount = float(data.get("amount", 0))

    try:
        member = Member.objects.get(phone=phone)

        member.balance += amount
        member.save()

        Transaction.objects.create(
            member=member,
            amount=amount,
            type="DEPOSIT"
        )

        return JsonResponse({
            "message": "Bank deposit successful",
            "balance": float(member.balance)
        })

    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)


# =========================
# STK PUSH
# =========================
@csrf_exempt
def stk_push(request):
    data = json.loads(request.body)

    phone = data.get("phone")
    amount = int(data.get("amount"))

    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    shortcode = "YOUR_PAYBILL"
    passkey = "YOUR_PASSKEY"

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (shortcode + passkey + timestamp).encode()
    ).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": "https://yourdomain.com/api/mpesa/callback/",
        "AccountReference": "SACCO Deposit",
        "TransactionDesc": "Deposit to SACCO"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )

    return JsonResponse(response.json())


# =========================
# M-PESA CALLBACK (DEPOSIT)
# =========================
@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)

    try:
        items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
        phone = items[4]["Value"]
        amount = float(items[0]["Value"])

        member = Member.objects.get(phone=phone)

        member.balance += amount
        member.save()

        Transaction.objects.create(
            member=member,
            amount=amount,
            type="DEPOSIT"
        )

        return JsonResponse({
            "message": "Deposit successful",
            "balance": float(member.balance)
        })

    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# =========================
# M-PESA LOAN REPAYMENT CALLBACK
# =========================
@csrf_exempt
def mpesa_repay_callback(request):
    data = json.loads(request.body)

    try:
        items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
        phone = items[4]["Value"]
        amount = float(items[0]["Value"])

        member = Member.objects.get(phone=phone)

        loan = Loan.objects.filter(
            member=member,
            status="APPROVED"
        ).last()

        if not loan:
            return JsonResponse({"error": "No active loan"}, status=404)

        loan.balance -= amount

        if loan.balance <= 0:
            loan.balance = 0
            loan.status = "REPAID"

        loan.save()

        Transaction.objects.create(
            member=member,
            loan=loan,
            amount=amount,
            type="LOAN_REPAYMENT"
        )

        return JsonResponse({
            "message": "Repayment successful",
            "remaining_balance": float(loan.balance),
            "status": loan.status
        })

    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# =========================
# MANUAL DEPOSIT
# =========================
@csrf_exempt
def deposit(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    phone = data.get("phone")
    amount = float(data.get("amount", 0))

    try:
        member = Member.objects.get(phone=phone)

        member.balance += amount
        member.save()

        Transaction.objects.create(
            member=member,
            amount=amount,
            type="DEPOSIT"
        )

        return JsonResponse({
            "message": "Deposit successful",
            "balance": float(member.balance)
        })

    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)


# =========================
# BALANCE CHECK
# =========================
@csrf_exempt
def balance(request, phone):
    try:
        member = Member.objects.get(phone=phone)

        return JsonResponse({
            "name": member.name,
            "balance": float(member.balance)
        })

    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)


# =========================
# APPLY LOAN
# =========================
@csrf_exempt
def apply_loan(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    phone = data.get("phone")
    amount = float(data.get("amount", 0))

    try:
        member = Member.objects.get(phone=phone)

        if member.balance < amount * 0.5:
            return JsonResponse({
                "error": "Insufficient savings for eligibility"
            }, status=400)

        loan = Loan.objects.create(
            member=member,
            amount=amount,
            balance=amount,
            status="PENDING"
        )

        return JsonResponse({
            "message": "Loan applied",
            "loan_id": loan.id,
            "status": loan.status
        })

    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)


# =========================
# APPROVE LOAN
# =========================
@csrf_exempt
def approve_loan(request, loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)

        loan.status = "APPROVED"
        loan.save()

        return JsonResponse({
            "message": "Loan approved",
            "loan_id": loan.id
        })

    except Loan.DoesNotExist:
        return JsonResponse({"error": "Loan not found"}, status=404)


# =========================
# MANUAL REPAY LOAN
# =========================
@csrf_exempt
def repay_loan(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    loan_id = data.get("loan_id")
    amount = float(data.get("amount", 0))

    try:
        loan = Loan.objects.get(id=loan_id)

        if loan.status != "APPROVED":
            return JsonResponse({"error": "Loan not active"}, status=400)

        loan.balance -= amount

        if loan.balance <= 0:
            loan.balance = 0
            loan.status = "REPAID"

        loan.save()

        Transaction.objects.create(
            member=loan.member,
            loan=loan,
            amount=amount,
            type="LOAN_REPAYMENT"
        )

        return JsonResponse({
            "message": "Repayment successful",
            "remaining_balance": float(loan.balance),
            "status": loan.status
        })

    except Loan.DoesNotExist:
        return JsonResponse({"error": "Loan not found"}, status=404)
# =========================
# DASHBOARD APIs (CLEAN)
# =========================

@api_view(["GET"])
def dashboard_summary(request):
    return Response({
        "total_members": Member.objects.count(),
        "total_savings": Savings.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "total_loans": Loan.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "total_repayments": LoanRepayment.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "active_loans": Loan.objects.filter(status="APPROVED").count(),
    })


@api_view(["GET"])
def member_dashboard(request, phone):
    try:
        member = Member.objects.get(phone=phone)

        savings = member.savings.aggregate(total=Sum("amount"))["total"] or 0
        loans = member.loans.aggregate(total=Sum("balance"))["total"] or 0
        repayments = LoanRepayment.objects.filter(
            loan__member=member
        ).aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "member": member.name,
            "phone": member.phone,
            "balance": float(member.balance),
            "total_savings": float(savings),
            "loan_balance": float(loans),
            "total_repayments": float(repayments),
            "loan_count": member.loans.count()
        })

    except Member.DoesNotExist:
        return Response({"error": "Member not found"}, status=404)
