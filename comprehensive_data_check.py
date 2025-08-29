#!/usr/bin/env python3
"""
Comprehensive check for all church data sources
"""

from app.db.session import SessionLocal
from app.services.church_data_context import get_church_context_data, format_context_for_prompt
from app.models.announcement import Announcement
from app.models.member import Member
from app.models.pastoral_care import PrayerRequest, PastoralCareRequest
from app.models.attendance import Attendance
from app.models.worship_schedule import WorshipService
from app.models.financial import Offering

def check_all_data_sources():
    """Check all church data sources for completeness"""
    db = SessionLocal()
    church_id = 9999  # Demo church
    
    try:
        print("🔍 Comprehensive Church Data Source Check")
        print("="*50)
        
        # Check raw data in database
        print("\n📊 Raw Database Data Check:")
        data_counts = {}
        
        # Check each data source
        data_sources = {
            "members": Member,
            "offerings": Offering, 
            "announcements": Announcement,
            "prayer_requests": PrayerRequest,
            "pastoral_care_requests": PastoralCareRequest,
            "attendances": Attendance,
            "worship_services": WorshipService
        }
        
        for source_name, model_class in data_sources.items():
            try:
                count = db.query(model_class).filter(model_class.church_id == church_id).count()
                data_counts[source_name] = count
                status = "✅" if count > 0 else "❌"
                print(f"   {status} {source_name}: {count} records")
            except Exception as e:
                print(f"   ⚠️ {source_name}: Error - {e}")
                data_counts[source_name] = 0
        
        # Test context data retrieval for each source
        print(f"\n🧪 Context Data Retrieval Test:")
        all_sources = {
            "announcements": True,
            "prayer_requests": True,
            "pastoral_care_requests": True,
            "offerings": True,
            "attendances": True,  # Note: might be "attendance" in some places
            "members": True,
            "worship_services": True
        }
        
        context_data = get_church_context_data(
            db=db,
            church_id=church_id,
            church_data_sources=all_sources,
            user_query="모든 정보를 알려줘",
            prioritize_church_data=True
        )
        
        print(f"   📋 Retrieved context keys: {list(context_data.keys())}")
        
        # Check what data was actually retrieved
        context_status = {}
        expected_keys = {
            "announcements": "announcements",
            "prayer_requests": "prayer_requests", 
            "pastoral_care_requests": "pastoral_care_requests",
            "offerings": "offering_stats",  # This was the key mismatch we found
            "attendances": "attendance_stats",  # Check if this is correct
            "members": "member_stats",
            "worship_services": "worship_schedule"
        }
        
        for source, expected_key in expected_keys.items():
            if expected_key in context_data:
                data = context_data[expected_key]
                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict):
                    # For stats, check if there's meaningful data
                    count = "has_data" if any(v for v in data.values() if v) else "empty"
                else:
                    count = "unknown_type"
                context_status[source] = count
                status = "✅" if (isinstance(count, int) and count > 0) or count == "has_data" else "❌"
                print(f"   {status} {source} → {expected_key}: {count}")
            else:
                context_status[source] = "missing"
                print(f"   ❌ {source} → {expected_key}: KEY NOT FOUND")
        
        # Test context formatting
        print(f"\n📝 Context Formatting Test:")
        formatted_context = format_context_for_prompt(context_data)
        
        if formatted_context:
            print(f"   ✅ Context formatted successfully ({len(formatted_context)} chars)")
            
            # Check which sections are included
            sections_found = []
            section_markers = [
                "[교회 공지사항]", "[중보기도 요청]", "[심방 요청]", 
                "[헌금 현황]", "[출석 현황]", "[교인 현황]", "[예배 일정]"
            ]
            
            for marker in section_markers:
                if marker in formatted_context:
                    sections_found.append(marker.replace("[", "").replace("]", ""))
            
            print(f"   📋 Sections included: {sections_found}")
            
            # Show preview of each section
            lines = formatted_context.split('\n')
            current_section = None
            sections_preview = {}
            
            for line in lines:
                for marker in section_markers:
                    if marker in line:
                        current_section = marker.replace("[", "").replace("]", "")
                        sections_preview[current_section] = []
                        break
                
                if current_section and line.strip():
                    sections_preview[current_section].append(line)
                    if len(sections_preview[current_section]) >= 3:  # Preview first 3 lines
                        current_section = None
            
            for section, preview_lines in sections_preview.items():
                print(f"\n   📄 {section}:")
                for line in preview_lines[:3]:
                    print(f"      {line}")
                    
        else:
            print(f"   ❌ Context formatting failed - empty result")
        
        # Identify potential issues
        print(f"\n🚨 Potential Issues Found:")
        issues = []
        
        # Check for data source/context key mismatches
        for source, expected_key in expected_keys.items():
            db_count = data_counts.get(source, 0)
            context_result = context_status.get(source)
            
            if db_count > 0 and context_result == "missing":
                issues.append(f"❌ {source}: Has {db_count} records but missing from context (expected key: {expected_key})")
            elif db_count > 0 and context_result in [0, "empty"]:
                issues.append(f"⚠️ {source}: Has {db_count} records but context shows empty data")
            elif db_count == 0:
                issues.append(f"📝 {source}: No sample data exists ({db_count} records)")
        
        if not issues:
            print("   ✅ No issues found - all data sources working correctly!")
        else:
            for issue in issues:
                print(f"   {issue}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if not issues:
            print("   🎉 All data sources are properly integrated!")
        else:
            empty_sources = [s for s, c in data_counts.items() if c == 0]
            if empty_sources:
                print(f"   📥 Create sample data for: {', '.join(empty_sources)}")
                
            key_mismatches = [i for i in issues if "missing from context" in i]
            if key_mismatches:
                print(f"   🔧 Fix key mappings in format_context_for_prompt function")
                print(f"   📝 Check church_data_context.py around line 1067+ for similar key mismatches")
        
    except Exception as e:
        print(f"❌ Error during comprehensive check: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_all_data_sources()