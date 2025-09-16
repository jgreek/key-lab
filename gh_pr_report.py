#!/usr/bin/env python3

import subprocess
import json
import argparse
import sys
from datetime import datetime, timedelta
import calendar

def get_date_range(period):
    """Convert period string to start and end dates."""
    now = datetime.now()
    current_year = now.year
    
    # Quarter mappings
    quarters = {
        'q1': (f"{current_year}-01-01", f"{current_year}-03-31"),
        'q2': (f"{current_year}-04-01", f"{current_year}-06-30"), 
        'q3': (f"{current_year}-07-01", f"{current_year}-09-30"),
        'q4': (f"{current_year}-10-01", f"{current_year}-12-31"),
    }
    
    # Handle previous year quarters
    prev_year_quarters = {
        f'q1-{current_year-1}': (f"{current_year-1}-01-01", f"{current_year-1}-03-31"),
        f'q2-{current_year-1}': (f"{current_year-1}-04-01", f"{current_year-1}-06-30"),
        f'q3-{current_year-1}': (f"{current_year-1}-07-01", f"{current_year-1}-09-30"),
        f'q4-{current_year-1}': (f"{current_year-1}-10-01", f"{current_year-1}-12-31"),
    }
    
    if period in quarters:
        return quarters[period]
    elif period in prev_year_quarters:
        return prev_year_quarters[period]
    elif period == 'h1':
        return (f"{current_year}-01-01", f"{current_year}-06-30")
    elif period == 'h2':
        return (f"{current_year}-07-01", f"{current_year}-12-31")
    elif period == f'h1-{current_year-1}':
        return (f"{current_year-1}-01-01", f"{current_year-1}-06-30")
    elif period == f'h2-{current_year-1}':
        return (f"{current_year-1}-07-01", f"{current_year-1}-12-31")
    elif period == '1y' or period == 'year':
        return (f"{current_year}-01-01", f"{current_year}-12-31")
    elif period == f'{current_year-1}' or period == f'year-{current_year-1}':
        return (f"{current_year-1}-01-01", f"{current_year-1}-12-31")
    elif period == 'this-month' or period == 'tm':
        start = now.replace(day=1)
        _, last_day = calendar.monthrange(now.year, now.month)
        end = now.replace(day=last_day)
        return (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    elif period == 'last-month' or period == 'lm':
        # Get first day of last month
        first_day_this_month = now.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        return (first_day_last_month.strftime('%Y-%m-%d'), last_day_last_month.strftime('%Y-%m-%d'))
    elif period == 'last-30' or period == '30d':
        end = now
        start = now - timedelta(days=30)
        return (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    elif period == 'last-90' or period == '90d':
        end = now
        start = now - timedelta(days=90)
        return (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    elif period == 'ytd':
        return (f"{current_year}-01-01", now.strftime('%Y-%m-%d'))
    else:
        # Try to parse as custom date range (YYYY-MM-DD:YYYY-MM-DD)
        if ':' in period:
            try:
                start_date, end_date = period.split(':')
                # Validate dates
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
                return (start_date, end_date)
            except ValueError:
                pass
        
        raise ValueError(f"Unknown period: {period}. Use q1-q4, h1-h2, year, this-month, last-month, 30d, 90d, ytd, or YYYY-MM-DD:YYYY-MM-DD")


def run_gh_command(cmd_args, debug=False):
    """Run a GitHub CLI command and return the result."""
    if debug:
        print(f"Running: gh {' '.join(cmd_args)}")
    
    try:
        result = subprocess.run(['gh'] + cmd_args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if debug:
            print(f"Error running gh command: {e}")
            print(f"Command: gh {' '.join(cmd_args)}")
            print(f"stderr: {e.stderr}")
        return None


def get_user_info():
    """Get current GitHub user info."""
    user_info = run_gh_command(['api', 'user'])
    if user_info:
        return json.loads(user_info)
    return None


def get_pr_details(repo, pr_number):
    """Get detailed PR information including stats."""
    pr_info = run_gh_command([
        'pr', 'view', str(pr_number),
        '--repo', repo,
        '--json', 'title,url,state,createdAt,closedAt,mergedAt,additions,deletions,changedFiles'
    ])
    
    if pr_info:
        return json.loads(pr_info)
    return None


def get_prs_from_repo(repo, author, start_date, end_date, state='all', debug=False):
    """Get PRs from a specific repository for the given author and date range."""
    if debug:
        print(f"Searching in repo: {repo}")
    
    # Use gh pr list for the specific repository
    cmd_args = ['pr', 'list', '--repo', repo, '--author', author, '--limit', '100']
    
    if state == 'merged':
        cmd_args.extend(['--state', 'merged'])
    elif state == 'closed':
        cmd_args.extend(['--state', 'closed'])
    elif state == 'open':
        cmd_args.extend(['--state', 'open'])
    # 'all' means we don't add a state filter
    
    cmd_args.extend(['--json', 'title,url,createdAt,closedAt,state,number,additions,deletions,changedFiles'])
    
    result = run_gh_command(cmd_args, debug=debug)
    
    if not result:
        return []
    
    prs = json.loads(result)
    
    # Filter by date range
    filtered_prs = []
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    for pr in prs:
        created_dt = datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00')).replace(tzinfo=None)
        if start_dt <= created_dt <= end_dt:
            # Add repository info
            pr['repository'] = {'nameWithOwner': repo}
            filtered_prs.append(pr)
    
    return filtered_prs


def search_pull_requests(author, start_date, end_date, state='all', repo=None, debug=False):
    """Search for pull requests in the date range."""
    all_prs = []
    
    if repo:
        # Search in specific repo
        prs = get_prs_from_repo(repo, author, start_date, end_date, state, debug)
        all_prs.extend(prs)
    else:
        # Search in default repos (common work repositories)
        default_repos = [
            '9537-GenAI/gpa',
            '9537-GenAI/openai-chatbot-ui'
        ]
        
        print(f"Searching in default repositories: {', '.join(default_repos)}")
        
        for repo_name in default_repos:
            if debug:
                print(f"\nSearching in {repo_name}...")
            prs = get_prs_from_repo(repo_name, author, start_date, end_date, state, debug)
            if prs:
                print(f"Found {len(prs)} PRs in {repo_name}")
                all_prs.extend(prs)
    
    if debug:
        print(f"Total PRs found: {len(all_prs)}")
    
    return all_prs


def format_pr_summary(prs, start_date, end_date):
    """Format PR data for performance review."""
    if not prs:
        return f"No pull requests found for period {start_date} to {end_date}"
    
    # Group by repository
    repos = {}
    total_additions = 0
    total_deletions = 0
    total_files = 0
    
    for pr in prs:
        repo_name = pr['repository']['nameWithOwner']
        if repo_name not in repos:
            repos[repo_name] = []
        repos[repo_name].append(pr)
        
        total_additions += pr.get('additions', 0)
        total_deletions += pr.get('deletions', 0)
        total_files += pr.get('changedFiles', 0)
    
    # Count by state
    merged_count = len([pr for pr in prs if pr['state'] == 'MERGED'])
    open_count = len([pr for pr in prs if pr['state'] == 'OPEN'])
    closed_count = len([pr for pr in prs if pr['state'] == 'CLOSED'])
    
    # Format output
    output = []
    output.append(f"📊 PULL REQUEST SUMMARY ({start_date} to {end_date})")
    output.append("=" * 60)
    output.append(f"Total PRs: {len(prs)}")
    output.append(f"  • Merged: {merged_count}")
    output.append(f"  • Open: {open_count}")  
    output.append(f"  • Closed: {closed_count}")
    output.append(f"Code Changes: +{total_additions:,} -{total_deletions:,} lines across {total_files:,} files")
    output.append("")
    
    # List by repository
    for repo_name in sorted(repos.keys()):
        repo_prs = repos[repo_name]
        output.append(f"📁 {repo_name} ({len(repo_prs)} PRs)")
        output.append("-" * 40)
        
        for pr in sorted(repo_prs, key=lambda x: x['createdAt'], reverse=True):
            state_emoji = {"MERGED": "✅", "OPEN": "🔄", "CLOSED": "❌"}
            emoji = state_emoji.get(pr['state'], "❓")
            
            created = datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
            changes = f"+{pr.get('additions', 0)} -{pr.get('deletions', 0)}"
            
            output.append(f"  {emoji} {pr['title']}")
            output.append(f"     {created} | {changes} | {pr['url']}")
        
        output.append("")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Generate GitHub PR reports for performance reviews',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Time Period Options:
  q1, q2, q3, q4        - Current year quarters
  q1-2023, q2-2023      - Previous year quarters  
  h1, h2                - Current year halves
  h1-2023, h2-2023      - Previous year halves
  year, 1y              - Current year
  2023, year-2023       - Specific year
  this-month, tm        - Current month
  last-month, lm        - Previous month
  30d, last-30          - Last 30 days
  90d, last-90          - Last 90 days
  ytd                   - Year to date
  2023-01-01:2023-12-31 - Custom date range

Examples:
  %(prog)s q3                    # Q3 current year
  %(prog)s q4-2023               # Q4 2023
  %(prog)s last-month --repo myorg/myrepo
  %(prog)s ytd --state merged --output summary.txt
        '''
    )
    
    parser.add_argument('period', help='Time period (see options below)')
    parser.add_argument('--repo', '-r', help='Filter by specific repository (org/repo)')
    parser.add_argument('--state', '-s', choices=['all', 'open', 'closed', 'merged'], 
                       default='all', help='PR state filter')
    parser.add_argument('--output', '-o', help='Output file (default: print to stdout)')
    parser.add_argument('--format', '-f', choices=['summary', 'json', 'csv'], 
                       default='summary', help='Output format')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    try:
        start_date, end_date = get_date_range(args.period)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Get current user
    user = get_user_info()
    if not user:
        print("Error: Could not get GitHub user info. Make sure you're logged in with 'gh auth login'")
        sys.exit(1)
    
    username = user['login']
    print(f"Fetching PRs for {username} from {start_date} to {end_date}...")
    
    # Search for PRs
    prs = search_pull_requests(username, start_date, end_date, args.state, args.repo, args.debug)
    
    # Format output
    if args.format == 'summary':
        output = format_pr_summary(prs, start_date, end_date)
    elif args.format == 'json':
        output = json.dumps(prs, indent=2)
    elif args.format == 'csv':
        # Simple CSV format
        output = "Title,Repository,State,Created,URL,Additions,Deletions,Files\n"
        for pr in prs:
            created = datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
            output += f'"{pr["title"]}",{pr["repository"]["nameWithOwner"]},{pr["state"]},{created},{pr["url"]},{pr.get("additions", 0)},{pr.get("deletions", 0)},{pr.get("changedFiles", 0)}\n'
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
