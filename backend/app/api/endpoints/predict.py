from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.schemas.predict_schema import PredictionRequest, PredictionResponse
from backend.app.services.inference_service import inference_service
from backend.app.db.database import get_db
from backend.app.db import crud

router = APIRouter()

@router.post("/", response_model=PredictionResponse)
async def predict_deterioration(request: PredictionRequest, db: Session = Depends(get_db)):
    """
    Accepts 60 minutes of vital signs, processes them, returns an AI risk score,
    and logs the data to the database.
    """
    try:
        # Pass the records to the inference service
        result = inference_service.predict(request.records)
        
        # Save to Database
        crud.create_vital_signs(db, request.records)
        crud.save_prediction(db, result)
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


@router.post("/explain")
async def explain_xgboost_prediction(request: PredictionRequest, top_n: int = 5):
    """
    Computes TreeSHAP feature contributions for the XGBoost model
    based on the provided 60-minute vital sign sequence.
    Does NOT alter model predictions or retrain models.
    """
    try:
        explanation = inference_service.explain_xgboost(request.records, top_n=top_n)
        return explanation
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Explanation failed: {str(e)}")


@router.post("/anomaly-explain")
async def explain_autoencoder_anomaly(request: PredictionRequest, top_n: int = 5):
    """
    Computes Autoencoder reconstruction error breakdown for each vital sign
    and time step based on the provided vital sign sequence (minimum 30 steps).
    Does NOT alter model predictions or retrain models.
    """
    try:
        explanation = inference_service.explain_autoencoder(request.records, top_n=top_n)
        return explanation
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Autoencoder explanation failed: {str(e)}")


@router.post("/attention-explain")
async def explain_transformer_attention(request: PredictionRequest, top_n: int = 5):
    """
    Computes Multi-Head Self-Attention temporal weights for the Transformer model
    based on the provided vital sign sequence (minimum 30 steps).
    Does NOT alter model predictions or retrain models.
    """
    try:
        explanation = inference_service.explain_transformer(request.records, top_n=top_n)
        return explanation
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transformer attention explanation failed: {str(e)}")


@router.post("/forecast")
async def get_transformer_multi_horizon_forecast(request: PredictionRequest):
    """
    Returns multi-horizon forecasting capability audit status for the existing Transformer.
    Reports exact technical limitations without fabricating fake forecasts.
    """
    try:
        forecast = inference_service.get_transformer_forecast(request.records)
        return forecast
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Forecast query failed: {str(e)}")




