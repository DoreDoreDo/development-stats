#!/usr/bin/env python3
import os
import glob
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from typing import List, Tuple, Dict
from tabulate import tabulate

CATEGORIES_TO_VISUALIZE: List[str] = ['api', 'app', 'other', 'infraestructure']
PALETTE: Dict[str, str] = {
    'api': 'rgba(255, 228, 225, 0.5)',
    'app': 'rgba(255, 250, 205, 0.5)',
    'other': 'rgba(255, 182, 193, 0.5)',
    'infraestructure': 'rgba(173, 216, 230, 0.5)'  # light blue
}
NUM_DAYS: int = 15  # Number of days to look back in graphic

DATA_DIR: str = 'daily'

# Find all stats CSVs
def find_csvs() -> Tuple[List[str], List[str]]:
    category_files: List[str] = sorted(glob.glob(os.path.join(DATA_DIR, '**', 'stats-by-category-*.csv'), recursive=True))
    repo_files: List[str] = sorted(glob.glob(os.path.join(DATA_DIR, '**', 'stats-per-repo-*.csv'), recursive=True))
    return category_files, repo_files

# Parse date from filename
def parse_date(filename: str) -> datetime:
    base: str = os.path.basename(filename)
    # Extract the last three components (year, month, day) before .csv
    parts: List[str] = base.replace('.csv', '').split('-')
    date_str: str = '-'.join(parts[-3:])
    return datetime.strptime(date_str, '%Y-%m-%d')

# Load and aggregate category stats
def load_category_stats(files: List[str]) -> pd.DataFrame:
    dfs: List[pd.DataFrame] = []
    for f in files:
        date: datetime = parse_date(f)
        df: pd.DataFrame = pd.read_csv(f)
        df['date'] = date
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

# Load and aggregate repo stats
def load_repo_stats(files: List[str]) -> pd.DataFrame:
    dfs: List[pd.DataFrame] = []
    for f in files:
        date: datetime = parse_date(f)
        df: pd.DataFrame = pd.read_csv(f)
        df['date'] = date
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

# Generate category trends plot
def plot_category_trends(df: pd.DataFrame, value_col: str, title: str, y_title: str) -> go.Figure:
    fig: go.Figure = go.Figure()
    if value_col == 'lines_changed':
        df = df.copy()
        df['lines_changed'] = df['lines_added'] + df['lines_deleted']
    for cat in df['category'].unique():
        sub: pd.DataFrame = df[df['category'] == cat]
        fig.add_trace(go.Scatter(x=sub['date'], y=sub[value_col], mode='lines+markers', name=cat))
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title=y_title)
    return fig

def plot_category_bar(df: pd.DataFrame, value_col: str, title: str, y_title: str) -> go.Figure:
    fig: go.Figure = go.Figure()
    if value_col == 'lines_changed':
        df = df.copy()
        df['lines_changed'] = df['lines_added'] + df['lines_deleted']
    for cat in df['category'].unique():
        sub: pd.DataFrame = df[df['category'] == cat]
        fig.add_trace(go.Bar(x=sub['date'], y=sub[value_col], name=cat))
    fig.update_layout(barmode='group', title=title, xaxis_title='Date', yaxis_title=y_title)
    return fig

def plot_category_area(df: pd.DataFrame, value_col: str, palette: Dict[str, str]) -> go.Figure:
    fig: go.Figure = go.Figure()
    if value_col == 'lines_changed':
        df = df.copy()
        df['lines_changed'] = df['lines_added'] + df['lines_deleted']
    for cat in CATEGORIES_TO_VISUALIZE:
        sub: pd.DataFrame = df[df['category'] == cat]
        color: str = palette.get(cat, 'rgba(200,200,200,0.5)')
        fig.add_trace(go.Scatter(x=sub['date'], y=sub[value_col], name=cat, fill='tozeroy', mode='none', fillcolor=color, line=dict(color=color)))
        fig.update_layout(
            title=None,
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(t=10),
            paper_bgcolor='rgba(255,255,255,0)',
            plot_bgcolor='rgba(250,250,250,1)',
            xaxis=dict(
                showline=True,
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                ticks='',
                linecolor='rgba(180,180,180,1)',
                linewidth=2,
                ticklabelposition='outside',
                ticklabelstandoff=10
            ),
            yaxis=dict(
                showline=False,
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                ticks='',
                linecolor='rgba(180,180,180,1)',
                linewidth=2,
                ticklabelposition='outside',
                ticklabelstandoff=10
            )
        )
    return fig

# Function to print dataframe using tabulate
def print_data_table(df: pd.DataFrame) -> None:
    # Format date column for display
    df_display = df.copy()
    df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d')

    print(tabulate(df_display, headers='keys', tablefmt='github', showindex=False))

# Main function
def main() -> None:
    category_files, _ = find_csvs()
    if not category_files:
        print('No category CSV files found.')
        return
    # Load template
    with open(os.path.join('gh_pages', 'template.html'), 'r') as tpl_file:
        template: str = tpl_file.read()
    cat_df: pd.DataFrame = load_category_stats(category_files)

    # Filter to last NUM_DAYS days
    today: datetime = datetime.today()
    cutoff_date: datetime = today - pd.Timedelta(days=NUM_DAYS)
    cat_df = cat_df[cat_df['date'] >= cutoff_date]

    # Print the filtered data table
    print_data_table(cat_df)

    fig: go.Figure = plot_category_area(cat_df, value_col='lines_changed', palette=PALETTE)
    graph_html: str = fig.to_html(full_html=False, include_plotlyjs="cdn")
    output_html: str = template.replace('<!--GRAPHS-->', graph_html)
    output_path: str = os.path.join('gh_pages', 'index.html')
    with open(output_path, 'w') as f:
        f.write(output_html)

    # Save the figure as a PNG image
    image_path: str = os.path.join('gh_pages', 'stats_screenshot.png')
    try:
        fig.write_image(image_path)
        print(f'Screenshot saved to {image_path}')
    except Exception as e:
        print(f'Could not save image: {e}\nIf you see a kaleido error, run: pip install -U kaleido')

if __name__ == '__main__':
    main()
