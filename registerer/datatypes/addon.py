from datetime import datetime

from .. import validator


class Addon(object):

    @classmethod
    def from_json(cls, json):
        if validator.validate_addon(json):
            data = json['node']['addons']
            return cls(data['github'], data['S3'],
                data['osffiles'], raw=data)

    def __init__(self, github, S3, osffiles, raw=None):
        self.names=[]
        if github:
            self.names.append("github")
            self.access_token = github['access_token']
            self.repo = github['repo']
            self.user = github['user']
        if S3:
            self.names.append('S3')
            self.access_key = S3['access_key']
            self.secret_key = S3['secret_key']
            self.bucket = S3['bucket']

    def addon(self):
        rv = []
        if 'github' in self.names:
            rv.append(
                {
                    "github": {
                        "access_token": "",
                        "repo": "",
                        "user": ""
                    }
                }
            )
        if 'S3' in self.names:
            rv.append(
                {
                    "s3": {
                        "access_key": "",
                        "secret_key": "",
                        "bucket": ""
                    }
                }
            )
        return {rv}