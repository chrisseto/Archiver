#Archiver
![Travis](https://travis-ci.org/chrisseto/Archiver.svg?branch=develop)

A lot of things work!

###Work flow

* Server sends [properly formatted json](formats/node.json)
* Json is parsed by flask app
* Job is passed to foreman
* 201 (created) and the node id are sent back to the server
* foreman begins the archival process
* Project is chunked up even more
* On completion a callback is fired and the celeryworker pings the foreman

###Vocabulary

* Node
    - Any given osf project that is not a registration
* Registration
    - A "frozen" osf project
* Foreman
    - The controlling flask app
* Worker
    - The celery worker


###Registration structure

registration will have directory structure as such:
(subject to change)

```
{project id}/
    metadata.json
    children/
        {child id}/
            {project}
    addons/
        github/
            {repo name}/
                {repo contents}
        s3/
            {bucket name}/
                {bucker contents}
```


###Progress

* Task Queueing
* Task Chaining
* Folder structure creation
* cloning of github addon
