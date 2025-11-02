"""
Migration to create users table for testing.
This migration only runs in test database.
"""
from django.db import migrations


def create_users_table(apps, schema_editor):
    """Create users table for testing"""
    if schema_editor.connection.settings_dict.get('NAME', '').startswith('file:memorydb'):
        # Only create table for test database
        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                department VARCHAR(100),
                position VARCHAR(100),
                role VARCHAR(20) DEFAULT 'viewer',
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)


def drop_users_table(apps, schema_editor):
    """Drop users table"""
    if schema_editor.connection.settings_dict.get('NAME', '').startswith('file:memorydb'):
        schema_editor.execute("DROP TABLE IF EXISTS users")


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_users_table, drop_users_table),
    ]