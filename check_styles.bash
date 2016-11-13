#!/bin/bash

pylint -f parseable -d I0011,R0801,C0103,C0111,E0401,R0201,W0622 app | tee pylint.out