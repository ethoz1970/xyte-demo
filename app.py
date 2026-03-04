import os
import json
from flask import Flask, Response, render_template, send_from_directory, jsonify, request

app = Flask(__name__)

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR     = os.path.join(BASE_DIR, 'videos')
SCENARIOS_FILE = os.path.join(BASE_DIR, 'scenarios.json')


def load_scenarios():
    """Load scenarios.json and return only entries whose video file exists."""
    with open(SCENARIOS_FILE) as f:
        all_scenarios = json.load(f)
    return [
        s for s in all_scenarios
        if os.path.isfile(os.path.join(VIDEOS_DIR, s['file']))
    ]


@app.route('/')
def index():
    return render_template('demo.html', scenarios=load_scenarios())


@app.route('/scenarios')
def get_scenarios():
    return jsonify(load_scenarios())


@app.route('/videos/<path:filename>')
def serve_video(filename):
    """Serve video files with range-request support (required by <video> elements)."""
    return send_from_directory(VIDEOS_DIR, filename)


@app.route('/upload', methods=['POST'])
def upload_video():
    """
    Password-protected upload endpoint for pushing video files onto the volume.

    Usage:
        curl -X POST https://<your-domain>/upload \\
             -H "X-Upload-Key: <UPLOAD_KEY>" \\
             -F "file=@/local/path/to/video.avi" \\
             -F "name=scenario-1.avi"

    Set the UPLOAD_KEY environment variable in Railway → Variables.
    """
    upload_key = os.environ.get('UPLOAD_KEY', '')
    if not upload_key or request.headers.get('X-Upload-Key', '') != upload_key:
        return jsonify({"error": "unauthorized"}), 401

    file = request.files.get('file')
    name = request.form.get('name', '')

    if not file:
        return jsonify({"error": "no file provided"}), 400
    if not name:
        return jsonify({"error": "no name provided"}), 400

    # Sanitize — only allow simple filenames, no path traversal
    name = os.path.basename(name)
    if not name.lower().endswith(('.avi', '.mp4', '.mov')):
        return jsonify({"error": "only .avi / .mp4 / .mov files allowed"}), 400

    os.makedirs(VIDEOS_DIR, exist_ok=True)
    dest = os.path.join(VIDEOS_DIR, name)
    file.save(dest)
    return jsonify({"saved": name, "path": dest})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5051))
    app.run(host='0.0.0.0', port=port, threaded=True)
