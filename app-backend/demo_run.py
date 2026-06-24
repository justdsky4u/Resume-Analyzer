import json
import pandas as pd
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

if __name__ == '__main__':
    df = pd.read_csv('demo_sample.csv')
    profile = profile_data(df)
    deep_corr = find_top_correlations(df)
    anomalies = detect_anomalies(df)
    strategic = {
        'time_series_candidates': identify_time_series_candidates(df),
        'high_cardinality': identify_high_cardinality(df),
        'duplicate_percent': calculate_duplicate_percent(df),
    }
    viz = build_visualization_blueprint(df)
    signals = risk_and_opportunities(df, profile, anomalies)
    advanced = {
        'imputation_suggestions': suggest_imputations(df),
        'predictive_signals': predictive_signal_scan(df, min_rows=5)
    }

    result = {
        'executive_summary': f"Dataset with {profile['rows']} rows and {profile['columns']} columns.",
        'surface_insights': profile,
        'deep_insights': {'top_correlations': deep_corr, **anomalies},
        'strategic_insights': strategic,
        'visualization_blueprint': viz,
        'recommended_actions': [],
        'risks': signals['risks'],
        'opportunities': signals['opportunities'],
        'advanced_insights': advanced,
    }

    print(json.dumps(result, indent=2, default=str))
