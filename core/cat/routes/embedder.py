from typing import Dict

from fastapi import Request, APIRouter, Body, HTTPException
from typing import Dict, List, Optional, Union, Type
from pydantic import BaseModel

from cat.factory.embedder import get_allowed_embedder_models,get_embedders_schemas, get_embedders_class
from cat.factory.embedder import EmbedderQdrantFastEmbedConfig ,\
        EmbedderOpenAIConfig,\
        EmbedderAzureOpenAIConfig,\
        EmbedderGeminiChatConfig,\
        EmbedderOpenAICompatibleConfig,\
        EmbedderCohereConfig,\
        EmbedderDumbConfig,\
        EmbedderFakeConfig, \
        EmbedderSettings

from cat.db import crud, models
from cat.log import log
from cat import utils


# Default router
router_v1 = APIRouter()

# Router v2
router_v2 = APIRouter()

# general embedder settings are saved in settings table under this category
EMBEDDER_SELECTED_CATEGORY = "embedder"

# embedder type and config are saved in settings table under this category
EMBEDDER_CATEGORY = "embedder_factory"

# embedder selected configuration is saved under this name
EMBEDDER_SELECTED_NAME = "embedder_selected"


class EmbedderSettingResponse(BaseModel):
    name:str
    value: Optional[Union[EmbedderQdrantFastEmbedConfig ,\
        EmbedderOpenAIConfig,\
        EmbedderAzureOpenAIConfig,\
        EmbedderGeminiChatConfig,\
        EmbedderOpenAICompatibleConfig,\
        EmbedderCohereConfig,\
        EmbedderDumbConfig,\
        EmbedderFakeConfig]] = None
    schema:Dict

    @classmethod
    # Constructs and returns an instance of the class it belongs to, based on the validation of configuration settings for an embedder. 
    # It takes as parameters a schema (a dictionary outlining required and optional settings), the name of the embedder class, the embedder class, and a dictionary of saved settings.
    def get_embedder_setting_response(self, schema:Dict, embedder_class_name:str, embedder_class:Type[EmbedderSettings], saved_setting:Dict):
        if len(saved_setting) == 0:
            return self(
                name=embedder_class_name,
                schema= schema,
                value=None
            )
            
        none_value:bool = False
        # If schema contains required fields and saved_setting is not empty
        if "required" in schema:
            # Check that all the required field are present in saved_setting, otherwise value = None 
            req_setting_not_present:List[str] = [req_setting for req_setting in schema["required"] if req_setting not in saved_setting]
            if len(req_setting_not_present) > 0:
                log.warning(f"Required settings {req_setting_not_present} not present in {embedder_class_name}; setting value to None")
                none_value = True
        return self(
            name=embedder_class_name,
            # if none_value is false create EmbedderSettings passing the saved_setting
            value = embedder_class.model_validate(saved_setting) if not none_value else None,
            schema= schema,
        )

class EmbeddersSettingsResponse(BaseModel):
    settings: List[EmbedderSettingResponse]
    selected_configuration: str



@router_v1.get("/settings", deprecated=True)
def get_embedders_settings_v1(request: Request) -> Dict:
    """Get the list of the Embedders"""
    log.warning("Deprecated: This endpoint will be removed in the next major version.")

    SUPPORTED_EMDEDDING_MODELS = get_allowed_embedder_models()
    # get selected Embedder, if any
    selected = crud.get_setting_by_name(name=EMBEDDER_SELECTED_NAME)
    if selected is not None:
        selected = selected["value"]["name"]
    else:
        # If DB does not contain a selected embedder, it means an embedder was automatically selected.
        # Deduce selected embedder:
        ccat = request.app.state.ccat
        for embedder_config_class in reversed(SUPPORTED_EMDEDDING_MODELS):
            if embedder_config_class._pyclass.default == type(ccat.embedder):
                selected = embedder_config_class.__name__
    
    saved_settings = crud.get_settings_by_category(category=EMBEDDER_CATEGORY)
    saved_settings = { s["name"]: s for s in saved_settings }

    settings = []
    for class_name, schema in get_embedders_schemas().items():
        
        if class_name in saved_settings:
            saved_setting = saved_settings[class_name]["value"]
        else:
            saved_setting = {}

        settings.append({
            "name"  : class_name,
            "value" : saved_setting,
            "schema": schema,
        })

    return {
        "settings": settings,
        "selected_configuration": selected,
    }

@router_v2.get("/settings", response_model_exclude_none=True)
def get_embedders_settings_v2(request: Request) -> EmbeddersSettingsResponse:
    """Get the list of the Embedders"""
    ccat = request.app.state.ccat
    embedder_class_dict = get_embedders_class()
    

    SUPPORTED_EMDEDDING_MODELS = get_allowed_embedder_models()
    # get selected Embedder, if any
    selected = crud.get_setting_by_name(name=EMBEDDER_SELECTED_NAME)
    if selected is not None:
        selected = selected["value"]["name"]
    else:
        # If DB does not contain a selected embedder, it means an embedder was automatically selected.
        # Deduce selected embedder:
        ccat = request.app.state.ccat
        for embedder_config_class in reversed(SUPPORTED_EMDEDDING_MODELS):
            if embedder_config_class._pyclass.default == type(ccat.embedder):
                selected = embedder_config_class.__name__
    
    # get stored settings from db
    saved_settings_list = crud.get_settings_by_category(category=EMBEDDER_CATEGORY)
    saved_settings = { s["name"]: s for s in saved_settings_list }

    settings = []
    for class_name, schema in get_embedders_schemas().items():
        
        saved_setting = {}
        if class_name in saved_settings:
            saved_setting = saved_settings[class_name]["value"]

        settings.append(
            EmbedderSettingResponse.get_embedder_setting_response(
                schema,
                class_name,
                embedder_class_dict[class_name],
                saved_setting 
            )
        )

    return EmbeddersSettingsResponse(
        settings=settings,
        selected_configuration=selected
    )


@router_v1.get("/settings/{languageEmbedderName}", deprecated=True)
def get_embedder_settings_v1(request: Request, languageEmbedderName: str) -> Dict:
    """Get settings and schema of the specified Embedder"""
    log.warning("Deprecated: This endpoint will be removed in the next major version.")

    EMBEDDER_SCHEMAS = get_embedders_schemas()
    # check that languageEmbedderName is a valid name
    allowed_configurations = list(EMBEDDER_SCHEMAS.keys())
    if languageEmbedderName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{languageEmbedderName} not supported. Must be one of {allowed_configurations}"
            }
        )
    
    setting = crud.get_setting_by_name(name=languageEmbedderName)
    schema = EMBEDDER_SCHEMAS[languageEmbedderName]

    if setting is None:
        setting = {}
    else:
        setting = setting["value"]

    return {
        "name": languageEmbedderName,
        "value": setting,
        "schema": schema
    }

@router_v2.get("/{languageEmbedderName}/settings", response_model_exclude_none=True)
def get_embedder_settings_v2(request: Request, languageEmbedderName: str) -> EmbedderSettingResponse:
    """Get settings and schema of the specified Embedder"""

    embedder_class_dict = get_embedders_class()

    embedder_schemas = get_embedders_schemas()
    # check that languageEmbedderName is a valid name
    allowed_configurations = list(embedder_schemas.keys())
    if languageEmbedderName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{languageEmbedderName} not supported. Must be one of {allowed_configurations}"
            }
        )
    
    setting = crud.get_setting_by_name(name=languageEmbedderName)
    schema = embedder_schemas[languageEmbedderName]

    setting = {} if setting is None else setting["value"]
    
    return EmbedderSettingResponse.get_embedder_setting_response(schema,languageEmbedderName,embedder_class_dict[languageEmbedderName],setting )



@router_v1.put("/settings/{languageEmbedderName}", deprecated=True)
def upsert_embedder_setting_v1(
    request: Request,
    languageEmbedderName: str,
    payload: Dict = Body({"openai_api_key": "your-key-here"}),
) -> Dict:
    """Upsert the Embedder setting"""    
    ccat = request.app.state.ccat
    log.warning("Deprecated: This endpoint will be removed in the next major version.")

    EMBEDDER_SCHEMAS = get_embedders_schemas()
    # check that languageModelName is a valid name
    allowed_configurations = list(EMBEDDER_SCHEMAS.keys())
    if languageEmbedderName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{languageEmbedderName} not supported. Must be one of {allowed_configurations}"
            }
        )
    
    # get selected config if any
    selected = crud.get_setting_by_name(name=EMBEDDER_SELECTED_NAME)
    if selected is not None:
        current_settings = crud.get_setting_by_name(name=selected["value"]["name"])

    # create the setting and upsert it
    final_setting = crud.upsert_setting_by_name(
        models.Setting(name=languageEmbedderName, category=EMBEDDER_CATEGORY, value=payload)
    )

    crud.upsert_setting_by_name(
        models.Setting(name=EMBEDDER_SELECTED_NAME, category=EMBEDDER_SELECTED_CATEGORY, value={"name":languageEmbedderName})
    )

    status = {
        "name": languageEmbedderName,
        "value": final_setting["value"]
    }

    # reload llm and embedder of the cat
    ccat.load_natural_language()
    # crete new collections (different embedder!)
    try:
        ccat.load_memory()
    except Exception as e:
        log.error(e)
        crud.delete_settings_by_category(category=EMBEDDER_SELECTED_CATEGORY)
        crud.delete_settings_by_category(category=EMBEDDER_CATEGORY)

        # if a selected config is present, restore it
        if selected is not None:
            languageEmbedderName = selected["value"]["name"]
            crud.upsert_setting_by_name(
                models.Setting(name=languageEmbedderName, category=EMBEDDER_CATEGORY, value=current_settings["value"])
            )
            crud.upsert_setting_by_name(
                models.Setting(name=EMBEDDER_SELECTED_NAME, category=EMBEDDER_SELECTED_CATEGORY, value={"name":languageEmbedderName})
            )
            # reload llm and embedder of the cat
            ccat.load_natural_language()

        raise HTTPException(
            status_code=400,
            detail={
                "error": utils.explicit_error_message(e)
            }
        )
    # recreate tools embeddings
    ccat.mad_hatter.find_plugins()

    return status


@router_v2.put("/{languageEmbedderName}/settings", response_model_exclude_none=True)
def upsert_embedder_setting_v2(
    request: Request,
    languageEmbedderName: str,
    payload: Dict = Body({"openai_api_key": "your-key-here"}),
) -> EmbedderSettingResponse:
    """Upsert the Embedder setting"""

    ccat = request.app.state.ccat
    embedder_class_dict = get_embedders_class()

    EMBEDDER_SCHEMAS = get_embedders_schemas()
    # check that languageModelName is a valid name
    allowed_configurations = list(EMBEDDER_SCHEMAS.keys())
    if languageEmbedderName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{languageEmbedderName} not supported. Must be one of {allowed_configurations}"
            }
        )
    
    # get selected config if any
    selected = crud.get_setting_by_name(name=EMBEDDER_SELECTED_NAME)
    if selected is not None:
        current_settings = crud.get_setting_by_name(name=selected["value"]["name"])

    # Check required field 
    schema = EMBEDDER_SCHEMAS[languageEmbedderName]
    # If schema contains required fields
    if "required" in schema:
        # Check that all the required fields are present in payload 
        req_setting_not_present = [req_setting for req_setting in schema["required"] if req_setting not in payload]
        if len(req_setting_not_present) > 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Required field {req_setting_not_present} for {languageEmbedderName}  are not configured."
                }
            )

    # Add that default field in payload
    for property in schema["properties"]:
        if "default" not in schema["properties"][property]:
            # required field, not optional, skip it
            continue
        if property in payload:
            # property in payload, skip it
            continue
        # property not in payload, add the default value
        default_value = schema["properties"][property]["default"]
        log.info(f"Insert in payload default property {property} : {default_value}")
        payload[property] = default_value
    
    # create the setting and upsert it
    final_setting = crud.upsert_setting_by_name(
        models.Setting(name=languageEmbedderName, category=EMBEDDER_CATEGORY, value=payload)
    )
    crud.upsert_setting_by_name(
        models.Setting(name=EMBEDDER_SELECTED_NAME, category=EMBEDDER_SELECTED_CATEGORY, value={"name":languageEmbedderName})
    )

    setting = final_setting["value"]
    
    try:
        # reload llm and embedder of the cat
        ccat.load_natural_language()
        # crete new collections (different embedder!)
        ccat.load_memory()
        # recreate tools embeddings
        ccat.mad_hatter.find_plugins()

    except Exception as e:
        log.error(e)
        crud.delete_settings_by_category(category=EMBEDDER_SELECTED_CATEGORY)
        crud.delete_settings_by_category(category=EMBEDDER_CATEGORY)

        # if a selected config is present, restore it
        if selected is not None:
            languageEmbedderName = selected["value"]["name"]
            crud.upsert_setting_by_name(
                models.Setting(name=languageEmbedderName, category=EMBEDDER_CATEGORY, value=current_settings["value"])
            )
            crud.upsert_setting_by_name(
                models.Setting(name=EMBEDDER_SELECTED_NAME, category=EMBEDDER_SELECTED_CATEGORY, value={"name":languageEmbedderName})
            )
            # reload llm and embedder of the cat
            ccat.load_natural_language()

        raise HTTPException(
            status_code=400,
            detail={
                "error": utils.explicit_error_message(e)
            }
        )

    return EmbedderSettingResponse.get_embedder_setting_response(
        schema,
        languageEmbedderName,
        embedder_class_dict[languageEmbedderName],setting 
    )
