# -*- coding: utf-8 -*-
"""novelWriter Project Item Class

 novelWriter – Project Item Class
==================================
 Class holding the data of a project tree item

 File History:
 Created: 2018-10-27 [0.0.1]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import nw

from lxml import etree

from nw.common import checkInt
from nw.constants import nwItemType, nwItemClass, nwItemLayout

logger = logging.getLogger(__name__)

class NWItem():

    def __init__(self, theProject):

        self.theProject = theProject

        self.itemName   = ""
        self.itemHandle = None
        self.parHandle  = None
        self.itemOrder  = None
        self.itemType   = nwItemType.NO_TYPE
        self.itemClass  = nwItemClass.NO_CLASS
        self.itemLayout = nwItemLayout.NO_LAYOUT
        self.itemStatus = None
        self.isExpanded = False
        self.isExported = True

        # Document Meta Data
        self.charCount = 0 # Current character count
        self.wordCount = 0 # Current word count
        self.paraCount = 0 # Current paragraph count
        self.initCount = 0 # Initial word count
        self.cursorPos = 0 # Last cursor position

        return

    ##
    #  XML Pack/Unpack
    ##

    def packXML(self, xParent):
        """Packs all the data in the class instance into an XML object.
        """
        xPack = etree.SubElement(xParent,"item",attrib={
            "handle" : str(self.itemHandle),
            "order"  : str(self.itemOrder),
            "parent" : str(self.parHandle),
        })
        xSub = self._subPack(xPack,"name",     text=str(self.itemName))
        xSub = self._subPack(xPack,"type",     text=str(self.itemType.name))
        xSub = self._subPack(xPack,"class",    text=str(self.itemClass.name))
        xSub = self._subPack(xPack,"status",   text=str(self.itemStatus))
        if self.itemType == nwItemType.FILE:
            xSub = self._subPack(xPack,"exported",  text=str(self.isExported))
            xSub = self._subPack(xPack,"layout",    text=str(self.itemLayout.name))
            xSub = self._subPack(xPack,"charCount", text=str(self.charCount), none=False)
            xSub = self._subPack(xPack,"wordCount", text=str(self.wordCount), none=False)
            xSub = self._subPack(xPack,"paraCount", text=str(self.paraCount), none=False)
            xSub = self._subPack(xPack,"cursorPos", text=str(self.cursorPos), none=False)
        else:
            xSub = self._subPack(xPack,"expanded", text=str(self.isExpanded))
        return

    def unpackXML(self, xItem):
        """Sets the values from an XML entry of type 'item'.
        """
        if xItem.tag != "item":
            logger.error("XML entry is not an NWItem")
            return False

        if "handle" in xItem.attrib:
            self.itemHandle = xItem.attrib["handle"]
        else:
            logger.error("XML item entry does not have a handle")
            return False

        if "parent" in xItem.attrib:
            self.parHandle = xItem.attrib["parent"]

        setMap = {
            "name"      : self.setName,
            "order"     : self.setOrder,
            "type"      : self.setType,
            "class"     : self.setClass,
            "layout"    : self.setLayout,
            "status"    : self.setStatus,
            "expanded"  : self.setExpanded,
            "exported"  : self.setExported,
            "charCount" : self.setCharCount,
            "wordCount" : self.setWordCount,
            "paraCount" : self.setParaCount,
            "cursorPos" : self.setCursorPos,
        }
        for xValue in xItem:
            if xValue.tag in setMap:
                setMap[xValue.tag](xValue.text)
            else:
                logger.error("Unknown tag '%s'" % xValue.tag)

        return True

    @staticmethod
    def _subPack(xParent, name, attrib=None, text=None, none=True):
        """Packs the values into an xml element.
        """
        if not none and (text == None or text == "None"):
            return None
        xSub = etree.SubElement(xParent, name, attrib=attrib)
        if text is not None:
            xSub.text = text
        return xSub

    ##
    #  Set Item Values
    ##

    def setName(self, theName):
        """Set the item name.
        """
        self.itemName = theName.strip()
        return

    def setHandle(self, theHandle):
        """Set the item handle, and ensure it is valid.
        """
        if isinstance(theHandle, str):
            if len(theHandle) == 13:
                self.itemHandle = theHandle
            else:
                self.itemHandle = None
        else:
            self.itemHandle = None
        return

    def setParent(self, theParent):
        """Set the parent handle, and ensure that it is valid.
        """
        if theParent is None:
            self.parHandle = None
        elif isinstance(theParent, str):
            if len(theParent) == 13:
                self.parHandle = theParent
            else:
                self.parHandle = None
        else:
            self.parHandle = None
        return

    def setOrder(self, theOrder):
        """Set the item order, and ensure that it is valid. This value
        is purely a meta value, not actually used by novelWriter.
        """
        self.itemOrder = checkInt(theOrder, 0)
        return

    def setType(self, theType):
        """Set the item type from either a proper nwItemType, or set it
        from a string representing a nwItemType.
        """
        if isinstance(theType, nwItemType):
            self.itemType = theType
        elif theType in nwItemType.__members__:
            self.itemType = nwItemType[theType]
        else:
            logger.error("Unrecognised item type '%s'" % theType)
            self.itemType = nwItemType.NO_TYPE
        return

    def setClass(self, theClass):
        """Set the item class from either a proper nwItemClass, or set
        it from a string representing a nwItemClass.
        """
        if isinstance(theClass, nwItemClass):
            self.itemClass = theClass
        elif theClass in nwItemClass.__members__:
            self.itemClass = nwItemClass[theClass]
        else:
            logger.error("Unrecognised item class '%s'" % theClass)
            self.itemClass = nwItemClass.NO_CLASS
        return

    def setLayout(self, theLayout):
        """Set the item layout from either a proper nwItemLayout, or set
        it from a string representing a nwItemLayout.
        """
        if isinstance(theLayout, nwItemLayout):
            self.itemLayout = theLayout
        elif theLayout in nwItemLayout.__members__:
            self.itemLayout = nwItemLayout[theLayout]
        else:
            logger.error("Unrecognised item layout '%s'" % theLayout)
            self.itemLayout = nwItemLayout.NO_LAYOUT
        return

    def setStatus(self, theStatus):
        """Set the item status by looking it up in the valid status
        items of the current project.
        """
        if self.itemClass == nwItemClass.NOVEL:
            self.itemStatus = self.theProject.statusItems.checkEntry(theStatus)
        else:
            self.itemStatus = self.theProject.importItems.checkEntry(theStatus)
        return

    def setExpanded(self, expState):
        """Save the expanded status of an item in the project tree.
        """
        if isinstance(expState, str):
            self.isExpanded = expState == str(True)
        else:
            self.isExpanded = expState == True
        return

    def setExported(self, expState):
        """Save the export flag.
        """
        if isinstance(expState, str):
            self.isExported = expState == str(True)
        else:
            self.isExported = expState == True
        return

    ##
    #  Set Document Meta Data
    ##

    def setCharCount(self, theCount):
        """Set the character count, and ensure that it is an integer.
        """
        self.charCount = checkInt(theCount, 0)
        return

    def setWordCount(self, theCount):
        """Set the word count, and ensure that it is an integer.
        """
        self.wordCount = checkInt(theCount, 0)
        return

    def setParaCount(self, theCount):
        """Set the paragraph count, and ensure that it is an integer.
        """
        self.paraCount = checkInt(theCount, 0)
        return

    def setCursorPos(self, thePosition):
        """Set the cursor position, and ensure that it is an integer.
        """
        self.cursorPos = checkInt(thePosition, 0)
        return

    def saveInitialCount(self):
        """Set the initial word count.
        """
        self.initCount = self.wordCount
        return

# END Class NWItem
