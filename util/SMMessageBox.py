#!/usr/bin/env python
#coding=utf-8
# This is only needed for Python v2 but is harmless for Python v3.
# -*- coding: utf-8 -*-
#include <QString>
"""
Module implementing QMessageBox replacements and more convenience function.
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox, QApplication

################################################################################
##  Mappings to standard QMessageBox                                          ##
################################################################################

# QMessageBox.Icon
Critical    = QMessageBox.Critical
Information = QMessageBox.Information
Question    = QMessageBox.Question
Warning     = QMessageBox.Warning

StandardButtons = QMessageBox.StandardButtons

# QMessageBox.StandardButton
Abort           = QMessageBox.Abort
Apply           = QMessageBox.Apply
Cancel          = QMessageBox.Cancel
Close           = QMessageBox.Close
Discard         = QMessageBox.Discard
Help            = QMessageBox.Help
Ignore          = QMessageBox.Ignore
No              = QMessageBox.No
NoToAll         = QMessageBox.NoToAll
Ok              = QMessageBox.Ok
Open            = QMessageBox.Open
Reset           = QMessageBox.Reset
RestoreDefaults = QMessageBox.RestoreDefaults
Retry           = QMessageBox.Retry
Save            = QMessageBox.Save
SaveAll         = QMessageBox.SaveAll
Yes             = QMessageBox.Yes
YesToAll        = QMessageBox.YesToAll
NoButton        = QMessageBox.NoButton

# QMessageBox.ButtonRole
AcceptRole      = QMessageBox.AcceptRole
ActionRole      = QMessageBox.ActionRole
ApplyRole       = QMessageBox.ApplyRole
DestructiveRole = QMessageBox.DestructiveRole
InvalidRole     = QMessageBox.InvalidRole
HelpRole        = QMessageBox.HelpRole
NoRole          = QMessageBox.NoRole
RejectRole      = QMessageBox.RejectRole
ResetRole       = QMessageBox.ResetRole
YesRole         = QMessageBox.YesRole

################################################################################
##  Replacement for the QMessageBox class                                     ##
################################################################################

class E5MessageBox(QMessageBox):
    """
    Class implementing a replacement for QMessageBox.
    """
    def __init__(self, icon, title, text, modal = False, 
                 buttons = QMessageBox.StandardButtons(QMessageBox.NoButton), 
                 parent = None):
        """
        Constructor
        
        @param icon type of icon to be shown (QMessageBox.Icon)
        @param title caption of the message box (string)
        @param text text to be shown by the message box (string)
        @keyparam modal flag indicating a modal dialog (boolean)
        @keyparam buttons set of standard buttons to generate (StandardButtons)
        @keyparam parent parent widget of the message box (QWidget)
        """
        QMessageBox.__init__(self, parent)
        self.setIcon(icon)
        if modal:
            if parent is not None:
                self.setWindowModality(Qt.WindowModal)
            else:
                self.setWindowModality(Qt.ApplicationModal)
        else:
            self.setWindowModality(Qt.NonModal)
        if title == "":
            self.setWindowTitle("{0}".format(
                QApplication.applicationName()))
        else:
            self.setWindowTitle("{0} - {1}".format(
                QApplication.applicationName(), title))
        self.setText(text)
        self.setStandardButtons(buttons)

################################################################################
##  Replacements for QMessageBox static methods                               ##
################################################################################

def __messageBox(parent, title, text, icon, 
                 buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
    """
    Private module function to show a modal message box.
    
    @param parent parent widget of the message box (QWidget)
    @param title caption of the message box (string)
    @param text text to be shown by the message box (string)
    @param icon type of icon to be shown (QMessageBox.Icon)
    @param buttons flags indicating which buttons to show 
        (QMessageBox.StandardButtons)
    @param defaultButton flag indicating the default button
        (QMessageBox.StandardButton)
    @return button pressed by the user (QMessageBox.StandardButton)
    """
    messageBox = QMessageBox(parent)
    messageBox.setIcon(icon)
    if parent is not None:
        messageBox.setWindowModality(Qt.WindowModal)
    if title == "":
        messageBox.setWindowTitle("{0}".format(
            QApplication.applicationName()))
    else:
        messageBox.setWindowTitle("{0}".format(title))
#        messageBox.setWindowTitle("{0} - {1}".format(
#            QApplication.applicationName(), title))            
    messageBox.setText(text)
    messageBox.setStandardButtons(buttons)
    messageBox.setDefaultButton(defaultButton)
    messageBox.exec_()
    clickedButton = messageBox.clickedButton()
    if clickedButton is None:
        return QMessageBox.NoButton
    else:
        return messageBox.standardButton(clickedButton)

# the about functions are here for consistancy
about = QMessageBox.about
aboutQt = QMessageBox.aboutQt

def critical(parent, title, text, 
             buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
    """
    Function to show a modal critical message box.
    
    @param parent parent widget of the message box (QWidget)
    @param title caption of the message box (string)
    @param text text to be shown by the message box (string)
    @param buttons flags indicating which buttons to show 
        (QMessageBox.StandardButtons)
    @param defaultButton flag indicating the default button
        (QMessageBox.StandardButton)
    @return button pressed by the user (QMessageBox.StandardButton)
    """
    return __messageBox(parent, title, text, QMessageBox.Critical, 
                        buttons, defaultButton)

def information(parent, title, text, 
                buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
    """
    Function to show a modal information message box.
    
    @param parent parent widget of the message box (QWidget)
    @param title caption of the message box (string)
    @param text text to be shown by the message box (string)
    @param buttons flags indicating which buttons to show 
        (QMessageBox.StandardButtons)
    @param defaultButton flag indicating the default button
        (QMessageBox.StandardButton)
    @return button pressed by the user (QMessageBox.StandardButton)
    """
    return __messageBox(parent, title, text, QMessageBox.Information, 
                        buttons, defaultButton)

def question(parent, title, text, 
             buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
    """
    Function to show a modal question message box.
    
    @param parent parent widget of the message box (QWidget)
    @param title caption of the message box (string)
    @param text text to be shown by the message box (string)
    @param buttons flags indicating which buttons to show 
        (QMessageBox.StandardButtons)
    @param defaultButton flag indicating the default button
        (QMessageBox.StandardButton)
    @return button pressed by the user (QMessageBox.StandardButton)
    """
    return __messageBox(parent, title, text, QMessageBox.Question, 
                        buttons, defaultButton)

def warning(parent, title, text, 
            buttons = QMessageBox.Ok, defaultButton = QMessageBox.NoButton):
    """
    Function to show a modal warning message box.
    
    @param parent parent widget of the message box (QWidget)
    @param title caption of the message box (string)
    @param text text to be shown by the message box (string)
    @param buttons flags indicating which buttons to show 
        (QMessageBox.StandardButtons)
    @param defaultButton flag indicating the default button
        (QMessageBox.StandardButton)
    @return button pressed by the user (QMessageBox.StandardButton)
    """
    return __messageBox(parent, title, text, QMessageBox.Warning, 
                        buttons, defaultButton)

################################################################################
##  Additional convenience functions                                          ##
################################################################################

def yesNo(parent, title, text, icon = Question, yesDefault = False):
    """
    Function to show a model yes/no message box.
    
    @param parent parent widget of the message box (QWidget)
    @param title caption of the message box (string)
    @param text text to be shown by the message box (string)
    @keyparam icon icon for the dialog (Critical, Information, Question or Warning)
    @keyparam yesDefault flag indicating that the Yes button should be the default
        button (boolean)
    @return flag indicating the selection of the Yes button (boolean)
    """
    assert icon in [Critical, Information, Question, Warning]
    
    res = __messageBox(parent, title, text, icon, 
                       QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No), 
                       yesDefault and QMessageBox.Yes or QMessageBox.No)
    return res == QMessageBox.Yes

def retryAbort(parent, title, text, icon = Question):
    """
    Function to show a model abort/retry message box.
    
    @param parent parent widget of the message box (QWidget)
    @param title caption of the message box (string)
    @param text text to be shown by the message box (string)
    @keyparam icon icon for the dialog (Critical, Information, Question or Warning)
    @return flag indicating the selection of the Retry button (boolean)
    """
    assert icon in [Critical, Information, Question, Warning]
    
    res = __messageBox(parent, title, text, icon, 
                    QMessageBox.StandardButtons(QMessageBox.Retry | QMessageBox.Abort), 
                    QMessageBox.Retry)
    return res == QMessageBox.Retry

def okToClearData(parent, title, text, saveFunc):
    """
    Function to show a model message box to ask for clearing the data.
    
    @param parent parent widget of the message box (QWidget)
    @param title caption of the message box (string)
    @param text text to be shown by the message box (string)
    @param saveFunc reference to a function performing the save action. It
        must be a parameterless function returning a flag indicating success.
    @return flag indicating that it is ok to clear the data (boolean)
    """
    res = __messageBox(parent, title, text, QMessageBox.Warning, 
        QMessageBox.StandardButtons(
            QMessageBox.Abort | QMessageBox.Discard | QMessageBox.Save), 
        QMessageBox.Save)
    if res == QMessageBox.Abort:
        return False
    if res == QMessageBox.Save:
        return saveFunc()
    return True
