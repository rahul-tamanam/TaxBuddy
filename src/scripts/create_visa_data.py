"""
Create visa type reference data
"""

import json
from pathlib import Path

VISA_DATA = {
    "F-1": {
        "description": "Academic Student",
        "exempt_individual": True,
        "fica_exempt": True,
        "exempt_duration": "5 years",
        "typical_income": [
            "On-campus employment (up to 20 hrs/week)",
            "Scholarships and fellowships",
            "Practical training (CPT/OPT)"
        ],
        "required_forms": ["Form 1040-NR", "Form 8843"],
        "notes": "Most common visa for international students"
    },
    "J-1": {
        "description": "Exchange Visitor (Student/Scholar)",
        "exempt_individual": True,
        "fica_exempt": True,
        "exempt_duration": "2 years (scholars) or duration of status (students)",
        "typical_income": [
            "Stipends",
            "Scholarships",
            "Teaching/research assistantships"
        ],
        "required_forms": ["Form 1040-NR", "Form 8843"],
        "notes": "For exchange programs, research, teaching"
    },
    "M-1": {
        "description": "Vocational Student",
        "exempt_individual": True,
        "fica_exempt": True,
        "exempt_duration": "5 years",
        "typical_income": [
            "Limited work authorization",
            "Practical training only"
        ],
        "required_forms": ["Form 1040-NR", "Form 8843"],
        "notes": "For vocational or technical studies"
    },
    "H-1B": {
        "description": "Specialty Occupation Worker",
        "exempt_individual": False,
        "fica_exempt": False,
        "exempt_duration": None,
        "typical_income": [
            "W-2 wages from employer"
        ],
        "required_forms": ["Form 1040-NR or 1040 (depending on residency)"],
        "notes": "Not an exempt individual, subject to FICA"
    }
}

def create_visa_database(output_dir: str = 'data/processed'):
    """Create visa type reference database"""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'visa_types.json'
    
    print("\n" + "="*60)
    print("Creating Visa Type Database")
    print("="*60 + "\n")
    
    with open(output_file, 'w') as f:
        json.dump(VISA_DATA, f, indent=2)
    
    print(f"✅ Created visa database: {output_file}")
    print(f"📊 Visa types included: {len(VISA_DATA)}")
    
    for visa_type in VISA_DATA.keys():
        print(f"   - {visa_type}: {VISA_DATA[visa_type]['description']}")
    
    print()

if __name__ == "__main__":
    create_visa_database()