#!/usr/bin/env python3
"""
Process the iPhone vCard databases (smaller files for quicker processing)
"""

import os
import json
import shutil
from datetime import datetime
from vcard_workflow import VCardWorkflow
import vobject

def get_vcard_stats(filepath):
    """Get basic stats about a vCard file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        vcards = list(vobject.readComponents(content))
        return {
            'count': len(vcards),
            'size_mb': os.path.getsize(filepath) / 1024 / 1024
        }
    except Exception as e:
        return {'count': 0, 'size_mb': 0, 'error': str(e)}

def process_iphone_databases():
    """Process iPhone databases only"""
    
    print("Processing iPhone vCard Databases")
    print("=" * 60)
    
    databases = [
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
    
    workflow = VCardWorkflow(
        auto_fix=True,
        backup=True,
        soft_compliance=True
    )
    
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    results = {}
    
    for db in databases:
        print(f"\nProcessing {db['name']}...")
        print("-" * 40)
        
        if not os.path.exists(db['file']):
            print(f"File not found: {db['file']}")
            continue
        
        # Get initial stats
        initial_stats = get_vcard_stats(db['file'])
        print(f"Initial: {initial_stats['count']} contacts, {initial_stats['size_mb']:.2f} MB")
        
        try:
            # Process
            result = workflow.process_file(db['file'])
            
            # Save output
            output_filename = f"{db['name']}_VALIDATED_{date_str}.vcf"
            output_path = os.path.join('data', output_filename)
            
            if result.get('working_file'):
                shutil.copy2(result['working_file'], output_path)
                
                # Get final stats
                final_stats = get_vcard_stats(output_path)
                
                print(f"Result:")
                print(f"  Initial errors: {result['initial_validation']['error_count']}")
                print(f"  Final errors: {result.get('post_soft_validation', {}).get('error_count', 0)}")
                print(f"  Contacts: {final_stats['count']}")
                print(f"  Output: {output_path}")
                
                # Store results
                results[db['name']] = {
                    'success': True,
                    'initial_contacts': initial_stats['count'],
                    'final_contacts': final_stats['count'],
                    'initial_errors': result['initial_validation']['error_count'],
                    'output_file': output_path,
                    'fixes': {
                        'hard': result.get('fix_report', {}).get('fixes_applied', {}),
                        'soft': result.get('soft_compliance_report', {}).get('fixes_applied', {})
                    }
                }
                
        except Exception as e:
            print(f"Error: {str(e)}")
            results[db['name']] = {'success': False, 'error': str(e)}
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, result in results.items():
        if result.get('success'):
            print(f"\n{name}: ✅ SUCCESS")
            print(f"  Contacts: {result['initial_contacts']} → {result['final_contacts']}")
            print(f"  Errors fixed: {result['initial_errors']}")
            print(f"  Output: {result['output_file']}")
        else:
            print(f"\n{name}: ❌ FAILED - {result.get('error', 'Unknown error')}")
    
    # Save summary
    summary_path = f"data/iphone_processing_summary_{date_str}.json"
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSummary saved to: {summary_path}")
    
    return results

if __name__ == "__main__":
    results = process_iphone_databases()