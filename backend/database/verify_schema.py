from typing import Dict, List, Any, Optional
from sqlalchemy import inspect, create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

# Import your database config
from database.config import engine, Base

# Expected schema definition
expected_schema = {
    'test_runs': [
        {'name': 'id', 'type': UUID, 'primary_key': True, 'nullable': False},
        {'name': 'created_at', 'type': DateTime, 'nullable': False},
        {'name': 'project_id', 'type': UUID, 'nullable': False},
        {'name': 'status', 'type': String(50), 'nullable': False},
        {'name': 'test_results', 'type': JSONB, 'nullable': True},
    ],
    'test_requests': [
        {'name': 'id', 'type': UUID, 'primary_key': True, 'nullable': False},
        {'name': 'project_id', 'type': UUID, 'nullable': False},
        {'name': 'user_input', 'type': Text, 'nullable': False},
        {'name': 'generated_tests', 'type': JSONB, 'nullable': True},
        {'name': 'status', 'type': String(50), 'nullable': False},
        {'name': 'created_by', 'type': UUID, 'nullable': False},
        {'name': 'created_at', 'type': DateTime, 'nullable': False},
    ],
    'performance_metrics': [
        {'name': 'id', 'type': UUID, 'primary_key': True, 'nullable': False},
        {'name': 'test_run_id', 'type': UUID, 'nullable': False, 'foreign_key': 'test_runs.id'},
        {'name': 'metric_name', 'type': String(100), 'nullable': False},
        {'name': 'metric_value', 'type': JSONB, 'nullable': False},
        {'name': 'created_at', 'type': DateTime, 'nullable': False},
    ]
}

def get_actual_schema() -> Dict[str, List[Dict[str, Any]]:
    """Get the actual database schema."""
    inspector = inspect(engine)
    schema = {}
    
    for table_name in inspector.get_table_names():
        columns = []
        for column in inspector.get_columns(table_name):
            col_info = {
                'name': column['name'],
                'type': type(column['type']),
                'nullable': column['nullable'],
                'default': column.get('default'),
                'primary_key': column.get('primary_key', False)
            }
            
            # Check for foreign keys
            fk_info = next(
                (fk for fk in inspector.get_foreign_keys(table_name) 
                 if fk['constrained_columns'] == [column['name']]),
                None
            )
            if fk_info:
                col_info['foreign_key'] = f"{fk_info['referred_table']}.{fk_info['referred_columns'][0]}"
                
            columns.append(col_info)
        schema[table_name] = columns
    
    return schema

def verify_schema() -> Dict[str, Any]:
    """Verify the actual schema against the expected schema."""
    actual_schema = get_actual_schema()
    results = {
        'status': 'success',
        'tables': {},
        'missing_tables': [],
        'extra_tables': [],
        'mismatched_tables': []
    }
    
    # Check for missing tables
    for table_name in expected_schema.keys():
        if table_name not in actual_schema:
            results['missing_tables'].append(table_name)
            results['status'] = 'error'
    
    # Check for extra tables
    for table_name in actual_schema.keys():
        if table_name not in expected_schema:
            results['extra_tables'].append(table_name)
    
    # Check table structures
    for table_name, expected_columns in expected_schema.items():
        if table_name not in actual_schema:
            continue
            
        actual_columns = actual_schema[table_name]
        table_results = {
            'status': 'success',
            'missing_columns': [],
            'extra_columns': [],
            'mismatched_columns': []
        }
        
        # Check for missing columns
        expected_column_names = {col['name']: col for col in expected_columns}
        actual_column_names = {col['name']: col for col in actual_columns}
        
        for col_name, expected_col in expected_column_names.items():
            if col_name not in actual_column_names:
                table_results['missing_columns'].append(col_name)
                table_results['status'] = 'error'
                continue
                
            # Check column properties
            actual_col = actual_column_names[col_name]
            if not isinstance(actual_col['type'], expected_col['type']):
                table_results['mismatched_columns'].append({
                    'column': col_name,
                    'expected': expected_col['type'].__name__,
                    'actual': actual_col['type'].__name__
                })
                table_results['status'] = 'warning'
                
            if 'foreign_key' in expected_col and 'foreign_key' not in actual_col:
                table_results['mismatched_columns'].append({
                    'column': col_name,
                    'issue': 'missing_foreign_key',
                    'expected': expected_col['foreign_key']
                })
                table_results['status'] = 'warning'
        
        # Check for extra columns
        for col_name in actual_column_names:
            if col_name not in expected_column_names:
                table_results['extra_columns'].append(col_name)
        
        if table_results['status'] != 'success':
            results['mismatched_tables'].append(table_name)
            if results['status'] != 'error':
                results['status'] = 'warning'
        
        results['tables'][table_name] = table_results
    
    return results

def print_verification_results(results: Dict[str, Any]) -> None:
    """Print the schema verification results in a readable format."""
    print("\n" + "="*80)
    print("DATABASE SCHEMA VERIFICATION")
    print("="*80)
    
    # Print overall status
    status_color = "\033[92m" if results['status'] == 'success' else "\033[93m"
    if results['status'] == 'error':
        status_color = "\033[91m"
    print(f"\nOverall Status: {status_color}{results['status'].upper()}\033[0m")
    
    # Print missing tables
    if results['missing_tables']:
        print("\n\033[91mMISSING TABLES:\033[0m")
        for table in results['missing_tables']:
            print(f"  - {table}")
    
    # Print extra tables
    if results['extra_tables']:
        print("\n\033[93mEXTRA TABLES (not in expected schema):\033[0m")
        for table in results['extra_tables']:
            print(f"  - {table}")
    
    # Print table details
    for table_name, table_info in results['tables'].items():
        status_color = "\033[92m" if table_info['status'] == 'success' else "\033[93m"
        if table_info['status'] == 'error':
            status_color = "\033[91m"
            
        print(f"\nTable: {table_name} - {status_color}{table_info['status'].upper()}\033[0m")
        
        # Print missing columns
        if table_info['missing_columns']:
            print("  \033[91mMissing columns:\033[0m")
            for col in table_info['missing_columns']:
                print(f"    - {col}")
        
        # Print extra columns
        if table_info['extra_columns']:
            print("  \033[93mExtra columns (not in expected schema):\033[0m")
            for col in table_info['extra_columns']:
                print(f"    - {col}")
        
        # Print mismatched columns
        if table_info['mismatched_columns']:
            print("  \033[93mMismatched columns:\033[0m")
            for col in table_info['mismatched_columns']:
                if 'issue' in col and col['issue'] == 'missing_foreign_key':
                    print(f"    - {col['column']}: Missing foreign key (expected: {col['expected']})")
                else:
                    print(f"    - {col['column']}: Expected {col['expected']}, got {col['actual']}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print("Verifying database schema...")
    results = verify_schema()
    print_verification_results(results)
