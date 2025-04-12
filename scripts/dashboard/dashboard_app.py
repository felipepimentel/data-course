#!/usr/bin/env python3
"""
People Analytics Dashboard Application

A local web interface for managing team data, visualizing performance metrics,
and building a high-performance team without directly editing files.
"""

import json
from datetime import datetime
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html

# Initialize directories
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
CAREER_DIR = DATA_DIR / "career_progression"

# Ensure directories exist
CAREER_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Create the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)

# Define app layout
app.layout = html.Div(
    [
        dbc.NavbarSimple(
            brand="People Analytics Pro",
            brand_href="#",
            color="primary",
            dark=True,
            children=[
                dbc.NavItem(dbc.NavLink("Dashboard", href="#")),
                dbc.NavItem(dbc.NavLink("Team Analysis", href="#")),
                dbc.NavItem(dbc.NavLink("Performance", href="#")),
                dbc.NavItem(dbc.NavLink("Feedback", href="#")),
            ],
        ),
        dbc.Container(
            [
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content", className="mt-4"),
            ],
            fluid=True,
        ),
    ]
)

# Dashboard page layout
dashboard_layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Team Performance Dashboard", className="text-primary"),
                        html.P(
                            "Monitor and analyze team performance metrics to build a high-performance organization"
                        ),
                        html.Hr(),
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("Team Overview")),
                                dbc.CardBody(
                                    [
                                        html.Div(id="team-stats"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("Nine Box Matrix")),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="nine-box-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("Skills Distribution")),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="skills-graph"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("Team Management")),
                                dbc.CardBody(
                                    [
                                        dbc.Tabs(
                                            [
                                                dbc.Tab(
                                                    label="Add Team Member",
                                                    tab_id="tab-add-member",
                                                ),
                                                dbc.Tab(
                                                    label="Update Performance",
                                                    tab_id="tab-update-performance",
                                                ),
                                                dbc.Tab(
                                                    label="Manage Skills",
                                                    tab_id="tab-manage-skills",
                                                ),
                                            ],
                                            id="team-tabs",
                                            active_tab="tab-add-member",
                                        ),
                                        html.Div(
                                            id="team-tab-content", className="mt-3"
                                        ),
                                    ]
                                ),
                            ],
                            className="mt-4",
                        ),
                    ],
                    width=12,
                ),
            ]
        ),
    ]
)

# Add team member form
add_member_form = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Employee Name"),
                        dbc.Input(
                            id="member-name", type="text", placeholder="Enter full name"
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("Current Position"),
                        dbc.Input(
                            id="member-position",
                            type="text",
                            placeholder="Current job title",
                        ),
                    ],
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Performance Rating (1-10)"),
                        dbc.Input(
                            id="member-performance",
                            type="number",
                            min=1,
                            max=10,
                            step=1,
                            value=5,
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("Potential Rating (1-10)"),
                        dbc.Input(
                            id="member-potential",
                            type="number",
                            min=1,
                            max=10,
                            step=1,
                            value=5,
                        ),
                    ],
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Technical Skills"),
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="skill-name-1",
                                    placeholder="Skill name (e.g., technical.python)",
                                ),
                                dbc.Input(
                                    id="skill-rating-1",
                                    type="number",
                                    min=1,
                                    max=5,
                                    step=1,
                                    value=3,
                                    style={"max-width": "80px"},
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(id="skill-name-2", placeholder="Skill name"),
                                dbc.Input(
                                    id="skill-rating-2",
                                    type="number",
                                    min=1,
                                    max=5,
                                    step=1,
                                    value=3,
                                    style={"max-width": "80px"},
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(id="skill-name-3", placeholder="Skill name"),
                                dbc.Input(
                                    id="skill-rating-3",
                                    type="number",
                                    min=1,
                                    max=5,
                                    step=1,
                                    value=3,
                                    style={"max-width": "80px"},
                                ),
                            ],
                            className="mb-2",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("Soft Skills"),
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="soft-skill-name-1",
                                    placeholder="Skill name (e.g., soft.communication)",
                                ),
                                dbc.Input(
                                    id="soft-skill-rating-1",
                                    type="number",
                                    min=1,
                                    max=5,
                                    step=1,
                                    value=3,
                                    style={"max-width": "80px"},
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="soft-skill-name-2", placeholder="Skill name"
                                ),
                                dbc.Input(
                                    id="soft-skill-rating-2",
                                    type="number",
                                    min=1,
                                    max=5,
                                    step=1,
                                    value=3,
                                    style={"max-width": "80px"},
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="soft-skill-name-3", placeholder="Skill name"
                                ),
                                dbc.Input(
                                    id="soft-skill-rating-3",
                                    type="number",
                                    min=1,
                                    max=5,
                                    step=1,
                                    value=3,
                                    style={"max-width": "80px"},
                                ),
                            ],
                            className="mb-2",
                        ),
                    ],
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Button("Add Team Member", id="btn-add-member", color="primary"),
        html.Div(id="add-member-output", className="mt-3"),
    ]
)

# Update performance form - will populate with existing team members
update_performance_form = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Select Team Member"),
                        dcc.Dropdown(
                            id="performance-member-select",
                            placeholder="Select team member",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("Evaluation Date"),
                        dbc.Input(id="performance-date", type="date"),
                    ],
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("New Performance Rating (1-10)"),
                        dbc.Input(
                            id="new-performance", type="number", min=1, max=10, step=1
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("New Potential Rating (1-10)"),
                        dbc.Input(
                            id="new-potential", type="number", min=1, max=10, step=1
                        ),
                    ],
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Achievements/Notes"),
                        dbc.Textarea(
                            id="performance-notes",
                            placeholder="Enter notable achievements or feedback...",
                            rows=3,
                        ),
                    ],
                    width=12,
                ),
            ],
            className="mb-3",
        ),
        dbc.Button("Update Performance", id="btn-update-performance", color="primary"),
        html.Div(id="update-performance-output", className="mt-3"),
    ]
)

# Skills management form
skills_form = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Select Team Member"),
                        dcc.Dropdown(
                            id="skills-member-select", placeholder="Select team member"
                        ),
                    ],
                    width=12,
                ),
            ],
            className="mb-3",
        ),
        html.Div(id="current-skills-display", className="mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Add/Update Skill"),
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="new-skill-name",
                                    placeholder="Skill name (e.g., technical.python)",
                                ),
                                dbc.Input(
                                    id="new-skill-rating",
                                    type="number",
                                    min=1,
                                    max=5,
                                    step=1,
                                    value=3,
                                    style={"max-width": "80px"},
                                ),
                                dbc.Button(
                                    "Add/Update", id="btn-add-skill", color="primary"
                                ),
                            ]
                        ),
                    ],
                    width=12,
                ),
            ],
            className="mb-3",
        ),
        html.Div(id="update-skills-output", className="mt-3"),
    ]
)


# Register callback for team tabs
@app.callback(Output("team-tab-content", "children"), Input("team-tabs", "active_tab"))
def render_team_tab_content(active_tab):
    if active_tab == "tab-add-member":
        return add_member_form
    elif active_tab == "tab-update-performance":
        return update_performance_form
    elif active_tab == "tab-manage-skills":
        return skills_form
    return html.P("Select a tab")


# Team stats callback
@app.callback(Output("team-stats", "children"), Input("url", "pathname"))
def update_team_stats(pathname):
    # Get team data
    team_members = get_team_members()

    if not team_members:
        return html.P("No team members found. Add team members to see statistics.")

    total_members = len(team_members)

    # Calculate stats
    # In a real app, these would come from your actual data
    high_performers = sum(
        1
        for m in team_members.values()
        if "nine_box" in m and m["nine_box"].get("performance", 0) >= 8
    )
    high_potential = sum(
        1
        for m in team_members.values()
        if "nine_box" in m and m["nine_box"].get("potential", 0) >= 8
    )

    stars = sum(
        1
        for m in team_members.values()
        if "nine_box" in m
        and m["nine_box"].get("performance", 0) >= 8
        and m["nine_box"].get("potential", 0) >= 8
    )

    # Return stats cards
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H3(
                                    total_members, className="card-title text-center"
                                ),
                                html.P(
                                    "Team Members", className="card-text text-center"
                                ),
                            ]
                        )
                    ]
                ),
                width=3,
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H3(
                                    f"{high_performers} ({high_performers / total_members * 100:.0f}%)"
                                    if total_members
                                    else "0 (0%)",
                                    className="card-title text-center",
                                ),
                                html.P(
                                    "High Performers", className="card-text text-center"
                                ),
                            ]
                        )
                    ]
                ),
                width=3,
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H3(
                                    f"{high_potential} ({high_potential / total_members * 100:.0f}%)"
                                    if total_members
                                    else "0 (0%)",
                                    className="card-title text-center",
                                ),
                                html.P(
                                    "High Potential", className="card-text text-center"
                                ),
                            ]
                        )
                    ]
                ),
                width=3,
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H3(
                                    f"{stars} ({stars / total_members * 100:.0f}%)"
                                    if total_members
                                    else "0 (0%)",
                                    className="card-title text-center",
                                ),
                                html.P(
                                    "Star Performers", className="card-text text-center"
                                ),
                            ]
                        )
                    ]
                ),
                width=3,
            ),
        ]
    )


# Nine box graph callback
@app.callback(Output("nine-box-graph", "figure"), Input("url", "pathname"))
def update_nine_box_graph(pathname):
    # Get team data for nine box
    team_members = get_team_members()

    # Create dataframe for plotting
    data = []
    for name, member in team_members.items():
        if "nine_box" in member:
            performance = member["nine_box"].get("performance", 5)
            potential = member["nine_box"].get("potential", 5)
            data.append(
                {
                    "name": name,
                    "performance": performance,
                    "potential": potential,
                    "quadrant": get_quadrant_name(performance, potential),
                }
            )

    if not data:
        # Return empty figure with instructions
        fig = go.Figure()
        fig.add_annotation(
            text="No nine box data available. Add team members with performance ratings.",
            showarrow=False,
            font=dict(size=14),
        )
        fig.update_layout(
            xaxis=dict(range=[0, 10], title="Performance"),
            yaxis=dict(range=[0, 10], title="Potential"),
        )
        return fig

    df = pd.DataFrame(data)

    # Create scatter plot
    fig = px.scatter(
        df,
        x="performance",
        y="potential",
        text="name",
        color="quadrant",
        title="Nine Box Matrix - Team Performance vs Potential",
        labels={
            "performance": "Performance Score (0-10)",
            "potential": "Potential Score (0-10)",
        },
    )

    # Customize the layout
    fig.update_traces(textposition="top center")
    fig.update_layout(
        xaxis=dict(range=[0, 10]),
        yaxis=dict(range=[0, 10]),
        xaxis_tickvals=[0, 3.33, 6.66, 10],
        yaxis_tickvals=[0, 3.33, 6.66, 10],
        shapes=[
            # Vertical lines
            dict(
                type="line",
                x0=3.33,
                y0=0,
                x1=3.33,
                y1=10,
                line=dict(color="Gray", width=1, dash="dash"),
            ),
            dict(
                type="line",
                x0=6.66,
                y0=0,
                x1=6.66,
                y1=10,
                line=dict(color="Gray", width=1, dash="dash"),
            ),
            # Horizontal lines
            dict(
                type="line",
                x0=0,
                y0=3.33,
                x1=10,
                y1=3.33,
                line=dict(color="Gray", width=1, dash="dash"),
            ),
            dict(
                type="line",
                x0=0,
                y0=6.66,
                x1=10,
                y1=6.66,
                line=dict(color="Gray", width=1, dash="dash"),
            ),
        ],
    )

    # Add quadrant labels
    quadrants = [
        {"x": 1.67, "y": 8.33, "text": "Low Performer<br>High Potential"},
        {"x": 5, "y": 8.33, "text": "Core Player<br>High Potential"},
        {"x": 8.33, "y": 8.33, "text": "Star<br>High Potential"},
        {"x": 1.67, "y": 5, "text": "Low Performer<br>Medium Potential"},
        {"x": 5, "y": 5, "text": "Core Player<br>Medium Potential"},
        {"x": 8.33, "y": 5, "text": "Star<br>Medium Potential"},
        {"x": 1.67, "y": 1.67, "text": "Low Performer<br>Low Potential"},
        {"x": 5, "y": 1.67, "text": "Core Player<br>Low Potential"},
        {"x": 8.33, "y": 1.67, "text": "Star<br>Low Potential"},
    ]

    for q in quadrants:
        fig.add_annotation(
            x=q["x"],
            y=q["y"],
            text=q["text"],
            showarrow=False,
            font=dict(size=10, color="gray"),
        )

    return fig


# Skills graph callback
@app.callback(Output("skills-graph", "figure"), Input("url", "pathname"))
def update_skills_graph(pathname):
    # Get team data for skills
    team_members = get_team_members()

    # Extract skills data
    data = []
    for name, member in team_members.items():
        if "matriz_habilidades" in member:
            for skill, level in member["matriz_habilidades"].items():
                skill_category = skill.split(".")[0] if "." in skill else "other"
                skill_name = skill.split(".")[1] if "." in skill else skill
                data.append(
                    {
                        "name": name,
                        "skill": skill,
                        "skill_category": skill_category,
                        "skill_name": skill_name,
                        "level": level,
                    }
                )

    if not data:
        # Return empty figure with instructions
        fig = go.Figure()
        fig.add_annotation(
            text="No skills data available. Add team members with skills ratings.",
            showarrow=False,
            font=dict(size=14),
        )
        return fig

    df = pd.DataFrame(data)

    # Create a bar chart grouped by category
    fig = px.bar(
        df.groupby(["name", "skill_category"])["level"].mean().reset_index(),
        x="name",
        y="level",
        color="skill_category",
        barmode="group",
        title="Team Skills by Category",
        labels={"level": "Average Skill Level (1-5)", "name": "Team Member"},
    )

    return fig


# Add member callback
@app.callback(
    Output("add-member-output", "children"),
    Input("btn-add-member", "n_clicks"),
    [
        State("member-name", "value"),
        State("member-position", "value"),
        State("member-performance", "value"),
        State("member-potential", "value"),
        State("skill-name-1", "value"),
        State("skill-rating-1", "value"),
        State("skill-name-2", "value"),
        State("skill-rating-2", "value"),
        State("skill-name-3", "value"),
        State("skill-rating-3", "value"),
        State("soft-skill-name-1", "value"),
        State("soft-skill-rating-1", "value"),
        State("soft-skill-name-2", "value"),
        State("soft-skill-rating-2", "value"),
        State("soft-skill-name-3", "value"),
        State("soft-skill-rating-3", "value"),
    ],
)
def add_team_member(
    n_clicks,
    name,
    position,
    performance,
    potential,
    skill1_name,
    skill1_rating,
    skill2_name,
    skill2_rating,
    skill3_name,
    skill3_rating,
    soft1_name,
    soft1_rating,
    soft2_name,
    soft2_rating,
    soft3_name,
    soft3_rating,
):
    if n_clicks is None or not name:
        return ""

    # Create skills dictionary
    skills = {}
    if skill1_name:
        skills[skill1_name] = skill1_rating
    if skill2_name:
        skills[skill2_name] = skill2_rating
    if skill3_name:
        skills[skill3_name] = skill3_rating
    if soft1_name:
        skills[soft1_name] = soft1_rating
    if soft2_name:
        skills[soft2_name] = soft2_rating
    if soft3_name:
        skills[soft3_name] = soft3_rating

    # Create member data
    member_data = {
        "nome": name,
        "cargo_atual": position,
        "matriz_habilidades": skills,
        "nine_box": {
            "performance": performance,
            "potential": potential,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "quadrant": get_quadrant_name(performance, potential),
        },
        "eventos_carreira": [],
        "metas_carreira": [],
        "certificacoes": [],
        "mentoria": [],
    }

    # Save to file
    file_path = CAREER_DIR / f"{name}.json"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(member_data, f, indent=2, ensure_ascii=False)
        return dbc.Alert(f"Team member '{name}' added successfully!", color="success")
    except Exception as e:
        return dbc.Alert(f"Error adding team member: {str(e)}", color="danger")


# Get team members helper function
def get_team_members():
    """Get all team members from career progression files"""
    members = {}

    if not CAREER_DIR.exists():
        return members

    for file_path in CAREER_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                members[file_path.stem] = data
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")

    return members


# Get quadrant name helper function
def get_quadrant_name(performance, potential):
    """Get the quadrant name based on performance and potential scores"""
    perf_level = (
        "Baixo" if performance < 3.33 else "Médio" if performance < 6.66 else "Alto"
    )
    pot_level = "Baixo" if potential < 3.33 else "Médio" if potential < 6.66 else "Alto"

    return f"{perf_level} Desempenho / {pot_level} Potencial"


# Update performance callbacks
@app.callback(Output("performance-member-select", "options"), Input("url", "pathname"))
def update_performance_member_options(pathname):
    members = get_team_members()
    return [{"label": name, "value": name} for name in members.keys()]


# Skills management callbacks
@app.callback(Output("skills-member-select", "options"), Input("url", "pathname"))
def update_skills_member_options(pathname):
    members = get_team_members()
    return [{"label": name, "value": name} for name in members.keys()]


# Main page routing
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/team":
        return html.P("Team page")
    else:
        return dashboard_layout


if __name__ == "__main__":
    print("Starting People Analytics Dashboard...")
    print("Open http://127.0.0.1:8050/ in your browser")
    app.run(debug=True)
