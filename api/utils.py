from datetime import datetime
from .models import *
from django.db.models import Sum
from django.core.cache import cache

import logging
logger = logging.getLogger(__name__)

CACHE_TTL = 60


class UsersUtility:
    def login(self, username: str, password: str):
        '''
        Authenticates User

        Parameters:
        username (str): Username of user
        password (str): Password of user

        Returns:
        Dict: User details/Error details

        '''

        logger.info("UsersUtility - Login - Invoked - {}".format(username))
        if not username or not password:
            logger.error(
                "UsersUtility - Login - ERROR - Username or password is blank")
            return {"message": "Wrong username or password!", "code": 401}

        user = cache.get("user_{}_{}".format(username, password))
        logger.info("UsersUtility - Login - Cache - GET")

        if not user:
            logger.info("UsersUtility - Login - Cache - MISS")
            user = Users.objects.filter(username=username, password=password)
            cache.set("user_{}_{}".format(username, password), user, CACHE_TTL)
            logger.info("UsersUtility - Login - Cache - SET")

        if not user:
            logger.error(
                "UsersUtility - Login - ERROR - User does not exists in DB")
            return {"message": "Wrong username or password!", "code": 401}

        result = {
            "name": user[0].name,
            "balance": user[0].balance,
            "user_id": str(user[0].id),
            "code": 200
        }
        logger.info(
            "UsersUtility - Login - SUCCESS - Executed - {}".format(username))

        return result

    def get_credit_score(self, user_id: str):
        '''
        Calculate User's credit score based on borrowed/lent amount

        Parameters:
        user_id (str): User id from Users model

        Returns:
        Dict: Credit score of user

        '''

        logger.info(
            "UsersUtility - GetCreditScore - Invoked - {}".format(user_id))
        if not user_id:
            logger.error(
                "UsersUtility - GetCreditScore - ERROR - UserId is blank")
            return {"message": "Please provide user id", "code": 400}

        transactions_lend = TransactionUtility().get_lend_transactions_by_user_id(
            user_id, "UsersUtility - GetCreditScore")
        lend_sum = transactions_lend.filter(
            transaction_status="paid").aggregate(Sum('transaction_amount'))

        lend_score = self.calculate_lend_score(
            lend_sum["transaction_amount__sum"])

        transactions_borrow = TransactionUtility().get_borrow_transactions_by_user_id(
            user_id, "UsersUtility - GetCreditScore")
        borrow_sum = transactions_borrow.filter(
            transaction_status="paid").aggregate(Sum('transaction_amount'))

        borrow_score = self.calculate_borrow_score(
            borrow_sum["transaction_amount__sum"])

        total_score = lend_score + borrow_score
        logger.info(
            "UsersUtility - GetCreditScore - TotalScore - {}".format(total_score))

        logger.info(
            "UsersUtility - GetCreditScore - SUCCESS - Executed - {}".format(user_id))

        return {"credit_score": total_score, "code": 200}

    def calculate_borrow_score(self, borrow_sum: float):
        '''According total borrowing amount it returns borrowing score'''

        logger.info(
            "UsersUtility - GetCreditScore - CalculateBorrowScore - BorrowSum - {}".format(borrow_sum))
        if borrow_sum in range(0, 101):
            return 100
        elif borrow_sum in range(101, 201):
            return 90
        elif borrow_sum in range(201, 301):
            return 80
        elif borrow_sum in range(301, 401):
            return 70
        elif borrow_sum in range(401, 501):
            return 60
        elif borrow_sum in range(501, 601):
            return 50
        elif borrow_sum in range(601, 701):
            return 40
        elif borrow_sum in range(701, 801):
            return 30
        elif borrow_sum in range(801, 901):
            return 20
        elif borrow_sum in range(901, 1001):
            return 10
        elif borrow_sum >= 1001:
            return 0
        else:
            return 100

    def calculate_lend_score(self, lend_sum: float):
        '''According total lending amount it returns lending score'''

        logger.info(
            "UsersUtility - GetCreditScore - CalculateLendScore - LendSum - {}".format(lend_sum))
        if lend_sum in range(0, 1001):
            return 0
        elif lend_sum in range(1001, 1101):
            return 10
        elif lend_sum in range(1101, 1201):
            return 20
        elif lend_sum in range(1201, 1301):
            return 30
        elif lend_sum in range(1301, 1401):
            return 40
        elif lend_sum in range(1401, 1501):
            return 50
        elif lend_sum in range(1501, 1601):
            return 60
        elif lend_sum in range(1601, 1701):
            return 70
        elif lend_sum in range(1701, 1801):
            return 80
        elif lend_sum in range(1801, 1901):
            return 90
        elif lend_sum in range(1901, 2001):
            return 100
        elif lend_sum >= 2001:
            return 100
        else:
            return 0


class TransactionUtility:
    def get_transactions_by_user_id(self, user_id: str):
        '''
        Fetches all the transactions for the user (he can be either borrower or lender)

        Parameters:
        user_id (str): User id from Users model

        Returns:
        Dict: Transaction history includes amount, type, status, transaction date, transaction with

        '''

        logger.info(
            "TransactionUtility - GetTransactionsByUserId - Invoked - {}".format(user_id))
        if not user_id:
            logger.error(
                "TransactionUtility - GetTransactionsByUserId - ERROR - UserId is blank")
            return {"message": "Please provide user id", "code": 400}

        result = []

        transactions_lend = self.get_lend_transactions_by_user_id(
            user_id, "TransactionUtility - GetTransactionsByUserId")

        for transaction in transactions_lend:
            temp_dict = transaction.__dict__
            result.append({
                "transaction_id": str(temp_dict["id"]),
                "transaction_date": self.format_datetime(
                    temp_dict["transaction_date"]),
                "transaction_from": str(
                    temp_dict["transaction_from_id"]),
                "transaction_with": str(
                    temp_dict["transaction_with_id"]),
                "transaction_status": temp_dict["transaction_status"],
                "transaction_amount": temp_dict["transaction_amount"],
                "transaction_type": "lend",
                "reason": temp_dict["reason"]
            })

        transactions_borrow = self.get_borrow_transactions_by_user_id(
            user_id, "TransactionUtility - GetTransactionsByUserId")

        for transaction in transactions_borrow:
            temp_dict = transaction.__dict__
            result.append({
                "transaction_id": str(temp_dict["id"]),
                "transaction_date": self.format_datetime(
                    temp_dict["transaction_date"]),
                "transaction_from": str(
                    temp_dict["transaction_with_id"]),
                "transaction_with": str(
                    temp_dict["transaction_from_id"]),
                "transaction_status": temp_dict["transaction_status"],
                "transaction_amount": temp_dict["transaction_amount"],
                "transaction_type": "borrow",
                "reason": temp_dict["reason"]
            })

        if len(result) == 0:
            logger.error(
                "TransactionUtility - GetTransactionsByUserId - ERROR - No transaction for given UserId")
            return {"message": "There is no transactions for given user id", "code": 404}

        logger.info(
            "TransactionUtility - GetTransactionsByUserId - SUCCESS - Executed {}".format(user_id))
        return {"user_id": user_id, "transactions": result, "code": 200}

    def format_datetime(self, datetime_obj: datetime):
        '''Format datetime object to YYYY-MM-DD string format'''

        return datetime_obj.strftime("%Y-%m-%d")

    def get_datetime_obj(self, date_str: str):
        '''Returns datetime obj from string date format YYYY-MM-DD'''

        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception as ex:
            # print(str(ex))
            return datetime.now()

    def add_transaction(self, transaction_from: str, transaction_with: str, amount: float, transaction_type: str, status: str, transaction_date: str, reason: str):
        '''
        Adds transaction in database

        Parameters:
        transaction_from (str): User responsible for transaction
        transaction_with (str): With whom transaction is done
        amount (float): Transaction amount(negative, positive)
        transaction_type (str): It can be lend/borrow
        status (str): Status of transaction like paid/unpaid
        transaction_date (str): Date and time of transaction
        reason (str): Reason of transaction

        Returns:
        Dict: Result of create transaction operation

        '''

        logger.info("TransactionUtility - AddTransaction - Invoked")

        if not transaction_from:
            logger.error(
                "TransactionUtility - AddTransaction - ERROR - Transaction FROM UserID is blank")
            return {"message": "Please provide transaction from user id", "code": 400}
        if not transaction_with:
            logger.error(
                "TransactionUtility - AddTransaction - ERROR - Transaction WITH UserID is blank")
            return {"message": "Please provide transaction with user id", "code": 400}
        if not amount:
            logger.error(
                "TransactionUtility - AddTransaction - ERROR - Transaction amount is blank")
            return {"message": "Please provide transaction amount", "code": 400}
        if not transaction_type:
            logger.error(
                "TransactionUtility - AddTransaction - ERROR - Transaction type is blank")
            return {"message": "Please provide transaction type", "code": 400}
        if not status:
            logger.error(
                "TransactionUtility - AddTransaction - ERROR - Transaction status is blank")
            return {"message": "Please provide transaction status", "code": 400}
        if amount <= 0:
            logger.error(
                "TransactionUtility - AddTransaction - ERROR - Transaction amount is negative/zero")
            return {"message": "Please provide postive non-zero transaction amount", "code": 400}


        try:
            transaction_from_user = Users.objects.get(id=transaction_from)
        except Users.DoesNotExist:
            logger.error(
                "TransactionUtility - AddTransaction - ERROR - Transaction FROM user does not exists in DB")
            return {"message": "Transaction From User does not exist", "code": 404}

        try:
            transaction_with_user = Users.objects.get(id=transaction_with)
        except Users.DoesNotExist:
            logger.error(
                "TransactionUtility - AddTransaction - ERROR - Transaction WITH user does not exists in DB")
            return {"message": "Transaction With User does not exist", "code": 404}

        try:
            if transaction_type == "borrow":
                logger.info(
                    "TransactionUtility - AddTransaction - Borrow - Create Transaction")
                transaction = Transactions.objects.create(
                    transaction_from=transaction_with_user,
                    transaction_with=transaction_from_user,
                    transaction_amount=amount,
                    transaction_status=status,
                    transaction_date=self.get_datetime_obj(transaction_date),
                    reason=reason
                )
                self.delete_transaction_cache(
                    [transaction_from_user.id, transaction_with_user.id], "TransactionUtility - AddTransaction")

                if status == "paid":
                    logger.info(
                        "TransactionUtility - AddTransaction - Borrow x Paid - Update Users Balance")
                    transaction_with_user.balance = transaction_with_user.balance - amount
                    transaction_with_user.save()

                    transaction_from_user.balance = transaction_from_user.balance + amount
                    transaction_from_user.save()
            else:
                logger.info(
                    "TransactionUtility - AddTransaction - Lend - Create Transaction")
                transaction = Transactions.objects.create(
                    transaction_from=transaction_from_user,
                    transaction_with=transaction_with_user,
                    transaction_amount=amount,
                    transaction_status=status,
                    transaction_date=self.get_datetime_obj(transaction_date),
                    reason=reason
                )
                self.delete_transaction_cache(
                    [transaction_from_user.id, transaction_with_user.id], "TransactionUtility - AddTransaction")

                if status == "paid":
                    logger.info(
                        "TransactionUtility - AddTransaction - Lend x Paid - Update Users Balance")
                    transaction_with_user.balance = transaction_with_user.balance + amount
                    transaction_with_user.save()

                    transaction_from_user.balance = transaction_from_user.balance - amount
                    transaction_from_user.save()

            logger.info(
                "TransactionUtility - AddTransaction - SUCCESS - Executed")
            return {"message": "Transaction successfully added - {}".format(transaction.id), "code": 200}

        except Exception as e:
            logger.error(
                "TransactionUtility - AddTransaction - ERROR - Exception - {}".format(e))
            return {"message": "Error occured while adding transaction", "code": 500}

    def mark_transaction_paid(self, transaction_id: str):
        '''
        Changes transacrtion status to paid

        Parameters:
        transaction_id (str): Transaction id from Transactions model

        Returns:
        Dict: Result of update transaction status

        '''

        logger.info(
            "TransactionUtility - MarkTransactionPaid - Invoked - {}".format(transaction_id))
        if not transaction_id:
            logger.error(
                "TransactionUtility - MarkTransactionPaid - ERROR - TransactionId is blank")
            return {"message": "Please provide transaction id", "code": 400}

        try:
            transaction = Transactions.objects.get(
                id=transaction_id)
        except Transactions.DoesNotExist:
            logger.error(
                "TransactionUtility - MarkTransactionPaid - ERROR - Exception - TransactionId does not exists in DB")
            return {"message": "Given transaction id does not exists", "code": 404}

        try:
            logger.info(
                "TransactionUtility - MarkTransactionPaid - Update transaction status to paid")
            transaction.transaction_status = "paid"
            transaction.save()

            transaction_from_user = transaction.transaction_from
            transaction_with_user = transaction.transaction_with

            self.delete_transaction_cache(
                [transaction_from_user.id, transaction_with_user.id], "TransactionUtility - MarkTransactionPaid")

            logger.info(
                "TransactionUtility - MarkTransactionPaid - Update Users Balance")
            transaction_with_user.balance = transaction_with_user.balance + \
                transaction.transaction_amount
            transaction_with_user.save()

            transaction_from_user.balance = transaction_from_user.balance - \
                transaction.transaction_amount
            transaction_from_user.save()

            logger.info(
                "TransactionUtility - MarkTransactionPaid - SUCCESS - Executed - {}".format(transaction_id))
            return {"message": "Transaction successfully updated - {}".format(transaction_id), "code": 200}
        except Exception as e:
            logger.error(
                "TransactionUtility - MarkTransactionPaid - ERROR - Exception - {}".format(e))
            return {"message": "Error occured while updating transaction", "code": 500}

    def get_lend_transactions_by_user_id(self, user_id: str, parent_util_function: str):
        '''
        Returns all transaction of type lend by user id

        Parameters:
        user_id (str): User id from Users model
        parent_util_function (str): From which parent function this function called

        Returns:
        Queryset: All lend transactions for given user id

        '''

        logger.info(
            "{} - GetLendTransactionsByUserId - Invoked - {}".format(parent_util_function, user_id))

        transactions_lend = cache.get("trans_lend_user_id_{}".format(user_id))
        logger.info(
            "{} - GetLendTransactionsByUserId - Cache - GET".format(parent_util_function))

        if not transactions_lend:
            logger.info(
                "{} - GetLendTransactionsByUserId - Cache - MISS".format(parent_util_function))
            transactions_lend = Transactions.objects.filter(
                transaction_from__id=user_id)
            cache.set("trans_lend_user_id_{}".format(
                user_id), transactions_lend, CACHE_TTL)
            logger.info(
                "{} - GetLendTransactionsByUserId - Cache - SET".format(parent_util_function))

        logger.info(
            "{} - GetLendTransactionsByUserId - Executed - {}".format(parent_util_function, user_id))

        return transactions_lend

    def get_borrow_transactions_by_user_id(self, user_id: str, parent_util_function: str):
        '''
        Returns all transaction of type borrow by user id

        Parameters:
        user_id (str): User id from Users model
        parent_util_function (str): From which parent function this function called

        Returns:
        Queryset: All borrow transactions for given user id

        '''

        logger.info(
            "{} - GetBorrowTransactionsByUserId - Invoked - {}".format(parent_util_function, user_id))

        transactions_borrow = cache.get(
            "trans_borrow_user_id_{}".format(user_id))
        logger.info(
            "{} - GetBorrowTransactionsByUserId - Cache - GET".format(parent_util_function))

        if not transactions_borrow:
            logger.info(
                "{} - GetBorrowTransactionsByUserId - Cache - MISS".format(parent_util_function))
            print("cache miss")
            transactions_borrow = Transactions.objects.filter(
                transaction_with__id=user_id)
            cache.set("trans_borrow_user_id_{}".format(
                user_id), transactions_borrow, CACHE_TTL)
            logger.info(
                "{} - GetBorrowTransactionsByUserId - Cache - SET".format(parent_util_function))

        logger.info(
            "{} - GetBorrowTransactionsByUserId - Executed - {}".format(parent_util_function, user_id))

        return transactions_borrow

    def delete_transaction_cache(self, user_ids: list, parent_util_function: str):
        '''Deletes tranaction details of user from cache'''

        logger.info(
            "{} - DeleteTransactionCache - Invoked - {}".format(parent_util_function, user_ids))
        for user_id in user_ids:
            cache.delete("trans_lend_user_id_{}".format(user_id))
            cache.delete("trans_borrow_user_id_{}".format(user_id))

        logger.info(
            "{} - DeleteTransactionCache - SUCCESS - Executed - {}".format(parent_util_function, user_ids))
