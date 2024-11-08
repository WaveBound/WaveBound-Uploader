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

        # Initialize GitHub connection
        g = github.Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

        # Get existing folders in the repository
        try:
            existing_contents = repo.get_contents(REPO_PATH)
            existing_folders = [content.name for content in existing_contents if content.type == 'dir']
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

        # Prepare file content
        content = base64.b64decode(file_data['content'])

        # Upload to GitHub
        repo.create_file(
            path=f"{REPO_PATH}{file_data['filename']}", 
            message=f"Upload {file_data['filename']}", 
            content=content
        )

        return jsonify({"success": True, "message": f"Uploaded {file_data['filename']}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health_check():
    return jsonify({"status": "Server is running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
