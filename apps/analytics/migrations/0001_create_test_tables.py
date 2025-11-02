"""
Migration to create analytics tables for testing.
This migration only runs in test database.
"""
from django.db import migrations


def create_analytics_tables(apps, schema_editor):
    """Create analytics tables for testing"""
    if schema_editor.connection.settings_dict.get('NAME', '').startswith('file:memorydb'):
        # Only create tables for test database

        # Department KPI table
        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS department_kpi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_year INTEGER,
                college VARCHAR(100),
                department VARCHAR(100),
                employment_rate DECIMAL(5, 2),
                research_performance DECIMAL(5, 2),
                student_faculty_ratio DECIMAL(5, 2),
                full_time_faculty INTEGER,
                visiting_faculty INTEGER,
                tech_transfer_income DECIMAL(15, 2),
                intl_conference_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Publications table
        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS publications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                publication_id VARCHAR(50),
                publication_date DATE,
                college VARCHAR(100),
                department VARCHAR(100),
                title TEXT,
                first_author VARCHAR(100),
                co_authors TEXT,
                journal_name VARCHAR(300),
                journal_grade VARCHAR(10),
                impact_factor DECIMAL(5, 2),
                project_linked VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Research Projects table
        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS research_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_number VARCHAR(50),
                project_name VARCHAR(300),
                principal_investigator VARCHAR(100),
                department VARCHAR(100),
                funding_agency VARCHAR(100),
                total_budget BIGINT,
                start_date DATE,
                end_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Execution Records table
        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS execution_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id VARCHAR(50),
                project_id INTEGER,
                execution_date DATE,
                expense_category VARCHAR(100),
                amount BIGINT,
                status VARCHAR(20),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES research_projects (id)
            )
        """)

        # Students table
        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_number VARCHAR(20) UNIQUE,
                name VARCHAR(100),
                college VARCHAR(100),
                department VARCHAR(100),
                grade INTEGER,
                program_type VARCHAR(20),
                enrollment_status VARCHAR(20),
                gender VARCHAR(10),
                nationality VARCHAR(50),
                admission_year INTEGER,
                graduation_year INTEGER,
                graduation_status VARCHAR(20),
                advisor VARCHAR(100),
                email VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Upload History table
        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS upload_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name VARCHAR(255),
                file_type VARCHAR(50),
                uploaded_by_id INTEGER,
                upload_status VARCHAR(20),
                rows_processed INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by_id) REFERENCES users (id)
            )
        """)


def drop_analytics_tables(apps, schema_editor):
    """Drop analytics tables"""
    if schema_editor.connection.settings_dict.get('NAME', '').startswith('file:memorydb'):
        tables = [
            'execution_records',  # Drop first due to foreign key
            'research_projects',
            'department_kpi',
            'publications',
            'students',
            'upload_history'
        ]
        for table in tables:
            schema_editor.execute(f"DROP TABLE IF EXISTS {table}")


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunPython(create_analytics_tables, drop_analytics_tables),
    ]