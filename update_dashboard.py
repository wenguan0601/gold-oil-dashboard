name: Daily Dashboard Update

on:
  schedule:
    - cron: '0 2 * * *' # 每天北京时间 10:00
  workflow_dispatch: # 允许手动触发

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: pip install requests beautifulsoup4
        
      - name: Run script
        run: python update_dashboard.py
        
      - name: Commit and Push
        run: |
          git config --global user.name "Auto Bot"
          git config --global user.email "bot@example.com"
          git add index.html
          git commit -m "Auto update dashboard data" || echo "No changes"
          git push
