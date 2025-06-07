#!/usr/bin/env python3
"""
Process Edgar's large vCard database
"""

import os
import time
from datetime import datetime
from vcard_workflow import VCardWorkflow

def process_edgar():
    """Process Edgar's database with progress reporting"""
    
    print("Processing Edgar's vCard Database")
    print("=" * 60)
    
    edgar_file = 'Imports/Edgar_Export_Edgar A and 24.836 others.vcf'
    
    if not os.path.exists(edgar_file):
        print(f"Error: File not found - {edgar_file}")
        return
    
    # Show file info
    file_size = os.path.getsize(edgar_file) / 1024 / 1024
    print(f"File: {edgar_file}")
    print(f"Size: {file_size:.2f} MB")
    print(f"Expected contacts: ~24,836")
    print("\nThis will take several minutes due to the large file size...")
    print("-" * 60)
    
    # Create workflow
    workflow = VCardWorkflow(
        auto_fix=True,
        backup=True,
        soft_compliance=True
    )
    
    start_time = time.time()
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        print("\nStarting processing...")
        result = workflow.process_file(edgar_file)
        
        # Save output
        output_filename = f"Edgar_VALIDATED_{date_str}.vcf"
        output_path = os.path.join('data', output_filename)
        
        if result.get('working_file') and os.path.exists(result['working_file']):
            import shutil
            shutil.copy2(result['working_file'], output_path)
            
            elapsed_time = time.time() - start_time
            
            print("\n" + "=" * 60)
            print("PROCESSING COMPLETE")
            print("=" * 60)
            print(f"Time taken: {elapsed_time/60:.1f} minutes")
            print(f"Contacts processed: {result['vcards_parsed']:,}")
            print(f"Initial errors: {result['initial_validation']['error_count']}")
            print(f"Final errors: {result.get('post_soft_validation', {}).get('error_count', 0)}")
            
            # Show fixes
            if result.get('fix_report'):
                print("\nHard fixes applied:")
                for fix, count in result['fix_report']['fixes_applied'].items():
                    if count > 0:
                        print(f"  - {fix}: {count}")
            
            if result.get('soft_compliance_report'):
                print("\nSoft fixes applied:")
                for fix, count in result['soft_compliance_report']['fixes_applied'].items():
                    if count > 0 and fix != 'total_improved':
                        print(f"  - {fix}: {count}")
            
            print(f"\n✅ Output saved to: {output_path}")
            print(f"✅ File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
            
            return output_path
            
    except Exception as e:
        print(f"\n❌ Error processing Edgar's database: {str(e)}")
        return None

if __name__ == "__main__":
    output = process_edgar()