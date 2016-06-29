import re, glob, os, datetime, shutil, sys, platform
from os import walk

logging = True
logFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'logfile.txt')
def textOutput(text):
    if logging:
        open(logFilePath,"a+b").write(text + '\n')
    else:
        print text

#rTorrent mode
try:
    title = str(sys.argv[1])
    location = str(sys.argv[2])
except:
    #manual
    try:
        location = str(sys.argv[1])
    except:
        textOutput("arg LOCATION not found")
        sys.exit()

textOutput('*****BEGIN*****')
textOutput(str(datetime.datetime.utcnow()))
textOutput('Location: ' + location)
#Set destination dir
#filmDstPath = os.path.join(os.path.dirname(os.path.abspath(__file__)) , ('converted/film'))
filmDstPath = os.path.realpath ('/home/feelin/www/dl/converted/film')
#showDstPath = os.path.join(os.path.dirname(os.path.abspath(__file__)) , ('converted/show'))
showDstPath = os.path.realpath ('/home/feelin/www/dl/converted/other')
srcPath = os.path.realpath( location )

#Regexes for folder and file detection
subfolderRegex = "\[subfolder\](.*?)\/"
showRegex = "\[show\](.*?)\/"
filmRegex = "\[film\](.*?)\/"
squareBracketsRegex = "(\[.*?\])"
fileNameRegex = "/([^/]*)\..*" 
fileTypeRegex = "\.([^/].*)"


#Regexes to detect different season filetypes. Order important
seasonRegexes = ["s(\d{1,2})e\d{1,2}", "(\d{1,2})x\d{2}", "[^(](\d{2})\d{2}"]
seasonManualRegex = "\[season\](\d*?)\/"
#sxxennRegex = "s(\d{1,2})e\d{1,2}"
#xXnnRegex = "(\d{1,2})x\d{2}"
#xxnnRegex = "[^(](\d{2})\d{2}"

#Regexes to detect different episode filetypes. Order important
episodeRegexes = ["s\d{1,2}e(\d{1,2})", "e(\d{2})", "\dx(\d{2})", "[^(]\d{2}(\d{2})", "\d(\d{2})", "(\d{2})"]
episodeManualRegex = "\[episode\](\d*?)\/"
#snnexxRegex = "s\d{1,2}e(\d{1,2})"
#exxRegex = "e(\d{2})"
#nXxxRegex = "\dx(\d{2})"
#nnxxRegex = "[^(]\d{2}(\d{2})"
#nxxRegex = "\d(\d{2})"
#xxRegex = "(\d{2})"
 
bracketsRegexes = ["(\[.*?\])", "(\(.*?\))", "(\{.*?\})"]

#Must be lower case
subFolderBrackets = '[subfolder]'
filmBrackets = '[film]'
showBrackets = '[show]'
seasonBrackets = '[season]'
episodeBrackets = '[episode]'

valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

#Resultion Types
resultionTypes = ['480', '720', '1080', '1280', '264']

#Remove .srt and .ass to ignore subtitles
allowedFileTypes = [".mkv", ".mp4", ".avi", ".mov", ".mpg", ".srt", ".ass"]
allowedSubtitleFileTypes = [".srt", ".ass"]

oneGB = 1000000000
tenGB = oneGB * 10

maxFileSize = tenGB

inputStringArr = []
fileMovedArr = []

#Checking to see if it we got a file or folder
if os.path.isdir(srcPath) == True:
    for (dirpath, dirnames, filenames) in walk(srcPath):
        for filename in filenames:
            for allowedFileType in allowedFileTypes:
                if filename.endswith(allowedFileType) and filename.find("sample") == -1:
                    if os.path.getsize(os.path.join(dirpath, filename)) < maxFileSize:
                        newEntry = (os.path.join(dirpath, filename))
                        if newEntry.find(".unwanted") == -1:
                            inputStringArr.append(newEntry)
                            
else:
    for allowedFileType in allowedFileTypes:
        if srcPath.endswith(allowedFileType):
            if os.path.getsize( srcPath ) < maxFileSize:
                inputStringArr.append(srcPath)
                
if len(inputStringArr) == 0:
    textOutput("No files found")
    sys.exit()

#Generate new file name
for index, inputString in enumerate(inputStringArr): 
    textOutput('**')
    try:
           textOutput("Title:    " + title)
    except:
          pass
    textOutput("From:     " + inputString)


    inputStringSplitArr = []
    pathDirs = inputString
    while True:
        pathDirs, leaf = os.path.split(pathDirs)
        if leaf:
            inputStringSplitArr.append(leaf)
        else:
            break;
    fileName, fileExt = os.path.splitext(inputStringSplitArr[0])
    if len(fileName) == 0 or len(fileExt) == 0:
        textOutput('File not Found: ' + inputString)
        continue
    for bracketsRegex in bracketsRegexes:
        fileName = re.sub(bracketsRegex, '', fileName) 
    for resultionType in resultionTypes:
        fileName = fileName.replace(resultionType, '')

    #insert subfolder path

    #For Film
    isFilm = False
    for inputStringSplit in inputStringSplitArr:
        if inputStringSplit.lower().find(filmBrackets) != -1:
            isFilm = True
            newFilePath = filmDstPath
            filmName = inputStringSplit.lstrip(filmBrackets)
            newFileName = ''.join(c for c in filmName if c in valid_chars).strip()
            if any( x == fileExt for x in allowedSubtitleFileTypes ):
                newFilePath = os.path.join(newFilePath, filmName)
            break


    #For Show
    if not isFilm:
        newFilePath = showDstPath

        for inputStringSplit in inputStringSplitArr:
            if inputStringSplit.lower().find(showBrackets) != -1:
                showName = inputStringSplit.lstrip(showBrackets)
                showName = ''.join(c for c in showName if c in valid_chars).strip()
        try: 
            newFilePath = os.path.join( newFilePath , showName )
        except:
            textOutput("No show name ( [show]name ) or film name ( [film]name ) found")
            continue

        season = "01"
        manualSeason = False
        for inputStringSplit in inputStringSplitArr:
            if inputStringSplit.lower().find(seasonBrackets) != -1: 
                season = inputStringSplit.lstrip(seasonBrackets)              
                manualSeason = True
                break
        if not manualSeason:
            for seasonRegex in seasonRegexes:
                try:
                    x = re.search(seasonRegex, fileName, re.IGNORECASE)
                    season = x.group(1)
                    break
                except:
                    pass

        newFilePath = os.path.join( newFilePath, ("Season " + season.zfill(2)) )

        episode = str(index)
        manualEpisode = False
        for inputStringSplit in inputStringSplitArr:
            if inputStringSplit.lower().find(episodeBrackets) != -1:  
                episode = inputStringSplit.lstrip(episodeBrackets)            
                manualEpisode = True
                break
        if not manualEpisode:
            for episodeRegex in episodeRegexes:
                try:
                    x = re.search(episodeRegex, fileName, re.IGNORECASE)
                    episode = x.group(1)
                    break
                except:
                    pass

        newFileName = showName + " - S" + season.zfill(2) + "E" + episode.zfill(2)

    newFileNameAndPath = os.path.join( newFilePath, (newFileName + fileExt) )

    if os.path.isfile(newFileNameAndPath):
        textOutput("File already exists. Creating copy")
        newFileNameAndPath = os.path.join( newFilePath ,(newFileName + " -copy(" + str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S-%f")) + ")" + newFileType) )

    if not os.path.exists(newFilePath):
        os.makedirs(newFilePath)

    try:
        #shutil.copy2(inputString, newFileNameAndPath)
        #shutil.move(inputString, newFileNameAndPath)
        #TODO windows security stuff    
        textOutput("Created:  " + newFileNameAndPath)
        fileMovedArr.append(newFileNameAndPath)
    except:
        print( "<p>Error: %s</p>" % sys.exc_info()[0] )

textOutput("Finished")
textOutput('Moved')
for fileMoved in fileMovedArr:
    textOutput(fileMoved)
textOutput(str(len(fileMovedArr)) + " files moved")