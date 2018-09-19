#! /bin/bash


basedir=$(realpath $(dirname $0)/../)

echo "Updating translations in '$basedir'"

cd $basedir/www

../manage.py makemessages --all --keep-pot -e html,txt,js,py
../manage.py compilemessages





