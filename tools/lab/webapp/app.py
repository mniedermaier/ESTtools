#!/usr/bin/env python3
"""
Embedded Security Testing - Lab Web Interface
Educational tool for firmware analysis and embedded systems security
"""

import os
import subprocess
import uuid
import mimetypes
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/data/uploads'
app.config['EXTRACT_FOLDER'] = '/data/extracts'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

ALLOWED_EXTENSIONS = {'bin', 'img', 'fw'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXTRACT_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filepath):
    """Get file type using file command"""
    try:
        result = subprocess.run(['file', '-b', filepath], capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except:
        return 'unknown'


def is_text_file(filepath):
    """Check if file is likely a text file"""
    mime, _ = mimetypes.guess_type(filepath)
    if mime and mime.startswith('text'):
        return True

    text_extensions = {'.txt', '.conf', '.cfg', '.ini', '.sh', '.py', '.js', '.html',
                       '.css', '.xml', '.json', '.md', '.c', '.h', '.cpp', '.hpp',
                       '.lua', '.pl', '.rb', '.php', '.asp', '.cgi', '.htaccess'}
    ext = os.path.splitext(filepath)[1].lower()
    if ext in text_extensions:
        return True

    # Check file content
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return False
            try:
                chunk.decode('utf-8')
                return True
            except:
                return False
    except:
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tools/md5check', methods=['POST'])
def md5check():
    """Analyze firmware MD5 checksum"""
    if 'firmware' not in request.files:
        return jsonify({'error': 'No firmware file provided'}), 400

    file = request.files['firmware']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        try:
            result = subprocess.run(
                ['mktplinkfw', '-i', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            output = "Error: Analysis timed out"
        except Exception as e:
            output = f"Error: {str(e)}"
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify({'output': output})

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/tools/extract', methods=['POST'])
def extract_firmware():
    """Extract firmware filesystem"""
    if 'firmware' not in request.files:
        return jsonify({'error': 'No firmware file provided'}), 400

    file = request.files['firmware']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        extract_id = uuid.uuid4().hex[:12]
        unique_name = f"{extract_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        extract_dir = os.path.join(app.config['EXTRACT_FOLDER'], extract_id)

        file.save(filepath)
        os.makedirs(extract_dir, exist_ok=True)

        try:
            # Extract using binwalk
            result = subprocess.run(
                ['binwalk', '--run-as=root', '-e', '-C', extract_dir, filepath],
                capture_output=True,
                text=True,
                timeout=120
            )
            output = result.stdout + result.stderr

            # Count extracted files
            file_count = 0
            if os.path.exists(extract_dir):
                for root, dirs, files in os.walk(extract_dir):
                    file_count += len(files)

            output += f"\n\nExtracted {file_count} files."

            return jsonify({
                'output': output,
                'extract_id': extract_id,
                'file_count': file_count
            })

        except subprocess.TimeoutExpired:
            return jsonify({'output': "Error: Extraction timed out", 'extract_id': None})
        except Exception as e:
            return jsonify({'output': f"Error: {str(e)}", 'extract_id': None})
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/browse/<extract_id>')
@app.route('/browse/<extract_id>/<path:subpath>')
def browse_files(extract_id, subpath=''):
    """Browse extracted files"""
    extract_dir = os.path.join(app.config['EXTRACT_FOLDER'], secure_filename(extract_id))

    if not os.path.exists(extract_dir):
        return jsonify({'error': 'Extraction not found'}), 404

    current_path = os.path.join(extract_dir, subpath) if subpath else extract_dir
    current_path = os.path.normpath(current_path)

    # Security check - ensure we're still within extract_dir
    if not current_path.startswith(extract_dir):
        return jsonify({'error': 'Invalid path'}), 403

    if not os.path.exists(current_path):
        return jsonify({'error': 'Path not found'}), 404

    if os.path.isfile(current_path):
        # Return file info
        file_type = get_file_type(current_path)
        is_text = is_text_file(current_path)
        size = os.path.getsize(current_path)

        return jsonify({
            'type': 'file',
            'name': os.path.basename(current_path),
            'path': subpath,
            'size': size,
            'file_type': file_type,
            'is_text': is_text
        })

    # It's a directory - list contents
    items = []
    try:
        for entry in sorted(os.listdir(current_path)):
            entry_path = os.path.join(current_path, entry)
            rel_path = os.path.join(subpath, entry) if subpath else entry

            if os.path.isdir(entry_path):
                items.append({
                    'name': entry,
                    'type': 'directory',
                    'path': rel_path
                })
            else:
                size = os.path.getsize(entry_path)
                items.append({
                    'name': entry,
                    'type': 'file',
                    'path': rel_path,
                    'size': size
                })
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403

    return jsonify({
        'type': 'directory',
        'path': subpath,
        'items': items,
        'parent': os.path.dirname(subpath) if subpath else None
    })


@app.route('/view/<extract_id>/<path:filepath>')
def view_file(extract_id, filepath):
    """View file contents"""
    extract_dir = os.path.join(app.config['EXTRACT_FOLDER'], secure_filename(extract_id))
    full_path = os.path.normpath(os.path.join(extract_dir, filepath))

    # Security check
    if not full_path.startswith(extract_dir):
        return jsonify({'error': 'Invalid path'}), 403

    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404

    if not os.path.isfile(full_path):
        return jsonify({'error': 'Not a file'}), 400

    size = os.path.getsize(full_path)
    file_type = get_file_type(full_path)

    # For text files, return content
    if is_text_file(full_path):
        try:
            with open(full_path, 'r', errors='replace') as f:
                # Limit to first 100KB
                content = f.read(100 * 1024)
                truncated = size > 100 * 1024
            return jsonify({
                'type': 'text',
                'content': content,
                'truncated': truncated,
                'size': size,
                'file_type': file_type
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # For binary files, return hex dump
    try:
        result = subprocess.run(
            ['xxd', '-l', '2048', full_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        return jsonify({
            'type': 'binary',
            'hexdump': result.stdout,
            'size': size,
            'file_type': file_type
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<extract_id>/<path:filepath>')
def download_file(extract_id, filepath):
    """Download a file"""
    extract_dir = os.path.join(app.config['EXTRACT_FOLDER'], secure_filename(extract_id))
    full_path = os.path.normpath(os.path.join(extract_dir, filepath))

    # Security check
    if not full_path.startswith(extract_dir):
        return jsonify({'error': 'Invalid path'}), 403

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(full_path, as_attachment=True)


@app.route('/cleanup/<extract_id>', methods=['POST'])
def cleanup_extraction(extract_id):
    """Clean up an extraction"""
    extract_dir = os.path.join(app.config['EXTRACT_FOLDER'], secure_filename(extract_id))
    if os.path.exists(extract_dir):
        subprocess.run(['rm', '-rf', extract_dir], capture_output=True)
    return jsonify({'success': True})


@app.route('/tools/strings', methods=['POST'])
def analyze_strings():
    """Extract strings from firmware"""
    if 'firmware' not in request.files:
        return jsonify({'error': 'No firmware file provided'}), 400

    file = request.files['firmware']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        try:
            result = subprocess.run(
                ['strings', '-n', '8', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            lines = result.stdout.strip().split('\n')[:200]  # Limit output
            output = f"Found {len(lines)} strings (showing first 200):\n\n" + '\n'.join(lines)
        except subprocess.TimeoutExpired:
            output = "Error: Analysis timed out"
        except Exception as e:
            output = f"Error: {str(e)}"
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify({'output': output})

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/tools/hexdump', methods=['POST'])
def hexdump():
    """Show hex dump of firmware header"""
    if 'firmware' not in request.files:
        return jsonify({'error': 'No firmware file provided'}), 400

    file = request.files['firmware']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        try:
            result = subprocess.run(
                ['xxd', '-l', '512', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = f"Firmware header (first 512 bytes):\n\n{result.stdout}"
        except subprocess.TimeoutExpired:
            output = "Error: Analysis timed out"
        except Exception as e:
            output = f"Error: {str(e)}"
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify({'output': output})

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/tools/fileinfo', methods=['POST'])
def fileinfo():
    """Get file information"""
    if 'firmware' not in request.files:
        return jsonify({'error': 'No firmware file provided'}), 400

    file = request.files['firmware']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        try:
            # File type
            file_result = subprocess.run(['file', filepath], capture_output=True, text=True, timeout=10)

            # Size
            stat_result = subprocess.run(['stat', '-c', 'Size: %s bytes', filepath], capture_output=True, text=True, timeout=10)

            # MD5
            md5_result = subprocess.run(['md5sum', filepath], capture_output=True, text=True, timeout=10)

            # Binwalk scan
            binwalk_result = subprocess.run(['binwalk', filepath], capture_output=True, text=True, timeout=30)

            output = f"=== File Information ===\n"
            output += f"Filename: {filename}\n"
            output += f"{stat_result.stdout}"
            output += f"MD5: {md5_result.stdout.split()[0]}\n"
            output += f"Type: {file_result.stdout.split(':', 1)[1].strip()}\n\n"
            output += f"=== Binwalk Analysis ===\n{binwalk_result.stdout}"

        except subprocess.TimeoutExpired:
            output = "Error: Analysis timed out"
        except Exception as e:
            output = f"Error: {str(e)}"
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify({'output': output})

    return jsonify({'error': 'Invalid file type'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
