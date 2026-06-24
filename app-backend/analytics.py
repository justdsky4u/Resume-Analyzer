from typing import Any, Dict, List
from io import StringIO
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score


def parse_input(data: Any) -> pd.DataFrame:
    if data is None:
        return pd.DataFrame()
    if isinstance(data, list):
        return pd.DataFrame(data)
    if isinstance(data, dict):
        if 'records' in data and isinstance(data['records'], list):
            return pd.DataFrame(data['records'])
        return pd.DataFrame(data)
    if isinstance(data, str):
        try:
            return pd.read_csv(StringIO(data))
        except Exception:
            try:
                return pd.read_json(StringIO(data), lines=True)
            except Exception:
                return pd.DataFrame({'raw': [data]})
    return pd.DataFrame()


def profile_data(df: pd.DataFrame) -> Dict[str, Any]:
    profile = {
        'rows': int(df.shape[0]),
        'columns': int(df.shape[1]),
        'dtypes': {c: str(dtype) for c, dtype in df.dtypes.items()},
        'missing_percent': {c: float(df[c].isna().mean() * 100) for c in df.columns},
        'sample': df.head(5).to_dict(orient='records')
    }
    numeric = df.select_dtypes(include=[np.number])
    if not numeric.empty:
        profile['numeric_summary'] = numeric.agg(
            ['mean', 'median', 'std', 'min', 'max']).to_dict()
        profile['numeric_ranges'] = {c: {'min': float(numeric[c].min()), 'max': float(
            numeric[c].max())} for c in numeric.columns}
    else:
        profile['numeric_summary'] = {}
        profile['numeric_ranges'] = {}
    return profile


def find_top_correlations(df: pd.DataFrame, top_n: int = 10) -> List[Dict[str, Any]]:
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] < 2:
        return []
    corr = numeric.corr()
    corr_unstack = corr.abs().stack().reset_index()
    corr_unstack.columns = ['a', 'b', 'corr']
    corr_unstack = corr_unstack[corr_unstack['a'] != corr_unstack['b']]
    top = corr_unstack.sort_values('corr', ascending=False).head(top_n)
    return top.to_dict(orient='records')


def detect_anomalies(df: pd.DataFrame) -> Dict[str, Any]:
    numeric = df.select_dtypes(include=[np.number])
    insight = {'anomaly_count': 0, 'anomaly_examples': []}
    if not numeric.empty and numeric.shape[0] >= 10:
        iso = IsolationForest(random_state=42, contamination=0.01)
        try:
            preds = iso.fit_predict(numeric.fillna(numeric.mean()))
            anomalies = np.where(preds == -1)[0]
            insight['anomaly_count'] = int(len(anomalies))
            insight['anomaly_examples'] = df.iloc[anomalies[:5]
                                                  ].to_dict(orient='records')
        except Exception:
            pass
    return insight


def identify_time_series_candidates(df: pd.DataFrame) -> List[str]:
    dt_candidates = []
    for c in df.columns:
        if df[c].dtype == 'object':
            try:
                parsed = pd.to_datetime(df[c], errors='coerce')
                if parsed.notna().sum() / max(1, len(parsed)) > 0.6:
                    dt_candidates.append(c)
            except Exception:
                pass
    return dt_candidates


def identify_high_cardinality(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if df[c].nunique(dropna=True) > max(50, 0.1 * max(1, len(df)))]


def calculate_duplicate_percent(df: pd.DataFrame) -> float:
    if df.shape[0] == 0:
        return 0.0
    dup_rate = 1 - (df.drop_duplicates().shape[0] / float(df.shape[0]))
    return float(dup_rate * 100)


def build_visualization_blueprint(df: pd.DataFrame) -> Dict[str, Any]:
    vb = {'line_charts': [], 'bar_charts': [],
          'heatmaps': [], 'pie_charts': []}
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical = df.select_dtypes(
        include=['object', 'category']).columns.tolist()
    for t in df.columns:
        try:
            parsed = pd.to_datetime(df[t], errors='coerce')
            if parsed.notna().sum() / max(1, len(parsed)) > 0.6 and numeric:
                vb['line_charts'].append({'x': t, 'y_candidates': numeric[:3]})
        except Exception:
            pass
    if categorical and numeric:
        vb['bar_charts'].append(
            {'x_candidates': categorical[:3], 'y_candidates': numeric[:3]})
    if len(numeric) >= 2:
        vb['heatmaps'].append({'columns': numeric})
    small_cat = [c for c in categorical if df[c].nunique() <= 10]
    for c in small_cat[:3]:
        vb['pie_charts'].append({'column': c})
    return vb


def risk_and_opportunities(df: pd.DataFrame, profile: Dict[str, Any], anomalies: Dict[str, Any]) -> Dict[str, Any]:
    risks = []
    opportunities = []
    if profile['rows'] == 0:
        return {'risks': [], 'opportunities': []}
    high_missing = [c for c, p in profile['missing_percent'].items() if p > 40]
    if high_missing:
        risks.append(
            f"High missingness in {', '.join(high_missing)} could distort models and decisions.")
    if anomalies['anomaly_count'] > 0:
        risks.append(
            f"Detected {anomalies['anomaly_count']} anomalies that may indicate data issues or emerging risk patterns.")
    if profile['columns'] > 20:
        opportunities.append(
            'Potential feature engineering win: reduce noise by focusing on the strongest signals.')
    if len(identify_time_series_candidates(df)) > 0:
        opportunities.append(
            'Time-based analysis is possible; build trend and seasonality models.')
    if profile['rows'] > 1000 and df.select_dtypes(include=[np.number]).shape[1] >= 2:
        opportunities.append(
            'Leverage predictive modeling on this dataset for growth or risk forecasting.')
    return {'risks': risks, 'opportunities': opportunities}


def suggest_imputations(df: pd.DataFrame) -> Dict[str, Any]:
    """Return simple imputation suggestions for columns based on type and missingness."""
    suggestions = {}
    for c in df.columns:
        miss = float(df[c].isna().mean() * 100)
        if miss == 0:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            # prefer median for skewed, mean for symmetric - use skewness heuristic
            try:
                skew = float(df[c].skew())
            except Exception:
                skew = 0.0
            method = 'median' if abs(skew) > 1 else 'mean'
            suggestions[c] = {'missing_percent': miss,
                              'suggested_method': method}
        else:
            suggestions[c] = {'missing_percent': miss,
                              'suggested_method': 'mode'}
    return suggestions


def predictive_signal_scan(df: pd.DataFrame, max_features: int = 10, min_rows: int = 200) -> Dict[str, Any]:
    """Quickly scan numeric columns to find which are predictable from others.

    Trains shallow RandomForestRegressor models (cross-validated) for candidate numeric targets.
    Returns top predictive signals with mean CV R^2.
    """
    results = []
    numeric = df.select_dtypes(include=[np.number]).dropna()
    if numeric.shape[0] < min_rows or numeric.shape[1] < 2:
        return {'note': 'Not enough numeric data for predictive scan', 'signals': []}

    cols = numeric.columns.tolist()
    for target in cols:
        X = numeric.drop(columns=[target])
        y = numeric[target]
        # limit features
        if X.shape[1] > max_features:
            X = X.iloc[:, :max_features]
        try:
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            scores = cross_val_score(model, X, y, cv=3, scoring='r2')
            mean_r2 = float(np.mean(scores))
            results.append(
                {'target': target, 'mean_cv_r2': mean_r2, 'n_features': X.shape[1]})
        except Exception:
            continue

    results = sorted(results, key=lambda r: r['mean_cv_r2'], reverse=True)
    top = [r for r in results if r['mean_cv_r2'] > 0.2][:10]
    return {'signals': top, 'all': results}
