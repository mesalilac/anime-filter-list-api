### Development

```sh
uv run fastapi dev app/main.py
```

### Deployment

#### Fastapi

```sh
uv run fastapi run app/main.py
```

#### Docker

```sh
./build-image.sh
```

```sh
docker run -p 8000:8000 animefillerlist:latest
```

##### Manually

```sh
docker build -t animefillerlist:latest .
```

```sh
docker run -p 8000:8000 animefillerlist:latest
```