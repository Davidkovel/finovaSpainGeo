from decimal import Decimal

from app.core.exceptions import InsufficientBalanceError
from app.database.repositories.moneyRepository import MoneyRepository
from app.schemas.common import UserId
from app.schemas.user import BalanceResponse


class MoneyIteractor:
    def __init__(self, money_repository: MoneyRepository):
        self.money_repository = money_repository

    async def get_user_balance(self, user_id: UserId) -> BalanceResponse:
        balance = await self.money_repository.get_balance(user_id)
        return BalanceResponse(balance=balance)

    async def make_deposit(self, user_id: UserId, amount: Decimal) -> BalanceResponse:
        new_balance = await self.money_repository.deposit_money(user_id, amount)
        return BalanceResponse(balance=new_balance)

    async def make_withdrawal(self, user_id: UserId, amount: Decimal) -> BalanceResponse:
        new_balance = await self.money_repository.withdraw_money(user_id, amount)
        balance = await self.money_repository.set_balance(user_id, new_balance)
        return BalanceResponse(balance=balance)

    async def set_user_balance(self, user_id: UserId, new_balance: Decimal) -> BalanceResponse:
        balance = await self.money_repository.set_balance(user_id, new_balance)
        return BalanceResponse(balance=balance)

    async def set_initial_balance(self, user_id: UserId, initial_deposit: Decimal) -> Decimal:
        """Установить начальный баланс (только первый депозит)"""
        initial_deposit = await self.money_repository.set_initial_balance(user_id, initial_deposit)
        return initial_deposit

    async def get_initial_balance(self, user_id: UserId) -> Decimal:
        """Получить начальный депозит пользователя"""
        return await self.money_repository.get_initial_balance(user_id)

    async def update_balance(self, user_id: UserId, amount_change: Decimal) -> BalanceResponse:
        new_balance = await self.money_repository.update_balance(user_id, amount_change)
        return BalanceResponse(balance=new_balance)


    async def multiply_money(self, user_id: UserId, multiply_time: Decimal) -> Decimal:
        balance = await self.money_repository.get_balance(user_id)
        return balance * multiply_time
