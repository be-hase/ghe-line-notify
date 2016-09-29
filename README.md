# ghe-line-notify

LINE Notify Gateway for Github Enterprise.
Of course, you can use not only Github Enterprise but also Github.

```
,-----------------.
|Github Enterprise|
`-----------------'
         |
         | Send webhook.
         ▽
 ,---------------.
 |ghe-line-notify|
 `---------------'
         |
         | Receive Webhook, render text, and call notify API.
         ▽
   ,-----------.
   |LINE Notify|
   `-----------'
```

Let's try. [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Getting start

### Prerequisites

* Python 3.x (3.5.x recomended)
* (pip)

### Setup

```
git clone https://github.com/be-hase/ghe-line-notify
cd ghe-line-notify

pip install -r requirements/common.txt

python manage.py db upgrade
```

Default uses sqlite, and creates sqlite's db file at `~/.ghe-line-notif/app.db`.

### Running Locally For Developing

```
python run_dev_server.py
```

### Running on Gunicorn

```
gunicorn -c gunicorn_config.py app:app
```

### Deploying to Heroku

```
heroku create
heroku addons:add heroku-postgresql:hobby-dev

git push heroku master

heroku run python manage.py db upgrade
heroku open
```

or [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Config

If you want to change config, set environment variables.

* GHE_LN_DATABASE_URI
  * Specify database URI.
    * `dialect+driver://username:password@host:port/database`
  * If not specified, uses sqlite, and creates sqlite's db file at `~/.ghe-line-notif/app.db`.
* GHE_LN_SECRET_KEY
  * Crypt for sign cookies and other things.
  * Default value is `to_be_overridden`.

for example `export GHE_LN_SECRET_KEY=hoge`.
