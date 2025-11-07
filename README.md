# Development Stats Visualizer

A tool to visualize daily development statistics and generate GitHub Pages content.

## Features

- Processes daily development statistics from CSV files
- Generates visualizations using Plotly
- Exports results for GitHub Pages deployment

## Usage

Create environment and install dependencies:
```bash
$(poetry env activate)
poetry install
```

Run the visualization script:

```bash
python visualize_stats.py
```

The script will process CSV files in the `daily/` directory and generate output in the `gh_pages/` directory.

## GitHub Actions Deployment

To enable automatic deployment to GitHub Pages, you must configure a Personal Access Token (PAT) with `repo` scope.

### How to Create a Personal Access Token (PAT)

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).
2. Click **"Fine-grained tokens"** or **"Generate new token (classic)"** (either works for public repo deployment).
3. Give your token a name (e.g., "gh-pages deploy token") and set an expiration date if desired.
4. Under **"Repository permissions"**, select at least:
	- `Contents: Read and write`
	- For classic tokens, select the `repo` scope.
5. Click **"Generate token"** and copy the token value. You will not be able to see it again!

### Add the PAT as a Repository Secret

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
2. Name: `PUBLIC_REPO_PAT`
3. Value: (paste your PAT here)

### Usage

The workflow will use this secret to push updates to the `gh-pages` branch for GitHub Pages deployment.

**Note:** The default `GITHUB_TOKEN` does not have write permissions if repository settings restrict it. The `PUBLIC_REPO_PAT` is required for deployment in this case.
