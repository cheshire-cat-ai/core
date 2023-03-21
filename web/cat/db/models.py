# SQLAlchemy models
# Here we create for each table a database model that has the fields required to add a new record to the database.


from sqlalchemy import TIMESTAMP, Column, String, Boolean
from sqlalchemy.sql import func
from cat.db.database import Base
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE


class Setting(Base):
    __tablename__ = "settings"
    setting_id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    category = Column(String, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())
