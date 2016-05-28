#!/usr/bin/env python3

"""
   Smoketest.py: Regression testing utility for Graphyne.  Multiprocessing wrapper for Smokest, allowing multiple simultaneous tests against different persistence types.
"""

__author__ = 'David Stocker'
__copyright__ = 'Copyright 2016, David Stocker'   
 
__license__ = 'MIT'
__version__ = '1.0.0'
__maintainer__ = 'David Stocker'
__email__ = 'mrdave991@gmail.com'
__status__ = 'Production'



from xml.dom import minidom
from time import ctime
from os.path import expanduser
import copy
import os
import codecs
import time
import decimal
import queue
import sys
#from os.path import expanduser

import Graphyne.Graph as Graph
import Graphyne.Fileutils as Fileutils
import Graphyne.Exceptions as Exceptions

responseQueue = queue.Queue()
entityList = []
scriptFacade = None


global testImplicit
testImplicit = True


#Globals
#graphDir = expanduser("~")
#graphDir = os.getcwd()
graphDir = os.path.dirname(os.path.abspath(__file__))
testDirPath = os.path.join("Config", "Test")
configDirPath = os.path.join("utils", "Config")
        
resultFile = None
moduleName = 'Smoketest'     
logType = Graph.logTypes.CONTENT
logLevel = Graph.logLevel




class DBError(ValueError):
    pass


def testMetaMemeProperty():
    method = moduleName + '.' + 'testMetaMemeProperty'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, "MetaMeme_Properties.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        n = n+1
        stringArray = str.split(eachReadLine)
        testArgumentMap = {stringArray[1] : stringArray[2]}
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, metameme %s" %(n, stringArray[0])])

        #colums after 2 can me repeated in pairs.  4/3 and 6/5 can also contain argument/vlaue pairs
        try: testArgumentMap[str(stringArray[3])] = str(stringArray[4])
        except: pass
        try: testArgumentMap[str(stringArray[5])] = str(stringArray[6])
        except: pass   
        try: testArgumentMap[str(stringArray[7])] = str(stringArray[8])
        except: pass
        try: testArgumentMap[str(stringArray[9])] = str(stringArray[10])
        except: pass   
        try: testArgumentMap[str(stringArray[11])] = str(stringArray[12])
        except: pass 
        
        removeMe = 'XXX'
        try:
            del testArgumentMap[removeMe]
        except: pass   

        allTrue = True
        errata = []
    
        try:
            mmToTest = Graph.templateRepository.templates[stringArray[0]]
            props = mmToTest.properties
            Graph.logQ.put( [logType , logLevel.DEBUG , method , "testing metameme %s, props = %s" %(mmToTest.path.fullTemplatePath, props)])
            for testKey in testArgumentMap.keys():
                testType = testArgumentMap[testKey]
                Graph.logQ.put( [logType , logLevel.DEBUG , method , "testKey = %s, testType = %s" %(testKey, testType)])
                #ToDo: Fix Me.  We should not be using temp properties anymore
                try:
                    prop = mmToTest.getProperty(testKey)
                    Graph.logQ.put( [logType , logLevel.DEBUG , method , "prop = %s" %(prop)])
                    splitName = testKey.rpartition('.')
                    if (prop is not None) and (prop.name.find(splitName[2]) < 0):
                        Graph.logQ.put( [logType , logLevel.DEBUG , method , "property %s and test property %s don't match" %(prop.name, testKey)])
                        allTrue = False
                    else:
                        Graph.logQ.put( [logType , logLevel.DEBUG , method , "property %s and test property %s match" %(prop.name, testKey)])
        
                    if prop is not None:
                        if prop.propertyType != testType:
                            Graph.logQ.put( [logType , logLevel.WARNING , method , "property %s type %s and testType %s do not match" %(prop.name, prop.propertyType, testType)])
                            allTrue = False
                        else:
                            Graph.logQ.put( [logType , logLevel.DEBUG , method , "property %s type %s and testType %s match" %(prop.name, prop.propertyType, testType)])
                    else:
                        Graph.logQ.put( [logType , logLevel.WARNING , method , "property %s is invalid" %(testKey)])
                except Exception as e:
                    Graph.logQ.put( [logType , logLevel.ERROR , method , "Error pulling testkey %s from %s's properties.  Traceback = %s" %(testKey, mmToTest.path.fullTemplatePath, e)])
                    allTrue = False
            if allTrue == False:
                Graph.logQ.put( [logType , logLevel.DEBUG , method , "testkey %s has no match" %(testKey)])
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(allTrue)
        expectedResult = stringArray[13]
        results = [n, testcase, allTrueResult, expectedResult, copy.deepcopy(errata)]
        resultSet.append(results)
        
        del errata
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    
    
    

def testMetaMemeSingleton():
    method = moduleName + '.' + 'testMetaMemeSingleton'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []

        
    #try:
    testFileName = os.path.join(testDirPath, "MetaMeme_Singleton.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, metameme %s" %(n, stringArray[0])])

        expectedTestResult = False
        if stringArray[1] == 'TRUE': 
            expectedTestResult = True
        Graph.logQ.put( [logType , logLevel.DEBUG , method , 'Metameme %s is expected to be a singleton == %s' %(stringArray[0], expectedTestResult)])
        testResult = False
        
        try:
            mmToTest = Graph.templateRepository.resolveTemplateAbsolutely(stringArray[0])
            if mmToTest.isSingleton == True:
                Graph.logQ.put( [logType , logLevel.DEBUG , method , 'Metameme %s is a singleton' %(stringArray[0])])
                testResult = True
            else:
                Graph.logQ.put( [logType , logLevel.DEBUG , method , 'Metameme %s is not a singleton' %(stringArray[0])])
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[1]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    
    
    
def testMetaMemeSwitch():
    method = moduleName + '.' + 'testMetaMemeSwitch'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []

        
    #try:
    testFileName = os.path.join(testDirPath, "MetaMeme_Switch.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, metameme %s" %(n, stringArray[0])])

        expectedTestResult = False
        if stringArray[1] == 'TRUE': 
            expectedTestResult = True
        Graph.logQ.put( [logType , logLevel.DEBUG , method , 'Metameme %s is expected to be a singleton == %s' %(stringArray[0], expectedTestResult)])
        testResult = False
        
        try:
            mmToTest = Graph.templateRepository.resolveTemplateAbsolutely(stringArray[0])
            if mmToTest.isSwitch == True:
                Graph.logQ.put( [logType , logLevel.DEBUG , method , 'Metameme %s is a switch' %(stringArray[0])])
                testResult = True
            else:
                Graph.logQ.put( [logType , logLevel.DEBUG , method , 'Metameme %s is not a switch' %(stringArray[0])])
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[1]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet




def testMetaMemeEnhancements():
    method = moduleName + '.' + 'testMetaMemeEnhancements'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []

        
    #try:
    testFileName = os.path.join(testDirPath, "MetaMeme_Enhances.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        testArgumentList = []
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, metameme %s" %(n, stringArray[0])])

        #columns 1&2 may contain data
        if stringArray[1] != 'XXX':
            testArgumentList.append(stringArray[1])
        if stringArray[2] != 'XXX':
            testArgumentList.append(stringArray[2])

        allTrue = False
        try:
            mmToTest = Graph.templateRepository.resolveTemplateAbsolutely(stringArray[0])
            Graph.logQ.put( [logType , logLevel.DEBUG , method , "testing metameme %s, enhancements = %s" %(mmToTest.path.fullTemplatePath, mmToTest.enhances)])
            for testArgument in testArgumentList:
                #Hack alert!  If we have no enhancements in the testcase, the result should be false.  
                #    Hence we initialize to false, but if we actually have test cases, we re-initialize to True
                allTrue = True
            for testArgument in testArgumentList:
                amIextended = Graph.templateRepository.resolveTemplate(mmToTest.path, testArgument)
                Graph.logQ.put( [logType , logLevel.DEBUG , method , "checking to see if %s, enhances %s" %(mmToTest.path.fullTemplatePath, amIextended.path.fullTemplatePath)])
                
                #iterate over the enhancement list and see if we have a match
                testResult = False 
                for enhancement in mmToTest.enhances:
                    Graph.logQ.put( [logType , logLevel.DEBUG , method , "testing enhancement %s against %s" %(enhancement, amIextended.path.fullTemplatePath)])
                    try:
                        enhancedMetaMeme = Graph.templateRepository.resolveTemplate(mmToTest.path, enhancement)
                        if enhancedMetaMeme.path.fullTemplatePath == amIextended.path.fullTemplatePath:
                            testResult = True
                            Graph.logQ.put( [logType , logLevel.DEBUG , method , "enhancement %s == %s" %(enhancement, amIextended.path.fullTemplatePath)])
                        else:
                            Graph.logQ.put( [logType , logLevel.DEBUG , method , "enhancement %s != %s" %(enhancement, amIextended.path.fullTemplatePath)])
                    except:
                        Graph.logQ.put( [logType , logLevel.DEBUG , method , "tested metameme %s extends metameme %s, but is not in the repository." %(enhancement, mmToTest.path.fullTemplatePath)])
                if testResult == False:
                    allTrue = False
                if allTrue == False:
                    Graph.logQ.put( [logType , logLevel.DEBUG , method , "tested metameme %s does not have sought tested enhancement %s" %(mmToTest.path.fullTemplatePath, amIextended.path.fullTemplatePath)])
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(allTrue)
        expectedResult = stringArray[3]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet    
    
    
    
def testMemeValidity():
    method = moduleName + '.' + 'testMemeValidity'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, "Meme_Validity.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    memeValid = False
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, metameme %s" %(n, stringArray[0])])

        expectedTestResult = False
        if stringArray[1] == 'TRUE': 
            expectedTestResult = True
        try:
            memeToTest = Graph.templateRepository.resolveTemplateAbsolutely(stringArray[0])
            memeValidReport = memeToTest.validate([])
            memeValid = memeValidReport[0]
            if expectedTestResult != memeValid:
                Graph.logQ.put( [logType , logLevel.DEBUG , method , "testkey %s has an unexpected validity status" %(memeToTest.path.fullTemplatePath)])
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(memeValid)
        expectedResult = stringArray[1]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    
    
    
def testMemeSingleton():
    method = moduleName + '.' + 'testMemeSingleton'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, "Meme_Singleton.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, metameme %s" %(n, stringArray[0])])

        expectedTestResult = False
        if stringArray[1] == 'TRUE': 
            expectedTestResult = True
        testResult = False
        try:
            mmToTest = Graph.templateRepository.templates[stringArray[0]]
            if expectedTestResult == mmToTest.isSingleton:
                if mmToTest.entityUUID is not None:
                    testResult = True
                else:
                    Graph.logQ.put( [logType , logLevel.DEBUG , method , "meme %s has no deployed entity" %(stringArray[0])])
            else:
                Graph.logQ.put( [logType , logLevel.DEBUG , method , "meme %s has an unexpected singleton status" %(stringArray[0])])
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[1]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
        


def testEntityPhase1(phaseName = 'testEntityPhase1', fName = "Entity_Phase1.atest"):
    ''' Create the entity from the meme and add it to the entity repo.  
        Retrieve the entity.  
        Check to see if it has the properties it is supposed to, 
            if the type is correct and if the value is correct. 
    
    Entity Phase 5 also uses this function        
    '''
    method = moduleName + '.' + phaseName
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, fName)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.INFO , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        try:
            entityID = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            Graph.logQ.put( [logType , logLevel.DEBUG , method , "Entity UUID = %s" %(entityID)])
            propTypeCorrect = False
            propValueCorrect = False
            
            Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])
            hasProp = Graph.scriptFacade.getEntityHasProperty(entityID, stringArray[1])
            if hasProp == False:
                Graph.logQ.put( [logType , logLevel.DEBUG , method , "entity from meme %s does not have property %s" %(entityID, stringArray[1])])
            else:
                propType = Graph.scriptFacade.getEntityPropertyType(entityID, stringArray[1])
                if stringArray[2] == propType:
                    propTypeCorrect = True
                else:
                    Graph.logQ.put( [logType , logLevel.DEBUG , method , "property %s in entity from meme %s is wrong type.  Expected %s.  Got %s" %(stringArray[1], entityID, stringArray[2], propType)])
                
                propValue = Graph.scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
                if propType == 'Boolean':
                    expValue = False
                    if stringArray[3].lower() == "true":
                        expValue = True
                    if propValue == expValue:
                        propValueCorrect = True
                elif propType == 'Decimal':
                    expValue = decimal.Decimal(stringArray[3])
                    if propValue == expValue:
                        propValueCorrect = True
                elif propType == 'Integer':
                    expValue = int(stringArray[3])
                    if propValue == expValue:
                        propValueCorrect = True
                else:
                    if propValue == stringArray[3]:
                        propValueCorrect = True
    
                if propValueCorrect == False:
                    Graph.logQ.put( [logType , logLevel.DEBUG , method , "property %s in entity from meme %s is wrong value.  Expected %s.  Got %s" %(stringArray[1], stringArray[0], stringArray[3], propValue)])
    
            if (propValueCorrect == True) and (propTypeCorrect == True) and (hasProp == True):
                testResult = True
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[4]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    
    
    
def testEntityPhase1_1(phaseName = 'testEntityPhase1_1', fName = "Entity_Phase1.atest"):
    ''' a repeat of testEntityPhase1, but using the Python script interface instead of going directly against Graph.scriptFacade 
        Tests the following script commands:
            createEntityFromMeme
            getEntityHasProperty
            getEntityPropertyType
            getEntityPropertyValue
    '''
    method = moduleName + '.' + phaseName
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, fName)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.INFO , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        try:
            #entityID = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            entityID = scriptFacade.createEntityFromMeme(stringArray[0])
            Graph.logQ.put( [logType , logLevel.DEBUG , method , "Entity UUID = %s" %(entityID)])
            propTypeCorrect = False
            propValueCorrect = False
            
            Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])
            #hasProp = Graph.scriptFacade.getEntityHasProperty(entityID, stringArray[1])
            hasProp = scriptFacade.getEntityHasProperty(entityID, stringArray[1])
            if hasProp == False:
                Graph.logQ.put( [logType , logLevel.DEBUG , method , "entity from meme %s does not have property %s" %(entityID, stringArray[1])])
            else:
                #propType = Graph.scriptFacade.getEntityPropertyType(entityID, stringArray[1])
                propType = scriptFacade.getEntityPropertyType(entityID, stringArray[1])
                if stringArray[2] == propType:
                    propTypeCorrect = True
                else:
                    Graph.logQ.put( [logType , logLevel.DEBUG , method , "property %s in entity from meme %s is wrong type.  Expected %s.  Got %s" %(stringArray[1], entityID, stringArray[2], propType)])
                
                #propValue = Graph.scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
                propValue = scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
                if propType == 'Boolean':
                    expValue = False
                    if stringArray[3].lower() == "true":
                        expValue = True
                    if propValue == expValue:
                        propValueCorrect = True
                elif propType == 'Decimal':
                    expValue = decimal.Decimal(stringArray[3])
                    if propValue == expValue:
                        propValueCorrect = True
                elif propType == 'Integer':
                    expValue = int(stringArray[3])
                    if propValue == expValue:
                        propValueCorrect = True
                else:
                    if propValue == stringArray[3]:
                        propValueCorrect = True
    
                if propValueCorrect == False:
                    Graph.logQ.put( [logType , logLevel.DEBUG , method , "property %s in entity from meme %s is wrong value.  Expected %s.  Got %s" %(stringArray[1], stringArray[0], stringArray[3], propValue)])
    
            if (propValueCorrect == True) and (propTypeCorrect == True) and (hasProp == True):
                testResult = True
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[4]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet

    
    
    
def testEntityPhase2(testPhase = 'testEntityPhase2', fileName = 'Entity_Phase2.atest'):
    ''' Change the values of the various properties.  
        Can we change the value to the desired value and are constraints working? '''
    method = moduleName + '.' + testPhase
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    testFileName = os.path.join(testDirPath, fileName)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        try:
            entityID = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            Graph.scriptFacade.setEntityPropertyValue(entityID, stringArray[1], stringArray[2])
            getter = Graph.scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
            propType = Graph.scriptFacade.getEntityPropertyType(entityID, stringArray[1])
            
            #reformat the expected result from unicode string to that which is expected in the property
            expectedResult = None
            if propType == "String":
                expectedResult = stringArray[2]
            elif propType == "Integer":    
                expectedResult = int(stringArray[2])
            elif propType == "Decimal":    
                expectedResult = decimal.Decimal(stringArray[2])
            else:    
                expectedResult = False
                if str.lower(stringArray[2]) == 'true':
                    expectedResult = True
        
            #now compare getter to the reformatted stringArray[2] and see if we have successfully altered the property
            if getter == expectedResult:
                testResult = True

        except Exceptions.ScriptError:
            #Some test cases violate restriction constraints and will raise an exception.
            # This works as intended  
            testResult = False
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[3]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    
    
    
def testEntityPhase2_1( testPhase = 'testEntityPhase2_1', fileName = 'Entity_Phase2.atest'):
    ''' a repeat of testEntityPhase2, but using the Python script interface instead of going directly against Graph.scriptFacade 
        Tests the following script commands:
            setEntityPropertyValue
            getEntityPropertyValue
            getEntityPropertyType 
    '''
    method = moduleName + '.' + testPhase
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    testFileName = os.path.join(testDirPath, fileName)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        try:
            entityID = scriptFacade.createEntityFromMeme(stringArray[0])
            scriptFacade.setEntityPropertyValue(entityID, stringArray[1], stringArray[2])
            getter = scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
            propType = scriptFacade.getEntityPropertyType(entityID, stringArray[1])
            
            #reformat the expected result from unicode string to that which is expected in the property
            expectedResult = None
            if propType == "String":
                expectedResult = stringArray[2]
            elif propType == "Integer":    
                expectedResult = int(stringArray[2])
            elif propType == "Decimal":    
                expectedResult = decimal.Decimal(stringArray[2])
            else:    
                expectedResult = False
                if str.lower(stringArray[2]) == 'true':
                    expectedResult = True

            #now compare getter to the reformatted stringArray[2] and see if we have successfully altered the property
            if getter == expectedResult:
                testResult = True

        except Exceptions.ScriptError:
            #Some test cases violate restriction constraints and will raise an exception.
            # This works as intended  
            testResult = False
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[3]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    
    


def testEntityPhase3():
    ''' Add and remove properties.  
        Remove custom properties.  
        
        Tests the following script commands:
            addEntityDecimalProperty
            addEntityIntegerProperty
            addEntityStringProperty
            addEntityBooleanProperty
            removeAllCustomPropertiesFromEntity
            removeEntityProperty
        
        Step 1.  add a prop and test its existence and value
        Step 2.  remove that custom prop and check to make sure it is gone (getHasProperty == False)
        Step 3.  add the prop again, test its existence and then use removeAllCustomPropertiesFromEntity to remove it'''
    method = moduleName + '.' + 'testEntityPhase3'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    testFileName = os.path.join(testDirPath, "Entity_Phase3.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        
        step1Result = False
        step2Result = False
        step3Result = False
        try:

            entityID = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            
            #step 1
            if stringArray[2] == "String":
                Graph.scriptFacade.addEntityStringProperty(entityID, stringArray[1], stringArray[3])
                expectedResult = stringArray[3]
            elif stringArray[2] == "Integer":
                Graph.scriptFacade.addEntityIntegerProperty(entityID, stringArray[1], stringArray[3])
                expectedResult = int(stringArray[3])
            elif stringArray[2] == "Decimal":
                Graph.scriptFacade.addEntityDecimalProperty(entityID, stringArray[1], stringArray[3])
                expectedResult = decimal.Decimal(stringArray[3])
            else:
                Graph.scriptFacade.addEntityBooleanProperty(entityID, stringArray[1], stringArray[3])
                expectedResult = False
                if str.lower(stringArray[3]) == 'true':
                    expectedResult = True
                    
            getter = Graph.scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
            #now compare getter to the reformatted stringArray[2] and see if we have successfully altered the property
            if getter == expectedResult:
                step1Result = True
                
            #step 2
            Graph.scriptFacade.removeEntityProperty(entityID, stringArray[1])
            getter = Graph.scriptFacade.getEntityHasProperty(entityID, stringArray[1])
            if getter == False:
                step2Result = True
                
            #step 3
            if stringArray[2] == "String":
                Graph.scriptFacade.addEntityStringProperty(entityID, stringArray[1], stringArray[3])
            elif stringArray[2] == "Integer":
                Graph.scriptFacade.addEntityIntegerProperty(entityID, stringArray[1], stringArray[3])
            elif stringArray[2] == "Decimal":
                Graph.scriptFacade.addEntityDecimalProperty(entityID, stringArray[1], stringArray[3])
            else:
                Graph.scriptFacade.addEntityBooleanProperty(entityID, stringArray[1], stringArray[3])
            Graph.scriptFacade.removeAllCustomPropertiesFromEntity(entityID)
            getter = Graph.scriptFacade.getEntityHasProperty(entityID, stringArray[1])
            if getter == False:
                step3Result = True

        except Exceptions.ScriptError:
            #Some test cases violate restriction constraints and will raise an exception.
            # This works as intended  
            testResult = False
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)
            
        if (step1Result == True) and (step2Result == True) and (step3Result == True):
            testResult = True

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = "True"
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    
    
    
def testEntityPhase3_1():
    ''' a repeat of testEntityPhase3, but using the Python script interface instead of going directly against Graph.scriptFacade  
        
        Tests the following script commands:
            addEntityDecimalProperty
            addEntityIntegerProperty
            addEntityStringProperty
            addEntityBooleanProperty
            removeAllCustomPropertiesFromEntity
            removeEntityProperty
    '''
    method = moduleName + '.' + 'testEntityPhase3_1'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    testFileName = os.path.join(testDirPath, "Entity_Phase3.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        
        step1Result = False
        step2Result = False
        step3Result = False
        try:

            entityID = scriptFacade.createEntityFromMeme(stringArray[0])
            
            #step 1
            if stringArray[2] == "String":
                #Graph.scriptFacade.addEntityStringProperty(entityID, stringArray[1], stringArray[3])
                scriptFacade.addEntityStringProperty(entityID, stringArray[1], stringArray[3])
                expectedResult = stringArray[3]
            elif stringArray[2] == "Integer":
                #Graph.scriptFacade.addEntityIntegerProperty(entityID, stringArray[1], stringArray[3])
                scriptFacade.addEntityIntegerProperty(entityID, stringArray[1], stringArray[3])
                expectedResult = int(stringArray[3])
            elif stringArray[2] == "Decimal":
                #Graph.scriptFacade.addEntityDecimalProperty(entityID, stringArray[1], stringArray[3])
                scriptFacade.addEntityDecimalProperty(entityID, stringArray[1], stringArray[3])
                expectedResult = decimal.Decimal(stringArray[3])
            else:
                Graph.scriptFacade.addEntityBooleanProperty(entityID, stringArray[1], stringArray[3])
                expectedResult = False
                if str.lower(stringArray[3]) == 'true':
                    expectedResult = True
                    
            #getter = Graph.scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
            getter = scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
            #now compare getter to the reformatted stringArray[2] and see if we have successfully altered the property
            if getter == expectedResult:
                step1Result = True
                
            #step 2
            #Graph.scriptFacade.removeEntityProperty(entityID, stringArray[1])
            #getter = Graph.scriptFacade.getEntityHasProperty(entityID, stringArray[1])
            scriptFacade.removeEntityProperty(entityID, stringArray[1])
            getter = scriptFacade.getEntityHasProperty(entityID, stringArray[1])
            if getter == False:
                step2Result = True
                
            #step 3
            if stringArray[2] == "String":
                #Graph.scriptFacade.addEntityStringProperty(entityID, stringArray[1], stringArray[3])
                scriptFacade.addEntityStringProperty(entityID, stringArray[1], stringArray[3])
            elif stringArray[2] == "Integer":
                #Graph.scriptFacade.addEntityIntegerProperty(entityID, stringArray[1], stringArray[3])
                scriptFacade.addEntityIntegerProperty(entityID, stringArray[1], stringArray[3])
            elif stringArray[2] == "Decimal":
                #Graph.scriptFacade.addEntityDecimalProperty(entityID, stringArray[1], stringArray[3])
                scriptFacade.addEntityIntegerProperty(entityID, stringArray[1], stringArray[3])
            else:
                #Graph.scriptFacade.addEntityBooleanProperty(entityID, stringArray[1], stringArray[3])
                scriptFacade.addEntityBooleanProperty(entityID, stringArray[1], stringArray[3])
            #Graph.scriptFacade.removeAllCustomPropertiesFromEntity(entityID)
            #getter = Graph.scriptFacade.getEntityHasProperty(entityID, stringArray[1])
            scriptFacade.removeAllCustomPropertiesFromEntity(entityID)
            getter = scriptFacade.getEntityHasProperty(entityID, stringArray[1])
            if getter == False:
                step3Result = True

        except Exceptions.ScriptError:
            #Some test cases violate restriction constraints and will raise an exception.
            # This works as intended  
            testResult = False
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)
            
        if (step1Result == True) and (step2Result == True) and (step3Result == True):
            testResult = True

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = "True"
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])  
    return resultSet  
    
    
    
    
def testEntityPhase4():
    ''' Revert the entity to original condition. 
        
        Tests the following script commands:
            revertEntityPropertyValues
        
        Step 1.  change a standard value
        Step 2.  use revertEntityPropertyValues to return it to stock'''
        
    method = moduleName + '.' + 'testEntityPhase4'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    testFileName = os.path.join(testDirPath, "Entity_Phase4.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        try:
            entityID = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            baseValue = Graph.scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
            
            Graph.scriptFacade.setEntityPropertyValue(entityID, stringArray[1], stringArray[2])
            getter = Graph.scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
            propType = Graph.scriptFacade.getEntityPropertyType(entityID, stringArray[1])
            
            #reformat the expected result from unicode string to that which is expected in the property
            expectedResult = None
            if propType == "String":
                expectedResult = stringArray[2]
            elif propType == "Integer":    
                expectedResult = int(stringArray[2])
            elif propType == "Decimal":    
                expectedResult = decimal.Decimal(stringArray[2])
            else:    
                expectedResult = False
                if str.lower(stringArray[2]) == 'true':
                    expectedResult = True

            #now compare getter to the reformatted stringArray[2] and see if we have successfully altered the property
            if getter == expectedResult:
                Graph.scriptFacade.revertEntityPropertyValues(entityID, False)
                getter = Graph.scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
                if getter == baseValue:
                    testResult = True

        except Exceptions.ScriptError:
            #Some test cases violate restriction constraints and will raise an exception.
            # This works as intended  
            testResult = False
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = "True"
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    
    
    
    
def testEntityPhase4_1():
    ''' a repeat of testEntityPhase3, but using the Python script interface instead of going directly against Graph.scriptFacade '''
        
    method = moduleName + '.' + 'testEntityPhase4.1'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    testFileName = os.path.join(testDirPath, "Entity_Phase4.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        try:
            entityID = scriptFacade.createEntityFromMeme(stringArray[0])
            baseValue = scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
            
            scriptFacade.setEntityPropertyValue(entityID, stringArray[1], stringArray[2])
            getter = scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
            propType = scriptFacade.getEntityPropertyType(entityID, stringArray[1])
            
            #reformat the expected result from unicode string to that which is expected in the property
            expectedResult = None
            if propType == "String":
                expectedResult = stringArray[2]
            elif propType == "Integer":    
                expectedResult = int(stringArray[2])
            elif propType == "Decimal":    
                expectedResult = decimal.Decimal(stringArray[2])
            else:    
                expectedResult = False
                if str.lower(stringArray[2]) == 'true':
                    expectedResult = True

            #now compare getter to the reformatted stringArray[2] and see if we have successfully altered the property
            if getter == expectedResult:
                scriptFacade.revertEntityPropertyValues(entityID, False)
                getter = scriptFacade.getEntityPropertyValue(entityID, stringArray[1])
                if getter == baseValue:
                    testResult = True

        except Exceptions.ScriptError:
            #Some test cases violate restriction constraints and will raise an exception.
            # This works as intended  
            testResult = False
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = "True"
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    



def testEntityPhase6():
    ''' Check and see if the meme is a singleton
    
    Tests getMemeIsSingleton
    Tests getEntityFromMeme in singleton context
    
    
    Strategy - 
    If the meme is a singleton, then it should have had an entity created already
    1 - Is the meme a singleton?
        2a - If not, then entity.uuid should be non-existent
        2b - If so, then entity.uuid should have a UUID
            3b - create an entiity
            4b - is the UUID the same as before?  It should be
    '''
    method = moduleName + '.' + 'testEntityPhase6'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    testFileName = os.path.join(testDirPath, "Entity_Phase6.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        expectedTestResult = False
        if stringArray[1] == 'TRUE': 
            expectedTestResult = True
        testResult = False
        
        
        mSingletonFlagCorrect = False
        mEntityUUIDCorrect = False
        eSingletonFlagCorrect = False
        eSameUUIDasInMeme = False

        try: 
        
            isSingleton = Graph.scriptFacade.getIsMemeSingleton(stringArray[0])
            if expectedTestResult == isSingleton:
                mSingletonFlagCorrect = True
                
            meme = Graph.templateRepository.resolveTemplateAbsolutely(stringArray[0])  
            oldEntityID = None
            
            #Is the meme a singleton?  
            if isSingleton == False:
                #2a - If not, then entity.uuid should be non-existent
                try:
                    if meme.entityUUID is None:
                        mEntityUUIDCorrect = True
                except:
                    mEntityUUIDCorrect = True
            else:
                #2b - If so, then entity.uuid should have a UUID
                if meme.entityUUID is not None:
                    mEntityUUIDCorrect = True
                    oldEntityID = meme.entityUUID 
    
    
                
            entityID = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            entityIsSingleton = Graph.scriptFacade.getIsEntitySingleton(entityID)
            if isSingleton == False:
                if entityIsSingleton == False:
                    eSingletonFlagCorrect = True
                eSameUUIDasInMeme = True
            else:
                if (entityIsSingleton == True) and (entityID == oldEntityID):
                    eSingletonFlagCorrect = True
                    eSameUUIDasInMeme = True
                
            #now compare getter to the reformatted stringArray[2] and see if we have successfully altered the property
            if (mSingletonFlagCorrect == True) and (mEntityUUIDCorrect == True) and (eSingletonFlagCorrect == True) and (eSameUUIDasInMeme == True):
                testResult = True

        except Exceptions.ScriptError:
            #Some test cases violate restriction constraints and will raise an exception.
            # This works as intended  
            testResult = False
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = "True"
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet

    
    
    
def testEntityPhase6_1():
    ''' Repeat 6 using python script interface.
    
    Tests the following script functions:
        getIsEntitySingleton
        getIsMemeSingleton
    '''
    method = moduleName + '.' + 'testEntityPhase6.1'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    testFileName = os.path.join(testDirPath, "Entity_Phase6.atest")
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.DEBUG , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        expectedTestResult = False
        if stringArray[1] == 'TRUE': 
            expectedTestResult = True
        testResult = False
        
        
        mSingletonFlagCorrect = False
        mEntityUUIDCorrect = False
        eSingletonFlagCorrect = False
        eSameUUIDasInMeme = False

        try: 
        
            isSingleton = scriptFacade.getIsMemeSingleton(stringArray[0])
            if expectedTestResult == isSingleton:
                mSingletonFlagCorrect = True
                
            meme = Graph.templateRepository.resolveTemplateAbsolutely(stringArray[0])  
            oldEntityID = None
            
            #Is the meme a singleton?  
            if isSingleton == False:
                #2a - If not, then entity.uuid should be non-existent
                try:
                    if meme.entityUUID is None:
                        mEntityUUIDCorrect = True
                except:
                    mEntityUUIDCorrect = True
            else:
                #2b - If so, then entity.uuid should have a UUID
                if meme.entityUUID is not None:
                    mEntityUUIDCorrect = True
                    oldEntityID = meme.entityUUID 
    
    
                
            entityID = scriptFacade.createEntityFromMeme(stringArray[0])
            entityIsSingleton = scriptFacade.getIsEntitySingleton(entityID)
            if isSingleton == False:
                if entityIsSingleton == False:
                    eSingletonFlagCorrect = True
                eSameUUIDasInMeme = True
            else:
                if (entityIsSingleton == True) and (entityID == oldEntityID):
                    eSingletonFlagCorrect = True
                    eSameUUIDasInMeme = True
                
            #now compare getter to the reformatted stringArray[2] and see if we have successfully altered the property
            if (mSingletonFlagCorrect == True) and (mEntityUUIDCorrect == True) and (eSingletonFlagCorrect == True) and (eSameUUIDasInMeme == True):
                testResult = True

        except Exceptions.ScriptError:
            #Some test cases violate restriction constraints and will raise an exception.
            # This works as intended  
            testResult = False
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = "True"
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])    
    return resultSet





def testEntityPhase7(phaseName = 'testEntityPhase7', fName = "Entity_Phase7.atest"):
    ''' Create entities from the meme in the first two colums.
        Add a link between the two at the location on entity in from column 3.
        Check and see if each is a counterpart as seen from the other using the addresses in columns 4&5 (CheckPath & Backpath)
            & the filter.  
        
        The filter must be the same as the type of link (or None)
        The check location must be the same as the added loation.
        
      
    '''
    method = moduleName + '.' + phaseName
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    lresultSet = []
    del lresultSet[:]
        
    #try:
    testFileName = os.path.join(testDirPath, fName)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.INFO , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        try:
            entityID0 = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            entityID1 = Graph.scriptFacade.createEntityFromMeme(stringArray[1])
            
            #Attach entityID1 at the mount point specified in stringArray[2]
            if stringArray[2] != "X":
                #mountPoints = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[2], {}, 1)
                mountPoints = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[2], 1)
                                
                unusedMountPointsOverview = {}
                for mountPoint in mountPoints:
                    try:
                        mpMemeType = scriptFacade.getEntityMemeType(mountPoint)
                        unusedMountPointsOverview[mountPoint] = mpMemeType
                    except Exception as e:
                        #errorMessage = "debugHelperMemeType warning in Smoketest.testEntityPhase7.  Traceback = %s" %e
                        #Graph.logQ.put( [logType , logLevel.WARNING , method , errorMessage])
                        raise e
                
                for mountPoint in mountPoints:
                    scriptFacade.addEntityLink(mountPoint, entityID1, int(stringArray[5]))
            else:
                scriptFacade.addEntityLink(entityID0, entityID1, int(stringArray[5]))
              
            backTrackCorrect = False
            linkType = None
            if stringArray[6] != "X":
                linkType = int(stringArray[6])
            
            #see if we can get from entityID0 to entityID1 via stringArray[3]
            addLocationCorrect = False
            #addLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[3], [}, linkType)
            addLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[3], linkType)
            if len(addLocationList) > 0:
                addLocationCorrect = True
                
            #see if we can get from entityID1 to entityID0 via stringArray[4]
            backTrackCorrect = False
            #backTrackLocationList = scriptFacade.getLinkCounterpartsByType(entityID1, stringArray[4], {}, linkType)
            backTrackLocationList = scriptFacade.getLinkCounterpartsByType(entityID1, stringArray[4], linkType)
            if len(backTrackLocationList) > 0:
                backTrackCorrect = True   
            
            if (backTrackCorrect == True) and (addLocationCorrect == True):
                testResult = True
                
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[7]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        lresultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return lresultSet




def testEntityPhase9(phaseName = 'testEntityPhase9', fName = "Entity_Phase9.atest"):
    ''' A modified phase 7 test with entity link removal after testing.
        Add a link between the two at the location on entity in from column 3.
        Check and see if each is a counterpart as seen from the other using the addresses in columns 4&5 (CheckPath & Backpath)
            & the filter.  
        The filter must be the same as the type of link (or None)
        The check location must be the same as the added loation.
        
        
        (So far, so good.  this is the same as in phase 7)
        added:
            Now remove the link
            Check again to make sure that the link no longer exists         
      
    '''
    method = moduleName + '.' + phaseName
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, fName)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.INFO , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        part1TestResult = False
        testResult = False
        try:
            entityID0 = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            entityID1 = Graph.scriptFacade.createEntityFromMeme(stringArray[1])
            
            #Attach entityID1 at the mount point specified in stringArray[2]
            rememberMe = {}
            
            #mountPoints = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[2], {}, 1)
            mountPoints = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[2], 1)
            for mountPoint in mountPoints:
                scriptFacade.addEntityLink(mountPoint, entityID1, int(stringArray[5]))
                rememberMe[mountPoint] = entityID1
             
            backTrackCorrect = False
            linkType = None
            if stringArray[6] != "X":
                linkType = int(stringArray[6])
            
            #see if we can get from entityID0 to entityID1 via stringArray[3]
            addLocationCorrect = False
            #addLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[3], {}, linkType)
            addLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[3], linkType)
            if len(addLocationList) > 0:
                addLocationCorrect = True
                
            #see if we can get from entityID1 to entityID0 via stringArray[4]
            backTrackCorrect = False
            #backTrackLocationList = scriptFacade.getLinkCounterpartsByType(entityID1, stringArray[4], {}, linkType)
            backTrackLocationList = scriptFacade.getLinkCounterpartsByType(entityID1, stringArray[4], linkType)
            if len(backTrackLocationList) > 0:
                backTrackCorrect = True   
            
            if (backTrackCorrect == True) and (addLocationCorrect == True):
                part1TestResult = True
                
            #Time for phase 2    
            #Now remove that added member.  This is why we kept track of that added member; to speed up removal
            for mountPoint in rememberMe.keys():
                scriptFacade.removeEntityLink(mountPoint, entityID1)
    
            secondAddLocationCorrect = False
            #addLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[3], {}, linkType)
            addLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[3], linkType)
                
            if len(addLocationList) == 0:
                secondAddLocationCorrect = True
                
            if (part1TestResult == True) and (secondAddLocationCorrect == True):
                testResult = True 
                    
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[7]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"]) 
    return resultSet
   



def testEntityPhase10(phaseName = 'testEntityPhase10', fName = "Entity_Phase10.atest"):
    """ Create two entities from the meme in the first two colums.
        Both will should have the same singleton in their association (link) networks
        Try to traverse from one to the other
        
        This tests the 'singleton bridge' with respect to souble and triple wildcards  
        
      
    """
    method = moduleName + '.' + phaseName
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, fName)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.INFO , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])

        testResult = False
        
        try:
            entityID0 = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            
            #trackLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[2], {}, None)
            trackLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[2], None)
            if len(trackLocationList) > 0:
                testResult = True
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[3]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet




def testTraverseParams(phaseName = 'testTraverseParams', fName = "TraverseWithParams.atest"):
    """ Create a TraverseParameters.A and TraverseParameters.B.  Attach them and assign values to the edges (links).
        Then fpor each test case:
            1 -Try to select A (with or without params, depending on the test case)
            2 -Try to navigate to B (with or without node/traverse params, depending on the test case
            3 -Compare our cuccessful reaching of B with the expected outcome.
              
    """
    method = moduleName + '.' + phaseName
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, fName)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = eachReadLine.split(' | ')
        Graph.logQ.put( [logType , logLevel.INFO , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])
        
        if n == 40:
            unusedCatch = True

        testResult = False
        
        try:
            entityID0 = Graph.scriptFacade.createEntityFromMeme("TraverseParameters.A")
            entityID1 = Graph.scriptFacade.createEntityFromMeme("TraverseParameters.B")
            Graph.scriptFacade.addEntityLink(entityID0, entityID1, 0, {'a':4})
            
            if n == 70:
                unusedCatchMe = True
            
            traversePath = stringArray[0].strip()
            trackLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, traversePath, None)
            if len(trackLocationList) > 0:
                testResult = True
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[1].strip()
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet





def testNumericValue(filename):
    #NumericValue.atest
    method = moduleName + '.' + 'testNumericValue'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])   
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        testArgumentMap = {}

        testResult = False
        try:
            entityIDList = scriptFacade.getEntitiesByMemeType(stringArray[0])
            for entityIDListEntry in entityIDList:
                entityID = entityIDListEntry
            numberList = scriptFacade.evaluateEntity(entityID, testArgumentMap)
            argAsDecimal = decimal.Decimal(stringArray[1])
            if argAsDecimal in numberList:
                testResult = True
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[2]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet 




def testImplicitMeme(phaseName = 'testImplicitMeme', fName = "ImplicitMeme.atest"):
    ''' Create entities from the meme in the first two colums.
        Add a link between the two at the location on entity in from column 3, if it is not direct.  Otherwise diorectly to entity 0
        Check and see if each is a counterpart as seen from the other using the addresses in columns 4&5 (CheckPath & Backpath)
            & the filter.  
        
        The filter must be the same as the type of link (or None)
        The check location must be the same as the added loation.      
    '''
    method = moduleName + '.' + phaseName
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, fName)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
    
    for eachReadLine in allLines:
        errata = []
        n = n+1
        stringArray = str.split(eachReadLine)
        Graph.logQ.put( [logType , logLevel.INFO , method , "Starting testcase %s, meme %s" %(n, stringArray[0])])
        #debug
        #print ("Starting testcase %s, meme %s" %(n, stringArray[0]))
        #if n == 30:
        #    pass
        #/debug
        testResult = False
        try:
            try:
                entityID0 = Graph.scriptFacade.createEntityFromMeme(stringArray[0])
            except Exception as e:
                raise DBError(stringArray[0])
            try:
                entityID1 = Graph.scriptFacade.createEntityFromMeme(stringArray[1])
            except Exception as e:
                raise DBError(stringArray[1])
                
            
            #Attach entityID1 at the mount point specified in stringArray[2]
            if (stringArray[2] != '**DIRECT**'):
                #mountPoints = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[2], {}, 1)
                mountPoints = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[2], 1)
                for mountPoint in mountPoints:
                    scriptFacade.addEntityLink(mountPoint, entityID1, 0)
            else:
                #If we have a **DIRECT** mount, then attach entity 1 to entity 0
                scriptFacade.addEntityLink(entityID0, entityID1, 0)
              
            backTrackCorrect = False
            linkType = None
            
            #see if we can get from entityID0 to entityID1 via stringArray[3]
            addLocationCorrect = False
            #addLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[3], {}, linkType)
            addLocationList = scriptFacade.getLinkCounterpartsByType(entityID0, stringArray[3], linkType)
            if len(addLocationList) > 0:
                addLocationCorrect = True
                
            #see if we can get from entityID1 to entityID0 via stringArray[4]
            backTrackCorrect = False
            #backTrackLocationList = scriptFacade.getLinkCounterpartsByType(entityID1, stringArray[4], {}, linkType)
            backTrackLocationList = scriptFacade.getLinkCounterpartsByType(entityID1, stringArray[4], linkType)
            if len(backTrackLocationList) > 0:
                backTrackCorrect = True   
            
            if (backTrackCorrect == True) and (addLocationCorrect == True):
                testResult = True
        
        except DBError as e:
            errorMsg = ('Database Error!  Check to see if the Database has been started and that meme %s is in the appropriate table.' % (e) )
            errata.append(errorMsg)                    
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[2])
        allTrueResult = str(testResult)
        expectedResult = stringArray[5]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet



def testCondition(filename):
    method = moduleName + '.' + 'testCondition'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        
        entityIDList = scriptFacade.getEntitiesByMemeType(stringArray[0])
        for entityIDListEntry in entityIDList:
            subjectID = entityIDListEntry
            testArgumentMap = {'subjectID' : subjectID, 'objectID': subjectID, stringArray[2] : stringArray[1]}
        try:
            testArgumentMap[stringArray[4]] = stringArray[3]
        except:
            pass
        try:
            testArgumentMap[stringArray[6]] = stringArray[5]
        except:
            pass
        try:
            del testArgumentMap['XXX']
        except:
            pass


        testResult = False
        try:
            entityIDList = scriptFacade.getEntitiesByMemeType(stringArray[0])
            for entityIDListEntry in entityIDList:
                entityID = entityIDListEntry
            testResult = scriptFacade.evaluateEntity(entityID, testArgumentMap)
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[7]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet



def testAACondition(filename):
    method = moduleName + '.' + 'testAACondition'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        testArgumentMap = {}
        subjectID = scriptFacade.createEntityFromMeme(stringArray[1])
        objectID = None
        try:
            objectID = scriptFacade.createEntityFromMeme(stringArray[2])
        except:
            pass

        testArgumentMap['subjectID'] = subjectID
        if objectID is None:
            testArgumentMap['objectID'] = subjectID
        else:
            testArgumentMap['objectID'] = objectID
            
        try:
            del testArgumentMap['XXX']
        except:
            pass
        
        testResult = False
        try:
            testResult = scriptFacade.evaluateEntity(stringArray[0], testArgumentMap)
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            errata.append(errorMsg)

        testcase = str(stringArray[0])
        allTrueResult = str(testResult)
        expectedResult = stringArray[3]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet




def testSourceCreateMeme(filename):
    method = moduleName + '.' + 'testSourceCreateMeme'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        metamemePath = stringArray[0]
        modulePath = stringArray[1]
        memeName = stringArray[2]
        operationResult = {}
        
        testResult = False
        try:
            operationResult = scriptFacade.sourceMemeCreate(modulePath, memeName, metamemePath)
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            operationResult = {"memeID" : "%s.%s" %(modulePath, memeName), "ValidationResults" : [False, errorMsg]}
            errata.append(errorMsg)

        testcase = str(operationResult["memeID"])
        validation = operationResult["ValidationResults"]
        if validation[0] == True:
            testResult = True
        else:
            testResult = False
            errata = testResult[1]
        
        allTrueResult = str(testResult)
        expectedResult = stringArray[3]
        results = [n, testcase, allTrueResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet



def testSourceProperty(filename):
    method = moduleName + '.' + 'testSourceProperty'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        metamemePath = stringArray[0]
        modulePath = stringArray[1]
        memeName = stringArray[2]
        propName = stringArray[3]
        propValueStr = stringArray[4]
        operationResult = {}
        
        testResult = "False"
        try:
            sourceMeme = scriptFacade.sourceMemeCreate(modulePath, memeName, metamemePath)
            operationResult = scriptFacade.sourceMemePropertySet(sourceMeme["memeID"], propName, propValueStr)
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            operationResult = {"memeID" : "%s.%s" %(modulePath, memeName), "ValidationResults" : [False, errorMsg]}
            errata.append(errorMsg)

        testcase = "%s with property %s, %s" %(testResult[0], propName, propValueStr)
        
        validation = operationResult["ValidationResults"]
        if validation[0] == True:
            testResult = str(True)
        else:
            testResult = str(False)
            errata = validation[1]
        
        expectedResult = stringArray[5]
        results = [n, testcase, testResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet



def testSourcePropertyRemove(filename):
    method = moduleName + '.' + 'testSourcePropertyRemove'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        metamemePath = stringArray[0]
        modulePath = "%s_remove" %stringArray[1]
        memeName = stringArray[2]
        propName = stringArray[3]
        propValueStr = stringArray[4]
        sourceMeme = []
        
        testResult = str(False)
        try:
            sourceMeme = scriptFacade.sourceMemeCreate(modulePath, memeName, metamemePath)
            unusedAddProp = scriptFacade.sourceMemePropertySet(sourceMeme["memeID"], propName, propValueStr)
            operationResult = scriptFacade.sourceMemePropertyRemove(sourceMeme["memeID"], propName)
            
            #list: [u'SourceProperty1_remove.L', [True, []]]
            validation = operationResult["ValidationResults"]
            if validation[0] == True:
                testResult = str(True)
            else:
                testResult = str(False)
                errata = validation[1]
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            operationResult = {"memeID" : "%s.%s" %(modulePath, memeName), "ValidationResults" : [False, errorMsg]}
            errata.append(errorMsg)

        testcase = "%s with property %s, %s removed" %(sourceMeme["memeID"], propName, propValueStr)
        expectedResult = stringArray[5]
        results = [n, testcase, testResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet




def testSourceMember(filename):
    method = moduleName + '.' + 'testSourceMember'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        #e.g. (Examples.M, SourceMember3, M, Examples.L, SourceMember3, L, 2, False)
        
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        metamemePath = stringArray[0]
        modulePath = stringArray[1]
        memeName = stringArray[2]
        memberMetamemePath = stringArray[3]
        memberModulePath = stringArray[4]
        memberMemeName = stringArray[5]
        occurrence = stringArray[6]
        sourceMeme = ['']
        sourceMemberMeme = ['']
        
        testResult = str(False)
        try:
            sourceMeme = scriptFacade.sourceMemeCreate(modulePath, memeName, metamemePath)
            sourceMemberMeme = scriptFacade.sourceMemeCreate(memberModulePath, memberMemeName, memberMetamemePath)
            operationResult = scriptFacade.sourceMemeMemberAdd(sourceMeme["memeID"], sourceMemberMeme["memeID"], occurrence)
            validation = operationResult["ValidationResults"]
            if validation[0] == True:
                testResult = str(True)
            else:
                testResult = str(False)
                errata = validation[1]
        except Exception as e:
            errorMsg = ('Error in testcase testSourceMember!  Traceback = %s' % (e) )
            scriptFacade.writeError(errorMsg)
            errata.append(errorMsg)

        testcase = "%s has member %s" %(sourceMeme["memeID"], sourceMemberMeme["memeID"])
        expectedResult = stringArray[7]
        results = [n, testcase, testResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet




def testSourceMemberRemove(filename):
    method = moduleName + '.' + 'testSourceMemberRemove'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        metamemePath = stringArray[0]
        modulePath = "%s_remove" %stringArray[1]
        memeName = stringArray[2]
        memberMetamemePath = stringArray[3]
        memberModulePath = "%s_remove" %stringArray[4]
        memberMemeName = stringArray[5]
        occurrence = stringArray[6]
        sourceMeme = ['']
        sourceMemberMeme = ['']
        
        testResult = str(False)
        try:
            sourceMeme = scriptFacade.sourceMemeCreate(modulePath, memeName, metamemePath)
            sourceMemberMeme = scriptFacade.sourceMemeCreate(memberModulePath, memberMemeName, memberMetamemePath)
            unusedAdd = scriptFacade.sourceMemeMemberAdd(sourceMeme["memeID"], sourceMemberMeme["memeID"], occurrence)
            operationResult = scriptFacade.sourceMemeMemberRemove(sourceMeme["memeID"], sourceMemberMeme["memeID"])
            validation = operationResult["ValidationResults"]
            if validation[0] == True:
                testResult = str(True)
            else:
                testResult = str(False)
                errata = validation[1]
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            operationResult = {"memeID" : "%s.%s" %(modulePath, memeName), "ValidationResults" : [False, errorMsg]}
            errata.append(errorMsg)

        testcase = "%s has member %s" %(sourceMeme["memeID"], sourceMemberMeme["memeID"])
        expectedResult = "True"
        results = [n, testcase, testResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet
    



def testSourceEnhancement(filename):
    method = moduleName + '.' + 'testSourceEnhancement'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        metamemePath = stringArray[0]
        modulePath = stringArray[1]
        memeName = stringArray[2]
        enhancedMetamemePath = stringArray[3]
        enhancedModulePath = stringArray[4]
        enhancedMemeName = stringArray[5]
        sourceMeme = ['']
        sourceMemberMeme = ['']
        
        testResult = str(False)
        try:
            sourceMeme = scriptFacade.sourceMemeCreate(modulePath, memeName, metamemePath)
            sourceMemberMeme = scriptFacade.sourceMemeCreate(enhancedModulePath, enhancedMemeName, enhancedMetamemePath)
            operationResult = scriptFacade.sourceMemeEnhancementAdd(sourceMeme["memeID"], sourceMemberMeme["memeID"])
            validation = operationResult["ValidationResults"]
            if validation[0] == True:
                testResult = str(True)
            else:
                testResult = str(False)
                errata = validation[1]
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            operationResult = {"memeID" : "%s.%s" %(modulePath, memeName), "ValidationResults" : [False, errorMsg]}
            errata.append(errorMsg)

        testcase = "%s enhancing %s" %(sourceMeme["memeID"], sourceMemberMeme["memeID"])
        
        expectedResult = stringArray[6]
        results = [n, testcase, testResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet





def testSourceEnhancementRemove(filename):
    method = moduleName + '.' + 'testSourceEnhancementRemove'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        metamemePath = stringArray[0]
        modulePath = "%s_remove" %stringArray[1]
        memeName = stringArray[2]
        enhancedMetamemePath = stringArray[3]
        enhancedModulePath = "%s_remove" %stringArray[4]
        enhancedMemeName = stringArray[5]
        sourceMeme = ['']
        sourceMemberMeme = ['']
        
        testResult = str(False)
        try:
            sourceMeme = scriptFacade.sourceMemeCreate(modulePath, memeName, metamemePath)
            sourceMemberMeme = scriptFacade.sourceMemeCreate(enhancedModulePath, enhancedMemeName, enhancedMetamemePath)
            unusedAddEnhancement = scriptFacade.sourceMemeEnhancementAdd(sourceMeme["memeID"], sourceMemberMeme["memeID"])
            operationResult = scriptFacade.sourceMemeEnhancementRemove(sourceMeme["memeID"], sourceMemberMeme["memeID"])
            validation = operationResult["ValidationResults"]
            if validation[0] == True:
                testResult = str(True)
            else:
                testResult = str(False)
                errata = validation[1]
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            operationResult = {"memeID" : "%s.%s" %(modulePath, memeName), "ValidationResults" : [False, errorMsg]}
            errata.append(errorMsg)

        testcase = "%s enhancing %s" %(sourceMeme["memeID"], sourceMemberMeme["memeID"])
        expectedResult = "True"
        results = [n, testcase, testResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet





def testSourceSingletonSet(filename):
    method = moduleName + '.' + 'testSourceEnhancementRemove'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    results = []
    resultSet = []
        
    #try:
    testFileName = os.path.join(testDirPath, filename)
    readLoc = codecs.open(testFileName, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    n = 0
        
    for eachReadLine in allLines:
        errata = []
        n = n+1
        unicodeReadLine = str(eachReadLine)
        stringArray = str.split(unicodeReadLine)
        metamemePath = stringArray[0]
        modulePath = "%s_singleton" %stringArray[1]
        memeName = stringArray[2]
        sourceMeme = ['']
        
        testResult = str(False)
        afterSingleton = False
        afterRemoval = False
        operationResult = {}
        try:
            sourceMeme = scriptFacade.sourceMemeCreate(modulePath, memeName, metamemePath)
            
            setAsSingleton = scriptFacade.sourceMemeSetSingleton(sourceMeme["memeID"], True)
            afterSingleton = scriptFacade.getIsMemeSingleton(sourceMeme["memeID"])
            if afterSingleton == False:
                verboseResults = setAsSingleton["ValidationResults"]
                errata.append(verboseResults[1]) 
                
            setAsNonSingleton = scriptFacade.sourceMemeSetSingleton(sourceMeme["memeID"], False)
            afterRemoval = scriptFacade.getIsMemeSingleton(sourceMeme["memeID"])
            if afterRemoval == True:
                verboseResults = setAsNonSingleton["ValidationResults"]
                errata.append(verboseResults[1]) 
                
            operationResult = {"memeID" : sourceMeme["memeID"], "ValidationResults" : [True, []]}
        except Exception as e:
            errorMsg = ('Error!  Traceback = %s' % (e) )
            operationResult = {"memeID" : "%s.%s" %(modulePath, memeName), "ValidationResults" : [False, errorMsg]}
            errata.append(errorMsg)

        if (afterSingleton == True) and (afterRemoval == False):
            testResult = str(True)
            
        testcase = str(operationResult["memeID"])

        expectedResult = "True"
        results = [n, testcase, testResult, expectedResult, errata]
        resultSet.append(results)
        
        Graph.logQ.put( [logType , logLevel.INFO , method , "Finished testcase %s" %(n)])
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    return resultSet



######################
#End Test Block
#####################


def getResultPercentage(resultSet):
    #results = [n, testcase, allTrueResult, expectedResult, errata]
    totalTests = len(resultSet)
    if totalTests == 0:
        return 0
    else:
        partialResult = 0
        if totalTests > 0:
            for test in resultSet:
                try:
                    if test[2].upper() == test[3].upper():
                        partialResult = partialResult + 1
                except Exception as e:
                    print(e)
        pp = partialResult/totalTests
        resultPercentage = pp * 100
        return int(resultPercentage)


def publishResults(testReports, css, fileName, titleText):
    #testReport = {"resultSet" : resultSet, "validationTime" : validationTime, "persistence" : persistence.__name__} 
    #resultSet = [u"Condition (Remote Child)", copy.deepcopy(testSetData), testSetPercentage])

    "Every report repeats exactly the same result sets, so we need only count onece"
    testCaseCount = 0
    exampleTestReport = testReports[0]
    exampleResultSet = exampleTestReport["resultSet"]
    for testScenario in exampleResultSet:
        testCaseCount = testCaseCount + len(testScenario[2])
        
    #Totals for time and number of test cases
    numReports = len(testReports)
    totalTCCount = testCaseCount * numReports
    totalTCTime = 0.0
    for countedTestReport in testReports:
        totalTCTime = totalTCTime + countedTestReport["validationTime"] 
        
    # Create the minidom document
    doc = minidom.Document()
    
    # Create the <html> base element
    html = doc.createElement("html")
    html.setAttribute("xmlns", "http://www.w3.org/1999/xhtml")
        
    # Create the <head> element
    head = doc.createElement("head")
    style = doc.createElement("style")
    defaultCSS = doc.createTextNode(css)
    style.appendChild(defaultCSS)
    title = doc.createElement("title")
    titleTextNode = doc.createTextNode(titleText)
    title.appendChild(titleTextNode)
    head.appendChild(style)
    head.appendChild(title)
        
    body = doc.createElement("body")
    h1 = doc.createElement("h1")
    h1Text = doc.createTextNode(titleText)
    h1.appendChild(h1Text)
    body.appendChild(h1)
    h2 = doc.createElement("h2")
    h2Text = doc.createTextNode("%s regression tests over %s persistence types in in %.1f seconds:  %s" %(totalTCCount, numReports, totalTCTime, ctime()))
    h2.appendChild(h2Text)
    body.appendChild(h2)
    h3 = doc.createElement("h2")
    h3Text = doc.createTextNode("Entity Count at start of tests:  %s" %(exampleTestReport["entityCount"]))
    h3.appendChild(h3Text)
    body.appendChild(h3)
    
    
    """
        The Master table wraps all the result sets.
        masterTableHeader contains all of the overview blocks
        masterTableBody contains all of the detail elements
    """  
    masterTable = doc.createElement("table")
    masterTableHeader = doc.createElement("table")
    masterTableBody = doc.createElement("table")
    
    for testReport in testReports:
        masterTableHeaderRow = doc.createElement("tr")
        masterTableBodyRow = doc.createElement("tr")
        
        localValTime = testReport["validationTime"]
        localPersistenceName = testReport["persistence"]
        resultSet = testReport["resultSet"]
        profileName = testReport["profileName"]
    
        #Module Overview
        numberOfColumns = 1
        numberOfModules = len(resultSet)
        if numberOfModules > 6:
            numberOfColumns = 2
        if numberOfModules > 12:
            numberOfColumns = 3
        if numberOfModules > 18:
            numberOfColumns = 4
        if numberOfModules > 24:
            numberOfColumns = 5
        rowsPerColumn = numberOfModules//numberOfColumns + 1
    
        listPosition = 0
        icTable = doc.createElement("table")
        
        icTableHead= doc.createElement("thead")
        icTableHeadText = doc.createTextNode("%s, %s: %.1f seconds" %(profileName, localPersistenceName, localValTime) )
        icTableHead.appendChild(icTableHeadText)
        icTableHead.setAttribute("class", "tableheader")
        icTable.appendChild(icTableHead)
        
        icTableFoot= doc.createElement("tfoot")
        icTableFootText = doc.createTextNode("Problem test case sets are detailed in tables below" )
        icTableFoot.appendChild(icTableFootText)
        icTable.appendChild(icTableFoot)
        
        icTableRow = doc.createElement("tr")
        
        for unusedI in range(0, numberOfColumns):
            bigCell = doc.createElement("td")
            nestedTable = doc.createElement("table")
            
            #Header
            headers = ["", "Tests", "Valid"]
            nestedTableHeaderRow = doc.createElement("tr")
            for headerElement in headers:
                nestedCell = doc.createElement("th")
                nestedCellText = doc.createTextNode("%s" %headerElement)
                nestedCell.appendChild(nestedCellText)
                nestedTableHeaderRow.appendChild(nestedCell)
                #nestedTableHeaderRow.setAttribute("class", "tableHeaderRow")
                nestedTable.appendChild(nestedTableHeaderRow)  
                      
            for dummyJ in range(0, rowsPerColumn):
                currPos = listPosition
                listPosition = listPosition + 1
                if listPosition <= numberOfModules:
                    try:
                        moduleReport = resultSet[currPos]
                        
                        #Write Data Row To Table
                        row = doc.createElement("tr")
                        
                        #Module Name is first cell
                        cell = doc.createElement("td")
                        cellText = doc.createTextNode("%s" %moduleReport[0])
                        hyperlinkNode = doc.createElement("a")
                        hyperlinkNode.setAttribute("href", "#%s%s" %(moduleReport[0], localPersistenceName)) 
                        hyperlinkNode.appendChild(cellText)
                        cell.appendChild(hyperlinkNode)
                        if moduleReport[1] < 100:
                            row.setAttribute("class", "badOverviewRow")
                        else:
                            row.setAttribute("class", "goodOverviewRow")                   
                        row.appendChild(cell) 
    
                        rowData = [len(moduleReport[2]), "%s %%" %moduleReport[1]]
                        for dataEntry in rowData:
                            percentCell = doc.createElement("td")
                            percentCellText = doc.createTextNode("%s" %dataEntry)
                            percentCell.appendChild(percentCellText)
                            row.appendChild(percentCell)
                        nestedTable.appendChild(row)
                    except:
                        pass
                else:
                    row = doc.createElement("tr")
                    cell = doc.createElement("td")
                    cellText = doc.createTextNode("")
                    cell.appendChild(cellText)
                    row.appendChild(cellText)
                    nestedTable.appendChild(row)
            nestedTable.setAttribute("class", "subdivision")
            bigCell.appendChild(nestedTable) 
            
            icTableRow.appendChild(bigCell)
            icTableDiv = doc.createElement("div")
            icTableDiv.setAttribute("class", "vAlignment")
            icTableDiv.appendChild(icTableRow) 
            icTable.appendChild(icTableDiv)
            
        #Add some blank spave before icTable
        frontSpacer = doc.createElement("div")
        frontSpacer.setAttribute("class", "vBlankSpace")
        frontSpacer.appendChild(icTable)
        
        masterTableDiv = doc.createElement("div")
        masterTableDiv.setAttribute("class", "vAlignment")
        masterTableDiv.appendChild(frontSpacer) 
        masterTableHeaderRow.appendChild(masterTableDiv)
        masterTableHeader.appendChild(masterTableHeaderRow)
                
            
        #Individual Data Sets
        for testSet in resultSet:
            
            #first, build up the "outer" table header, which has the header
            idHash = "%s%s" %(testSet[0], localPersistenceName)
            oTable = doc.createElement("table")
            oTable.setAttribute("style", "border-style:solid")
            tableHeader= doc.createElement("thead")
            tableHeaderText = doc.createTextNode("%s (%s)" %(testSet[0], localPersistenceName) )
            tableAnchor = doc.createElement("a")
            tableAnchor.setAttribute("id", idHash)
            tableAnchor.appendChild(tableHeaderText)
            tableHeader.appendChild(tableAnchor)
            tableHeader.setAttribute("class", "tableheader")
            oTable.appendChild(tableHeader)
            oTableRow = doc.createElement("tr")
            oTableContainer = doc.createElement("td")
    
            #Inner Table         
            table = doc.createElement("table")
            headers = ["#", "Test Case", "Result", "Expected Result", "Notes"]
            tableHeaderRow = doc.createElement("tr")
            for headerEntry in headers:
                cell = doc.createElement("th")
                cellText = doc.createTextNode("%s" %headerEntry)
                cell.appendChild(cellText)
                cell.setAttribute("class", "tableHeaderRow")
                tableHeaderRow.appendChild(cell)
            table.appendChild(tableHeaderRow)
            
            for fullTestRow in testSet[2]:
                #fullTestRow = [n, testcase, allTrueResult, expectedResult, errata]
                test = [fullTestRow[0], fullTestRow[1], fullTestRow[2], fullTestRow[3]]
                tableRow = doc.createElement("tr")
                for dataEntry in test:
                    cell = doc.createElement("td")
                    cellText = doc.createTextNode("%s" %dataEntry)
                    cell.appendChild(cellText)
                    cell.setAttribute("class", "detailsCell")
                    tableRow.appendChild(cell)
                    try:
                        if test[2].upper() != test[3].upper():
                            #then mark the whole row as red
                            tableRow.setAttribute("class", "badDRow")
                        else:
                            tableRow.setAttribute("class", "goodDRow")
                    except:
                        cell = doc.createElement("td")
                        cellText = doc.createTextNode("Please check Testcase code: actual test result = %s, expected = %s" %(test[2], test[3]))
                        cell.appendChild(cellText)
                        cell.setAttribute("class", "detailsCell")
                        tableRow.appendChild(cell) 
                        tableRow.setAttribute("class", "badDRow")                   
    
                errataCell = doc.createElement("td")
                if type(fullTestRow[4]) == type([]):
                    filteredErrata = Graph.filterListDuplicates(fullTestRow[4])
                    for bulletpointElement in filteredErrata:
                        
                        paragraph = doc.createElement("p")
                        pText = doc.createTextNode("%s" %bulletpointElement)
                        paragraph.appendChild(pText)
                        errataCell.appendChild(paragraph)
                        tableRow.appendChild(cell)
                else:
                    filteredErrata = Graph.filterListDuplicates(fullTestRow[4])
                    paragraph = doc.createElement("p")
                    pText = doc.createTextNode("%s" %filteredErrata)
                    paragraph.appendChild(pText)
                    #rowValidityCell.appendChild(paragraph)
                    errataCell.appendChild(paragraph)
                tableRow.appendChild(errataCell)
                table.appendChild(tableRow)
            oTableContainer.appendChild(table)
            oTableRow.appendChild(oTableContainer)
            oTable.appendChild(oTableRow)
            
            #Add some blank spave before any tables
            tableSpacer = doc.createElement("div")
            tableSpacer.setAttribute("class", "vBlankSpace")
            tableSpacer.appendChild(oTable)
            
            masterTableDivL = doc.createElement("div")
            masterTableDivL.setAttribute("class", "vAlignment")
            masterTableDivL.appendChild(tableSpacer) 
            masterTableBodyRow.appendChild(masterTableDivL)
            masterTableBody.appendChild(masterTableBodyRow)

    masterTable.appendChild(masterTableHeader)
    masterTable.appendChild(masterTableBody)
    body.appendChild(masterTable)
    html.appendChild(head)
    html.appendChild(body)
    doc.appendChild(html)
        
    fileStream = doc.toprettyxml(indent = "    ")
    logRoot =  expanduser("~")
    logDir = os.path.join(logRoot, "Graphyne")
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    resultFileLoc = os.path.join(logDir, fileName)
    fileObject = open(resultFileLoc, "w", encoding="utf-8")
    #fileObject.write(Fileutils.smart_str(fileStream))
    fileObject.write(fileStream)
    fileObject.close()
        


def usage():
    print(__doc__)

    
def runTests(css):
    global testImplicit
    method = moduleName + '.' + 'main'
    Graph.logQ.put( [logType , logLevel.DEBUG , method , "entering"])
    
    #Make sure that we have a script facade available
    global scriptFacade
    scriptFacade = Graph.scriptFacade.getFacade()
    
    # A line to prevent pydev from complaining about unused variables
    dummyIgnoreThis = str(scriptFacade)
    
    # a helper item for debugging whther or not a particular entity is in the repo
    debugHelperIDs = scriptFacade.getAllEntities()
    for debugHelperID in debugHelperIDs:
        try:
            debugHelperMemeType = scriptFacade.getEntityMemeType(debugHelperID)
            entityList.append([str(debugHelperID), debugHelperMemeType])
        except Exception as unusedE:
            #This exception is normally left as a pass.  If you need to debug the preceeding code, then uncomment the block below.
            #  The exception is called 'unusedE', so that Pydev will ignore the unused variable
            
            #errorMessage = "debugHelperMemeType warning in Smoketest.Runtests.  Traceback = %s" %unusedE
            #Graph.logQ.put( [logType , logLevel.WARNING , method , errorMessage])
            pass

    #test
    resultSet = []

    print("Meta Meme Properties")
    testSetData = testMetaMemeProperty()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Meta Meme Properties", testSetPercentage, copy.deepcopy(testSetData)])
    
    print("Meta Meme Singleton")
    testSetData = testMetaMemeSingleton()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Meta Meme Singleton", testSetPercentage, copy.deepcopy(testSetData)])
    
    print("Meta Meme Switch")
    testSetData = testMetaMemeSwitch()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Meta Meme Switch", testSetPercentage, copy.deepcopy(testSetData)])

    print("Meta Meme Enhancements")
    testSetData = testMetaMemeEnhancements()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Meta Meme Enhancements", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testMemeValidity()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Meme Validity", testSetPercentage, copy.deepcopy(testSetData)])

    testSetData = testEntityPhase1()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 1", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testEntityPhase1_1()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 1.1", testSetPercentage, copy.deepcopy(testSetData)])

    testSetData = testEntityPhase2()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 2", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testEntityPhase2_1()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 2.1", testSetPercentage, copy.deepcopy(testSetData)])

    testSetData = testEntityPhase3()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 3", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testEntityPhase3_1()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 3.1", testSetPercentage, copy.deepcopy(testSetData)])

    testSetData = testEntityPhase4()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 4", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testEntityPhase4_1()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 4.1", testSetPercentage, copy.deepcopy(testSetData)])

    testSetData = testEntityPhase1('testEntityPhase5', 'Entity_Phase5.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 5", testSetPercentage, copy.deepcopy(testSetData)])

    testSetData = testEntityPhase1_1('testEntityPhase5.1', 'Entity_Phase5.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 5.1", testSetPercentage, copy.deepcopy(testSetData)])

    testSetData = testEntityPhase6()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 6", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testEntityPhase6_1()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 6.1", testSetPercentage, copy.deepcopy(testSetData)])

    testSetData = testEntityPhase7()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 7", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testEntityPhase2('testEntityPhase8', 'Entity_Phase8.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 8", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testEntityPhase2_1('testEntityPhase8_1', 'Entity_Phase8.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 8.1", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testEntityPhase9()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 9", testSetPercentage, copy.deepcopy(testSetData)])
    
    testSetData = testEntityPhase10()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 10", testSetPercentage, copy.deepcopy(testSetData)])
    
    #Repeats 7, but with directional references
    testSetData = testEntityPhase7('testEntityPhase11', "Entity_Phase11.atest")
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Entity Phase 11", testSetPercentage, copy.deepcopy(testSetData)])
    
    #Repeats 7, but with directionasl references filters
    testSetData = testTraverseParams()
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Traverse Params", testSetPercentage, copy.deepcopy(testSetData)])
    
    #NumericValue.atest
    testSetData = testNumericValue('NumericValue.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["NumericValue", testSetPercentage, copy.deepcopy(testSetData)])
    
    if (testImplicit == True):
        print("Implicit Memes")
        testSetData = testImplicitMeme()
        testSetPercentage = getResultPercentage(testSetData)
        resultSet.append(["Implicit Meme", testSetPercentage, copy.deepcopy(testSetData)])
    else:
        print("No Persistence:  Skipping Implicit Memes")
    
    print("Conditions")
    testSetData = testCondition('ConditionSimple.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Condition (Simple)", testSetPercentage, copy.deepcopy(testSetData)])
    
    #ConditionSet.atest
    testSetData = testCondition('ConditionSet.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Condition (Set)", testSetPercentage, copy.deepcopy(testSetData)])
    
    # Script Conditions
    testSetData = testCondition('ConditionScript.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Condition (Script)", testSetPercentage, copy.deepcopy(testSetData)])
    
    #Child conditions in remote packages
    testSetData = testCondition('ConditionRemotePackage.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Condition (Remote Child)", testSetPercentage, copy.deepcopy(testSetData)])
    
    #String and Numeric Conditions with Agent Attributes
    testSetData = testAACondition('ConditionAA.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Condition (Agent Attributes)", testSetPercentage, copy.deepcopy(testSetData)])
    
    #String and Numeric Conditions with Multi Agent Attributes
    testSetData = testAACondition('ConditionMAA.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Condition (Multi Agent Attributes)", testSetPercentage, copy.deepcopy(testSetData)])
    
    #Creating source metamemes via the script facade
    testSetData = testSourceCreateMeme('SourceCreateMeme.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Editor Meme Creation", testSetPercentage, copy.deepcopy(testSetData)])
    
    #Set a source meme property via the script facade
    testSetData = testSourceProperty('SourceProperty.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Editor Meme Property Set", testSetPercentage, copy.deepcopy(testSetData)])

    #Delete a source meme property via the script facade
    testSetData = testSourcePropertyRemove('SourceProperty.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Editor Meme Property Remove", testSetPercentage, copy.deepcopy(testSetData)])
    
    #Add a member meme via the script facade
    testSetData = testSourceMember('SourceMember.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Editor Member Meme Add", testSetPercentage, copy.deepcopy(testSetData)])

    #Remove a member meme via the script facade
    testSetData = testSourceMemberRemove('SourceMember.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Editor Member Meme Remove", testSetPercentage, copy.deepcopy(testSetData)])

    #Add an enhancement via the script facade
    testSetData = testSourceEnhancement('SourceEnhancement.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Editor Enhancement Add", testSetPercentage, copy.deepcopy(testSetData)])

    #Remove an enhancement via the script facade
    testSetData = testSourceEnhancementRemove('SourceEnhancement.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Editor Enhancement Remove", testSetPercentage, copy.deepcopy(testSetData)])
    
    #Set the singleton flag via the script facade
    testSetData = testSourceSingletonSet('SourceCreateMeme.atest')
    testSetPercentage = getResultPercentage(testSetData)
    resultSet.append(["Editor Singleton Setting", testSetPercentage, copy.deepcopy(testSetData)])

    #endTime = time.time()
    #validationTime = endTime - startTime     
    #publishResults(resultSet, validationTime, css)
    return resultSet
    #Graph.logQ.put( [logType , logLevel.DEBUG , method , "exiting"])
    



def smokeTestSet(persistence, lLevel, css, profileName, persistenceArg = None, persistenceType = None, resetDatabase = False, createTestDatabase = False, scaleFactor = 0):
    '''
    repoLocations = a list of all of the filesystem location that that compose the repository.
    useDeaultSchema.  I True, then load the 'default schema' of Graphyne
    persistenceType = The type of database used by the persistence engine.  This is used to determine which flavor of SQL syntax to use.
        Enumeration of Possible values:
        Default to None, which is no persistence
        "sqlite" - Sqlite3
        "mssql" - Miscrosoft SQL Server
        "hana" - SAP Hana
    persistenceArg = the Module/class supplied to host the entityRepository and LinkRepository.  If default, then use the Graphyne.DatabaseDrivers.NonPersistent module.
        Enumeration of possible values:
        None - May only be used in conjunction with "sqlite" as persistenceType and will throw an InconsistentPersistenceArchitecture otherwise
        "none" - no persistence.  May only be used in conjunction with "sqlite" as persistenceType and will throw an InconsistentPersistenceArchitecture otherwise
        "memory" - Use SQLite in in-memory mode (connection = ":memory:")
        "<valid filename with .sqlite as extension>" - Use SQLite, with that file as the database
        "<filename with .sqlite as extension, but no file>" - Use SQLite and create that file to use as the DB file
        "<anything else>" - Presume that it is a pyodbc connection string and throw a InconsistentPersistenceArchitecture exception if the dbtype is "sqlite".
    createTestDatabase = a flag for creating regression test data.  This flag is only to be used for regression testing the graph and even then, only if the test 
        database does not already exist.
        
    scaleFactor = Scale factor (S).  Given N non-singleton memes, N*S "ballast" entities will be created in the DB before starting the test suite.  This allows us
        to use larger datasets to test scalability (at least with regards to entity repository size)
        
        *If persistenceType is None (no persistence, then this is ignored and won't throw any InconsistentPersistenceArchitecture exceptions)
    '''
    global testImplicit
    print(("\nStarting Graphyne Smoke Test: %s") %(persistence.__name__))
    print(("...%s: Engine Start") %(persistence.__name__))
    
    #Only test implicit memes in the case that we are using persistence
    if persistenceType is None:
        testImplicit = False
        
    #Don't validate the repo when we are performance testing
    if scaleFactor < 1:
        validateOnLoad = True
    else:
        validateOnLoad = False
    
    time.sleep(10.0)

    installFilePath = os.path.dirname(__file__)
    testRepo = os.path.join(installFilePath, "Config", "Test", "TestRepository")
    #mainAngRepo = os.path.join(os.environ['ANGELA_HOME'], "RMLRepository") 
    try:
        Graph.startLogger(lLevel)
        Graph.startDB([testRepo], persistenceType, persistenceArg, True, resetDatabase, True, validateOnLoad)
    except Exception as e:
        print(("Graph not started.  Traceback = %s" %e))
        raise e 
    print(("...Engine Started: %s") %persistence.__name__)
    
    time.sleep(30.0)
    print(("...%s: Engine Started") %(persistence.__name__))
    
    #If scaleFactor > 0, then we are also testing performance
    if (scaleFactor > 0):
        print("Performance Test: ...Creating Content")
        for unusedj in range(1, scaleFactor):
            for moduleID in Graph.templateRepository.modules.keys():
                if moduleID != "BrokenExamples":
                    #The module BrokenExamples contaons mmemes that are deliberately malformed.  Don't beother with these
                    module = Graph.templateRepository.modules[moduleID]
                    for listing in module:
                        template = Graph.templateRepository.resolveTemplateAbsolutely(listing[1])
                        if template.className == "Meme":
                            if template.isSingleton != True:
                                try:
                                    unusedEntityID = Graph.scriptFacade.createEntityFromMeme(template.path.fullTemplatePath)
                                except Exception as e:
                                    pass
        print("Performance Test: Finished Creating Content")
    # /Scale Factor'
    
    entityCount = Graph.countEntities()

    
    startTime = time.time()
    try:
        resultSet = runTests(css)   
    except Exception as e:
        print(("test run problem.  Traceback = %s" %e))
        raise e 
    endTime = time.time()
    validationTime = endTime - startTime
    testReport = {"resultSet" : resultSet, "validationTime" : validationTime, "persistence" : persistence.__name__, "profileName" : profileName, "entityCount" : entityCount}     
    #publishResults(resultSet, validationTime, css)
    
    print(("...%s: Test run finished.  Waiting 30 seconds for log thread to catch up before starting shutdown") %(persistence.__name__))
    time.sleep(30.0)
    
    print(("...%s: Engine Stop (%s)") %(persistence.__name__, profileName)) 
    Graph.stopLogger()
    print(("...%s: Engine Stopped (%s)") %(persistence.__name__, profileName))   
    return testReport 

    
if __name__ == "__main__":
    '''         
    Three (optional) initial params:
        sys.argv[1] - Is the connection string.
            "none" - no persistence
            "memory" - Use SQLite in in-memory mode (connection = ":memory:")
            "<valid filename>" - Use SQLite, with that file as the database
            "<filename with .sqlite as extension, but no file>" - Use SQLite and create that file to use as the DB file
            "<anything else>" - Presume that it is a pyodbc connection string
            Default to None, which is no persistence

        sys.argv[2]     persistenceType = The type of database used by the persistence engine.  This is used to determine which flavor of SQL syntax to use.
            Enumeration of Possible values:
            Default to None, which is no persistence
            "sqlite" - Sqlite3
            "mssql" - Miscrosoft SQL Server
            "hana" - SAP Hana
                        
        sys.argv[3] - Is the log level.
            "info", "debug" and "warning" are valid options.    
            Default to "warning"
        
    E.g. Smoketest.py 'memory' 'sqlite'      #For sqlite3 database, with :memory: connection
    E.g. Smoketest.py                        #For no persistence
    
    '''
        
    print("\nStarting Graphyne Smoke Test")
    
    lLevel = Graph.logLevel.DEBUG
    try:
        if sys.argv[4] == "info":
            lLevel = Graph.logLevel.INFO
        elif sys.argv[4] == "debug":
            lLevel = Graph.logLevel.DEBUG
    except:
        pass
    
    persistenceType = None
    dbConnectionString = None
    try:
        if sys.argv[1] is not None:
            #dbConnectionString = sys.argv[1]
            dbConnectionString = sys.argv[1]
    except:
        pass
    try:
        if sys.argv[2] is not None:
            #dbConnectionString = sys.argv[1]
            persistenceType = sys.argv[2]
    except:
        pass
    
    resetDatabase = True
    try:
        if sys.argv[3] is not None:
            if sys.argv[3] == "false":
                resetDatabase = False
            elif sys.argv[3] == "False":
                resetDatabase = False
    except:
        pass
    
    print(("   ...params: log level = %s, db driver = %s, connection string = %s" %(lLevel, persistenceType, dbConnectionString)))
    
    testReport = None
    css = Fileutils.defaultCSS()
    try:
        if persistenceType is None:
            from Graphyne.DatabaseDrivers import NonPersistent as persistenceModule1
            testReport = smokeTestSet(persistenceModule1, lLevel, css, "No-Persistence", dbConnectionString, persistenceType, resetDatabase, True)
        elif ((persistenceType == "sqlite") and (dbConnectionString== "memory")):
            from Graphyne.DatabaseDrivers import RelationalDatabase as persistenceModule2
            testReport = smokeTestSet(persistenceModule2, lLevel, css, "sqllite", dbConnectionString, persistenceType, resetDatabase, True)
        elif persistenceType == "sqlite":
            from Graphyne.DatabaseDrivers import RelationalDatabase as persistenceModule4
            testReport = smokeTestSet(persistenceModule4, lLevel, css, "sqllite", dbConnectionString, persistenceType, resetDatabase)
        else:
            from Graphyne.DatabaseDrivers import RelationalDatabase as persistenceModul3
            testReport = smokeTestSet(persistenceModul3, lLevel, css, persistenceType, dbConnectionString, persistenceType, resetDatabase)
    except Exception as e:
            from Graphyne.DatabaseDrivers import RelationalDatabase as persistenceModul32
            testReport = smokeTestSet(persistenceModul32, lLevel, css, persistenceType, dbConnectionString, persistenceType, resetDatabase)

    titleText = "Graphyne Smoke Test Suite - Results"
    publishResults([testReport], css, "GraphyneTestResult.html", titleText)