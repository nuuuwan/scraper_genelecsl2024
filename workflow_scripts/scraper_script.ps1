print_highlight("1. ECLK Scrape")
python workflows/scrape/eclk.py

print_highlight("2. CommonLocalState Update")
python .\src\common_local_state\CommonLocalState.py

print_highlight("3. Local App File DB Copy")
cp C:\Users\ASUS\AppData\Local\Temp\scraper_genelecsl2024\eclk\election.tsv C:\Users\ASUS\Not.Dropbox\CODING\js_react\election\public\data\elections\government-elections-parliamentary.regions-ec.2024.tsv

print_highlight("4. Local App to Remote App Push/Deploy")
cd C:\Users\ASUS\Not.Dropbox\CODING\js_react\election
git add *
git commit -m "updated election data"
git push origin main

cd C:\Users\ASUS\Dropbox\_CODING\py\scraper_genelecsl2024
print_highlight("// All Done!")