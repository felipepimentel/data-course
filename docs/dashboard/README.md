# People Analytics Dashboard

## Overview

The People Analytics Dashboard provides a user-friendly interface for managing team data, visualizing performance metrics, and building a high-performance team without directly editing files.

## Getting Started

### Prerequisites

Before running the dashboard, ensure you have all the required dependencies:

```bash
pip install -r requirements.txt
```

### Populating Sample Data

To populate the dashboard with sample data:

```bash
python scripts/populate_sample_data.py
```

This will create sample team members with various skills and performance ratings.

### Running the Dashboard

To start the dashboard:

```bash
python scripts/run_dashboard.py
```

Then open your browser to [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

## Dashboard Features

### Team Overview

The dashboard provides a high-level overview of your team composition, including:
- Total number of team members
- Percentage of high performers
- Percentage of high potential individuals
- Percentage of star performers (high performance/high potential)

### Nine Box Matrix

The Nine Box Matrix visualization plots team members based on their performance and potential:
- **Stars**: High performance, high potential
- **Core Players**: Medium-high performance with varying potential
- **Specialists**: High performance, lower potential
- **Developing Talent**: Medium performance, high potential

### Skills Distribution

The Skills Distribution chart shows the average skill level by category for each team member, helping identify:
- Team strengths and capabilities
- Skill gaps across the team
- Individual areas for development

## Managing Team Data

### Adding Team Members

1. Go to the "Add Team Member" tab
2. Enter the person's name, position, performance and potential ratings
3. Add technical and soft skills with ratings (1-5)
4. Click "Add Team Member"

### Updating Performance

1. Go to the "Update Performance" tab
2. Select an existing team member
3. Enter new performance and potential ratings
4. Add notes about achievements or feedback
5. Click "Update Performance"

### Managing Skills

1. Go to the "Manage Skills" tab
2. Select an existing team member
3. View their current skills
4. Add or update skills as needed

## Building a High-Performance Team

Use the dashboard to implement these key strategies:

1. **Balanced Team Composition**
   - Aim for ~15-20% stars/high potentials
   - Maintain ~60-70% reliable core performers
   - Include ~10-15% specialists/domain experts

2. **Strategic Talent Development**
   - Identify high potentials for accelerated growth
   - Create development plans based on Nine Box positions
   - Address team-wide skill gaps

3. **Data-Driven Decisions**
   - Monitor skill distribution across the team
   - Track performance trends over time
   - Identify areas for team improvement

## Technical Information

- Built with Dash and Plotly
- Data stored in JSON files in the data/career_progression directory
- Visualizations generated dynamically based on current data 