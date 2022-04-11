import json
import time

from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from .utils import *

import logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):
    '''
    This class handles Users model related API endpoints

    GET: Return credit score of User
    POST: User login(this can be GET call also, but preferred way to do sign in and sign out is POST call)

    '''

    def post(self, request, *args, **kwargs):
        logger.info("UserView - POST - Login - Invoked")
        start_time = time.time()
        request_body = json.loads(request.body.decode('utf-8'))
        payload = UsersUtility().login(request_body.get(
            "username"), request_body.get("password"))
        code = payload.pop("code", 500)
        logger.info(
            "UserView - POST - Login - Executed - {}".format(time.time() - start_time))

        return HttpResponse(json.dumps(payload), content_type="application/json", status=code)

    def get(self, request, *args, **kwargs):
        logger.info("UserView - GET - GetCreditScore - Invoked")
        start_time = time.time()
        request_body = json.loads(request.body.decode('utf-8'))
        payload = UsersUtility().get_credit_score(request_body.get(
            "user_id"))
        code = payload.pop("code", 500)
        logger.info(
            "UserView - GET - GetCreditScore - Executed - {}".format(time.time() - start_time))

        return HttpResponse(json.dumps(payload), content_type="application/json", status=code)


@method_decorator(csrf_exempt, name='dispatch')
class TransactionView(View):
    '''
    This class handles Transactions model related API endpoints

    GET: Returns transactions history of user
    POST: Adds transaction
    PATCH: Marks transaction as paid

    '''

    def get(self, request,  *args, **kwargs):
        logger.info("TransactionView - GET - GetTransactionsByUserId - Invoked")
        start_time = time.time()
        request_body = json.loads(request.body.decode('utf-8'))
        payload = TransactionUtility().get_transactions_by_user_id(
            request_body.get("user_id"))
        code = payload.pop("code", 500)
        logger.info(
            "TransactionView - GET - GetTransactionsByUserId - Executed - {}".format(time.time() - start_time))

        return HttpResponse(json.dumps(payload), content_type="application/json", status=code)

    def post(self, request,  *args, **kwargs):
        logger.info("TransactionView - POST - AddTransaction - Invoked")
        start_time = time.time()
        request_body = json.loads(request.body.decode('utf-8'))
        payload = TransactionUtility().add_transaction(
            request_body.get("transaction_from"),
            request_body.get("transaction_with"),
            request_body.get("transaction_amount"),
            request_body.get("transaction_type"),
            request_body.get("transaction_status"),
            request_body.get("transaction_date"),
            request_body.get("reason")
        )
        code = payload.pop("code", 500)
        logger.info(
            "TransactionView - POST - AddTransaction - Executed - {}".format(time.time() - start_time))

        return HttpResponse(json.dumps(payload), content_type="application/json", status=code)

    def patch(self, request,  *args, **kwargs):
        logger.info("TransactionView - PATCH - MarkTransactionPaid - Invoked")
        start_time = time.time()
        request_body = json.loads(request.body.decode('utf-8'))
        payload = TransactionUtility().mark_transaction_paid(
            request_body.get("transaction_id")
        )
        code = payload.pop("code", 500)
        logger.info(
            "TransactionView - PATCH - MarkTransactionPaid - Executed - {}".format(time.time() - start_time))

        return HttpResponse(json.dumps(payload), content_type="application/json", status=code)
