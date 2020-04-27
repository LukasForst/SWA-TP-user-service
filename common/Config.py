import logging
import os
from dataclasses import dataclass
from typing import Callable

from flask import current_app as app, g

logger = logging.getLogger(__name__)


@dataclass
class Config:
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_url: str


def get_config() -> Config:
    """
    Obtains configuration from the application context.
    """
    return get_or_set('config', build_configuration)


def build_configuration() -> Config:
    """
    Builds configuration from environment or from the Flask properties
    """
    logger.debug('Building configuration.')
    config = Config(postgres_user=get_prop('POSTGRES_USER', True),
                    postgres_password=get_prop('POSTGRES_PASSWORD', True),
                    postgres_db=get_prop('POSTGRES_DB', True),
                    postgres_url=get_prop('POSTGRES_URL', True))
    logger.debug(f'Used configuration: {config}')
    return config


def get_prop(name: str, optional: bool = False) -> str:
    """
    Gets property from environment or from the flask env.
    """
    config = os.environ.get(name, app.config.get(name))
    if not optional and not config:
        logger.error(f'It was not possible to retrieve configuration for property "{name}"!')
        raise EnvironmentError(f'No existing configuration for "{name}" found!')
    return config


def get_or_set(prop: str, factory: Callable):
    """
    Gets or sets context property.
    """
    if not hasattr(g, prop):
        setattr(g, prop, factory())

    return getattr(g, prop)
