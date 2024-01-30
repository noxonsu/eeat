import subprocess

scripts = [
    '1loadSerp.py',
    '2loadSummaries.py',
    '4searchProducts.py',
    '2loadSummaries.py',  # Если это не ошибка и вы действительно хотите запустить его дважды
    '3searchPrices.py',
    '5analyseProduct.py',
    '6ClasterizeFeautres.py',
    '8visualPricing.py',
    '9visual.py'

]

for script in scripts:
    subprocess.run(['python', script])
