import logging

from flask import jsonify, request, make_response
from flask_restx import Namespace, Resource, fields

from common.Db import db
from services.Crypto import encode_auth_token, compare_passwords, decode_auth_token
from services.User import User

logger = logging.getLogger(__name__)

user_api = Namespace('user')


@user_api.route('/register', methods=['PUT'])
class RegistrationApi(Resource):
    registration_model = user_api.model('UserRegistration', {
        'first_name': fields.String(required=True, description='First name.'),
        'last_name': fields.String(required=True, description='Surname.'),
        'email': fields.String(required=True, description='Email used for authentication.'),
        'password': fields.String(required=True, description='Users password.'),
    })

    @user_api.doc(
        body=registration_model
    )
    def put(self):
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
                return jsonify(responseObject)
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject), 502)
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject), 409)


@user_api.route('/login', methods=['POST'])
class LoginApi(Resource):
    login_model = user_api.model('UserLogin', {
        'email': fields.String(required=True, description='Email of the user to login.'),
        'password': fields.String(required=True, description='Users password.')
    })

    @user_api.doc(
        body=login_model
    )
    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            user = User.query.filter_by(email=post_data.get('email')).first()
            if user and compare_passwords(user.password, post_data.get('password')):
                auth_token = encode_auth_token(user)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return jsonify(responseObject)
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject), 401)

        except Exception as e:
            logger.error(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject), 401)


@user_api.route('', methods=['GET'])
class UserAPI(Resource):
    status = user_api.model('AuthMessage', {
        'status': fields.String(required=True, description='Indication of successful auth..', enum=['fail', 'success']),
        'message': fields.String(required=False, description='Message why request failed.')
    })

    user = user_api.model('User', {
        'user_id': fields.String(required=True, description='Id of the user'),
        'email': fields.String(required=True, description="User's email")
    })

    @user_api.response(code=200, model=user, description="Returns user information.")
    @user_api.response(code=401, model=status,
                       description="Returns message why it was not possible to fulfil request.")
    @user_api.doc(
        security='bearer'
    )
    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except Exception:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject), 401)
        else:
            auth_token = ''

        if auth_token:
            user_id, error = decode_auth_token(auth_token)
            if user_id:
                user = User.query.filter_by(id=user_id).first()
                responseObject = {
                    'user_id': user.id,
                    'email': user.email
                }
                return jsonify(responseObject)

            responseObject = {
                'status': 'fail',
                'message': error
            }
            return make_response(jsonify(responseObject), 401)
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject), 401)
