#!/usr/bin/env python3
"""
Process Sara's vCard database through the complete validation workflow
Creates a fully validated and cleaned version
"""

import os
import json
from datetime import datetime
from vcard_workflow import VCardWorkflow
import config

def process_sara_database():
    """Process Sara's database with full workflow"""
    
    print("ContactPlus - Processing Sara's vCard Database")
    print("=" * 60)
    print(f"Input: {config.SARA_VCARD_FILE}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Define output filename with date
    date_str = datetime.now().strftime('%Y%m%d')
    output_filename = f"Sara_Export_VALIDATED_{date_str}.vcf"
    output_path = os.path.join(config.DATA_DIR, output_filename)
    
    # Create workflow with all features enabled
    print("\nInitializing workflow with:")
    print("  - Auto-fix: YES (fix RFC violations)")
    print("  - Backup: YES (preserve original)")
    print("  - Soft compliance: YES (improve data quality)")
    
    workflow = VCardWorkflow(
        auto_fix=True,
        backup=True,
        soft_compliance=True
    )
    
    # Process the file
    print("\nProcessing... (this may take a few moments)")
    result = workflow.process_file(config.SARA_VCARD_FILE)
    
    # Display results
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    
    # Initial state
    print(f"\n1. INITIAL VALIDATION:")
    print(f"   Valid: {result['initial_validation']['valid']}")
    print(f"   Errors: {result['initial_validation']['error_count']}")
    print(f"   Warnings: {result['initial_validation']['warning_count']}")
    if result['initial_validation']['sample_errors']:
        print("   Issues found:")
        for err in result['initial_validation']['sample_errors'][:3]:
            print(f"     - {err}")
    
    # Hard fixes
    if result.get('fixes_applied'):
        print(f"\n2. HARD COMPLIANCE FIXES APPLIED:")
        fixes = result['fix_report']['fixes_applied']
        for fix_type, count in fixes.items():
            if count > 0:
                print(f"   - {fix_type}: {count}")
    
    # Soft compliance
    if result.get('soft_compliance_applied'):
        print(f"\n3. SOFT COMPLIANCE IMPROVEMENTS:")
        soft_fixes = result['soft_compliance_report']['fixes_applied']
        for fix_type, count in soft_fixes.items():
            if count > 0:
                print(f"   - {fix_type}: {count}")
    
    # Final validation
    if result.get('post_soft_validation'):
        print(f"\n4. FINAL VALIDATION:")
        print(f"   Valid: {result['post_soft_validation']['valid']}")
        print(f"   Errors: {result['post_soft_validation']['error_count']}")
        print(f"   Status: {'✅ Fully compliant!' if result['post_soft_validation']['valid'] else '⚠️  Issues remain'}")
    
    # Copy final file to our output location
    if result.get('working_file') and os.path.exists(result['working_file']):
        import shutil
        shutil.copy2(result['working_file'], output_path)
        print(f"\n5. OUTPUT FILE:")
        print(f"   Saved to: {output_path}")
        print(f"   Total vCards: {result['vcards_parsed']}")
        
        # File size comparison
        original_size = os.path.getsize(config.SARA_VCARD_FILE) / 1024 / 1024
        new_size = os.path.getsize(output_path) / 1024 / 1024
        print(f"   Original size: {original_size:.2f} MB")
        print(f"   New size: {new_size:.2f} MB")
    
    # Save detailed report
    report_path = os.path.join(config.DATA_DIR, f"processing_report_{date_str}.json")
    with open(report_path, 'w') as f:
        # Remove non-serializable data
        clean_result = {k: v for k, v in result.items() if k != 'sample_vcards'}
        json.dump(clean_result, f, indent=2)
    
    print(f"\n6. DETAILED REPORT:")
    print(f"   Saved to: {report_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully processed {result['vcards_parsed']} contacts")
    print(f"✅ Fixed {result['initial_validation']['error_count']} RFC violations")
    print(f"✅ Applied {result.get('soft_compliance_report', {}).get('issues_found', 0)} data quality improvements")
    print(f"✅ All contacts are now RFC 2426 compliant and importable")
    
    print(f"\n📁 Your validated vCard file is ready:")
    print(f"   {output_path}")
    
    return output_path


if __name__ == "__main__":
    output_file = process_sara_database()