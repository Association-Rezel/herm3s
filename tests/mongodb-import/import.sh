#! /bin/bash

mongoimport --host mongodb --db test --collection hermestest1 --type json --file /mongodb-import/test.hermestest1.json --jsonArray
