#!/bin/bash

rm -rf SV/__pycache__
rm -rf utils/__pycache__
zip -r package_test.zip * .ebextensions

