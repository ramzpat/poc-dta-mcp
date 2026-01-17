---
applyTo: '**/*.py'
description: 'Data analytics best practices for pandas, numpy, and statistical analysis in the POC DTA MCP project'
---

# Data Analytics Instructions

## Your Mission

As GitHub Copilot, you are an expert in data analytics with deep knowledge of pandas, numpy, scipy, and statistical analysis. Your goal is to help developers write efficient, accurate, and reproducible data analysis code for the MCP-based data analytics system.

## Core Principles

1. **Reproducibility**: All analysis must be reproducible with fixed random seeds
2. **Data Quality**: Always validate and clean data before analysis
3. **Performance**: Optimize for memory efficiency and computation speed
4. **Clarity**: Write self-documenting code with clear variable names
5. **Error Handling**: Handle missing data, outliers, and edge cases gracefully

## Data Loading and Validation

### Best Practices

```python
import pandas as pd
import numpy as np
from typing import Optional

def load_and_validate_data(
    file_path: str,
    expected_columns: list[str],
    date_columns: Optional[list[str]] = None
) -> pd.DataFrame:
    """
    Load data from file and validate schema.
    
    Args:
        file_path: Path to data file
        expected_columns: List of required column names
        date_columns: Columns to parse as dates
        
    Returns:
        Validated DataFrame
        
    Raises:
        ValueError: If required columns are missing
    """
    # Load data
    df = pd.read_csv(file_path, parse_dates=date_columns)
    
    # Validate columns
    missing_cols = set(expected_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Check for empty dataframe
    if df.empty:
        raise ValueError("Loaded data is empty")
    
    # Log data quality metrics
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    print(f"Missing values: {df.isnull().sum().sum()}")
    
    return df
```

### Data Type Validation

```python
def validate_data_types(df: pd.DataFrame, schema: dict[str, str]) -> pd.DataFrame:
    """
    Validate and convert data types according to schema.
    
    Args:
        df: Input DataFrame
        schema: Dict mapping column names to expected types
        
    Returns:
        DataFrame with corrected types
    """
    for col, dtype in schema.items():
        if col not in df.columns:
            continue
            
        try:
            if dtype == 'numeric':
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif dtype == 'datetime':
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif dtype == 'category':
                df[col] = df[col].astype('category')
            elif dtype == 'string':
                df[col] = df[col].astype('string')
        except Exception as e:
            raise ValueError(f"Failed to convert column {col} to {dtype}: {e}")
    
    return df
```

## Data Cleaning

### Handle Missing Data

```python
def handle_missing_data(
    df: pd.DataFrame,
    strategy: dict[str, str]
) -> pd.DataFrame:
    """
    Handle missing data using specified strategies.
    
    Args:
        df: Input DataFrame
        strategy: Dict mapping column names to strategies:
            - 'drop': Drop rows with missing values
            - 'mean': Fill with column mean
            - 'median': Fill with column median
            - 'mode': Fill with column mode
            - 'forward': Forward fill
            - 'zero': Fill with zero
            
    Returns:
        DataFrame with missing values handled
    """
    df = df.copy()
    
    for col, method in strategy.items():
        if col not in df.columns:
            continue
            
        if method == 'drop':
            df = df.dropna(subset=[col])
        elif method == 'mean':
            df[col].fillna(df[col].mean(), inplace=True)
        elif method == 'median':
            df[col].fillna(df[col].median(), inplace=True)
        elif method == 'mode':
            df[col].fillna(df[col].mode()[0], inplace=True)
        elif method == 'forward':
            df[col].fillna(method='ffill', inplace=True)
        elif method == 'zero':
            df[col].fillna(0, inplace=True)
    
    return df
```

### Detect and Handle Outliers

```python
from scipy import stats

def detect_outliers_iqr(
    df: pd.DataFrame,
    column: str,
    multiplier: float = 1.5
) -> pd.Series:
    """
    Detect outliers using IQR method.
    
    Args:
        df: Input DataFrame
        column: Column name to check
        multiplier: IQR multiplier for outlier detection
        
    Returns:
        Boolean Series marking outliers as True
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    return (df[column] < lower_bound) | (df[column] > upper_bound)

def detect_outliers_zscore(
    df: pd.DataFrame,
    column: str,
    threshold: float = 3.0
) -> pd.Series:
    """
    Detect outliers using Z-score method.
    
    Args:
        df: Input DataFrame
        column: Column name to check
        threshold: Z-score threshold for outliers
        
    Returns:
        Boolean Series marking outliers as True
    """
    z_scores = np.abs(stats.zscore(df[column].dropna()))
    return z_scores > threshold
```

## Exploratory Data Analysis (EDA)

### Generate Summary Statistics

```python
def generate_summary_stats(df: pd.DataFrame) -> dict:
    """
    Generate comprehensive summary statistics.
    
    Returns:
        Dict containing:
            - basic_stats: describe() output
            - missing: Missing value counts
            - dtypes: Data types
            - memory: Memory usage
            - correlations: Correlation matrix for numeric columns
    """
    return {
        'basic_stats': df.describe(include='all').to_dict(),
        'missing': df.isnull().sum().to_dict(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'memory_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'correlations': df.select_dtypes(include=[np.number]).corr().to_dict()
    }
```

### Distribution Analysis

```python
def analyze_distribution(df: pd.DataFrame, column: str) -> dict:
    """
    Analyze distribution of a numeric column.
    
    Returns:
        Dict containing distribution metrics
    """
    series = df[column].dropna()
    
    return {
        'mean': float(series.mean()),
        'median': float(series.median()),
        'std': float(series.std()),
        'skewness': float(series.skew()),
        'kurtosis': float(series.kurtosis()),
        'min': float(series.min()),
        'max': float(series.max()),
        'q25': float(series.quantile(0.25)),
        'q75': float(series.quantile(0.75))
    }
```

## Statistical Analysis

### Hypothesis Testing

```python
from scipy.stats import ttest_ind, chi2_contingency

def compare_groups_ttest(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    group1: str,
    group2: str
) -> dict:
    """
    Perform t-test to compare two groups.
    
    Returns:
        Dict with test results
    """
    data1 = df[df[group_col] == group1][value_col].dropna()
    data2 = df[df[group_col] == group2][value_col].dropna()
    
    statistic, p_value = ttest_ind(data1, data2)
    
    return {
        'statistic': float(statistic),
        'p_value': float(p_value),
        'significant': p_value < 0.05,
        'group1_mean': float(data1.mean()),
        'group2_mean': float(data2.mean()),
        'group1_n': len(data1),
        'group2_n': len(data2)
    }

def chi_square_test(df: pd.DataFrame, col1: str, col2: str) -> dict:
    """
    Perform chi-square test of independence.
    
    Returns:
        Dict with test results
    """
    contingency_table = pd.crosstab(df[col1], df[col2])
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    return {
        'chi2': float(chi2),
        'p_value': float(p_value),
        'degrees_of_freedom': int(dof),
        'significant': p_value < 0.05,
        'contingency_table': contingency_table.to_dict()
    }
```

### Time Series Analysis

```python
def calculate_time_series_metrics(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    freq: str = 'D'
) -> pd.DataFrame:
    """
    Calculate time series metrics.
    
    Args:
        df: Input DataFrame
        date_col: Date column name
        value_col: Value column name
        freq: Frequency for resampling ('D', 'W', 'M')
        
    Returns:
        DataFrame with time series metrics
    """
    ts = df.set_index(date_col)[value_col].resample(freq).agg([
        'mean',
        'median',
        'sum',
        'count',
        'std'
    ])
    
    # Calculate rolling metrics
    ts['rolling_mean_7d'] = ts['mean'].rolling(window=7).mean()
    ts['rolling_std_7d'] = ts['mean'].rolling(window=7).std()
    
    return ts.reset_index()
```

## Performance Optimization

### Memory Efficiency

```python
def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame memory usage by downcasting numeric types.
    
    Returns:
        Optimized DataFrame
    """
    df = df.copy()
    
    # Downcast integers
    int_cols = df.select_dtypes(include=['int']).columns
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    # Downcast floats
    float_cols = df.select_dtypes(include=['float']).columns
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    # Convert to category for low-cardinality string columns
    for col in df.select_dtypes(include=['object']).columns:
        num_unique = df[col].nunique()
        num_total = len(df[col])
        if num_unique / num_total < 0.5:
            df[col] = df[col].astype('category')
    
    return df
```

### Vectorization

```python
# BAD: Using iterrows
total = 0
for _, row in df.iterrows():
    total += row['value'] * row['multiplier']

# GOOD: Using vectorization
total = (df['value'] * df['multiplier']).sum()

# GOOD: Using numpy for complex operations
import numpy as np
result = np.where(
    df['condition'] > threshold,
    df['value_a'],
    df['value_b']
)
```

## Data Aggregation

### Group-By Operations

```python
def aggregate_by_groups(
    df: pd.DataFrame,
    group_cols: list[str],
    agg_config: dict
) -> pd.DataFrame:
    """
    Perform group-by aggregation with custom configuration.
    
    Args:
        df: Input DataFrame
        group_cols: Columns to group by
        agg_config: Dict mapping column names to aggregation functions
        
    Returns:
        Aggregated DataFrame
    """
    result = df.groupby(group_cols).agg(agg_config).reset_index()
    
    # Flatten multi-level column names
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = ['_'.join(col).strip('_') for col in result.columns]
    
    return result

# Example usage
agg_result = aggregate_by_groups(
    df,
    group_cols=['customer_segment', 'region'],
    agg_config={
        'revenue': ['sum', 'mean', 'count'],
        'churn': 'mean'
    }
)
```

## Telco-Specific Analytics

### Churn Analysis

```python
def calculate_churn_rate(
    df: pd.DataFrame,
    segment_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Calculate churn rate overall and by segment.
    
    Args:
        df: DataFrame with 'is_churned' boolean column
        segment_col: Optional column for segmentation
        
    Returns:
        DataFrame with churn rates
    """
    if segment_col:
        churn_stats = df.groupby(segment_col).agg({
            'is_churned': ['sum', 'count', 'mean']
        })
        churn_stats.columns = ['churned_count', 'total_count', 'churn_rate']
    else:
        churned = df['is_churned'].sum()
        total = len(df)
        churn_stats = pd.DataFrame({
            'churned_count': [churned],
            'total_count': [total],
            'churn_rate': [churned / total]
        })
    
    return churn_stats.reset_index()

def identify_churn_factors(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str = 'is_churned'
) -> pd.DataFrame:
    """
    Identify factors correlated with churn.
    
    Returns:
        DataFrame with feature correlations sorted by absolute value
    """
    correlations = df[feature_cols + [target_col]].corr()[target_col].drop(target_col)
    
    result = pd.DataFrame({
        'feature': correlations.index,
        'correlation': correlations.values
    })
    
    return result.sort_values('correlation', key=abs, ascending=False)
```

### Network Quality Analysis

```python
def calculate_network_quality_metrics(
    df: pd.DataFrame,
    quality_col: str = 'network_quality_score',
    group_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Calculate network quality metrics.
    
    Returns:
        DataFrame with quality metrics
    """
    metrics = {
        'mean_quality': df[quality_col].mean(),
        'median_quality': df[quality_col].median(),
        'poor_quality_pct': (df[quality_col] < 3.0).mean() * 100,
        'excellent_quality_pct': (df[quality_col] >= 4.5).mean() * 100
    }
    
    if group_col:
        result = df.groupby(group_col)[quality_col].agg([
            'mean', 'median', 'std', 'count'
        ]).reset_index()
        result.columns = [group_col, 'mean_quality', 'median_quality', 'std_quality', 'event_count']
    else:
        result = pd.DataFrame([metrics])
    
    return result
```

### ARPU Calculation

```python
def calculate_arpu(
    df: pd.DataFrame,
    revenue_col: str = 'amount',
    customer_col: str = 'customer_id',
    period_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Calculate Average Revenue Per User (ARPU).
    
    Args:
        df: Revenue DataFrame
        revenue_col: Column containing revenue amounts
        customer_col: Column containing customer IDs
        period_col: Optional column for time period (e.g., 'month')
        
    Returns:
        DataFrame with ARPU metrics
    """
    if period_col:
        arpu = df.groupby(period_col).apply(
            lambda x: x[revenue_col].sum() / x[customer_col].nunique()
        ).reset_index(name='arpu')
    else:
        total_revenue = df[revenue_col].sum()
        unique_customers = df[customer_col].nunique()
        arpu = pd.DataFrame({
            'arpu': [total_revenue / unique_customers],
            'total_revenue': [total_revenue],
            'unique_customers': [unique_customers]
        })
    
    return arpu
```

## Error Handling Best Practices

```python
import logging
from typing import Union

logger = logging.getLogger(__name__)

def safe_analyze(
    df: pd.DataFrame,
    analysis_func: callable,
    **kwargs
) -> Union[dict, pd.DataFrame, None]:
    """
    Safely execute analysis function with error handling.
    
    Returns:
        Analysis result or None if error
    """
    try:
        # Validate input
        if df.empty:
            logger.warning("Empty DataFrame provided")
            return None
        
        # Execute analysis
        result = analysis_func(df, **kwargs)
        
        # Log success
        logger.info(f"Analysis {analysis_func.__name__} completed successfully")
        
        return result
        
    except KeyError as e:
        logger.error(f"Missing required column: {e}")
        return None
    except ValueError as e:
        logger.error(f"Invalid value in analysis: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in analysis: {e}", exc_info=True)
        return None
```

## Code Review Checklist

When reviewing data analytics code, check for:

- [ ] Data validation before analysis
- [ ] Missing data handling strategy
- [ ] Outlier detection and handling
- [ ] Vectorized operations (no iterrows)
- [ ] Memory optimization for large datasets
- [ ] Fixed random seeds for reproducibility
- [ ] Proper data type usage
- [ ] Clear variable naming
- [ ] Comprehensive error handling
- [ ] Performance considerations
- [ ] Documentation of assumptions
- [ ] Unit tests for analysis functions

## Common Pitfalls to Avoid

1. **SettingWithCopyWarning**: Always use `.copy()` or `.loc[]` for assignments
2. **Chained indexing**: Use single `.loc[]` instead of multiple brackets
3. **Unnecessary loops**: Vectorize operations with pandas/numpy
4. **Memory leaks**: Clear large DataFrames when no longer needed
5. **Type mismatches**: Validate and convert data types early
6. **Ignoring NaN**: Explicitly handle missing values
7. **Hardcoded values**: Use constants or configuration
8. **No reproducibility**: Set random seeds

## Performance Tips

1. Use `category` dtype for low-cardinality string columns
2. Use `eval()` and `query()` for complex filtering
3. Use `nlargest()` / `nsmallest()` instead of `sort_values().head()`
4. Use `isin()` instead of multiple OR conditions
5. Use `apply()` with `raw=True` for numpy arrays
6. Consider `dask` or `vaex` for datasets > 1GB
7. Use `chunked` reading for very large files
8. Profile with `%%timeit` in notebooks

---

**Remember**: The goal is to produce accurate, reproducible, and efficient data analysis that enables AI agents to make data-driven decisions autonomously.
