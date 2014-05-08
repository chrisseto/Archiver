import os


class Addon(object):

    def __init__(self, json, parent):
        self.addon, self.raw_json = json.items()[0]
        self.parent = parent

    @property
    def path(self):
        #note addons will have to each append their id to the end of the path
        # ie bucket name, repo name etc
        return os.path.join(self.parent.path, 'addons', 'self.addon')

    def __get__(self, key):
        return self.raw_json[key]

    # @classmethod
    # def from_json(cls, json):
    #     if validator.validate_addon(json):
    #         data = json['node']['addons']
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

    # def addon(self):
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
