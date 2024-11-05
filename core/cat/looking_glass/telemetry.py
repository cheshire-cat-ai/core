from pydantic import BaseModel,Field
from typing import Optional
import psutil
from cat.looking_glass.white_rabbit import WhiteRabbit
from cat.utils import singleton
import httpx
from cat.log import log


class SystemData(BaseModel):
    ram_gb: float =Field(frozen=True, default=round(psutil.virtual_memory().total / (1024.0 ** 3), 2))
    cpu_count: int = Field(frozen=True, default=psutil.cpu_count())



class TelemetryData(BaseModel):
    country: Optional[str] = None
    llm_model: Optional[str] = None
    embedder_model: Optional[str] = None
    system: SystemData

@singleton
class TelemetryHandler:
    
    def __init__(self):
        system=SystemData()
        self.data = TelemetryData(system=system)
       
    def set_country(self,country: str):
        # should be ISO3166
        self.data.country = country

    def set_llm_model(self, llm_model: str):
        self.data.llm_model = llm_model
    
    def set_embedder_model(self, embedder_model: str):
        self.data.embedder_model = embedder_model

    # @property
    # def data(self) -> TelemetryData:
    #     return self.data
    
def send_telemetry():
    telemetry = TelemetryHandler()
    try:
        log.info(f"Sending this chunk of data:{telemetry.data}")
        # res = httpx.post("http://telemetry.cheshirecat.ai", data=telemetry.data)
        # res.raise_for_status()
    except httpx.HTTPStatusError as e:
        log.error(f"Error when sending telemetry {e.response.status_code}")

    

WhiteRabbit().schedule_interval_job(send_telemetry,hours=6)