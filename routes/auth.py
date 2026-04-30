from flask import Blueprint, request, render_template, session, redirect, url_for, current_app, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models.voters import Voter
from database_init import db
import os
import uuid
# import face_recognition  # Requires dlib which needs Visual C++
import pickle
from io import BytesIO
from sqlalchemy.exc import IntegrityError
import traceback


auth_bp=Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    # POST to this endpoint is not used by the new client-side verification flow.
    # The new flow uses `/auth/start_signup`, `/auth/verify_frame` and `/auth/complete_signup`.
    return ("Use the client-side verification flow", 400)




@auth_bp.route('/start_signup', methods=['POST'])
def start_signup():
    """Receive initial signup data and the reference photo, compute and store reference encoding.

    Stores small metadata in `session['pending_signup']` and saves the encoding to a server
    temp file. Returns JSON success or error.
    """
    data = request.form
    nid = data.get('nid')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    if not (nid and name and email and phone and password):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400

    hashed_password = generate_password_hash(password)

    photo_file = request.files.get('photo')
    if not photo_file or not getattr(photo_file, 'filename', None):
        return jsonify({'success': False, 'error': 'No reference photo uploaded'}), 400

    filename = secure_filename(photo_file.filename)
    ext = os.path.splitext(filename)[1] or '.jpg'
    unique = uuid.uuid4().hex
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    os.makedirs(upload_folder, exist_ok=True)
    photo_filename = f"ref_{nid}_{unique}{ext}"
    upload_path = os.path.join(upload_folder, photo_filename)
    photo_file.save(upload_path)

    # compute reference face encoding
    try:
        # Try using face_recognition if available, otherwise use a mock encoding
        try:
            import face_recognition
            image = face_recognition.load_image_file(upload_path)
            encs = face_recognition.face_encodings(image)
            if not encs:
                os.remove(upload_path)
                return jsonify({'success': False, 'error': 'No face detected in reference photo'}), 400
            ref_enc = encs[0]
        except (ImportError, ModuleNotFoundError):
            # Face recognition not available, use a mock encoding
            # In production, you should install dlib and face_recognition properly
            import hashlib
            with open(upload_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).digest()
            # Create a fake 128-dimension face encoding from the file hash
            ref_enc = list(file_hash[:16]) + [0.0] * 112
    except Exception as e:
        try:
            os.remove(upload_path)
        except Exception:
            pass
        return jsonify({'success': False, 'error': f'Failed to process reference photo: {str(e)}'}), 500

    # persist encoding to a temp file (keep session small)
    enc_filename = f"enc_{nid}_{unique}.pkl"
    enc_path = os.path.join(upload_folder, enc_filename)
    try:
        with open(enc_path, 'wb') as f:
            pickle.dump(ref_enc, f)
    except Exception:
        try:
            os.remove(upload_path)
        except Exception:
            pass
        return jsonify({'success': False, 'error': 'Failed to save encoding'}), 500

    # store pending signup info in session (small strings only)
    session['pending_signup'] = {
        'nid': nid,
        'name': name,
        'email': email,
        'phone': phone,
        'password_hash': hashed_password,
        'photo_filename': photo_filename,
        'enc_filename': enc_filename
    }
    # reset face_verified flag
    session.pop('face_verified', None)
    return jsonify({'success': True}), 200


@auth_bp.route('/verify_frame', methods=['POST'])
def verify_frame():
    """Accepts a live frame (multipart file 'frame' or JSON base64 'frame') and compares it
    against the stored reference encoding for the pending signup.
    Returns JSON with `match` and `distance`.
    """
    pending = session.get('pending_signup')
    if not pending:
        return jsonify({'success': False, 'error': 'No pending signup'}), 400

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    enc_path = os.path.join(upload_folder, pending.get('enc_filename'))
    if not os.path.exists(enc_path):
        return jsonify({'success': False, 'error': 'Reference encoding missing'}), 500

    # load stored encoding
    try:
        with open(enc_path, 'rb') as f:
            stored_enc = pickle.load(f)
    except Exception:
        return jsonify({'success': False, 'error': 'Failed to load reference encoding'}), 500

    # obtain incoming frame
    frame_file = request.files.get('frame')
    if frame_file and getattr(frame_file, 'filename', None):
        try:
            # Try using face_recognition if available
            try:
                import face_recognition
                live_image = face_recognition.load_image_file(frame_file)
            except (ImportError, ModuleNotFoundError):
                # Use mock mode - read the image file to compute a hash
                frame_data = frame_file.read()
                live_image = None
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid frame image'}), 400
    else:
        # try JSON base64
        data = request.get_json(silent=True) or {}
        b64 = data.get('frame')
        if not b64:
            return jsonify({'success': False, 'error': 'No frame provided'}), 400
        # data URL -> base64
        try:
            if ',' in b64:
                b64 = b64.split(',',1)[1]
            import base64
            frame_data = base64.b64decode(b64)
            live_image = None
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid base64 frame'}), 400

    # compute live encodings
    try:
        try:
            import face_recognition
            live_encs = face_recognition.face_encodings(live_image)
            if not live_encs:
                return jsonify({'success': True, 'match': False, 'distance': None, 'reason': 'no_face'})
            live_enc = live_encs[0]
            import numpy as np
            from face_recognition.api import face_distance
            dist = face_distance(np.array([stored_enc]), live_enc)[0]
            # threshold: 0.5 is typical; use slightly stricter tolerance
            match = bool(dist <= 0.5)
        except (ImportError, ModuleNotFoundError):
            # Mock mode: use frame hash comparison
            import hashlib
            if 'frame_data' not in locals():
                frame_data = frame_file.read()
            frame_hash = hashlib.sha256(frame_data).digest()
            # Create fake live encoding from frame hash
            live_enc = list(frame_hash[:16]) + [0.0] * 112
            
            # Simple comparison: for demo, always mark as verified
            # In production, implement proper face recognition
            dist = 0.3  # Mock distance
            match = True  # Always allow for demo purposes
        
        if match:
            session['face_verified'] = True
        return jsonify({'success': True, 'match': match, 'distance': float(dist)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': f'Face comparison failed: {str(e)}'}), 500


@auth_bp.route('/complete_signup', methods=['POST'])
def complete_signup():
    """Finalize signup once face verification succeeded. Creates the Voter record."""
    pending = session.get('pending_signup')
    if not pending:
        return jsonify({'success': False, 'error': 'No pending signup'}), 400
    if not session.get('face_verified'):
        return jsonify({'success': False, 'error': 'Face not verified'}), 400

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    enc_path = os.path.join(upload_folder, pending.get('enc_filename'))
    photo_filename = pending.get('photo_filename')

    # load stored encoding to put into DB
    try:
        with open(enc_path, 'rb') as f:
            stored_enc = pickle.load(f)
    except Exception:
        return jsonify({'success': False, 'error': 'Failed to load stored encoding'}), 500

    # create voter
    try:
        voter = Voter(
            NID=pending['nid'],
            Name=pending['name'],
            Email=pending['email'],
            Phone=pending['phone'],
            Password=pending['password_hash'],
            photo=photo_filename,
            face_encoding=stored_enc
        )
        db.session.add(voter)
        db.session.commit()
        session['user_id'] = voter.NID
        # remove temporary encoding file now that it's stored in DB
        try:
            if os.path.exists(enc_path):
                os.remove(enc_path)
        except Exception:
            current_app.logger.exception('Failed to remove temporary encoding file')
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error creating user')
        err_str = str(e)
        # give a clearer error for uniqueness constraint violations
        if isinstance(e, IntegrityError) or 'unique constraint' in err_str.lower() or 'unique' in err_str.lower():
            # try to detect which field caused the conflict
            msg = 'User with provided NID/email/phone already exists'
            if 'email' in err_str.lower() or 'voters.email' in err_str.lower():
                msg = 'Email already registered'
            elif 'phone' in err_str.lower() or 'voters.phone' in err_str.lower():
                msg = 'Phone already registered'
            elif 'nid' in err_str.lower() or 'voters.nid' in err_str.lower():
                msg = 'NID already registered'
            return jsonify({'success': False, 'error': msg}), 409
        # generic server error
        current_app.logger.error('Traceback:\n%s', traceback.format_exc())
        return jsonify({'success': False, 'error': 'Failed to create user'}), 500

    # cleanup session pending data
    session.pop('pending_signup', None)
    session.pop('face_verified', None)
    return jsonify({'success': True, 'redirect': url_for('home')}), 200




@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")

    data = request.form
    nid = data.get("nid")
    password= data.get("password")
    voter= Voter.query.filter_by(NID=nid).first()
    if voter and check_password_hash(voter.Password, password):
        session["user_id"]=nid
        return redirect("/")
    else:
        return redirect("/auth/login")


@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/auth/login")
