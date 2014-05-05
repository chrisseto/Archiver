#Registerer

Nothing works!

###Proposed work flow

* Server sends json formatted as formats/node.json
* Json is parsed by flask app
* Job is passed to foreman
* foreman begins the archival process
    - adds into the database?
* Project is chunked up even more
* whenever a piece is finished query the database to see if the archive is finished
    - if it is ping a callback url
    - else get next job
