from contextlib import asynccontextmanager

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Query
from fastapi_mqtt import FastMQTT, MQTTConfig

from routers import user_api, utils_api, device_api, data_api, location_api
from schemas.data_schema import Command
from schemas.responses_schema import Responses


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    await mqtt.mqtt_startup()
    yield
    await mqtt.mqtt_shutdown()


app = FastAPI(lifespan=_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_api.router)
app.include_router(location_api.router)
app.include_router(device_api.router)
app.include_router(data_api.router)
app.include_router(utils_api.router)

mqtt_config = MQTTConfig(
    host="w99564f6.ala.cn-hangzhou.emqxsl.cn",
    port=8883,
    ssl=True,
    username='sensor',
    password='B2w.N_KaRWp:Nye',
    reconnect_retries=10,
    reconnect_delay=5
)

mqtt = FastMQTT(config=mqtt_config)
mqtt.init_app(app)


@app.get("/")
async def root():
    return {"message": "Main Application"}


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("/actuators/sg90")
    print("Connected: ", client, flags, rc, properties)


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")


@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: ", topic, payload.decode(), qos, properties)
    return 0


@app.post("/actuators/sg90", response_model=Responses)
async def func(command: Command):
    if command.command == "open":
        mqtt.publish("/actuators/sg90", command.command)
        return Responses(message="open")
    elif command.command == "close":
        mqtt.publish("/actuators/sg90", command.command)
        return Responses(message="close")
