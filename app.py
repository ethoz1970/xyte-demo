import os
import json
from flask import Flask, render_template, send_from_directory, jsonify

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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5051))
    app.run(host='0.0.0.0', port=port, threaded=True)
