import uuid
from datetime import date, datetime

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table, Numeric,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.database.postgres.base import Base

class PromoCodeModel(Base):
    __tablename__ = "promo_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    bonus_percent = Column(Integer, nullable=False)  # 20, 30, 40
    is_active = Column(Boolean, default=True, nullable=False)
    max_uses = Column(Integer, default=None, nullable=True)  # None = unlimited
    current_uses = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class UserPromoCodeUsageModel(Base):
    __tablename__ = "user_promo_code_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    promo_code_id = Column(UUID(as_uuid=True), ForeignKey("promo_codes.id"), nullable=False)
    used_at = Column(DateTime, default=datetime.utcnow)
    bonus_amount = Column(Numeric(15, 2), nullable=False)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    initial_balance = Column(Numeric(15, 2), default=0.00, nullable=False)  # 🔹 Добавляем
    has_initial_deposit = Column(Boolean, default=False, nullable=False)  # 🔹 Флаг первого депозита
    promo_code_used = Column(String(50), nullable=True)  # Код при регистрации
    registration_promo_percent = Column(Integer, default=0)  # Процент бонуса
    promo_bonus_received = Column(Numeric(15, 2), default=0.00)  # Получено бонуса


class BankCardModel(Base):
    __tablename__ = "card"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    bank_name = Column(String(200), default="Banco Pichincha", nullable=False)  # 🔹 Название банка
    account_type = Column(String(100), default="Cuenta de ahorro transaccional")  # 🔹 Тип счета
    account_number = Column(String(100), nullable=False)  # 🔹 Номер счета
    card_holder_name = Column(String(200), nullable=False)  # 🔹 Имя держателя
    holder_id = Column(String(50), nullable=True)  # 🔹 CI/DNI/Passport
    phone_number = Column(String(50), nullable=True)  # 🔹 Телефон

    photo_path  = Column(String, nullable=True)

    # Устаревшее поле (для обратной совместимости)
    card_number = Column(String(100), nullable=True)


class PositionsHistoryModel(Base):
    __tablename__ = "positions_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    type = Column(String(10), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    profit = Column(Numeric(15, 2), nullable=False)
    roi = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
