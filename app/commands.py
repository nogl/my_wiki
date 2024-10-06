from app import logger
from app.db import engine
from app.models import  Base
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
