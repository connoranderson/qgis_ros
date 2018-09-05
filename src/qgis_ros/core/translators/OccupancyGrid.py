import uuid
import json
import os
from pathlib import Path
import subprocess

from catkin.find_in_workspaces import find_in_workspaces as catkin_find
from nav_msgs.msg import OccupancyGrid

from .translator import Translator, RasterTranslatorMixin


class OccupancyGridTranslator(Translator, RasterTranslatorMixin):
    '''A really terrible implementation to generate rasters from ROS topics.

    This is because of an unresolved issue where GDAL's underlying C++ implementation crashes unexplainably
    when used in this context. As its own process it works fine.
    https://issues.qgis.org/issues/19252
    '''

    messageType = OccupancyGrid

    @staticmethod
    def translate(msg):
        datafile = '/tmp/{}.json'.format(uuid.uuid4())

        data = {
            'height': msg.info.height,
            'width': msg.info.width,
            'resolution': msg.info.resolution,
            'origin_x': msg.info.origin.position.x,
            'origin_y': msg.info.origin.position.y,
            'data': msg.data
        }

        # Save the message data to be read by external translator.
        with open(datafile, 'w') as f:
            json.dump(data, f)

        # Run external translator.
        geotiffFilename = '/tmp/{}.tif'.format(uuid.uuid4())

        # TODO use catkin to find the script. Oh my.
        rasterize_script = catkin_find(project='qgis-ros', path='scripts/msg_to_geotiff.py', first_match_only=True)[0]
        # script = str(Path(os.path.dirname(os.path.realpath(__file__))) / '..' / '..' / '..' / '..' / 'scripts' / 'msg_to_geotiff.py')

        subprocess.check_call([rasterize_script, datafile, geotiffFilename])

        # Return filename.
        return geotiffFilename