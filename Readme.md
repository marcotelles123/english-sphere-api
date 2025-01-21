db:
- name: db-english-sphere
- user: usr-marco
- pass: 1234
- collection: questions

- docker 
  - pipreqs --force
  - docker build -t english-sphere-app .
  - ~~docker run -p 5000:5000 sound-to-text-app~~
    - http://localhost:5003.
  - docker-compose up --build
  - troubleshooting
    - docker exec -it 115b789263a6082e92139b20bc9802f4f1df17a5a1f076bb22d94f1dcccc0cdf /bin/bash
    - cd \temp\logs
    - cat app.log

- mongo first setup
  - docker exec -it mongo-english-sphere mongosh
  - use db-english-sphere
  - db.createCollection("questions")
  - db.createUser({
          user: "usr-marco",
          pwd: "1234",
          roles: [
                   { role: "readWrite", db: "db-english-sphere" }
                 ]
               })

- mongo log db
  - docker exec -it mongo-english-sphere mongosh
  - use db-english-sphere-log
  - db.createCollection("logs")
  - db.createUser({
          user: "usr-marco",
          pwd: "1234",
          roles: [
                   { role: "readWrite", db: "db-english-sphere-log" }
                 ]
               })


TODO:
improve the system_propmt, to ask to send thje coprrect version of my sentence
te new questions seems to be the same as the forts, we are not going further the conversation

adjusts the integration between service to check the sataus code and process the exception properly


