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

        # Get existing folders in the repository
        # Check if file already exists
        try:
            existing_contents = repo.get_contents(REPO_PATH)
            existing_folders = [content.name for content in existing_contents if content.type == 'dir']
            repo.get_contents(f"{REPO_PATH}{filename}")
            return jsonify({"error": "File Name Taken, Rename To Upload"}), 409
        except github.GithubException as e:
            existing_folders = []
        # Extract folder name from filename (assuming filename includes full path)
        folder_name = os.path.dirname(file_data['filename'])
        # Check if folder already exists
        if folder_name in existing_folders:
            return jsonify({
                "error": "Folder already exists", 
                "message": "The folder already exists on GitHub. Skipping upload."
            }), 409
            if e.status != 404:  # If error is not "file not found"
                raise e
        
        # Prepare file content
        content = base64.b64decode(file_data['content'])

        # Upload to GitHub
        repo.create_file(
            path=f"{REPO_PATH}{file_data['filename']}", 
            message=f"Upload {file_data['filename']}", 
            path=f"{REPO_PATH}{filename}", 
            message=f"Upload {filename}", 
            content=content
        )

        return jsonify({"success": True, "message": f"Uploaded {file_data['filename']}"}), 200
        return jsonify({"success": True, "message": f"Uploaded {filename}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health_check():
    return jsonify({"status": "Server is running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
