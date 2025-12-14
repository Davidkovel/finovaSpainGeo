from app.database.repositories.cardRepository import CardRepository
from app.schemas.user import BankCardResponse, BankCardAndHolderResponse


class CardIteractor:
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    async def get_bank_card(self) -> BankCardResponse:
        """Получить реквизиты банка"""
        card = await self.card_repository.get_card_data()

        if card is None:
            # Возвращаем дефолтные значения
            return BankCardResponse(
                bank_name="Banco Pichincha",
                account_type="Cuenta de ahorro transaccional",
                account_number="2215000531",
                card_holder_name="Carlos Santiago Sarabia Garces",
                holder_id="0605104458",
                phone_number=None,
                photo_path=None
            )

        return BankCardResponse(
            bank_name=card.bank_name,
            account_type=card.account_type,
            account_number=card.account_number,
            card_holder_name=card.card_holder_name,
            holder_id=card.holder_id,
            phone_number=card.phone_number,
            photo_path=card.photo_path
        )

    async def set_bank_card(
            self,
            bank_name: str = None,
            account_type: str = None,
            account_number: str = None,
            card_holder_name: str = None,
            holder_id: str = None,
            phone_number: str = None,
            photo_path: str = None
    ) -> BankCardResponse:
        """Сохранить реквизиты банка"""

        card = await self.card_repository.set_card_data(
            bank_name=bank_name or "Banco Pichincha",
            account_type=account_type or "Cuenta de ahorro transaccional",
            account_number=account_number,
            card_holder_name=card_holder_name,
            holder_id=holder_id,
            phone_number=phone_number,
            photo_path=photo_path
        )

        return BankCardResponse(
            bank_name=card.bank_name,
            account_type=card.account_type,
            account_number=card.account_number,
            card_holder_name=card.card_holder_name,
            holder_id=card.holder_id,
            phone_number=card.phone_number,
            photo_path=card.photo_path
        )

    async def set_bank_card_with_photo(
            self,
            photo_path: str,
            bank_name: str = None,
            account_type: str = None,
            account_number: str = None,
            card_holder_name: str = None,
            holder_id: str = None,
            phone_number: str = None,
    ) -> BankCardResponse:
        """Специальный метод для установки карты с фото"""
        return await self.set_bank_card(
            bank_name=bank_name,
            account_type=account_type,
            account_number=account_number,
            card_holder_name=card_holder_name,
            holder_id=holder_id,
            phone_number=phone_number,
            photo_path=photo_path
        )
