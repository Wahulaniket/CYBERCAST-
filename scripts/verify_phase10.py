import os
import time
import torch
import numpy as np
import pandas as pd
from src.world_model_v2.inference import InferenceEngine

def verify_phase10():
    model_path = r"D:\working_projects\SIH\cyberCast2\models\world_model_packet_v2.pt"
    scaler_path = r"D:\working_projects\SIH\cyberCast2\models\scaler_packet_v2.pkl"
    data_path = r"D:\working_projects\SIH\cyberCast2\data\processed\global_states_v2\friday_global.parquet"
    
    df = pd.read_parquet(data_path).head(100)
    
    # Measure CPU
    engine_cpu = InferenceEngine(model_path, scaler_path, device='cpu')
    
    # Warmup
    engine_cpu.predict_attack_progression(df, k=3)
    
    t0 = time.perf_counter()
    res_cpu = engine_cpu.predict_attack_progression(df, k=3)
    cpu_latency = time.perf_counter() - t0
    
    gpu_inference_latency = "N/A"
    gpu_end_to_end_latency = "N/A"
    peak_vram = "N/A"
    gpu_pass = "NOT_AVAILABLE"
    
    if torch.cuda.is_available():
        gpu_pass = "PASS"
        engine_gpu = InferenceEngine(model_path, scaler_path, device='cuda')
        
        # Warmup
        engine_gpu.predict_attack_progression(df, k=3)
        torch.cuda.synchronize()
        
        # GPU inference timing
        t0 = time.perf_counter()
        res_gpu = engine_gpu.predict_attack_progression(df, k=3)
        torch.cuda.synchronize()
        gpu_end_to_end_latency = time.perf_counter() - t0
        
        # Pure model inference latency on GPU (without pandas preprocessing)
        X_seq, _ = engine_gpu._validate_and_preprocess(df)
        X_tensor = torch.tensor(np.array([X_seq]), dtype=torch.float32, device=engine_gpu.device)
        
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        engine_gpu.model.eval()
        with torch.no_grad():
            s_hat, r_hat = engine_gpu.model(X_tensor)
        torch.cuda.synchronize()
        gpu_inference_latency = time.perf_counter() - t0
        
        peak_vram = res_gpu.model_metadata['gpu_vram_peak_mb']
        
    print(f"CPU_LATENCY_SECONDS: {cpu_latency:.4f}")
    if torch.cuda.is_available():
        print(f"GPU_LATENCY_SECONDS: {gpu_inference_latency:.4f}")
        print(f"GPU_END_TO_END_LATENCY_SECONDS: {gpu_end_to_end_latency:.4f}")
        print(f"PEAK_GPU_VRAM_MB: {peak_vram:.2f}")
    else:
        print(f"GPU_LATENCY_SECONDS: N/A")
        print(f"GPU_END_TO_END_LATENCY_SECONDS: N/A")
        print(f"PEAK_GPU_VRAM_MB: N/A")
        
    print(f"GPU_INFERENCE: {gpu_pass}")

if __name__ == '__main__':
    verify_phase10()
