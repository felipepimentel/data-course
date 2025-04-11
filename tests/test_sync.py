import os
import sys
from pathlib import Path
from peopleanalytics.data_processor import DataProcessor
from peopleanalytics.sync import Sync
from peopleanalytics.manager_feedback import ManagerFeedback

def main():
    # Initialize paths
    data_path = Path("data")
    output_path = Path("output")
    
    # Initialize data processor
    processor = DataProcessor(data_path, output_path)
    
    # Generate individual reports
    print("Generating individual reports...")
    success = processor.generate_individual_reports()
    
    if success:
        print("\nReports generated successfully!")
    else:
        print("No reports were generated")
        return
    
    # Test sync functionality
    print("\nTesting sync functionality...")
    sync = Sync(data_path, output_path)
    
    # First sync will create manager feedback templates
    print("\nFirst sync - creating manager feedback templates...")
    sync_results = sync.sync_all()
    
    if sync_results:
        print("\nFirst sync results:")
        for result in sync_results:
            print(f"- {result}")
    else:
        print("No sync results")
        return
    
    # Create a sample completed manager feedback form for testing
    print("\nCreating sample completed manager feedback form...")
    create_sample_manager_feedback(data_path, "john")
    
    # Run second sync to process the manager feedback form
    print("\nSecond sync - processing manager feedback...")
    sync_results = sync.sync_all()
    
    if sync_results:
        print("\nSecond sync results:")
        for result in sync_results:
            print(f"- {result}")
    else:
        print("No sync results from second sync")
        return
    
    # Verify sync results
    print("\nVerifying sync results...")
    for result in sync_results:
        if "error" in result.lower():
            print(f"Error in sync: {result}")
            return
    
    print("\nAll tests completed successfully!")

def create_sample_manager_feedback(data_path: Path, employee_name: str):
    """Create a sample completed manager feedback form for testing"""
    manager_feedback_dir = data_path / "manager_feedback"
    manager_feedback_dir.mkdir(parents=True, exist_ok=True)
    
    feedback_file = manager_feedback_dir / f"{employee_name}_manager_feedback.md"
    
    # Check if the file exists first (generated from the first sync)
    if not feedback_file.exists():
        print(f"Manager feedback template not found for {employee_name}")
        return
    
    # Read the template
    with open(feedback_file, 'r') as f:
        content = f.readlines()
    
    # Fill out the template
    filled_content = []
    for line in content:
        # Fill out ratings
        if ": [1-5]" in line:
            filled_content.append(line.replace("[1-5]", "4"))
        elif ": [Y/N/P]" in line:
            filled_content.append(line.replace("[Y/N/P]", "Y"))
        elif "List 2-3 key areas" in line:
            filled_content.append(line)
            filled_content.append("  1. Improve code testing coverage\n")
            filled_content.append("  2. Enhance system design skills\n")
            filled_content.append("  3. Develop more advanced troubleshooting techniques\n")
        elif "Key growth objectives" in line:
            filled_content.append(line)
            filled_content.append("  1. Complete advanced testing certification\n")
            filled_content.append("  2. Lead a small project team\n")
            filled_content.append("  3. Contribute to architecture decisions\n")
        elif "Resources needed" in line:
            filled_content.append(line)
            filled_content.append("  1. Access to online training courses\n")
            filled_content.append("  2. Mentoring from a senior engineer\n")
        elif "## Additional Comments" in line:
            filled_content.append(line)
            filled_content.append("John is showing great potential and is consistently improving. His attention to detail and willingness to learn are notable strengths. He should focus on developing more advanced technical skills to prepare for a more senior role in the future.\n")
        else:
            filled_content.append(line)
    
    # Write the filled out form
    with open(feedback_file, 'w') as f:
        f.writelines(filled_content)
    
    print(f"Created sample manager feedback for {employee_name}")

if __name__ == "__main__":
    main() 