import os
import json
import pandas as pd
import numpy as np
import torch
import pickle
import nbformat

def run_audit():
    project_dir = r"D:\working_projects\SIH\cyberCast2"
    notebook_path = os.path.join(project_dir, "notebooks", "Phase_9_World_Model_V2_Professional_Training.ipynb")
    model_path = os.path.join(project_dir, "models", "world_model_packet_v2.pt")
    scaler_path = os.path.join(project_dir, "models", "scaler_packet_v2.pkl")
    config_path = os.path.join(project_dir, "models", "world_model_packet_v2_config.json")
    data_dir = os.path.join(project_dir, "data", "processed", "labeled_v2")
    
    audit_results = {}
    
    # 2. Inspect Notebook
    if os.path.exists(notebook_path):
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        cells = nb.cells
        code_cells = [c for c in cells if c.cell_type == 'code']
        executed_cells = [c for c in code_cells if c.get('execution_count') is not None]
        has_outputs = any(len(c.get('outputs', [])) > 0 for c in code_cells)
        has_errors = any(any(out.get('output_type') == 'error' for out in c.get('outputs', [])) for c in code_cells)
        
        audit_results['NOTEBOOK'] = {
            'EXISTS': True,
            'SIZE': os.path.getsize(notebook_path),
            'NUMBER_OF_CELLS': len(cells),
            'NUMBER_OF_CODE_CELLS': len(code_cells),
            'NUMBER_OF_EXECUTED_CELLS': len(executed_cells),
            'LAST_EXECUTED_CELL': executed_cells[-1]['execution_count'] if executed_cells else None,
            'HAS_OUTPUTS': has_outputs,
            'HAS_ERRORS': has_errors,
            'EXECUTION_STATUS': "COMPLETE" if len(executed_cells) == len(code_cells) and len(code_cells) > 0 else ("PARTIAL" if len(executed_cells) > 0 else "NOT_EXECUTED")
        }
    else:
        audit_results['NOTEBOOK'] = {'EXISTS': False, 'EXECUTION_STATUS': 'NOT_EXECUTED'}

    # 3. Data Structure Audit
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    total_unique_windows = {}
    
    min_rows = float('inf')
    max_rows = 0
    all_rows_per_window = []
    
    for day in days:
        file_path = os.path.join(data_dir, f"{day}_labeled.parquet")
        if os.path.exists(file_path):
            df = pd.read_parquet(file_path, columns=['window_start'])
            counts = df['window_start'].value_counts()
            
            total_unique_windows[day] = len(counts)
            min_rows = int(min(min_rows, counts.min()))
            max_rows = int(max(max_rows, counts.max()))
            all_rows_per_window.extend(counts.values)
            
    median_rows = int(np.median(all_rows_per_window)) if all_rows_per_window else 0
    
    audit_results['DATASET'] = {
        'UNIQUE_WINDOWS': total_unique_windows,
        'MIN_ROWS_PER_WINDOW': min_rows,
        'MEDIAN_ROWS_PER_WINDOW': median_rows,
        'MAX_ROWS_PER_WINDOW': max_rows
    }
    
    # Model Artifacts
    audit_results['MODEL_LOAD'] = os.path.exists(model_path)
    audit_results['SCALER_LOAD'] = os.path.exists(scaler_path)
    
    with open("audit_results.json", "w") as f:
        json.dump(audit_results, f)

if __name__ == '__main__':
    run_audit()
