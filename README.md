# WORD CLOUD MAKER

Create a word cloud from a text input.

You can try the app in the following url: `IN PROGRESS`

`Note: Heroku is a free host with CPU and request time limitations, i'm sorry for any inconvenience this may cause`

## FOR DEVELOPERS

### Start the App Locally
Install the python packages specified in the `requirements.txt` by running the following command:

```
pip install -r requirements.txt
```

Then, run the following command to execute the app:

```
gunicorn -b 0.0.0.0:8080 app.app:server --reload --timeout 120
```

The `--reload` tag at the end for live reloading on changes.

Navigate to: `http://localhost:8080/`

### Dockerize the app
Run:

```
docker build -t word-cloud-maker .
docker run -p 8080:80 word-cloud-maker
```