# app/interactors/telegram_ai.py
import asyncio
import os
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from typing import List
from loguru import logger

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import AsyncContainer

from app.core.config import TelegramConfig
from app.interactors.cardIteractor import CardIteractor
from app.interactors.moneyIteractor import MoneyIteractor

CARD_PHOTOS_DIR = "./card_photos"


class TelegramInteractor:
    def __init__(self, bot_token: str, chat_ids: List[int]):
        self.bot_token = bot_token
        self.chat_ids = chat_ids
        self.bot = Bot(token=self.bot_token, default=DefaultBotProperties(parse_mode="Markdown"))
        self.dp = Dispatcher()
        self._is_running = False
        self._polling_task = None
        self.container: AsyncContainer = None  # Будет установлен в lifespan
        self.card_repository: AsyncContainer = None

        self._register_handlers()

    def set_container(self, container: AsyncContainer):
        """Установка контейнера для получения зависимостей"""
        self.container = container

    def set_container_card(self, container: AsyncContainer):
        self.card_repository = container

    def _register_handlers(self):
        """Регистрация обработчиков callback'ов"""

        @self.dp.callback_query(F.data.startswith("withdraw_confirm_"))
        async def confirm_withdraw(callback: types.CallbackQuery):
            try:
                _, _, user_id, amount_str = callback.data.split("_", 3)
                amount = Decimal(amount_str)

                # Получаем MoneyIteractor из контейнера
                # async with self.container() as request_container:
                #     from app.interactors.moneyIteractor import MoneyIteractor
                #     money_interactor = await request_container.get(MoneyIteractor)
                #     new_balance = await money_interactor.make_withdrawal(user_id, amount)
                # await money_interactor.set_user_balance(user_id, new_balance.balance)
                # new_caption = f"✅ Вывод *{amount:,.2f} UZS* пользователю `{user_id}` подтвержден."

                # await callback.message.edit_caption(
                #     caption=new_caption,
                #     reply_markup=None  # Убираем кнопки
                # )

                # await callback.answer("Вывод подтвержден")

            except Exception as e:
                await callback.answer(f"Ошибка: {str(e)}")
                print(f"[TelegramInteractor] Confirm withdraw error: {e}")

        # 🔹 Отклонение вывода
        @self.dp.callback_query(F.data.startswith("withdraw_reject_"))
        async def reject_withdraw(callback: types.CallbackQuery):
            try:
                _, _, user_id, amount_str = callback.data.split("_", 3)
                amount = Decimal(amount_str)

                new_caption = f"❌ Запрос на вывод *{amount:,.2f} USD* пользователю `{user_id}` отклонен."
                await callback.message.edit_caption(
                    caption=new_caption,
                    reply_markup=None  # Убираем кнопки
                )

                await callback.answer("Вывод отклонен")

            except Exception as e:
                await callback.answer(f"Ошибка: {str(e)}")
                print(f"[TelegramInteractor] Reject withdraw error: {e}")

        @self.dp.callback_query(F.data.startswith("confirm_"))
        async def confirm_callback(callback: types.CallbackQuery):
            try:
                # Разбираем callback_data: "confirm_{user_id}_{amount}"
                parts = callback.data.split("_")
                if len(parts) != 3:
                    await callback.answer("Неверный формат данных")
                    return

                _, user_id, amount_str = parts
                amount = Decimal(amount_str)

                # Получаем MoneyIteractor из контейнера
                async with self.container() as request_container:
                    from app.interactors.moneyIteractor import MoneyIteractor
                    money_interactor = await request_container.get(MoneyIteractor)
                    await money_interactor.update_balance(user_id, amount)
                    await money_interactor.set_initial_balance(user_id, amount)

                # Редактируем caption сообщения с фото
                new_caption = f"✅ Баланс пользователя {user_id} обновлен на {amount:,} USD"

                # Способ 1: Редактируем только подпись
                await callback.message.edit_caption(
                    caption=new_caption,
                    reply_markup=None  # Убираем кнопки
                )

                await callback.answer("Баланс подтвержден")
                return True

            except Exception as e:
                await callback.answer(f"Ошибка: {str(e)}")
                print(f"Confirm callback error: {e}")

        @self.dp.callback_query(F.data.startswith("reject_"))
        async def reject_callback(callback: types.CallbackQuery):
            try:
                parts = callback.data.split("_")
                if len(parts) != 3:
                    await callback.answer("Неверный формат данных")
                    return

                _, user_id, amount_str = parts

                new_caption = f"❌ Пополнение пользователя {user_id} отклонено"

                await callback.message.edit_caption(
                    caption=new_caption,
                    reply_markup=None  # Убираем кнопки
                )

                await callback.answer("Пополнение отклонено")
                return False

            except Exception as e:
                await callback.answer(f"Ошибка: {str(e)}")
                print(f"Reject callback error: {e}")

        @self.dp.message(F.text == "/set_card_photo")
        async def set_card_photo_handler(message: types.Message):
            logger.debug('adsdasdasdasdsad')
            if not message.reply_to_message or not message.reply_to_message.photo:
                await message.reply("Отправьте команду /set_card_photo В ОТВЕТ на фото!", parse_mode=None)
                return

            tg_photo = message.reply_to_message.photo[-1]
            photo_file_id = tg_photo.file_id

            logger.debug(f"Получено фото для сохранения: {photo_file_id}")

            try:
                saved_path = await save_photo_locally(photo_file_id, self.bot)

                if not saved_path:
                    await message.reply("Ошибка при сохранении фото. Смотри bot_log.txt", parse_mode=None)
                    return

                async with self.card_repository() as request_container:
                    card_iteractor = await request_container.get(CardIteractor)
                    card_data = await card_iteractor.get_bank_card()

                    await card_iteractor.set_bank_card_with_photo(card_data.card_number,
                                                                  card_data.card_holder_name,
                                                                  card_data.phone_number,
                                                                  saved_path)

                await message.reply("Фото успешно сохранено!", parse_mode=None)

            except Exception as e:
                logger.error(f"Error in set_card_photo_handler: {e}")
                await message.reply("Ошибка при обработке фото.", parse_mode=None)

        @self.dp.message(F.text.startswith("/set_card "))  # Обратите внимание на пробел
        async def set_card_handler(message: types.Message, bot):
            parts = message.text.split()

            if len(parts) < 4:
                await message.reply(
                    "⚠️ Формат:\n"
                    "1️⃣ /set_card 1234 5678 9012 3456 Ivan Ivanov +7999...\n"
                    "2️⃣ /set_card CCI 92200300000327457291 Elisa Angela Pasco Acosta +51993789016",
                    parse_mode=None
                )
                return

            second_part = parts[1].upper() if len(parts) > 1 else ""

            # Список известных банковских префиксов
            bank_prefixes = {"CCI", "BANCO", "BANK", "BBVA", "SANTANDER", "INTERBANK", "BCP", "SCOTIABANK"}

            # Определяем формат: CCI или обычная карта
            if second_part in bank_prefixes:
                # Формат CCI: /set_card CCI 92200300000327457291 Elisa Angela Pasco Acosta +51993789016
                if len(parts) < 5:
                    await message.reply(
                        "❌ Неверный формат CCI. Используйте:\n"
                        "/set_card CCI [номер_счета] [Имя Фамилия] [телефон]",
                        parse_mode=None
                    )
                    return

                cci_prefix = parts[1]  # "CCI"
                account_number = parts[2]  # Номер счета
                phone_number = parts[-1]  # Телефон (последний элемент)

                # Имя - все между номером счета и телефоном
                name_parts = parts[3:-1]
                if not name_parts:
                    await message.reply("❌ Укажите имя держателя счета", parse_mode=None)
                    return

                card_holder_name = " ".join(name_parts)
                card_number = f"{cci_prefix} {account_number}"

            else:
                # Формат обычной карты: /set_card 1234 5678 9012 3456 Ivan Ivanov +7999
                if len(parts) < 6:
                    await message.reply(
                        "⚠️ Формат: /set_card 1234 5678 9012 3456 Ivan Ivanov +7999...",
                        parse_mode=None
                    )
                    return

                # НОМЕР КАРТЫ (части 1-4)
                card_parts = parts[1:5]
                if not all(p.isdigit() and len(p) == 4 for p in card_parts):
                    await message.reply(
                        "❌ Неверный номер карты. Используйте формат: 1234 5678 9012 3456",
                        parse_mode=None
                    )
                    return

                card_number = " ".join(card_parts)
                phone_number = parts[-1]

                # ИМЯ (все части между номером карты и телефоном)
                name_parts = parts[5:-1]
                if not name_parts:
                    await message.reply("❌ Укажите имя держателя карты", parse_mode=None)
                    return

                card_holder_name = " ".join(name_parts)

            # Валидация телефона (базовая)
            if not phone_number.startswith('+') and not phone_number[0].isdigit():
                await message.reply("❌ Номер телефона должен начинаться с + или цифры", parse_mode=None)
                return

            try:
                async with self.card_repository() as request_container:
                    card_iteractor = await request_container.get(CardIteractor)
                    await card_iteractor.set_bank_card(card_number, card_holder_name, phone_number)

                await message.reply(
                    f"✅ Данные карты сохранены:\n\n"
                    f"💳 Карта: {card_number}\n"
                    f"👤 Владелец: {card_holder_name}\n"
                    f"📞 Телефон: {phone_number}\n\n"
                    f"ℹ️ Фото карты не установлено. Используйте /set_card_photo",
                    parse_mode=None
                )

            except Exception as e:
                logger.error(f"Error in set_card_handler: {e}")
                await message.reply("❌ Ошибка при сохранении данных карты. Проверьте логи.", parse_mode=None)

        async def save_photo_locally(photo_file_id: str, bot) -> str:

            try:
                file = await bot.get_file(photo_file_id)

                photo_bytes = await bot.download_file(file.file_path)

                Path(CARD_PHOTOS_DIR).mkdir(parents=True, exist_ok=True)

                extension = Path(file.file_path).suffix or ".jpg"
                filename = f"card_photo_{int(datetime.utcnow().timestamp())}{extension}"

                file_path = Path(CARD_PHOTOS_DIR) / filename

                with open(file_path, "wb") as f:
                    f.write(photo_bytes.read())

                return str(file_path)

            except Exception as e:
                logger.error(f"[ERROR_SAVE_PHOTO]: {e}")
                return None

    async def send_invoice_notification(
            self,
            user_id: str,
            user_email: str,
            amount: Decimal,
            file_path: str,
    ):
        formatted_amount = f"{amount:,.2f} USD"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"confirm_{user_id}_{amount}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"reject_{user_id}_{amount}"
                )
            ]
        ])

        caption_text = (
            f"💰 *НОВОЕ ПОПОЛНЕНИЕ БАЛАНСА*\n\n"
            f"👤 *Пользователь:* {user_id}\n"
            f"📧 *Email:* {user_email}\n"
            f"💵 *Сумма:* {formatted_amount}\n"
            f"⏰ *Время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        success_count = 0
        for chat_id in self.chat_ids:
            try:

                with open(file_path, "rb") as photo_file:
                    photo = FSInputFile(file_path)
                    await self.bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=caption_text,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )

                success_count += 1
            except Exception as e:
                print(f"Error sending to chat {chat_id}: {e}")
                continue

        return success_count > 0

    async def send_withdraw_notification(
            self,
            user_id: str,
            user_email: str,
            amount: Decimal,
            file_path: str,
            card_number: str,
            full_name: str
    ) -> bool:
        """Отправка уведомления о запросе на вывод средств"""

        formatted_amount = f"{amount:,.2f} USD"

        # keyboard = InlineKeyboardMarkup(
        #     inline_keyboard=[
        #         [
        #             InlineKeyboardButton(
        #                 text="✅ Подтвердить вывод",
        #                 callback_data=f"withdraw_confirm_{user_id}_{amount}"
        #             ),
        #             InlineKeyboardButton(
        #                 text="❌ Отклонить вывод",
        #                 callback_data=f"withdraw_reject_{user_id}_{amount}"
        #             )
        #         ]
        #     ]
        # )

        caption_text = (
            "🏧 *ЧЕК ЗА ВЫВОД СРЕДСТВ*\n\n"
            f"👤 *Пользователь:* `{user_id}` | Full Name: `{full_name}`\n"
            f"📧 *Email:* `{user_email}` | Card Number `{card_number}`\n"
            f"💸 *Сумма:* `{formatted_amount}`\n"
            f"🕒 *Время:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        )

        success_count = 0
        for chat_id in self.chat_ids:
            try:
                photo = FSInputFile(file_path)
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption_text,
                    # reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                success_count += 1

            except Exception as e:
                print(f"❌ Error sending withdraw message to chat {chat_id}: {e}")
                continue

        return success_count > 0

    async def start_polling(self):
        """Запуск бота для обработки callback'ов"""
        if self._is_running:
            print("⚠️ Bot is already running")
            return

        try:
            self._is_running = True
            print("🤖 Starting Telegram bot polling...")

            # Запускаем polling в фоне
            self._polling_task = asyncio.create_task(
                self.dp.start_polling(self.bot)
            )

            print("✅ Telegram bot started successfully")

        except Exception as e:
            self._is_running = False
            print(f"❌ Failed to start bot: {e}")
            raise

    async def stop_polling(self):
        """Остановка бота"""
        if not self._is_running:
            return

        print("🛑 Stopping Telegram bot...")

        self._is_running = False

        # Останавливаем polling
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None

        # Закрываем сессии
        await self.dp.storage.close()
        await self.bot.session.close()

        print("✅ Telegram bot stopped successfully")

    @property
    def is_running(self) -> bool:
        """Проверка запущен ли бот"""
        return self._is_running
