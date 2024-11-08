from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import github
import base64

app = Flask(__name__)
CORS(app)

# GitHub configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = "WaveBound"
REPO_NAME = "WaveBound_Configs"
REPO_PATH = "Configs/"

@app.route('/upload', methods=['POST'])
def upload_to_github():
    try:
        # Get file data from request
        file_data = request.json
        
        # Validate required fields
        if not all(key in file_data for key in ['filename', 'content']):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Check if file is JSON
        filename = file_data['filename']
        if not filename.lower().endswith('.json'):
            return jsonify({"error": "Only JSON files are allowed"}), 400
        
        # Initialize GitHub connection
        g = github.Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
        
        # Check if the folder already exists
        try:
            repo.get_contents(REPO_PATH)
            # If folder exists, skip uploading and return a message
            return jsonify({"error": "Folder already exists, skipping upload."}), 409
        except github.GithubException as e:
            if e.status == 404:  # Folder does not exist
                # Create the folder (by creating a dummy file)
                repo.create_file(
                    path=f"{REPO_PATH}.keep", 
                    message="Create folder for Configs", 
                    content=""
                )
            else:
                raise e
        
        # Since we skip uploading if the folder exists, the following code will not run
        # Check if file already exists
        try:
            repo.get_contents(f"{REPO_PATH}{filename}")
            return jsonify({"error": "File Name Taken, Rename To Upload"}), 409
        except github.GithubException as e:
            if e.status != 404:  # If error is not "file not found"
                raise e
        
        # Prepare file content
        content = base64.b64decode(file_data['content'])
        
        # Upload to GitHub
        repo.create_file(
            path=f"{REPO_PATH}{filename}", 
            message=f"Upload {filename}", 
            content=content
        )
        
        return jsonify({"success": True, "message": f"Uploaded {filename}"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health_check():
    return jsonify({"status": "Server is running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
