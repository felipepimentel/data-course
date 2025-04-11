from pathlib import Path
from peopleanalytics.manager_feedback import ManagerFeedback

def main():
    mf = ManagerFeedback(Path('data'), Path('output'))
    
    # Generate templates for different role levels
    mf.generate_template('john', 'mid')
    mf.generate_template('mary', 'senior')
    mf.generate_template('bob', 'jr')
    mf.generate_template('alice', 'techlead')
    
    print("Created templates for all employees")

if __name__ == "__main__":
    main() 