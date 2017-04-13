# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FixThisFeature
                                 A QGIS plugin
 FixThisFeature
                             -------------------
        begin                : 2017-04-06
        copyright            : (C) 2017 by Stéphane Malta e Sousa
        email                : sos@ylb.ch
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FixThisFeature class from file FixThisFeature.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .fix_this_feature import FixThisFeature
    return FixThisFeature(iface)
