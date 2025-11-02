"""
Chart.js data serializers.

This module contains functions to convert database querysets and data structures
into Chart.js-compatible JSON formats.

Functions:
- to_bar_chart_data: Convert data to bar chart format
- to_line_chart_data: Convert data to line chart format
- to_pie_chart_data: Convert data to pie chart format
- to_multi_dataset_chart_data: Convert data to multi-dataset chart format
- to_dual_axis_chart_data: Convert data to dual-axis chart format

Color Palette:
CHART_COLORS provides a consistent color scheme across all visualizations.
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional, Union


# Chart.js color palette
CHART_COLORS = [
    '#4e73df',  # Primary blue
    '#1cc88a',  # Success green
    '#36b9cc',  # Info cyan
    '#f6c23e',  # Warning yellow
    '#e74a3b',  # Danger red
    '#858796',  # Secondary gray
    '#5a5c69',  # Dark gray
    '#60c060',  # Light green
]


def _convert_value(value: Any) -> Union[int, float, str, None]:
    """
    Convert a value to a JSON-serializable type.

    Args:
        value: The value to convert (can be Decimal, int, float, str, etc.)

    Returns:
        JSON-serializable value (int, float, str, or None)
    """
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float, str)):
        return value
    # For other types (like dates), convert to string
    return str(value)


def _get_color(index: int) -> str:
    """
    Get a color from the palette by index, cycling if necessary.

    Args:
        index: The index of the color to retrieve

    Returns:
        Hex color code
    """
    return CHART_COLORS[index % len(CHART_COLORS)]


def to_bar_chart_data(
    data: List[Dict[str, Any]],
    label_field: str,
    value_field: str,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert data to Chart.js bar chart format.

    Args:
        data: List of dictionaries containing the data
        label_field: Field name to use for chart labels (x-axis)
        value_field: Field name to use for chart values (y-axis)
        title: Optional title for the dataset

    Returns:
        Dictionary in Chart.js format:
        {
            'labels': [...],
            'datasets': [{
                'label': '...',
                'data': [...],
                'backgroundColor': [...]
            }]
        }

    Example:
        >>> data = [
        ...     {'department': 'CS', 'budget': 1000000},
        ...     {'department': 'EE', 'budget': 1500000},
        ... ]
        >>> to_bar_chart_data(data, 'department', 'budget', 'Budget by Department')
    """
    labels = []
    values = []
    colors = []

    for i, item in enumerate(data):
        labels.append(_convert_value(item.get(label_field)))
        values.append(_convert_value(item.get(value_field)))
        colors.append(_get_color(i))

    dataset = {
        'data': values,
        'backgroundColor': colors,
    }

    if title:
        dataset['label'] = title

    return {
        'labels': labels,
        'datasets': [dataset]
    }


def to_line_chart_data(
    data: List[Dict[str, Any]],
    x_field: str,
    y_field: str,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert data to Chart.js line chart format.

    Args:
        data: List of dictionaries containing the data
        x_field: Field name to use for x-axis (labels)
        y_field: Field name to use for y-axis (values)
        title: Optional title for the dataset

    Returns:
        Dictionary in Chart.js format:
        {
            'labels': [...],
            'datasets': [{
                'label': '...',
                'data': [...],
                'borderColor': '...',
                'fill': False
            }]
        }

    Example:
        >>> data = [
        ...     {'year': 2021, 'enrollment': 450},
        ...     {'year': 2022, 'enrollment': 480},
        ... ]
        >>> to_line_chart_data(data, 'year', 'enrollment', 'Student Enrollment')
    """
    labels = []
    values = []

    for item in data:
        labels.append(_convert_value(item.get(x_field)))
        values.append(_convert_value(item.get(y_field)))

    dataset = {
        'data': values,
        'borderColor': CHART_COLORS[0],
        'fill': False,
    }

    if title:
        dataset['label'] = title

    return {
        'labels': labels,
        'datasets': [dataset]
    }


def to_pie_chart_data(
    data: List[Dict[str, Any]],
    label_field: str,
    value_field: str,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert data to Chart.js pie chart format.

    Args:
        data: List of dictionaries containing the data
        label_field: Field name to use for slice labels
        value_field: Field name to use for slice values
        title: Optional title (not used for pie charts typically)

    Returns:
        Dictionary in Chart.js format:
        {
            'labels': [...],
            'datasets': [{
                'data': [...],
                'backgroundColor': [...]
            }]
        }

    Note:
        Pie charts typically don't have a dataset label, only segment labels.

    Example:
        >>> data = [
        ...     {'grade': 'SCI', 'count': 30},
        ...     {'grade': 'SCIE', 'count': 20},
        ... ]
        >>> to_pie_chart_data(data, 'grade', 'count')
    """
    labels = []
    values = []
    colors = []

    for i, item in enumerate(data):
        labels.append(_convert_value(item.get(label_field)))
        values.append(_convert_value(item.get(value_field)))
        colors.append(_get_color(i))

    dataset = {
        'data': values,
        'backgroundColor': colors,
    }
    # Note: Pie charts typically don't have dataset labels

    return {
        'labels': labels,
        'datasets': [dataset]
    }


def to_multi_dataset_chart_data(
    data: List[Dict[str, Any]],
    x_field: str,
    datasets_config: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Convert data to Chart.js format with multiple datasets.

    Args:
        data: List of dictionaries containing the data
        x_field: Field name to use for x-axis (shared labels)
        datasets_config: List of dataset configurations, each containing:
            - 'label': Display name for the dataset
            - 'field': Field name to extract values from

    Returns:
        Dictionary in Chart.js format:
        {
            'labels': [...],
            'datasets': [
                {'label': '...', 'data': [...], 'backgroundColor': '...'},
                {'label': '...', 'data': [...], 'backgroundColor': '...'},
            ]
        }

    Example:
        >>> data = [
        ...     {'year': 2021, 'domestic': 100, 'international': 50},
        ...     {'year': 2022, 'domestic': 120, 'international': 60},
        ... ]
        >>> config = [
        ...     {'label': 'Domestic', 'field': 'domestic'},
        ...     {'label': 'International', 'field': 'international'},
        ... ]
        >>> to_multi_dataset_chart_data(data, 'year', config)
    """
    # Extract labels from x_field
    labels = [_convert_value(item.get(x_field)) for item in data]

    # Build datasets
    datasets = []
    for i, ds_config in enumerate(datasets_config):
        field = ds_config['field']
        label = ds_config['label']

        values = [_convert_value(item.get(field)) for item in data]

        dataset = {
            'label': label,
            'data': values,
            'backgroundColor': _get_color(i),
        }
        datasets.append(dataset)

    return {
        'labels': labels,
        'datasets': datasets
    }


def to_dual_axis_chart_data(
    data: List[Dict[str, Any]],
    x_field: str,
    y1_field: str,
    y2_field: str,
    y1_label: str,
    y2_label: str
) -> Dict[str, Any]:
    """
    Convert data to Chart.js format with dual y-axes.

    Creates a mixed chart with:
    - First dataset: Bar chart on left y-axis (y1)
    - Second dataset: Line chart on right y-axis (y2)

    Args:
        data: List of dictionaries containing the data
        x_field: Field name to use for x-axis (labels)
        y1_field: Field name for left y-axis (bar chart)
        y2_field: Field name for right y-axis (line chart)
        y1_label: Display label for left y-axis dataset
        y2_label: Display label for right y-axis dataset

    Returns:
        Dictionary in Chart.js format:
        {
            'labels': [...],
            'datasets': [
                {
                    'label': '...',
                    'data': [...],
                    'yAxisID': 'y1',
                    'type': 'bar',
                    'backgroundColor': '...'
                },
                {
                    'label': '...',
                    'data': [...],
                    'yAxisID': 'y2',
                    'type': 'line',
                    'borderColor': '...',
                    'fill': False
                }
            ]
        }

    Example:
        >>> data = [
        ...     {'dept': 'CS', 'budget': 10000000, 'exec_rate': 85.5},
        ...     {'dept': 'EE', 'budget': 15000000, 'exec_rate': 92.3},
        ... ]
        >>> to_dual_axis_chart_data(
        ...     data, 'dept', 'budget', 'exec_rate',
        ...     'Budget (KRW)', 'Execution Rate (%)'
        ... )
    """
    # Extract labels
    labels = [_convert_value(item.get(x_field)) for item in data]

    # Extract values for both y-axes
    y1_values = [_convert_value(item.get(y1_field)) for item in data]
    y2_values = [_convert_value(item.get(y2_field)) for item in data]

    # First dataset: Bar chart on left y-axis
    dataset1 = {
        'label': y1_label,
        'data': y1_values,
        'yAxisID': 'y1',
        'type': 'bar',
        'backgroundColor': CHART_COLORS[0],
    }

    # Second dataset: Line chart on right y-axis
    dataset2 = {
        'label': y2_label,
        'data': y2_values,
        'yAxisID': 'y2',
        'type': 'line',
        'borderColor': CHART_COLORS[1],
        'fill': False,
    }

    return {
        'labels': labels,
        'datasets': [dataset1, dataset2]
    }
