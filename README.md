#Registerer

~~Nothing works!~~

Somethings work!

###Proposed work flow

* Server sends [properly formatted json](formats/node.json)
* Json is parsed by flask app
* Job is passed to foreman
* 201 (created) and the node id are sent back to the server
* foreman begins the archival process
    - adds into the database?
* Project is chunked up even more
* whenever a piece is finished query the database to see if the archive is finished
    - if it is ping a callback url
    - else get next job


###Vocabulary

* Node
    - Any given osf project that is not a registration
* Registration
    - A "frozen" osf project


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
