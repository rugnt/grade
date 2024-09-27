#!/bin/bash
set -e
#first cd current dir
cd "$(dirname "${BASH_SOURCE[0]}")"

export DEFAULT_USER="1000";
export DEFAULT_GROUP="1000";

export USER_ID=`id -u`
export GROUP_ID=`id -g`
export USER=$USER


if [ "$USER_ID" == "0" ];
then
    export USER_ID=$DEFAULT_USER;
fi

if [ "$GROUP_ID" == "0" ];
then
    export GROUP_ID=$DEFAULT_GROUP;
fi



#load .env
export $(egrep -v '^#' .env | xargs)

if [ $# -eq 0 ]
  then
    echo "HELP:"
    echo "build - make docker build"
    echo "up - docker up in console"
    echo "down - docker down"
    echo "run - run in php container from project root"
fi

function applyDump {
    cat $1 | docker exec -i ${PROJECT_PREFIX}_mysql mysql -u $MYSQL_USER -p"$MYSQL_PASSWORD" $MYSQL_DATABASE;
    return $?
}

function runInMySql {
    local command=$@
    docker exec -i ${PROJECT_PREFIX}_mysql su mysql -c "$command"
    return $?
}

function runInPython {
    local command=$@
    echo $command;
    docker exec -i ${PROJECT_PREFIX}_web su www-data -c "cd /var/www/html/;$command"
    return $?
}

function runInRabbitMq {
    local command=$@
    echo $command;
    docker exec -i ${PROJECT_PREFIX}_rabbitmq bash -c "$command"
    return $?
}


if [ "$1" == "make" ];
  then
    if [ "$2" == "env" ];
        then
            cp .env.example .env
    fi

    if [ "$2" == "app" ];
        then
            docker-compose run  web bash -c "/usr/src/app/.local/bin/django-admin startproject ${PROJECT_PREFIX} ./src"
    fi

    if [ "$2" == "lib" ];
        then
            docker-compose -p ${PROJECT_PREFIX} run --no-deps  web bash -c "rm -rf ./lib && cp -r /usr/local/lib/python3.10/site-packages ./lib"
    fi

    if [ "$2" == "migrations" ];
        then
        docker exec ${PROJECT_PREFIX}_web alembic revision --autogenerate
    fi



fi

if [ "$1" == "db" ];
  then

    if [ "$2" == "" ];
        then
        docker exec -it ${PROJECT_PREFIX}_pgsql psql -U user defaultdb;
    fi

    if [ "$2" == "migrate" ];
        then
        docker exec ${PROJECT_PREFIX}_web alembic upgrade heads
    fi

    if [ "$2" == "import" ];
        then
        cat $3 | docker exec -i ${PROJECT_PREFIX}_pgsql psql -U user
    fi

    if [ "$2" == "export" ];
        then
        docker exec -it ${PROJECT_PREFIX}_pgsql pg_dump -U user defaultdb
    fi

fi

if [ "$1" == "build" ];
  then
    docker-compose -p ${PROJECT_PREFIX} build
fi

if [ "$1" == "up" ];
  then
    if [ "$2" == "verbose" ];
        then
            docker-compose -p ${PROJECT_PREFIX} up;
        else
            docker-compose -p ${PROJECT_PREFIX} up -d
    fi
fi

if [ "$1" == "down" ];
  then
    docker-compose -p ${PROJECT_PREFIX} down
fi

if [ "$1" == "fulldown" ];
  then
    docker-compose -p ${PROJECT_PREFIX} down --rmi local
fi



if [ "$1" == "run" ];
  then
    if [ "$2" == "" ];
        then
        docker exec -it ${PROJECT_PREFIX}_web bash
        else
        runInPhp "${@:2}"
    fi
fi

if [ "$1" == "prepare" ];
  then
    docker-compose run --no-deps  web bash -c "${@:2}"
fi

if [ "$1" == "rabbitmq" ];
  then

    if [ "$2" == "up" ];
        then
            runInRabbitMq "rabbitmqctl delete_user guest"
            runInRabbitMq "rabbitmqctl add_vhost /"
            runInRabbitMq "rabbitmqctl add_user $RABBITMQ_LOGIN $RABBITMQ_PASSWORD"
            runInRabbitMq "rabbitmqctl set_user_tags $RABBITMQ_LOGIN administrator"
            runInRabbitMq "rabbitmqctl set_permissions -p / $RABBITMQ_LOGIN '.*' '.*' '.*'"
    fi

fi
