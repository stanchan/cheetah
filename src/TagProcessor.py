#!/usr/bin/env python
# $Id: TagProcessor.py,v 1.4 2001/08/10 19:26:02 tavis_rudd Exp $
"""Tag Processor class Cheetah's codeGenerator

Meta-Data
================================================================================
Author: Tavis Rudd <tavis@calrudd.com>
License: This software is released for unlimited distribution under the
         terms of the Python license.
Version: $Revision: 1.4 $
Start Date: 2001/08/01
Last Revision Date: $Date: 2001/08/10 19:26:02 $
"""
__author__ = "Tavis Rudd <tavis@calrudd.com>"
__version__ = "$Revision: 1.4 $"[11:-2]

##################################################
## DEPENDENCIES ##

import re

# intra-package imports ...

##################################################
## CONSTANTS & GLOBALS ##

True = (1==1)
False = (0==1)

# tag types for the main tags
EVAL_TAG_TYPE = 0
EXEC_TAG_TYPE = 1
EMPTY_TAG_TYPE = 2

##################################################
## CLASSES ##

class Error(Exception):
    pass

class TagProcessor:
    _tagType = EVAL_TAG_TYPE

    def __init__(self, templateObj):
        """Setup some internal references to the templateObj. This method must
        be called by subclasses."""

        self._templateObj = templateObj
        ## setup some method mappings for convenience
        self.state = templateObj._getCodeGeneratorState
        self.settings = templateObj.settings
        self.setting = templateObj.setting
        self.searchList = templateObj.searchList
        
    def templateObj(self):
        """Return a reference to the templateObj that controls this processor"""
        return self._templateObj

    def preProcess(self, templateObj, templateDef):
        delims = self.setting('internalDelims')
        tagTokenSeparator = self.setting('tagTokenSeparator')
        def subber(match, delims=delims, token=self._token,
                   tagTokenSeparator=tagTokenSeparator,
                   templateObj=templateObj):

            ## escape any placeholders in the tag so they aren't picked up as
            ## top-level placeholderTags
            tag = templateObj.placeholderProcessor.escapePlaceholders(match.group(1))
            
            return delims[0] + token + tagTokenSeparator  +\
                   tag + delims[1]

        for RE in self._delimRegexs:
            templateDef = RE.sub(subber, templateDef)

        return templateDef
   
    def initializeTemplateObj(self):
        """Initialize the templateObj so that all the necessary attributes are
        in place for the tag-processing stage

        This must be called by subclasses"""
        templateObj = self.templateObj()
        
        if not self.state().has_key('indentLevel'):
            self.state()['indentLevel'] = \
                          self.settings()['initialIndentLevel']
        if not hasattr(templateObj, '_localVarsList'):
            # may have already been set by #set or #for
            templateObj._localVarsList = []
            
        if not hasattr(templateObj,'_perResponseSetupCodeChunks'):
            templateObj._perResponseSetupCodeChunks = {}

        if not self.state().has_key('defaultCacheType'):
            self.state()['defaultCacheType'] = None

    
    def processTag(self, tag):
        return self.wrapTagCode( self.translateTag(tag) )

    def validateTag(self, tag):
        """A hook for doing security and syntax checks on a tag"""
        pass

    def translateTag(self, tag):
        pass

    def wrapExecTag(self, translatedTag):
        return "''',])\n" + translatedTag + "outputList.extend(['''"

    def wrapEvalTag(self, translatedTag):
        templateObj = self.templateObj()
        indent = self.setting('indentationStep') * \
                 self.state()['indentLevel']
        return "''',\n" + indent + translatedTag + ", '''"

    def wrapTagCode(self, translatedTag):
        if self._tagType == EVAL_TAG_TYPE:
            return self.wrapEvalTag(translatedTag)
        elif self._tagType == EXEC_TAG_TYPE:
            return self.wrapExecTag(translatedTag)
        elif self._tagType == EMPTY_TAG_TYPE:
            return ''
