param (
       [Parameter(Mandatory=$false, Position=0)]
       [string]$Prompt
   )
   # Load API key from .env file
   Get-Content "C:\Users\shaun\.env" | ForEach-Object {
       if ($_ -match "^XAI_API_KEY=(.+)$") {
           $env:XAI_API_KEY = $matches[1]
       }
   }
   & C:\Users\shaun\AppData\Local\Programs\Python\Python312\python.exe C:\Users\shaun\OneDrive\Documents\GitHub\campaignforge-backend\grok_query.py $Prompt