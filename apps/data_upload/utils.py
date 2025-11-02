"""
Data Upload Utilities

Smart file type identification based on column headers
"""
import pandas as pd
import os
from apps.data_upload.parsers import (
    DepartmentKPIParser,
    PublicationParser,
    ResearchBudgetParser,
    StudentParser
)


# Define required headers for each file type
# Matching rate threshold: 80% of required headers must be present
FILE_TYPE_SIGNATURES = {
    'department_kpi': (
        ['평가년도', '단과대학', '학과', '졸업생 취업률 (%)'],
        DepartmentKPIParser
    ),
    'publication': (
        ['논문ID', '게재일', '논문제목', '주저자'],
        PublicationParser
    ),
    'research_budget': (
        ['집행ID', '과제번호', '과제명', '총연구비', '집행금액'],
        ResearchBudgetParser
    ),
    'student': (
        ['학번', '이름', '단과대학', '학과', '학적상태'],
        StudentParser
    ),
}


def identify_file_type(file_path: str):
    """
    Identify file type by analyzing column headers.

    Strategy:
    1. Read only the headers (first row) of the file
    2. Compare headers against known signatures
    3. Return parser class for best match (>= 80% match rate)
    4. Return None if no good match found

    Args:
        file_path: Path to Excel or CSV file

    Returns:
        Parser class (e.g., DepartmentKPIParser) or None
    """
    try:
        # Determine file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # Read only headers (no data rows)
        if ext == '.csv':
            df_header = pd.read_csv(file_path, nrows=0, encoding='utf-8-sig')
        elif ext in ['.xlsx', '.xls']:
            engine = 'openpyxl' if ext == '.xlsx' else 'xlrd'
            df_header = pd.read_excel(file_path, nrows=0, engine=engine)
        else:
            return None

        # Get set of column names from file
        file_headers = set(df_header.columns)

        # Find best match
        best_match = None
        best_score = 0
        best_threshold = 0

        for file_type, (required_headers, parser_class) in FILE_TYPE_SIGNATURES.items():
            # Calculate how many required headers are present
            required_set = set(required_headers)
            matches = len(file_headers.intersection(required_set))
            total_required = len(required_set)

            # Calculate match rate
            match_rate = matches / total_required if total_required > 0 else 0

            # Update best match if this is better
            if match_rate > best_score:
                best_score = match_rate
                best_match = parser_class
                best_threshold = 0.8  # 80% threshold

        # Return parser class if match rate is above threshold
        if best_score >= best_threshold:
            return best_match
        else:
            return None

    except Exception as e:
        # Log error if needed
        print(f"Error identifying file type: {e}")
        return None
