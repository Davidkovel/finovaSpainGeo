from datetime import datetime
from pathlib import Path
from typing import List, Any, Coroutine

from dns.e164 import query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres.models import BankCardModel


class CardRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    # async def get_card_number(self) -> str:
    #     query = select(BankCardModel.card_number)
    #     result = await self.db_session.execute(query)
    #     card_number = result.scalar_one_or_none()
    #
    #     # Если карты нет в базе, возвращаем дефолтное значение
    #     if card_number is None:
    #         return "8600 0000 0000 0000"  # или любое другое дефолтное значение
    #
    #     return card_number

    async def get_card_data(self) -> BankCardModel | None:
        """Получить реквизиты банка"""
        query = select(BankCardModel).limit(1)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_card_number(self) -> str:
        card_number, _, _, _ = await self.get_card_data()
        return card_number

    async def get_card_holder_name(self) -> str:
        _, card_holder_name, _, _ = await self.get_card_data()
        return card_holder_name

    async def get_phone_number(self) -> str:
        _, _, phone_number, _ = await self.get_card_data()
        return phone_number

    async def get_photo_file_id(self) -> str:
        _, _, _, photo_file_id = await self.get_card_data()
        return photo_file_id

    async def set_card_data(
            self,
            bank_name: str,
            account_type: str,
            account_number: str,
            card_holder_name: str,
            holder_id: str = None,
            phone_number: str = None,
            photo_path: str = None
    ) -> BankCardModel:  # 🔹 ИЗМЕНЕНО: возвращаем модель
        """Сохранить или обновить реквизиты банка"""

        # Проверяем существующую запись
        existing_query = select(BankCardModel)
        existing_result = await self.db_session.execute(existing_query)
        existing_card = existing_result.scalar_one_or_none()

        if existing_card:
            # Обновляем существующую
            if photo_path is None:
                photo_path = existing_card.photo_path

            query = (
                update(BankCardModel)
                .where(BankCardModel.id == existing_card.id)
                .values(
                    bank_name=bank_name,
                    account_type=account_type,
                    account_number=account_number,
                    card_holder_name=card_holder_name,
                    holder_id=holder_id,
                    phone_number=phone_number,
                    photo_path=photo_path,
                )
            )
            await self.db_session.execute(query)
            await self.db_session.commit()

            # Получаем обновленную запись
            result = await self.db_session.execute(
                select(BankCardModel).where(BankCardModel.id == existing_card.id)
            )
            return result.scalar_one()
        else:
            # Создаем новую
            new_card = BankCardModel(
                bank_name=bank_name,
                account_type=account_type,
                account_number=account_number,
                card_holder_name=card_holder_name,
                holder_id=holder_id,
                phone_number=phone_number,
                photo_path=photo_path
            )
            self.db_session.add(new_card)
            await self.db_session.commit()
            await self.db_session.refresh(new_card)
            return new_card

    # async def set_card_number(self, card_number: str) -> str:
    #     current_holder_name = await self.get_card_holder_name()
    #     current_phone = await self.get_phone_number()
    #     current_photo = await self.get_photo_file_id()
    #     card_number, _, _, _ = await self.set_card_data(
    #         card_number,
    #         current_holder_name,
    #         current_phone,
    #         current_photo
    #     )
    #     return card_number
    #
    # async def set_card_holder_name(self, holder_name: str) -> str:
    #     current_card_number = await self.get_card_number()
    #     current_phone = await self.get_phone_number()
    #     current_photo = await self.get_photo_file_id()
    #     _, holder_name, _, _ = await self.set_card_data(
    #         current_card_number,
    #         holder_name,
    #         current_phone,
    #         current_photo
    #     )
    #     return holder_name
    #
    # async def set_phone_number(self, phone_number: str) -> str:
    #     current_card_number = await self.get_card_number()
    #     current_holder_name = await self.get_card_holder_name()
    #     current_photo = await self.get_photo_file_id()
    #     _, _, phone_number, _ = await self.set_card_data(
    #         current_card_number,
    #         current_holder_name,
    #         phone_number,
    #         current_photo
    #     )
    #     return phone_number
    #
    # async def set_photo_file_id(self, photo_file_id: str) -> str:
    #     current_card_number = await self.get_card_number()
    #     current_holder_name = await self.get_card_holder_name()
    #     current_phone = await self.get_phone_number()
    #     _, _, _, photo_file_id = await self.set_card_data(
    #         current_card_number,
    #         current_holder_name,
    #         current_phone,
    #         photo_file_id
    #     )
    #     return photo_file_id
