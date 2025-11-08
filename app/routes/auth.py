from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page dan handler"""
    if current_user.is_authenticated:
        return redirect(url_for('lecturer.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me', False)

        if not username or not password:
            flash('Username dan password harus diisi', 'error')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            logger.warning(f"Login gagal untuk user: {username}")
            flash('Username atau password salah', 'error')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('User tidak aktif', 'error')
            return redirect(url_for('auth.login'))

        # Login successful
        login_user(user, remember=bool(remember_me))
        logger.info(f"User {username} berhasil login")

        next_page = request.args.get('next')
        if not next_page or url_has_allowed_host_and_scheme(next_page):
            next_page = url_for('lecturer.dashboard')

        return redirect(next_page)

    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """Logout handler"""
    username = current_user.username
    logout_user()
    logger.info(f"User {username} berhasil logout")
    flash('Anda telah logout', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/api/login', methods=['POST'])
def api_login():
    """API login endpoint (untuk mobile apps)"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username dan password harus diisi'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        logger.warning(f"API login gagal: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'User tidak aktif'}), 403

    login_user(user)
    logger.info(f"API login berhasil: {username}")

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200


@bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """API logout endpoint"""
    username = current_user.username
    logout_user()
    logger.info(f"API logout: {username}")
    return jsonify({'message': 'Logout successful'}), 200


def url_has_allowed_host_and_scheme(url):
    """Check if URL is safe to redirect to"""
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    return parsed_url.scheme in ('', 'http', 'https') and not parsed_url.netloc
