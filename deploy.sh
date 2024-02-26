 #!/bin/bash -e

 docker rm -f testing-web-console
 
 docker run -it -d --name testing-web-console -p 8000:8000 altipeak/testing-web-console:latest