#!/usr/bin/env python3
"""
Process all four vCard databases through the complete validation workflow
Creates validated versions and generates a comprehensive report
"""

import os
import json
import shutil
from datetime import datetime
from vcard_workflow import VCardWorkflow
from vcard_validator import VCardStandardsValidator
import vobject

def get_vcard_count(filepath):
    """Get the number of vCards in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        return len(vcards)
    except:
        return 0

def process_all_databases():
    """Process all vCard databases with full workflow"""
    
    print("ContactPlus - Processing All vCard Databases")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Define all databases to process
    databases = [
        {
            'name': 'Sara',
            'file': 'Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf',
            'description': 'Sara A. Kerner and 3,074 others'
        },
        {
            'name': 'Edgar',
            'file': 'Imports/Edgar_Export_Edgar A and 24.836 others.vcf',
            'description': 'Edgar A and 24,836 others'
        },
        {
            'name': 'iPhone_Contacts',
            'file': 'Imports/iPhone_Contacts_Contacts.vcf',
            'description': 'iPhone Contacts'
        },
        {
            'name': 'iPhone_Suggested',
            'file': 'Imports/iPhone_Suggested_Suggested Contacts.vcf',
            'description': 'iPhone Suggested Contacts'
        }
    ]
    
    # Create workflow instance
    workflow = VCardWorkflow(
        auto_fix=True,
        backup=True,
        soft_compliance=True
    )
    
    # Process results
    results = {}
    date_str = datetime.now().strftime('%Y%m%d')
    
    # Create master backup directory
    master_backup_dir = f"backup/all_databases_backup_{date_str}"
    os.makedirs(master_backup_dir, exist_ok=True)
    
    print(f"\n1. Creating backups in: {master_backup_dir}")
    print("-" * 60)
    
    # First, create backups of all files
    for db in databases:
        src_path = db['file']
        if os.path.exists(src_path):
            backup_name = f"{db['name']}_BACKUP_{date_str}.vcf"
            backup_path = os.path.join(master_backup_dir, backup_name)
            shutil.copy2(src_path, backup_path)
            print(f"   ✓ Backed up {db['name']}: {backup_name}")
        else:
            print(f"   ✗ File not found: {src_path}")
    
    print(f"\n2. Processing databases:")
    print("-" * 60)
    
    # Process each database
    for i, db in enumerate(databases, 1):
        print(f"\n[{i}/4] Processing {db['name']} ({db['description']})...")
        
        if not os.path.exists(db['file']):
            print(f"   ⚠️  File not found: {db['file']}")
            results[db['name']] = {'status': 'not_found'}
            continue
        
        try:
            # Get initial count
            initial_count = get_vcard_count(db['file'])
            
            # Process the file
            result = workflow.process_file(db['file'])
            
            # Define output path
            output_filename = f"{db['name']}_VALIDATED_{date_str}.vcf"
            output_path = os.path.join('data', output_filename)
            
            # Copy processed file to output location
            if result.get('working_file') and os.path.exists(result['working_file']):
                shutil.copy2(result['working_file'], output_path)
                
                # Store results
                results[db['name']] = {
                    'status': 'success',
                    'input_file': db['file'],
                    'output_file': output_path,
                    'initial_count': initial_count,
                    'final_count': result['vcards_parsed'],
                    'initial_errors': result['initial_validation']['error_count'],
                    'final_errors': result.get('post_soft_validation', {}).get('error_count', 0),
                    'hard_fixes': result.get('fix_report', {}).get('fixes_applied', {}),
                    'soft_fixes': result.get('soft_compliance_report', {}).get('fixes_applied', {}),
                    'file_size': {
                        'original': os.path.getsize(db['file']) / 1024 / 1024,
                        'processed': os.path.getsize(output_path) / 1024 / 1024
                    }
                }
                
                print(f"   ✓ Success: {initial_count} → {result['vcards_parsed']} contacts")
                print(f"   ✓ Fixed {result['initial_validation']['error_count']} errors")
                print(f"   ✓ Output: {output_path}")
            else:
                results[db['name']] = {'status': 'processing_failed'}
                print(f"   ✗ Processing failed")
                
        except Exception as e:
            results[db['name']] = {'status': 'error', 'error': str(e)}
            print(f"   ✗ Error: {str(e)}")
    
    # Generate comprehensive report
    print(f"\n3. Generating comprehensive report...")
    print("=" * 80)
    
    report = {
        'processing_date': datetime.now().isoformat(),
        'databases_processed': len([r for r in results.values() if r.get('status') == 'success']),
        'total_contacts_processed': sum(r.get('final_count', 0) for r in results.values()),
        'total_errors_fixed': sum(r.get('initial_errors', 0) for r in results.values()),
        'individual_results': results
    }
    
    # Save report
    report_path = f"data/all_databases_report_{date_str}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\nPROCESSING SUMMARY")
    print("=" * 80)
    
    total_contacts = 0
    total_errors_fixed = 0
    total_soft_fixes = 0
    
    for name, result in results.items():
        if result.get('status') == 'success':
            print(f"\n{name}:")
            print(f"  Contacts: {result['initial_count']} → {result['final_count']}")
            print(f"  RFC errors fixed: {result['initial_errors']}")
            
            # Count soft fixes
            soft_fixes = result.get('soft_fixes', {})
            soft_fix_count = sum(v for k, v in soft_fixes.items() if k != 'total_improved')
            print(f"  Data improvements: {soft_fix_count}")
            print(f"  File size: {result['file_size']['original']:.2f} MB → {result['file_size']['processed']:.2f} MB")
            print(f"  ✓ Output: {result['output_file']}")
            
            total_contacts += result['final_count']
            total_errors_fixed += result['initial_errors']
            total_soft_fixes += soft_fix_count
        else:
            print(f"\n{name}: ❌ {result.get('status', 'unknown')}")
    
    print("\n" + "=" * 80)
    print("GRAND TOTAL")
    print("=" * 80)
    print(f"✅ Databases processed: {report['databases_processed']}/4")
    print(f"✅ Total contacts: {total_contacts:,}")
    print(f"✅ RFC errors fixed: {total_errors_fixed}")
    print(f"✅ Data improvements: {total_soft_fixes:,}")
    print(f"\n📁 All validated files saved to: data/")
    print(f"📊 Detailed report: {report_path}")
    print(f"💾 Backups saved to: {master_backup_dir}/")
    
    return report


if __name__ == "__main__":
    report = process_all_databases()