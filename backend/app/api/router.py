
from fastapi import APIRouter
from backend.app.api.endpoints import predict, stream, chatbot, patient, import_api

api_router = APIRouter()
api_router.include_router(predict.router, prefix='/predict', tags=['Prediction'])
api_router.include_router(stream.router, prefix='/stream', tags=['Stream'])
api_router.include_router(chatbot.router, prefix='/chat', tags=['Chatbot'])
api_router.include_router(patient.router, prefix='/patients', tags=['Patients'])
api_router.include_router(import_api.router, prefix='/data', tags=['Import'])

