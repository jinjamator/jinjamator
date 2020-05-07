import logging

from flask import request, flash, url_for
from flask import Flask, url_for, session, redirect

from flask_restx import Resource, abort
from jinjamator.daemon.api.serializers import environments
from jinjamator.daemon.aaa import aaa_providers
from jinjamator.daemon.api.restx import api
from jinjamator.daemon.api.serializers import aaa_post_data

from flask import current_app as app
import glob
import os
import xxhash
from pprint import pformat

log = logging.getLogger()

ns = api.namespace(
    "aaa", description="Operations related to jinjamator Authentication Authorization and Accounting"
)

current_provider = None

@ns.route('/login/<provider>')
class Login(Resource):
    @api.response(400, "Unknown Login Provider <provider>")
    @api.response(200, "Success")
    def get(self, provider='local'):
        """
        Login User.
        """
        if provider in aaa_providers:
            return aaa_providers[provider].login(request)
        abort(400, f'Unknown Login Provider {provider}')
    @api.expect(aaa_post_data)
    def post(self, provider='local'):
        """
        Login User.
        """
        if provider in aaa_providers:
            return aaa_providers[provider].login(request)
        abort(400, f'Unknown Login Provider {provider}')




@ns.route("/logout")
class Logout(Resource):
    def get(self):
        """
        Logout User and terminate all session information.
        """
        if current_provider:
            
            return {'message': 'not implemented'}
        else:
            abort(400, 'Not logged in')


@ns.route('/auth')
class Auth(Resource):
    def get(self):
        global current_provider
        access_token = None

        for aaa_provider in aaa_providers:
            log.debug(f'trying to use {aaa_provider}')
            if aaa_providers[aaa_provider].authorize(request):
                current_provider = aaa_providers[aaa_provider]
                return {'message': f'Successfully logged in user: {current_provider.logged_in_user}'}
            # obj = getattr(aaa_providers[aaa_provider], aaa_provider)
            # try:
            #     access_token = obj.authorize_access_token()
            #     current_provider = obj
            #     break
            # except:
            #     pass
            # if access_token:
            #     id_token = obj.parse_id_token(access_token)
            #     log.info(f'logged in user {pformat(id_token)} with token {pformat(access_token)}')
            #     session['user'] = id_token
            #     return access_token['access_token']
        abort(400,'Cannot find valid login provider')
        