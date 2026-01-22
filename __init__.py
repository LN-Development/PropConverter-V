# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import i18n
from . import logger
from . import properties
from . import operators
from . import ui


def register():   
    # Initialize i18n system first
    i18n.initialize()
    
    # Register logger for popup notifications
    logger.register()
    
    properties.register()
    operators.register()
    ui.register()



def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()
    logger.unregister()

