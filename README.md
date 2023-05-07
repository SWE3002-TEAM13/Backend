## 📣 실행방법

### Install

```shell
$ git clone https://github.com/SWE3002-TEAM13/Backend.git
$ cd Backend
$ git checkout develope
```

### Setup

```shell
$ touch dev.db
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### run server

```shell
$ uvicorn main:app --reload
```
