import os
   import sys
   import requests
   import subprocess
   import re
   import json

   def read_file(file_path):
       try:
           with open(file_path, 'r', encoding='utf-8') as file:
               return file.read()
       except Exception as e:
           return f"Error reading file {file_path}: {str(e)}"

   def write_file(file_path, content):
       try:
           with open(file_path, 'w', encoding='utf-8') as file:
               file.write(content)
           return f"Successfully updated {file_path}"
       except Exception as e:
           return f"Error writing to {file_path}: {str(e)}"

   def git_commit_push(repo_path, commit_message):
       try:
           subprocess.run(['git', '-C', repo_path, 'add', '.'], check=True)
           subprocess.run(['git', '-C', repo_path, 'commit', '-m', commit_message], check=True)
           subprocess.run(['git', '-C', repo_path, 'push', 'origin', 'main'], check=True)
           return f"Committed and pushed to {repo_path}: {commit_message}"
       except subprocess.CalledProcessError as e:
           return f"Git error in {repo_path}: {str(e)}"

   def query_grok(prompt):
       api_key = os.getenv("XAI_API_KEY")
       if not api_key:
           return "Error: XAI_API_KEY environment variable not set"

       headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
       data = {"prompt": prompt}

       # Extract file paths from prompt
       file_paths = re.findall(r'C:\\Users\\shaun\\OneDrive\\Documents\\GitHub\\[^ ]+', prompt)
       file_contents = {}
       for path in file_paths:
           if os.path.exists(path):
               file_contents[path] = read_file(path)
           else:
               file_contents[path] = f"File not found: {path}"

       # Include file contents in prompt
       if file_contents:
           data["prompt"] = f"{prompt}\n\nFile contents:\n" + "\n".join([f"{path}:\n{file_contents[path]}" for path in file_contents])

       try:
           response = requests.post("https://api.x.ai/v1/grok", headers=headers, json=data, timeout=30)
           response.raise_for_status()
           api_response = response.json().get("response", "Error: No response field in API response")
       except requests.exceptions.RequestException as e:
           return f"API request failed: {str(e)}"

       # Handle file modification suggestions
       if "UPDATE_FILE" in api_response:
           try:
               update_match = re.search(r"UPDATE_FILE: (.*?)\nCONTENT: (.*?)(?=\nUPDATE_FILE|$)", api_response, re.DOTALL)
               if update_match:
                   file_path, new_content = update_match.groups()
                   write_result = write_file(file_path, new_content.strip())
                   repo_path = os.path.dirname(file_path) if os.path.isfile(file_path) else file_path
                   git_result = git_commit_push(repo_path, f"Updated {file_path} via grok CLI")
                   return f"{api_response}\n{write_result}\n{git_result}"
           except Exception as e:
               return f"{api_response}\nError processing file update: {str(e)}"

       return api_response

   if __name__ == "__main__":
       prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello, Grok! Provide a test response."
       print(query_grok(prompt))