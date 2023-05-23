# Running the docker container 

- Install docker
- Run the following command:

```bash
docker build .
```

- We have now built the image. Run the following command:

```bash
docker images
```

- Grab the IMAGE_ID 
- Run the following command
```bash
docker run -p 8080:8080 IMAGE_ID
```

- Now visit localhost:8080