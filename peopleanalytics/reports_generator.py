import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from .data_model import PersonData

def generate_report(report_type: str, data: Union[List[PersonData], Dict[str, Any]], output_dir: str = "output/reports") -> str:
    """
    Generate a report based on the specified type.
    
    Args:
        report_type: Type of report to generate ('attendance', 'payment', etc.)
        data: Data to include in the report
        output_dir: Directory to save the report
        
    Returns:
        Path to the generated report file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if report_type.lower() == 'attendance':
        if not isinstance(data, list):
            raise ValueError("Attendance report requires a list of PersonData objects")
        return generate_attendance_report(data, output_dir)
    
    elif report_type.lower() == 'payment':
        if not isinstance(data, list):
            raise ValueError("Payment report requires a list of PersonData objects")
        return generate_payment_report(data, output_dir)
    
    elif report_type.lower() == 'custom':
        if not isinstance(data, dict):
            raise ValueError("Custom report requires a dictionary with report parameters")
        return generate_custom_report(data, output_dir)
    
    else:
        raise ValueError(f"Unknown report type: {report_type}")

def generate_custom_report(data: Dict[str, Any], output_dir: str) -> str:
    """Generate a custom report based on provided data dictionary."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = data.get('report_name', 'custom')
    
    # Save the data as JSON
    json_path = os.path.join(output_dir, f"{report_name}_{timestamp}.json")
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Generated custom report: {json_path}")
    return json_path

def generate_attendance_report(data_list: List[PersonData], output_dir: str) -> str:
    """Generate attendance report for the given data list."""
    
    # Prepare data for the report
    report_data = []
    
    for person_data in data_list:
        for record in person_data.attendance_records:
            entry = {
                'Person': person_data.name,
                'Year': person_data.year,
                'Date': record.date,
                'Status': record.status,
                'Hours': record.hours,
                'Notes': record.notes
            }
            
            # Add profile information if available
            if person_data.profile:
                entry['Department'] = person_data.profile.department
                entry['Position'] = person_data.profile.position
                entry['Manager'] = person_data.profile.manager
            else:
                entry['Department'] = ''
                entry['Position'] = ''
                entry['Manager'] = ''
                
            report_data.append(entry)
    
    if not report_data:
        print("No attendance data available for report.")
        return ""
    
    # Create DataFrame
    df = pd.DataFrame(report_data)
    
    # Calculate statistics
    stats = {
        'total_days': len(df),
        'present_days': len(df[df['Status'] == 'present']),
        'absent_days': len(df[df['Status'] == 'absent']),
        'late_days': len(df[df['Status'] == 'late']),
        'total_hours': df['Hours'].sum()
    }
    
    # Generate report files
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw data as CSV
    csv_path = os.path.join(output_dir, f"attendance_report_{timestamp}.csv")
    df.to_csv(csv_path, index=False)
    
    # Save statistics as JSON
    stats_path = os.path.join(output_dir, f"attendance_stats_{timestamp}.json")
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Generate visualization
    plt.figure(figsize=(10, 6))
    status_counts = df['Status'].value_counts()
    status_counts.plot(kind='bar', color=['green', 'red', 'orange'])
    plt.title('Attendance Status Distribution')
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.tight_layout()
    
    plot_path = os.path.join(output_dir, f"attendance_plot_{timestamp}.png")
    plt.savefig(plot_path)
    plt.close()
    
    # If profile information is available, generate a department-wise report
    if 'Department' in df.columns and not df['Department'].isna().all():
        dept_stats = df.groupby('Department')['Status'].value_counts().unstack().fillna(0)
        plt.figure(figsize=(12, 8))
        dept_stats.plot(kind='bar', stacked=True)
        plt.title('Attendance by Department')
        plt.xlabel('Department')
        plt.ylabel('Count')
        plt.tight_layout()
        
        dept_plot_path = os.path.join(output_dir, f"attendance_by_dept_{timestamp}.png")
        plt.savefig(dept_plot_path)
        plt.close()
    
    print(f"Generated attendance report with {len(df)} records.")
    return csv_path

def generate_payment_report(data_list: List[PersonData], output_dir: str) -> str:
    """Generate payment report for the given data list."""
    
    # Prepare data for the report
    report_data = []
    
    for person_data in data_list:
        for record in person_data.payment_records:
            entry = {
                'Person': person_data.name,
                'Year': person_data.year,
                'Date': record.date,
                'Amount': record.amount,
                'Type': record.type,
                'Notes': record.notes
            }
            
            # Add profile information if available
            if person_data.profile:
                entry['Department'] = person_data.profile.department
                entry['Position'] = person_data.profile.position
                entry['Manager'] = person_data.profile.manager
            else:
                entry['Department'] = ''
                entry['Position'] = ''
                entry['Manager'] = ''
                
            report_data.append(entry)
    
    if not report_data:
        print("No payment data available for report.")
        return ""
    
    # Create DataFrame
    df = pd.DataFrame(report_data)
    
    # Calculate statistics
    stats = {
        'total_payments': len(df),
        'total_amount': df['Amount'].sum(),
        'average_amount': df['Amount'].mean(),
        'max_amount': df['Amount'].max(),
        'min_amount': df['Amount'].min(),
        'payment_types': df['Type'].value_counts().to_dict()
    }
    
    # Generate report files
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw data as CSV
    csv_path = os.path.join(output_dir, f"payment_report_{timestamp}.csv")
    df.to_csv(csv_path, index=False)
    
    # Save statistics as JSON
    stats_path = os.path.join(output_dir, f"payment_stats_{timestamp}.json")
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Generate visualization
    plt.figure(figsize=(10, 6))
    type_amounts = df.groupby('Type')['Amount'].sum()
    type_amounts.plot(kind='bar', color=['blue', 'green', 'orange'])
    plt.title('Payment Amounts by Type')
    plt.xlabel('Payment Type')
    plt.ylabel('Total Amount')
    plt.tight_layout()
    
    plot_path = os.path.join(output_dir, f"payment_plot_{timestamp}.png")
    plt.savefig(plot_path)
    plt.close()
    
    # If profile information is available, generate a department-wise report
    if 'Department' in df.columns and not df['Department'].isna().all():
        dept_amounts = df.groupby('Department')['Amount'].sum().sort_values(ascending=False)
        plt.figure(figsize=(12, 8))
        dept_amounts.plot(kind='bar')
        plt.title('Total Payments by Department')
        plt.xlabel('Department')
        plt.ylabel('Total Amount')
        plt.tight_layout()
        
        dept_plot_path = os.path.join(output_dir, f"payment_by_dept_{timestamp}.png")
        plt.savefig(dept_plot_path)
        plt.close()
    
    print(f"Generated payment report with {len(df)} records.")
    return csv_path 