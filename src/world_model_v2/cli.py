import argparse
import json
import pandas as pd
from .inference import InferenceEngine

def main():
    parser = argparse.ArgumentParser(description="World Model V2 Inference CLI")
    parser.add_argument("--input", type=str, required=True, help="Path to reconstructed network-state parquet/csv")
    parser.add_argument("--k", type=int, default=3, help="Autoregressive rollout steps")
    parser.add_argument("--model", type=str, default=r"D:\working_projects\SIH\cyberCast2\models\world_model_packet_v2.pt")
    parser.add_argument("--scaler", type=str, default=r"D:\working_projects\SIH\cyberCast2\models\scaler_packet_v2.pkl")
    
    args = parser.parse_args()
    
    engine = InferenceEngine(model_path=args.model, scaler_path=args.scaler)
    
    if args.input.endswith(".parquet"):
        df = pd.read_parquet(args.input)
    else:
        df = pd.read_csv(args.input)
        
    result = engine.predict_attack_progression(df, k=args.k)
    
    output = {
        "Current risk": f"{result.current_risk * 100:.2f}%",
        "Risk forecast": result.risk_forecast,
        "Predicted stage": result.predicted_stage,
        "Top features": result.top_features[:5],
        "Input quality": result.input_quality,
        "Inference latency": f"{result.model_metadata['inference_latency_seconds']:.4f} sec"
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
