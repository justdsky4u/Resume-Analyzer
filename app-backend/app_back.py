from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from analytics import (
    parse_input,
    profile_data,
    find_top_correlations,
    detect_anomalies,
    identify_time_series_candidates,
    identify_high_cardinality,
    calculate_duplicate_percent,
    build_visualization_blueprint,
    risk_and_opportunities,
    suggest_imputations,
    predictive_signal_scan,
)

app = FastAPI(title="AI Decision Intelligence - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    data: Any


@app.get('/health')
async def health():
    return {"status": "ok"}


@app.post('/analyze')
async def analyze(req: AnalyzeRequest) -> Dict[str, Any]:
    df = parse_input(req.data)
    if df.empty:
        return {
            'executive_summary': 'No usable data provided.',
            'surface_insights': {},
            'deep_insights': {},
            'strategic_insights': {},
            'visualization_blueprint': {},
            'recommended_actions': [],
            'risks': [],
            'opportunities': [],
        }

    surface = profile_data(df)
    deep = {
        'top_correlations': find_top_correlations(df),
        **detect_anomalies(df),
    }
    strategic = {
        'time_series_candidates': identify_time_series_candidates(df),
        'high_cardinality': identify_high_cardinality(df),
        'duplicate_percent': calculate_duplicate_percent(df),
    }
    viz = build_visualization_blueprint(df)
    signals = risk_and_opportunities(df, surface, deep)
    # advanced
    advanced = {
        'imputation_suggestions': suggest_imputations(df),
        'predictive_signals': predictive_signal_scan(df)
    }

    exec_summary = f"Dataset with {surface['rows']} rows and {surface['columns']} columns."
    if strategic['time_series_candidates']:
        exec_summary += f" Time-series candidates: {', '.join(strategic['time_series_candidates'])}."
    if surface['missing_percent']:
        high_missing = [
            c for c, p in surface['missing_percent'].items() if p > 30]
        if high_missing:
            exec_summary += f" High missingness in: {', '.join(high_missing)}."

    recommended = []
    if surface['missing_percent'] and any(p > 30 for p in surface['missing_percent'].values()):
        recommended.append(
            'Prioritize cleaning or imputing columns with >30% missing values.')
    if strategic['duplicate_percent'] > 5:
        recommended.append(
            'Investigate duplicate records and deduplicate to avoid biased analysis.')
    if deep['anomaly_count'] > 0:
        recommended.append(
            'Review detected anomalies; consider exclusion or special handling.')
    if strategic['high_cardinality']:
        recommended.append(
            'Watch high-cardinality features for noisy signals or segmentation opportunities.')

    return {
        'executive_summary': exec_summary,
        'surface_insights': surface,
        'deep_insights': deep,
        'strategic_insights': strategic,
        'visualization_blueprint': viz,
        'recommended_actions': recommended,
        'advanced_insights': advanced,
        'risks': signals['risks'],
        'opportunities': signals['opportunities'],
    }


@app.post('/analyze_file')
async def analyze_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    content = await file.read()
    try:
        text = content.decode('utf-8')
    except Exception:
        text = None
    df = parse_input(text) if text else parse_input(None)
    req = AnalyzeRequest(data=df.to_dict(orient='records'))
    return await analyze(req)
