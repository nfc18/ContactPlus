#!/usr/bin/env python3
"""
Final merge of cleaned databases
"""

import os
import vobject
from datetime import datetime
from intelligent_merge import IntelligentContactMerger

def main():
    """Perform final merge of cleaned databases"""
    
    print("Final Database Merge")
    print("=" * 80)
    print("Merging three cleaned databases into master contact database...")
    
    # Get the latest cleaned databases
    timestamp = "20250606_141000"  # From the cleaning process
    databases = {
        "Sara Export": f"data/Sara_Export_VALIDATED_20250606_CLEANED_{timestamp}.vcf",
        "iPhone Contacts": f"data/iPhone_Contacts_VALIDATED_20250606_120917_CLEANED_{timestamp}.vcf",
        "iPhone Suggested": f"data/iPhone_Suggested_VALIDATED_20250606_120917_CLEANED_{timestamp}.vcf"
    }
    
    # Verify all databases exist
    for db_name, db_path in databases.items():
        if not os.path.exists(db_path):
            print(f"Error: Database not found - {db_path}")
            return
    
    # Create merger
    merger = IntelligentContactMerger()
    
    # Setup output path
    output_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"data/MASTER_CONTACTS_{output_timestamp}.vcf"
    
    # Merge all databases
    print("\nMerging databases...")
    merger.merge_databases(databases, output_path)
    
    # Load the merged file to get contact count
    with open(output_path, 'r', encoding='utf-8') as f:
        merged_contacts = list(vobject.readComponents(f.read()))
    
    print(f"\n✅ Master database created: {output_path}")
    print(f"📊 Total contacts in master database: {len(merged_contacts)}")
    
    # Show merge statistics
    print("\nMerge Statistics:")
    print("-" * 40)
    print(f"Total contacts processed: {merger.stats['total_contacts_processed']}")
    print(f"Unique contacts: {merger.stats['unique_contacts']}")
    print(f"Exact duplicates removed: {merger.stats['exact_duplicates']}")
    print(f"Smart merges performed: {merger.stats['smart_merges']}")
    print(f"Emails preserved: {merger.stats['emails_preserved']}")
    print(f"Phone numbers preserved: {merger.stats['phones_preserved']}")
    print(f"Photos selected: {merger.stats['photos_selected']}")
    
    # Create summary report
    report = {
        'merge_date': datetime.now().isoformat(),
        'input_databases': list(databases.values()),
        'output_database': output_path,
        'statistics': merger.stats,
        'final_contact_count': len(merged_contacts)
    }
    
    report_path = f"data/final_merge_report_{output_timestamp}.json"
    import json
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Merge report saved to: {report_path}")
    print(f"\n🎉 SUCCESS! Your master contact database is ready for import.")
    print(f"   File: {output_path}")
    print(f"   Contacts: {len(merged_contacts)}")

if __name__ == "__main__":
    main()