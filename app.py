from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import psutil
import subprocess

app = Flask(__name__)
CORS(app)

stress_process = None

@app.route('/')
def index():
    hostname = subprocess.check_output(['hostname']).decode('utf-8').strip()
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>CloudFolks HUB - CPU Control</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        .branding { color: #0077B5; font-weight: bold; font-size: 24px; margin-top: 20px; }
        .meter { height: 20px; background: #555; border-radius: 25px; width: 70%; margin: 0 auto; }
        .meter > span { display: block; height: 100%; border-radius: 20px; background-color: #33cc33; }
    </style>
</head>
<body onload="updateCpuUsage()">
    <h2 class="branding">CloudFolks HUB</h2>
    <p>Hostname: {{ hostname }}</p>
    <div class="meter"><span id="cpu-percentage-meter" style="width: 0%;"></span></div>
    <p id="cpu-text" style="margin-top: 20px;">CPU Usage: 0%</p>
    <button onclick="increaseLoad()">Increase CPU Load</button>
    <button onclick="cancelLoad()">Cancel Load</button>
    <script>
        function updateCpuUsage() {
            fetch('/cpu_percentage')
                .then(response => response.json())
                .then(data => {
                    const percentage = data.cpu;
                    document.getElementById('cpu-percentage-meter').style.width = percentage + '%';
                    document.getElementById('cpu-text').innerText = 'CPU Usage: ' + percentage + '%';
                });
        }
        function increaseLoad() { fetch('/increase_load'); }
        function cancelLoad() { fetch('/cancel_load'); }
        setInterval(updateCpuUsage, 2000);
    </script>
</body>
</html>
    """, hostname=hostname)

@app.route('/cpu_percentage')
def cpu_percentage():
    return jsonify(cpu=psutil.cpu_percent(interval=1))

@app.route('/increase_load')
def increase_load():
    global stress_process
    if not stress_process:
        stress_process = subprocess.Popen(['stress', '--cpu', '1'])
    return jsonify(status='Load Increased')

@app.route('/cancel_load')
def cancel_load():
    global stress_process
    if stress_process:
        subprocess.run(['pkill', 'stress'])
        stress_process = None
    return jsonify(status='Load Cancelled')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
