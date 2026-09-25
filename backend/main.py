from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io

from backend.schemas import HealthResponse, ModelInfoResponse, AnalyzeRequest
from backend.services.inference_service import inference_service

app = FastAPI(title="CyberCast SOC API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    inference_service.load()

@app.get("/api/health", response_model=HealthResponse)
async def get_health():
    return inference_service.get_health()

@app.get("/api/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    info = inference_service.get_model_info()
    if not info:
        raise HTTPException(status_code=503, detail="Model info not available")
    return info

@app.get("/api/demo")
async def get_demo_data():
    try:
        df = inference_service.get_demo_data()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        df = pd.DataFrame(request.data)
        result = inference_service.analyze(df, request.k)
        
        # Build network graph from available telemetry endpoints
        nodes = {}
        edges = []
        for _, row in df.iterrows():
            src = f"Port {int(row.get('src_port', 0))}" if 'src_port' in row else "Unknown Src"
            dst = f"Port {int(row.get('dst_port', 0))}" if 'dst_port' in row else "Unknown Dst"
            
            if src not in nodes:
                nodes[src] = {"id": src, "activity": 0, "type": "source"}
            if dst not in nodes:
                nodes[dst] = {"id": dst, "activity": 0, "type": "destination"}
                
            nodes[src]["activity"] += int(row.get('packet_count', row.get('fwd_packet_count', 1)))
            nodes[dst]["activity"] += int(row.get('packet_count', row.get('bwd_packet_count', 1)))
            
            edges.append({
                "source": src,
                "target": dst,
                "weight": int(row.get('flow_byte_count', 1)),
                "packets": int(row.get('packet_count', 1))
            })
            
        network_graph = {
            "nodes": list(nodes.values()),
            "edges": edges
        }
        
        return {
            "current_risk": result.current_risk,
            "risk_forecast": result.risk_forecast,
            "predicted_states": result.predicted_states,
            "predicted_stage": result.predicted_stage,
            "stage_confidence": result.stage_confidence,
            "top_features": result.top_features,
            "temporal_importance": result.temporal_importance,
            "input_quality": result.input_quality,
            "model_metadata": result.model_metadata,
            "network_graph": network_graph,
            "telemetry": request.data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/validate")
async def validate_upload(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(".parquet"):
            df = pd.read_parquet(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="INVALID_FILE_TYPE")

        # Validate by calling validate_and_preprocess without failing API
        try:
            _, quality = inference_service.engine._validate_and_preprocess(df)
            return {"status": "valid", "quality": quality, "data": df.to_dict(orient="records")}
        except ValueError as ve:
            return JSONResponse(status_code=400, content={"error": str(ve)})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
