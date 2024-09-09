from datetime import datetime, timezone

import sqlmodel


def get_utc_now():
    return datetime.now(timezone.utc)


def get_datetime_column():
    return sqlmodel.Field(
        default_factory=lambda : get_utc_now(),
        sa_type=sqlmodel.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sqlmodel.func.now(),
        },
        nullable=False,
    )
