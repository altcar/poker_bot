$ErrorActionPreference = "Continue"
$root = "L:\save\userdata\Downloads\poker_bot"
Set-Location $root
$log = Join-Path $root "eval_results.txt"
"Started $(Get-Date -Format o)" | Tee-Object -FilePath $log -Append

foreach ($x in @("a","b","c","d","e")) {
    Copy-Item "model_$x.py" "model.py" -Force
    "" | Out-File -FilePath $log -Append -Encoding utf8
    "================ model_$x ================" | Tee-Object -FilePath $log -Append

    "--- pytest tests/test_model.py -q ---" | Tee-Object -FilePath $log -Append
    & .\.venv\Scripts\python -m pytest tests/test_model.py -q 2>&1 |
        Tee-Object -FilePath $log -Append

    "--- evals --opponents tight equity --deals 1000 --table ---" | Tee-Object -FilePath $log -Append
    & .\.venv\Scripts\python -m evals --opponents tight equity --deals 1000 --table 2>&1 |
        Tee-Object -FilePath $log -Append

    "--- evals (default, 500 deals, all dummies) ---" | Tee-Object -FilePath $log -Append
    & .\.venv\Scripts\python -m evals 2>&1 |
        Tee-Object -FilePath $log -Append
}

# Leave the submitted variant (B) in place.
Copy-Item "model_b.py" "model.py" -Force
"Finished $(Get-Date -Format o)" | Tee-Object -FilePath $log -Append
