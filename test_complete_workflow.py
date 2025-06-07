#!/usr/bin/env python3
"""
Test the complete vCard processing workflow:
1. Hard compliance validation
2. Fix RFC violations
3. Soft compliance improvements
4. Final processing
"""

from vcard_workflow import VCardWorkflow
import json


def test_complete_workflow():
    """Test the full workflow on a sample file"""
    
    print("Complete vCard Processing Workflow Test")
    print("=" * 60)
    print("Steps: Validate → Fix → Soft Compliance → Process")
    print("=" * 60)
    
    # Use sample file for testing
    test_file = "sample_10_vcards.vcf"
    
    # Create workflow with all features enabled
    workflow = VCardWorkflow(
        auto_fix=True,         # Fix RFC violations
        backup=True,           # Create backup
        soft_compliance=True   # Apply soft rules
    )
    
    # Process the file
    print("\nProcessing vCard file...")
    result = workflow.process_file(test_file)
    
    # Display results
    print("\n" + "-" * 60)
    print("WORKFLOW RESULTS")
    print("-" * 60)
    
    # Initial state
    print(f"\n1. INITIAL VALIDATION:")
    print(f"   Valid: {result['initial_validation']['valid']}")
    print(f"   Errors: {result['initial_validation']['error_count']}")
    print(f"   Warnings: {result['initial_validation']['warning_count']}")
    
    # Hard compliance fixes
    if result.get('fixes_applied'):
        print(f"\n2. HARD COMPLIANCE FIXES:")
        fix_report = result['fix_report']
        print(f"   Fixed errors: {fix_report['improvement']['errors_fixed']}")
        for fix, count in fix_report['fixes_applied'].items():
            if count > 0:
                print(f"   - {fix}: {count}")
    
    # Soft compliance
    if result.get('soft_compliance_applied'):
        print(f"\n3. SOFT COMPLIANCE IMPROVEMENTS:")
        soft_report = result['soft_compliance_report']
        print(f"   Issues found: {soft_report['issues_found']}")
        for fix, count in soft_report['fixes_applied'].items():
            if count > 0:
                print(f"   - {fix}: {count}")
    
    # Final state
    print(f"\n4. FINAL STATE:")
    print(f"   Valid: {result['final_valid']}")
    print(f"   vCards parsed: {result['vcards_parsed']}")
    print(f"   Working file: {result.get('working_file', 'N/A')}")
    
    # Save detailed report
    report_file = 'complete_workflow_report.json'
    with open(report_file, 'w') as f:
        # Remove non-serializable data
        clean_result = {k: v for k, v in result.items() if k != 'sample_vcards'}
        json.dump(clean_result, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    # Show sample of processed vCards
    if result.get('sample_vcards'):
        print(f"\nSample processed vCards:")
        for i, sample in enumerate(result['sample_vcards'][:3]):
            if sample.get('fn'):
                print(f"   {i+1}. {sample['fn']} (FN:{sample['has_fn']}, N:{sample['has_n']}, V:{sample['has_version']})")


if __name__ == "__main__":
    test_complete_workflow()