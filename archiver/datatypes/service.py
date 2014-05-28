import os
import errno


class Service(object):

    def __init__(self, json, parent):
        self.service, self.raw_json = json.items()[0]
        self.parent = parent

    def path(self, extra):
        return os.path.join(self.parent.path, 'services', self.service, extra) + os.sep

    def full_path(self, extra):
        return os.path.join(self.parent.TEMP_DIR, self.path(extra))

    def make_dir(self, extra):
        try:
            os.makedirs(self.full_path(extra))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def get(self, key, default=None):
        return self.raw_json.get(key, default)

    def __getitem__(self, key):
        return self.raw_json[key]

    # @classmethod
    # def from_json(cls, json):
    #     if validator.validate_service(json):
    #         data = json['container']['services']
    #         return cls(data['github'], data['S3'],
    #             data['osffiles'], raw=data)

    # def __init__(self, github, S3, osffiles, raw=None):
    #     self.names=[]
    #     if github:
    #         self.names.append("github")
    #         self.access_token = github['access_token']
    #         self.repo = github['repo']
    #         self.user = github['user']
    #     if S3:
    #         self.names.append('S3')
    #         self.access_key = S3['access_key']
    #         self.secret_key = S3['secret_key']
    #         self.bucket = S3['bucket']

    # def service(self):
    #     rv = []
    #     if 'github' in self.names:
    #         rv.append(
    #             {
    #                 "github": {
    #                     "access_token": "",
    #                     "repo": "",
    #                     "user": ""
    #                 }
    #             }
    #         )
    #     if 'S3' in self.names:
    #         rv.append(
    #             {
    #                 "s3": {
    #                     "access_key": "",
    #                     "secret_key": "",
    #                     "bucket": ""
    #                 }
    #             }
    #         )
    #     return {rv}
