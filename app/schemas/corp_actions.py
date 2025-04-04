from enum import StrEnum
from typing import Self

from pydantic import model_validator, NaiveDatetime
from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field

from app.constants import HIGHEST_DATETIME, LOWEST_DATETIME


class CorpActionsTypes(StrEnum):
    STOCK_SPLIT = "STOCK_SPLIT"
    DIVIDEND = "DIVIDEND"
    MERGER = "MERGER"
    ACQUISITION = "ACQUISITION"
    RIGHTS_ISSUE = "RIGHTS_ISSUE"
    BONUS_ISSUE = "BONUS_ISSUE"
    SPIN_OFF = "SPIN_OFF"
    OTHER = "OTHER"


class CorpAction(SQLModel):
    """CorpAction model in database."""

    ref_data_uuid: str = Field(
        primary_key=True,
        description="Reference data UUID to assign corp action to a security.",
    )
    # noinspection PyTypeChecker
    effective_time: NaiveDatetime = Field(
        primary_key=True,
        sa_type=DateTime,
        le=HIGHEST_DATETIME,
        ge=LOWEST_DATETIME,
        description="Effective time of the corp action.",
    )
    action_type: CorpActionsTypes = Field(description="Type of the corp action.")
    additive_adjustment: float | None = Field(
        default=0.0, description="Additive adjustment to the security price."
    )
    multiplicative_adjustment: float | None = Field(
        default=1.0, description="Multiplicative adjustment to the security price."
    )


class CorpActionDb(CorpAction, table=True):
    pass


class CorpActionCreate(CorpAction):
    """CorpAction create model. To be used for creating a new corp action."""

    ref_data_uuid: str | None = None
    symbology: str | None = None
    symbol: str | None = None

    @model_validator(mode="after")
    def verify_a_or_b(self) -> Self:
        is_symbology_and_symbol_provided = self.symbology and self.symbol

        if (is_symbology_and_symbol_provided and self.ref_data_uuid) or (
            not is_symbology_and_symbol_provided and not self.ref_data_uuid
        ):
            raise ValueError(
                "Expected ref_data_uuid or (symbology, symbol) pair but not both."
            )
        return self


class CorpActionPublic(CorpAction):
    """CorpAction public model. To be used for returning corp action to the client."""

    ref_data_uuid: str | None = None
    message: str | None = None
    error: str | None = None
