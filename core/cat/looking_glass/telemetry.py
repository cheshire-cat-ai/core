from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
import psutil
from cat.looking_glass.white_rabbit import WhiteRabbit
import httpx
from cat.log import log
from cat.env import get_env
from cat.utils import get_cat_version
from cat.db import crud, models


class SystemData(BaseModel):
    ram_gb: float = Field(
        frozen=True, default=round(psutil.virtual_memory().total / (1024.0**3), 2)
    )
    cpu_count: int = Field(frozen=True, default=psutil.cpu_count())


class TelemetryData(BaseModel):
    telemetry_id: UUID
    country: Optional[str] = None
    version: str = get_cat_version()
    llm_model: Optional[str] = None
    embedder_model: Optional[str] = None
    system: SystemData


class TelemetryHandler:
    def __init__(self):
        self.enable: bool = get_env("CCAT_TELEMETRY") == "true"
        if self.enable:
            log.info("Load Telemetry")

            telemetry_settings = crud.get_setting_by_name("Telemetry")
            if telemetry_settings:
                # we use the setting_id as telemetry id
                telemetry_id = telemetry_settings["setting_id"]
            else:
                setting = crud.create_setting(
                    models.Setting(name="Telemetry", category="telemetry", value={})
                )
                telemetry_id = setting["setting_id"]

            system = SystemData()
            self.data = TelemetryData(telemetry_id=telemetry_id, system=system)
            WhiteRabbit().schedule_interval_job(self.send_telemetry, seconds=6)
        else:
            log.info("Telemetry is disable")

    def set_country(self, country: str):
        if not self.enable:
            return
        # should be ISO3166
        self.data.country = country

    def set_llm_model(self, llm_model: str):
        if not self.enable:
            return
        self.data.llm_model = llm_model

    def set_embedder_model(self, embedder_model: str):
        if not self.enable:
            return
        self.data.embedder_model = embedder_model

    def send_telemetry(self):
        try:
            log.info(f"Sending this chunk of data:{self.data}")
            # res = httpx.post("http://telemetry.cheshirecat.ai", data=self.data)
            # res.raise_for_status()
        except httpx.HTTPStatusError as e:
            log.error(f"Error when sending telemetry {e.response.status_code}")
