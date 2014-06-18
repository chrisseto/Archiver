#Archiver
[![Travis](https://travis-ci.org/chrisseto/Archiver.svg?branch=develop)](https://travis-ci.org/chrisseto/Archiver)
[![Coverage Status](https://coveralls.io/repos/chrisseto/Archiver/badge.png?branch=develop)](https://coveralls.io/r/chrisseto/Archiver?branch=develop)

###Work flow

* Server sends [properly formatted json](formats/container.json)
* Json is parsed by flask app
* Job is passed to foreman
* [201 (created)](formats/confirmation.json) and the container id are sent back to the server
* foreman begins the archival process
* Project is chunked up even more
* On completion a callback is fired and the celeryworker pings the foreman

###Vocabulary

* [Container](formats/container.json)
    - Any given osf project that is not a registration
* Registration
    - A "frozen" osf project
* Foreman
    - The controlling flask app
* Worker
    - The celery worker
* [Service](formats/services)
    - An arbitrary 3rd party service

###Registration structure

registration will have directory structure as such:
(subject to change)
```
Directory Structures/
    {See Below}
File Metadata/
    {some sha256}.json
    {some sha256}.par2.json
Files/
    {some sha256}
Manifests/
    {some container id}.manifest.json
    {some container id}.{some 3rd party service}.manifest.json
Parities/
    {some sha256}.par2
    {some sha256}.vol00+xxx.par2
```

The directory structure of Directory Structures is as follows
```
{some container id id}/
    manifest.json
    children/
        {child id}/
            {container}
    github/
        {repo name}/
            {repo contents}
    s3/
        {bucket name}/
            {bucker contents}
    figshare/
        {id}/
            {figshare contents}
    dropbox/
        {folder}/
            {folder contents}
```


###Setting up the Archiver to run locally
* `mv group_vars/archiver.example group_vars/archiver`
* Fill out archiver with the proper information
    - Minimally your S3 keys and bucket name

1. Change directorys to vagrant
2. `vagrant up`
3. `invoke provision`
4. `cd ..`
5. `invoke notebook`
6. From here you will need the API key from whatever service you wish to archiver.
7. Fill out the cell defining `container` and run the notebook
8. ???
9. profit
