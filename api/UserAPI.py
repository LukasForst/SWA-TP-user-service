import logging

from flask import jsonify, request, make_response
from flask_restx import Namespace, Resource, fields

from common.Db import db
from services.Crypto import encode_auth_token, compare_passwords
from services.User import User

logger = logging.getLogger(__name__)

user_api = Namespace('user')


@user_api.route('/register', methods=['PUT'])
class RegistrationApi(Resource):
    dummy_model = user_api.model('UserRegistration', {
        'first_name': fields.String(required=True, description='First name.'),
        'last_name': fields.String(required=True, description='Surname.'),
        'email': fields.String(required=True, description='Email used for authentication.'),
        'password': fields.String(required=True, description='Users password.'),
    })

    @user_api.doc(
        body=dummy_model
    )
    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if user already exists
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    first_name=post_data.get('first_name'),
                    last_name=post_data.get('last_name'),
                    email=post_data.get('email'),
                    password=post_data.get('password')
                )
                # insert the user
                db.session.add(user)
                db.session.commit()
                # generate the auth token
                auth_token = encode_auth_token(user)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode()
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202


@user_api.route('/login', methods=['POST'])
class LoginApi(Resource):
    dummy_model = user_api.model('UserLogin', {
        'email': fields.String(required=True, description='Email of the user to login.'),
        'password': fields.String(required=True, description='Users password.')
    })

    @user_api.doc(
        security='bearer',
        body=dummy_model
    )
    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            user = User.query.filter_by(email=post_data.get('email')).first()
            if user and compare_passwords(user.password, post_data.get('password')):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject)), 401

        except Exception as e:
            logger.error(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500
