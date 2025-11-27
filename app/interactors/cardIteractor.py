from app.database.repositories.cardRepository import CardRepository
from app.schemas.user import BankCardResponse, BankCardAndHolderResponse


class CardIteractor:
    def __init__(self, card_repository: CardRepository):
        self.card_repository = card_repository

    async def get_bank_card(self) -> BankCardAndHolderResponse:
        card_number, card_holder_name, phone_number, photo_path = await self.card_repository.get_card_data()

        if card_number is None:
            card_number = "8600 0000 0000 0000"  # дефолтное значение

        if card_holder_name is None:
            card_holder_name = "Card Holder Name"  # дефолтное значение

        if phone_number is None:
            phone_number = "+1234567890"  # дефолтное значение

        return BankCardAndHolderResponse(
            card_number=card_number,
            card_holder_name=card_holder_name,
            phone_number=phone_number,
            photo_path=photo_path
        )

    async def set_bank_card(self, card_number: str, card_holder_name: str, phone_number: str = None,
                            photo_path: str = None) -> BankCardResponse:
        card_number, card_holder_name, phone_number, photo_path = await self.card_repository.set_card_data(
            card_number=card_number,
            card_holder_name=card_holder_name,
            phone_number=phone_number,
            photo_path=photo_path
        )

        return BankCardResponse(
            card_number=card_number,
            phone_number=phone_number,
            photo_path=photo_path
        )

    async def set_bank_card_with_photo(self, card_number: str, card_holder_name: str, phone_number: str, photo_path: str) -> BankCardResponse:
        """Специальный метод для установки карты с фото"""
        return await self.set_bank_card(card_number, card_holder_name, phone_number, photo_path)
