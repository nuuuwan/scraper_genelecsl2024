function print_highlight {
    echo '----------------------------------------'
    Write-Host -ForegroundColor Blue $args[0]
    echo '----------------------------------------'
}

print_highlight("1. Running scrape")
python workflows/scrape/eclk.py


print_highlight("2. Copying to React Repo & Pushing to GitHub")
cp C:\Users\ASUS\AppData\Local\Temp\scraper_genelecsl2024\eclk\election.tsv C:\Users\ASUS\Not.Dropbox\CODING\js_react\election\public\data\elections\government-elections-parliamentary.regions-ec.2024.tsv

cd C:\Users\ASUS\Not.Dropbox\CODING\js_react\election
git add *
git commit -m "updated election data"
git push origin main

cd C:\Users\ASUS\Dropbox\_CODING\py\scraper_genelecsl2024
print_highlight("// All Done!")