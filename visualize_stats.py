#!/usr/bin/env python3
import os
import glob
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime

CATEGORIES_TO_VISUALIZE = ['api', 'app']

# Directory containing daily CSVs
data_dir = 'daily'

# Find all stats CSVs
def find_csvs():
    category_files = sorted(glob.glob(os.path.join(data_dir, 'stats-by-category-*.csv')))
    repo_files = sorted(glob.glob(os.path.join(data_dir, 'stats-per-repo-*.csv')))
    return category_files, repo_files

# Parse date from filename
def parse_date(filename):
    base = os.path.basename(filename)
    # Extract the last three components (year, month, day) before .csv
    parts = base.replace('.csv', '').split('-')
    date_str = '-'.join(parts[-3:])
    return datetime.strptime(date_str, '%Y-%m-%d')

# Load and aggregate category stats
def load_category_stats(files):
    dfs = []
    for f in files:
        date = parse_date(f)
        df = pd.read_csv(f)
        df['date'] = date
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

# Load and aggregate repo stats
def load_repo_stats(files):
    dfs = []
    for f in files:
        date = parse_date(f)
        df = pd.read_csv(f)
        df['date'] = date
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

# Generate category trends plot
def plot_category_trends(df, value_col, title, y_title):
    fig = go.Figure()
    if value_col == 'lines_changed':
        df = df.copy()
        df['lines_changed'] = df['lines_added'] + df['lines_deleted']
    for cat in df['category'].unique():
        sub = df[df['category'] == cat]
        fig.add_trace(go.Scatter(x=sub['date'], y=sub[value_col], mode='lines+markers', name=cat))
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title=y_title)
    return fig

def plot_category_bar(df, value_col, title, y_title):
    fig = go.Figure()
    if value_col == 'lines_changed':
        df = df.copy()
        df['lines_changed'] = df['lines_added'] + df['lines_deleted']
    for cat in df['category'].unique():
        sub = df[df['category'] == cat]
        fig.add_trace(go.Bar(x=sub['date'], y=sub[value_col], name=cat))
    fig.update_layout(barmode='group', title=title, xaxis_title='Date', yaxis_title=y_title)
    return fig

def plot_category_area(df, value_col, palette):
    fig = go.Figure()
    if value_col == 'lines_changed':
        df = df.copy()
        df['lines_changed'] = df['lines_added'] + df['lines_deleted']
    for cat in CATEGORIES_TO_VISUALIZE:
        sub = df[df['category'] == cat]
        color = palette.get(cat, 'rgba(200,200,200,0.5)')
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
    # ...existing code...

# Main function
def main():
    category_files, _ = find_csvs()
    if not category_files:
        print('No category CSV files found.')
        return
    # Load template
    with open(os.path.join('gh_pages', 'template.html'), 'r') as tpl_file:
        template = tpl_file.read()
    cat_df = load_category_stats(category_files)
    # Filter to previous calendar month
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_month_end = first_day_this_month - pd.Timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    cat_df = cat_df[(cat_df['date'] >= last_month_start) & (cat_df['date'] <= last_month_end)]
    palette = {'api': 'rgba(255, 228, 225, 0.5)', 'app': 'rgba(255, 250, 205, 0.5)', 'other': 'rgba(255, 182, 193, 0.5)'}
    fig = plot_category_area(cat_df, value_col='lines_changed', palette=palette)
    graph_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    output_html = template.replace('<!--GRAPHS-->', graph_html)
    output_path = os.path.join('gh_pages', 'index.html')
    with open(output_path, 'w') as f:
        f.write(output_html)
    print(f'{output_path} generated.')

if __name__ == '__main__':
    main()
