"""
Tests for Chart.js serializers.

This module contains tests for functions that convert database querysets
and data structures into Chart.js-compatible JSON formats.

Test Coverage:
- Bar chart data serialization
- Line chart data serialization
- Pie chart data serialization
- Multi-dataset chart data serialization
- Dual-axis chart data serialization
- Edge cases: empty data, missing fields, None values

Following TDD RED-GREEN-REFACTOR cycle:
- RED: These tests will fail until serializers.py is implemented
- GREEN: Implement minimal code to pass
- REFACTOR: Optimize and clean up
"""

from django.test import TestCase
from decimal import Decimal
from apps.analytics.serializers import (
    to_bar_chart_data,
    to_line_chart_data,
    to_pie_chart_data,
    to_multi_dataset_chart_data,
    to_dual_axis_chart_data,
    CHART_COLORS,
)


class BarChartSerializerTest(TestCase):
    """
    Test suite for to_bar_chart_data serializer.

    Validates conversion of data to Chart.js bar chart format:
    {
        'labels': [...],
        'datasets': [{
            'label': '...',
            'data': [...],
            'backgroundColor': [...]
        }]
    }
    """

    def test_basic_bar_chart_with_dict_list(self):
        """Should convert list of dicts to bar chart format."""
        # Arrange
        data = [
            {'department': '컴퓨터공학과', 'budget': 1000000},
            {'department': '전자공학과', 'budget': 1500000},
            {'department': '기계공학과', 'budget': 1200000},
        ]

        # Act
        result = to_bar_chart_data(data, 'department', 'budget')

        # Assert
        self.assertEqual(result['labels'], ['컴퓨터공학과', '전자공학과', '기계공학과'])
        self.assertEqual(result['datasets'][0]['data'], [1000000, 1500000, 1200000])
        self.assertIn('backgroundColor', result['datasets'][0])
        self.assertEqual(len(result['datasets'][0]['backgroundColor']), 3)

    def test_bar_chart_with_custom_title(self):
        """Should include custom title in dataset label."""
        # Arrange
        data = [
            {'name': 'A', 'value': 100},
            {'name': 'B', 'value': 200},
        ]

        # Act
        result = to_bar_chart_data(data, 'name', 'value', title='Test Data')

        # Assert
        self.assertEqual(result['datasets'][0]['label'], 'Test Data')

    def test_bar_chart_with_decimal_values(self):
        """Should handle Decimal values correctly."""
        # Arrange
        data = [
            {'category': 'X', 'amount': Decimal('1234.56')},
            {'category': 'Y', 'amount': Decimal('7890.12')},
        ]

        # Act
        result = to_bar_chart_data(data, 'category', 'amount')

        # Assert
        self.assertEqual(result['datasets'][0]['data'], [1234.56, 7890.12])

    def test_bar_chart_with_empty_data(self):
        """Should return empty structure for empty data."""
        # Arrange
        data = []

        # Act
        result = to_bar_chart_data(data, 'label', 'value')

        # Assert
        self.assertEqual(result['labels'], [])
        self.assertEqual(result['datasets'][0]['data'], [])
        self.assertEqual(result['datasets'][0]['backgroundColor'], [])

    def test_bar_chart_uses_color_palette(self):
        """Should use colors from CHART_COLORS palette."""
        # Arrange
        data = [{'x': f'Item{i}', 'y': i*100} for i in range(5)]

        # Act
        result = to_bar_chart_data(data, 'x', 'y')

        # Assert
        colors = result['datasets'][0]['backgroundColor']
        for color in colors:
            self.assertIn(color, CHART_COLORS)


class LineChartSerializerTest(TestCase):
    """
    Test suite for to_line_chart_data serializer.

    Validates conversion to Chart.js line chart format:
    {
        'labels': [...],
        'datasets': [{
            'label': '...',
            'data': [...],
            'borderColor': '...',
            'fill': False
        }]
    }
    """

    def test_basic_line_chart_with_dates(self):
        """Should convert time series data to line chart format."""
        # Arrange
        data = [
            {'year': 2021, 'enrollment': 450},
            {'year': 2022, 'enrollment': 480},
            {'year': 2023, 'enrollment': 520},
        ]

        # Act
        result = to_line_chart_data(data, 'year', 'enrollment')

        # Assert
        self.assertEqual(result['labels'], [2021, 2022, 2023])
        self.assertEqual(result['datasets'][0]['data'], [450, 480, 520])
        self.assertIn('borderColor', result['datasets'][0])
        self.assertEqual(result['datasets'][0]['fill'], False)

    def test_line_chart_with_custom_title(self):
        """Should include custom title in dataset label."""
        # Arrange
        data = [{'month': 'Jan', 'sales': 100}]

        # Act
        result = to_line_chart_data(data, 'month', 'sales', title='Monthly Sales')

        # Assert
        self.assertEqual(result['datasets'][0]['label'], 'Monthly Sales')

    def test_line_chart_with_string_x_values(self):
        """Should handle string x-axis values."""
        # Arrange
        data = [
            {'quarter': 'Q1', 'revenue': 10000},
            {'quarter': 'Q2', 'revenue': 15000},
        ]

        # Act
        result = to_line_chart_data(data, 'quarter', 'revenue')

        # Assert
        self.assertEqual(result['labels'], ['Q1', 'Q2'])

    def test_line_chart_with_empty_data(self):
        """Should return empty structure for empty data."""
        # Arrange
        data = []

        # Act
        result = to_line_chart_data(data, 'x', 'y')

        # Assert
        self.assertEqual(result['labels'], [])
        self.assertEqual(result['datasets'][0]['data'], [])


class PieChartSerializerTest(TestCase):
    """
    Test suite for to_pie_chart_data serializer.

    Validates conversion to Chart.js pie chart format:
    {
        'labels': [...],
        'datasets': [{
            'data': [...],
            'backgroundColor': [...]
        }]
    }
    """

    def test_basic_pie_chart(self):
        """Should convert data to pie chart format."""
        # Arrange
        data = [
            {'grade': 'SCI', 'count': 30},
            {'grade': 'SCIE', 'count': 20},
            {'grade': 'SCOPUS', 'count': 15},
        ]

        # Act
        result = to_pie_chart_data(data, 'grade', 'count')

        # Assert
        self.assertEqual(result['labels'], ['SCI', 'SCIE', 'SCOPUS'])
        self.assertEqual(result['datasets'][0]['data'], [30, 20, 15])
        self.assertEqual(len(result['datasets'][0]['backgroundColor']), 3)

    def test_pie_chart_with_percentage_values(self):
        """Should handle percentage values correctly."""
        # Arrange
        data = [
            {'category': 'A', 'percentage': 45.5},
            {'category': 'B', 'percentage': 30.2},
            {'category': 'C', 'percentage': 24.3},
        ]

        # Act
        result = to_pie_chart_data(data, 'category', 'percentage')

        # Assert
        self.assertEqual(result['datasets'][0]['data'], [45.5, 30.2, 24.3])

    def test_pie_chart_no_label_in_dataset(self):
        """Pie charts should not have a dataset label."""
        # Arrange
        data = [{'x': 'A', 'y': 10}]

        # Act
        result = to_pie_chart_data(data, 'x', 'y', title='Test')

        # Assert
        # Pie charts typically don't have dataset labels, only segment labels
        self.assertNotIn('label', result['datasets'][0])


class MultiDatasetChartSerializerTest(TestCase):
    """
    Test suite for to_multi_dataset_chart_data serializer.

    Validates conversion to Chart.js format with multiple datasets:
    {
        'labels': [...],
        'datasets': [
            {'label': '...', 'data': [...], 'backgroundColor': '...'},
            {'label': '...', 'data': [...], 'backgroundColor': '...'},
        ]
    }
    """

    def test_multi_dataset_bar_chart(self):
        """Should create multiple datasets from configuration."""
        # Arrange
        data = [
            {'year': 2021, 'domestic': 100, 'international': 50},
            {'year': 2022, 'domestic': 120, 'international': 60},
            {'year': 2023, 'domestic': 140, 'international': 70},
        ]

        datasets_config = [
            {'label': 'Domestic Students', 'field': 'domestic'},
            {'label': 'International Students', 'field': 'international'},
        ]

        # Act
        result = to_multi_dataset_chart_data(data, 'year', datasets_config)

        # Assert
        self.assertEqual(result['labels'], [2021, 2022, 2023])
        self.assertEqual(len(result['datasets']), 2)
        self.assertEqual(result['datasets'][0]['label'], 'Domestic Students')
        self.assertEqual(result['datasets'][0]['data'], [100, 120, 140])
        self.assertEqual(result['datasets'][1]['label'], 'International Students')
        self.assertEqual(result['datasets'][1]['data'], [50, 60, 70])

    def test_multi_dataset_with_different_colors(self):
        """Should assign different colors to each dataset."""
        # Arrange
        data = [{'x': 1, 'y1': 10, 'y2': 20, 'y3': 30}]

        datasets_config = [
            {'label': 'Series 1', 'field': 'y1'},
            {'label': 'Series 2', 'field': 'y2'},
            {'label': 'Series 3', 'field': 'y3'},
        ]

        # Act
        result = to_multi_dataset_chart_data(data, 'x', datasets_config)

        # Assert
        colors = [ds['backgroundColor'] for ds in result['datasets']]
        self.assertEqual(len(set(colors)), 3)  # All different colors

    def test_multi_dataset_with_empty_data(self):
        """Should handle empty data gracefully."""
        # Arrange
        data = []
        datasets_config = [
            {'label': 'Test', 'field': 'value'},
        ]

        # Act
        result = to_multi_dataset_chart_data(data, 'x', datasets_config)

        # Assert
        self.assertEqual(result['labels'], [])
        self.assertEqual(result['datasets'][0]['data'], [])


class DualAxisChartSerializerTest(TestCase):
    """
    Test suite for to_dual_axis_chart_data serializer.

    Validates conversion to Chart.js format with two y-axes:
    {
        'labels': [...],
        'datasets': [
            {'label': '...', 'data': [...], 'yAxisID': 'y1', 'type': 'bar'},
            {'label': '...', 'data': [...], 'yAxisID': 'y2', 'type': 'line'},
        ]
    }
    """

    def test_dual_axis_budget_vs_execution_rate(self):
        """Should create dual-axis chart for budget and execution rate."""
        # Arrange
        data = [
            {'department': '컴퓨터공학과', 'budget': 10000000, 'execution_rate': 85.5},
            {'department': '전자공학과', 'budget': 15000000, 'execution_rate': 92.3},
            {'department': '기계공학과', 'budget': 12000000, 'execution_rate': 78.9},
        ]

        # Act
        result = to_dual_axis_chart_data(
            data,
            x_field='department',
            y1_field='budget',
            y2_field='execution_rate',
            y1_label='Budget (KRW)',
            y2_label='Execution Rate (%)'
        )

        # Assert
        self.assertEqual(result['labels'], ['컴퓨터공학과', '전자공학과', '기계공학과'])
        self.assertEqual(len(result['datasets']), 2)

        # First dataset (bar chart for budget)
        self.assertEqual(result['datasets'][0]['label'], 'Budget (KRW)')
        self.assertEqual(result['datasets'][0]['data'], [10000000, 15000000, 12000000])
        self.assertEqual(result['datasets'][0]['yAxisID'], 'y1')
        self.assertEqual(result['datasets'][0]['type'], 'bar')

        # Second dataset (line chart for execution rate)
        self.assertEqual(result['datasets'][1]['label'], 'Execution Rate (%)')
        self.assertEqual(result['datasets'][1]['data'], [85.5, 92.3, 78.9])
        self.assertEqual(result['datasets'][1]['yAxisID'], 'y2')
        self.assertEqual(result['datasets'][1]['type'], 'line')

    def test_dual_axis_with_decimal_values(self):
        """Should handle Decimal values in dual-axis charts."""
        # Arrange
        data = [
            {'x': 'A', 'value1': Decimal('1000.50'), 'value2': Decimal('75.25')},
        ]

        # Act
        result = to_dual_axis_chart_data(
            data, 'x', 'value1', 'value2', 'Value 1', 'Value 2'
        )

        # Assert
        self.assertEqual(result['datasets'][0]['data'], [1000.50])
        self.assertEqual(result['datasets'][1]['data'], [75.25])

    def test_dual_axis_with_empty_data(self):
        """Should handle empty data gracefully."""
        # Arrange
        data = []

        # Act
        result = to_dual_axis_chart_data(
            data, 'x', 'y1', 'y2', 'Label 1', 'Label 2'
        )

        # Assert
        self.assertEqual(result['labels'], [])
        self.assertEqual(result['datasets'][0]['data'], [])
        self.assertEqual(result['datasets'][1]['data'], [])


class ChartColorsTest(TestCase):
    """
    Test suite for CHART_COLORS constant.

    Validates the color palette used across all charts.
    """

    def test_chart_colors_exist(self):
        """Should have a defined color palette."""
        self.assertIsNotNone(CHART_COLORS)
        self.assertIsInstance(CHART_COLORS, (list, tuple))

    def test_chart_colors_count(self):
        """Should have at least 8 colors for variety."""
        self.assertGreaterEqual(len(CHART_COLORS), 8)

    def test_chart_colors_are_hex(self):
        """All colors should be valid hex codes."""
        for color in CHART_COLORS:
            self.assertRegex(color, r'^#[0-9a-fA-F]{6}$')

    def test_chart_colors_are_unique(self):
        """All colors should be unique."""
        self.assertEqual(len(CHART_COLORS), len(set(CHART_COLORS)))
