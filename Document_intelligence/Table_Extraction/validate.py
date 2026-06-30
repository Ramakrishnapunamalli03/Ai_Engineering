def is_clean_table(df) -> bool:
    if df.empty: return False
    # Every row should have ~the same non-null cell count
    non_null = df.notna().sum(axis=1)
    if non_null.std() > 1.5: return False
    # Header row should be string-y, not numeric
    if not all(isinstance(c, str) for c in df.columns): return False
    return True