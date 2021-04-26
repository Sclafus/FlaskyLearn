from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(403)
def forbidden(e):
    '''Error page for 403 forbidden http error'''
    return render_template('errors/403.html'), 403


@errors.app_errorhandler(404)
def not_found(e):
    '''Error page for 404 not found http error'''
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(500)
def not_found(e):
    '''Error page for 500 internal server http error'''
    return render_template('errors/500.html'), 500
