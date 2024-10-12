import sqlalchemy

from app import logger
from app.db import engine
from app.models import Base
import click
from flask.cli import AppGroup

db_cli = AppGroup('db_cli')


@db_cli.command('db_init')
def db_init():
    logger.info(f'command - db_init')
    Base.metadata.create_all(bind=engine)


@db_cli.command('db_delete')
def db_delete():
    logger.info(f'command - db_delete')
    Base.metadata.drop_all(bind=engine)


@db_cli.command('db_query')
@click.option("--query")
def db_delete(query):
    logger.info(f'command - db_query')
    with engine.connect() as conn:
        data = conn.execute(sqlalchemy.sql.text(query)).mappings().fetchall()
        for index, row in enumerate(data, 1):
            logger.info(f'#{index}/{len(data)} - {row}')
    logger.success(f'Completed - {len(data)}')
