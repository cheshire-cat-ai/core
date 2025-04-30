from typing import Dict, List, Type, Union
from pydantic import BaseModel, ValidationError


def cast_obj(class_: Type[BaseModel], obj: Union[Dict, List, BaseModel, object]) -> Union[BaseModel, object, None]:
    """
    Cast an object to the specified Pydantic model class.

    This function converts objects between different formats and ensures they
    conform to the specified Pydantic model schema. Handles multiple input types
    and performs recursive conversion where needed.

    Args:
        class_ (Type[BaseModel]): Target Pydantic model class to convert to
        obj (Union[Dict, List, BaseModel, object]): Object to be converted

    Returns:
        Union[BaseModel, object]: The input object converted to the target model
            class if possible, or the original object if conversion fails

    Examples:
        >>> class User(BaseModel):
        ...     name: str
        ...     age: int
        ...
        >>> # Convert from dictionary
        >>> user_dict = {"name": "Alice", "age": 30}
        >>> user = cast_obj(User, user_dict)  # Returns User instance
    """
    # Handle empty values
    if not obj:
        return obj

    if not issubclass(class_, BaseModel):
        return obj

    if isinstance(obj, class_):
        # If obj is already an instance of the target class, return it
        return obj

    # Handle basic types - return as is
    if isinstance(obj, (str, int, float, bool, bytes, bytearray)):
        return obj

    # Handle lists - recursively cast each item
    elif isinstance(obj, (List, set)):
        return [cast_obj(item) for item in obj]

    # Handle dictionaries - convert directly to Pydantic model
    elif isinstance(obj, Dict):
        return class_.model_validate(obj)

    # Handle existing Pydantic models - convert between model types
    elif isinstance(obj, BaseModel):
        return class_.model_validate(obj.model_dump())

    # Handle SQLAlchemy model instances or other objects with __dict__
    elif hasattr(obj, "__dict__"):
        try:
            return class_.model_validate(obj.__dict__)
        except ValidationError:
            return obj

    # Return unchanged if no conversion possible
    return obj


def cast_result(class_field_name: str):
    """
    Cast the result of a SQLAlchemy query to a Pydantic model.

    This decorator function converts query results into Pydantic model instances
    specified by a class attribute of the decorated object. It handles various
    result types including:
    - Single objects
    - Dictionaries
    - Lists of objects or dictionaries
    - Other Pydantic models

    Args:
        class_field_name (str): The name of the attribute in the decorated class
            that contains the target Pydantic model class to cast results to

    Returns:
        Callable: A decorator function that wraps database query functions

    Example:
        >>> class UserRepository:
        >>>     model_class = UserModel
        >>>
        >>>     @cast_result('model_class')
        >>>     def get_user(self, user_id):
        >>>         return session.query(UserTable).filter_by(id=user_id).first()
        >>>
        >>> # Result is automatically cast to the UserModel defined in the class
        >>> user_repo = UserRepository()
        >>> user = user_repo.get_user(1)
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Execute the original function and cast its result
            result = func(self, *args, **kwargs)

            class_ = getattr(self, class_field_name, None)
            if not class_:
                return result
            return cast_obj(getattr(self, class_field_name), result)

        return wrapper
    return decorator
