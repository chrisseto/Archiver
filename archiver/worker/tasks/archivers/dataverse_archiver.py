import requests

from celery import chord

from dataverse import Connection

from bs4 import BeautifulSoup

from archiver import celery
from archiver.backend import store
from archiver.exceptions.archivers import DataverseArchiverError

from base import ServiceArchiver


class DataverseArchiver(ServiceArchiver):
    ARCHIVES = 'dataverse'
    RESOURCE = 'study'

    def __init__(self, service):
        try:
            self.user = service['username']
            self.password = service['password']
            self.dataverse_name = service['dataverse']
            self.study_doi = service['studyDoi']
            self.host = service.get('host', 'dvn-demo.iq.harvard.edu')
        except KeyError as e:
            raise DataverseArchiverError('Miss argument "%s"' % e.message)
        super(DataverseArchiver, self).__init__(service)

    @classmethod
    def requests_save(cls, response):
        fobj, tpath = cls.get_temp_file()
        for chunk in response.iter_contents(chunk_size=1024):
            if chunk:
                fobj.write(chunk)
                fobj.flush()
        return tpath

    def clone(self):
        #Disables ssl validation
        c = Connection(self.user, self.password, self.host, disable_ssl=True)
        if not c.connected:
            raise DataverseArchiverError('Invalid creditials or host')

        dv = c.get_dataverse(self.dataverse_name)
        if not dv:
            raise DataverseArchiverError('Invalid dataverse alias')

        study = dv.get_study(self.study_doi)
        if not study:
            raise DataverseArchiverError('Invalid study doi')

        header = [
            self.download_file.si(self, f.download_url)
            for f in
            study.get_released_files()
        ]

        return chord(header, self.clone_done.s(self))

    @celery.task
    def download_file(self, file_url):
        session = requests.session()

        response = session.get(file_url, stream=True)

        # Agree to terms if a redirect has occurred
        if response.history:
            parsed = BeautifulSoup(response.content)
            try:
                view_state = parsed.find(id='javax.faces.ViewState').attrs['value']
            except (KeyError, AttributeError):
                raise DataverseArchiverError('Could not get ViewState value')

            data = {
                'form1': 'form1',
                'javax.faces.ViewState': view_state,
                'form1:termsAccepted': 'on',
                'form1:termsButton': 'Continue',
            }

            session.post(response.url, data=data)
            response = session.get(file_url, stream=True)

        try:
            filename = response.headers['content-disposition'].split('"')[1]
        except KeyError:
            raise DataverseArchiverError('File not found')

        tpath = self.requests_save(response.iter_contents())

        metadata = self.get_metadata(tpath, filename)
        store.push_file(tpath, metadata['sha256'])
        store.push_metadata(metadata, metadata['sha256'])

        return metadata

    @celery.task
    def clone_done(rets, self):
        service = {
            'service': 'dataverse',
            'resource': '%s, %s' % (self.dataverse_name, self.study_doi),
            'files': rets
        }
        store.push_manifest(service, '%s.figshare' % self.cid)
