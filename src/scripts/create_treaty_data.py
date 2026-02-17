"""
Create structured tax treaty data for common countries
"""

import json
from pathlib import Path

class TreatyDataCreator:
    """Create and manage tax treaty information"""
    
    # Treaty information for top countries
    TREATY_DATA = {
        "India": {
            "has_treaty": True,
            "student_article": "Article 21",
            "student_exemption": "$5,000 per year",
            "duration": "5 years",
            "conditions": [
                "Present in US solely for education or training",
                "Payments received from outside the US",
                "For maintenance, education, study, research, or training"
            ],
            "effective_date": "1991",
            "source": "Publication 901, India Treaty"
        },
        "China": {
            "has_treaty": True,
            "student_article": "Article 20",
            "student_exemption": "$5,000 per year",
            "duration": "5 years",
            "conditions": [
                "Present in US solely for education or training",
                "Payments from outside the US",
                "For maintenance, education, or training"
            ],
            "effective_date": "1987",
            "source": "Publication 901, China Treaty"
        },
        "South Korea": {
            "has_treaty": True,
            "student_article": "Article 20",
            "student_exemption": "Full exemption for qualified amounts",
            "duration": "5 years",
            "conditions": [
                "Present in US solely for education",
                "Qualified scholarship or fellowship grant",
                "From governmental, religious, charitable, or educational organization"
            ],
            "effective_date": "1980",
            "source": "Publication 901, South Korea Treaty"
        },
        "Canada": {
            "has_treaty": True,
            "student_article": "Article XX",
            "student_exemption": "Full exemption for certain amounts",
            "duration": "Not specified",
            "conditions": [
                "Present in US solely for education",
                "Scholarship or fellowship grant from outside US"
            ],
            "effective_date": "1984",
            "source": "Publication 901, Canada Treaty"
        },
        "Mexico": {
            "has_treaty": True,
            "student_article": "Article 22",
            "student_exemption": "Qualified amounts exempt",
            "duration": "Not specified",
            "conditions": [
                "Present in US solely for education or training",
                "Payments from outside the US"
            ],
            "effective_date": "1994",
            "source": "Publication 901, Mexico Treaty"
        },
        "Germany": {
            "has_treaty": True,
            "student_article": "Article 20",
            "student_exemption": "Qualified amounts exempt",
            "duration": "Not specified",
            "conditions": [
                "Present in US solely for study or training",
                "Grants, allowances, or awards from governmental or charitable organizations"
            ],
            "effective_date": "1990",
            "source": "Publication 901, Germany Treaty"
        },
        "Vietnam": {
            "has_treaty": False,
            "student_article": None,
            "student_exemption": None,
            "duration": None,
            "conditions": [],
            "effective_date": None,
            "source": "No treaty with US"
        },
        "Brazil": {
            "has_treaty": False,
            "student_article": None,
            "student_exemption": None,
            "duration": None,
            "conditions": [],
            "effective_date": None,
            "source": "No treaty with US"
        },
    }
    
    def __init__(self, output_dir: str = 'data/processed'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_treaty_database(self):
        """Create JSON database of treaty information"""
        
        output_file = self.output_dir / 'treaty_lookup.json'
        
        print("\n" + "="*60)
        print("Creating Tax Treaty Database")
        print("="*60 + "\n")
        
        # Save treaty data
        with open(output_file, 'w') as f:
            json.dump(self.TREATY_DATA, f, indent=2)
        
        print(f"✅ Created treaty database: {output_file}")
        print(f"📊 Countries included: {len(self.TREATY_DATA)}")
        
        # Show summary
        with_treaty = sum(1 for v in self.TREATY_DATA.values() if v['has_treaty'])
        without_treaty = len(self.TREATY_DATA) - with_treaty
        
        print(f"   - With treaties: {with_treaty}")
        print(f"   - Without treaties: {without_treaty}")
        print()
        
        return output_file
    
    def show_treaty_info(self, country: str):
        """Display treaty information for a specific country"""
        
        if country not in self.TREATY_DATA:
            print(f"❌ No data for {country}")
            return
        
        info = self.TREATY_DATA[country]
        
        print(f"\n{'='*60}")
        print(f"Tax Treaty Information: {country}")
        print(f"{'='*60}\n")
        
        if info['has_treaty']:
            print(f"✅ Treaty exists")
            print(f"Article: {info['student_article']}")
            print(f"Exemption: {info['student_exemption']}")
            print(f"Duration: {info['duration']}")
            print(f"\nConditions:")
            for condition in info['conditions']:
                print(f"  • {condition}")
        else:
            print(f"❌ No tax treaty with US")
        
        print()


def main():
    """Main execution"""
    
    creator = TreatyDataCreator()
    
    # Create treaty database
    creator.create_treaty_database()
    
    # Show example
    print("\nExample treaty information:")
    creator.show_treaty_info("India")
    creator.show_treaty_info("Vietnam")


if __name__ == "__main__":
    main()