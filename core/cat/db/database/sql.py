from typing import Any, Type
from pydantic import BaseModel

from sqlalchemy import create_engine, update
from cat.db.utils import Session, select

from cat.utils import singleton
from cat.db.models import Setting, SQLBase
from cat.db.database.abstract import AbstractDatabase
from cat.db.tables import DefaultTable


@singleton
class SQLDatabase(AbstractDatabase):
    """
    SQL database implementation using SQLModel/SQLAlchemy.
    Provides a robust relational database interface.
    """

    setting_table_class: Type = DefaultTable
    setting_model_class: Type = None
    setting_pydantic_model_class: Type = Setting

    def __init__(self, db_name: str = None, db_url: str = None, connect: bool = False, *args, **kwargs):
        """
        Initialize SQL database connection.

        Args:
            db_name: Name of database file (without extension)
            db_url: Full database connection URL (takes precedence over db_name)
            connect: Whether to connect immediately

        Raises:
            ValueError: If neither db_name nor db_url is provided
        """
        if not db_name and not db_url:
            db_name = self.get_file_name()

        # Extract db_name from URL if not provided directly
        if not db_name:
            db_name = db_url.split("/")[-1].split(".")[0]

        super().__init__(db_name=db_name, connect=False, *args, **kwargs)

        # Build connection URL if not provided
        if not db_url:
            db_url = f"sqlite:///{db_name}.db"

        # Initialize engine with echo enabled for debugging
        self.db = create_engine(db_url, echo=False)

        # Initialize settings table if model classes are available
        if self.setting_table_class and (self.setting_model_class or self.setting_pydantic_model_class):
            self._setting_table = self.setting_table_class(
                db=self,
                model=self.setting_model_class,
                pydantic_model=self.setting_pydantic_model_class,
                primary_key=self.setting_primary_key,
                table_name="setting",
            )

        if connect:
            self.connect()

    def get_setting(self):
        """Get settings table instance"""
        return self._setting_table

    def connect(self):
        """Create all tables defined in SQLBase metadata"""
        SQLBase.metadata.create_all(self.db)

    def disconnect(self):
        """Close all connections"""
        self.db.dispose()

    # Query building methods
    def _build_query(self, model: Type, field_name: str, field_value: Any):
        """Build a field equality condition for SQL queries"""
        return getattr(model, field_name) == field_value

    def _get_table(self, model: Type, **kwargs):
        """Create a base select statement for a model"""
        return select(model)

    def _select_statement(self, model: Type, field_name: str, field_value: Any, **kwargs):
        """Create a filtered select statement"""
        statement = self._get_table(model).where(self._build_query(model, field_name, field_value))
        return statement

    # Core database operations
    def search_query(self, model: Type, query: Any, first: bool = True, **kwargs):
        """
        Execute a custom query against the database.

        Args:
            model: SQLAlchemy table class to query
            query: SQLAlchemy compatible WHERE condition
            first: Return only first result if True
        """
        with Session(self.db) as session:
            statement = self._get_table(model).where(query)

            if first:
                return session.exec(statement).first()
            else:
                return session.exec(statement).all()

    def select(self, model: Type, field_name: str, field_value: Any, **kwargs):
        """Select all records matching a field value"""
        with Session(self.db) as session:
            statement = self._select_statement(model, field_name, field_value, **kwargs)
            return session.exec(statement).all()

    def get_data(self, model: Type, field_name: str, field_value: Any, **kwargs):
        """Get single record matching a field value or None"""
        with Session(self.db) as session:
            statement = self._select_statement(model, field_name, field_value, **kwargs)
            return session.exec(statement).first()

    def create_table(self, model: Type, data: BaseModel, **kwargs):
        """Insert a new record into the database"""
        with Session(self.db) as session:
            session.add(self._convert_data_into_table(model=model, data=data))
            session.commit()

    def drop_table(self, **kwargs):
        """Drop table (not implemented)"""
        pass

    def update_table(self, model: Type, data: BaseModel, field_name: str, field_value: Any, **kwargs):
        """
        Update an existing record.

        Returns:
            bool: False if record doesn't exist, True if updated
        """
        with Session(self.db) as session:
            # Perform UPDATE operation
            result = session.exec(
                update(model)
                .where(self._build_query(model, field_name, field_value))
                .values(**data.model_dump())
            )

            if result.rowcount == 0:
                return False

            session.commit()
            return True

    def upsert_table(self, data: BaseModel, **kwargs):
        """Insert or update a record"""
        result = self.update_table(data=data, **kwargs)

        if result is False:
            self.create_table(data=data, **kwargs)

    def delete_table(self, model: Type, field_name: str, field_value: Any, **kwargs):
        """Delete a record from the database"""
        with Session(self.db) as session:
            record = self.get_data(model=model, field_name=field_name, field_value=field_value)
            if record:
                session.delete(record)
                session.commit()

    def all_table(self, model: Type, **kwargs):
        """Get all records from a table"""
        with Session(self.db) as session:
            statement = self._get_table(model)
            return session.exec(statement).all()


