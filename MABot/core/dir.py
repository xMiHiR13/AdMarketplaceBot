from os import mkdir, path

from MABot.logging import LOGGER

async def dir():
    for dir_name in ["cache"]:
        if not path.exists(dir_name):
            mkdir(dir_name)
    LOGGER(__name__).info("All Necessary Folders Created!")
