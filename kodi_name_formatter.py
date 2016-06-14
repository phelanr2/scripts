import re, glob, os, datetime, shutil, sys
from os import walk

try:
    title = str(sys.argv[1])
except:
    title = 'no title'

try:
    #location = str(sys.argv[2])
    location = '/Users/rossphelan/Documents/test_folder'
except:
    print "2nd arg LOCATION not found"
    sys.exit()

#Set destination dir
#dstPath = 'myPath'
dstPath = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'converted')

srcPath = os.path.realpath( location )

#Regexes for folder and file detection
subfolderRegex = "\[subfolder\](.*?)\/"
showRegex = "\[show\](.*?)\/"
filmRegex = "\[film\](.*?)\/"
seasonRegex = "\[season\](\d*?)\/"
episodeRegex = "\[episode\](\d*?)\/"
squareBracketsRegex = "(\[.*?\])"
fileNameRegex = "/([^/]*)\..*" 
fileTypeRegex = "\.([^/].*)"


#Regexes to detect different season filetypes
#TODO put these in array
sxxennRegex = "s(\d{1,2})e\d{1,2}"
xXnnRegex = "(\d{1,2})x\d{2}"
xxnnRegex = "[^(](\d{2})\d{2}"

#Regexes to detect different episode filetypes
#TODO put these in array
snnexxRegex = "s\d{1,2}e(\d{1,2})"
exxRegex = "e(\d{2})"
nXxxRegex = "\dx(\d{2})"
nnxxRegex = "[^(]\d{2}(\d{2})"
nxxRegex = "\d(\d{2})"
xxRegex = "(\d{2})"

#Remove .srt and .ass to ignore subtitles
allowedFileTypes = [".mkv", ".mp4", ".avi", ".mov", ".mpg", ".srt", ".ass"]
allowedSubtitleFileTypes = [".srt", ".ass"]

oneGB = 1000000000
tenGB = oneGB * 10

maxFileSize = tenGB

inputStringArr = []

print "Beginning"

#Checking to see if it we got a file or folder
if os.path.isdir(srcPath) == True:
    #Gathering all allowed files
    for (dirpath, dirnames, filenames) in walk(srcPath):
        for filename in filenames:
            for allowedFileType in allowedFileTypes:
                if filename.endswith(allowedFileType) and filename.find("sample") == -1:
                    if os.path.getsize(os.path.join(dirpath, filename)) < maxFileSize:
                        newEntry = (os.path.join(dirpath, filename))
                        if newEntry.find(".unwanted") == -1:
                            inputStringArr.append(newEntry)
                            
else:
    #Gathering 
    for allowedFileType in allowedFileTypes:
        if srcPath.endswith(allowedFileType):
            if os.path.getsize( srcPath ) < maxFileSize:
                inputStringArr.append(srcPath)
                
if len(inputStringArr) == 0:
    print "No files found"
    sys.exit()

#Generate new file name
for index, inputString in enumerate(inputStringArr): 
    newFilePath = dstPath

    try:
        x = re.search(subfolderRegex, inputString, re.IGNORECASE)
        newFilePath = os.path.join(newFilePath , x.group(1))
    except:
        pass

    #FOR FILM
    try:
        x = re.search(filmRegex, inputString, re.IGNORECASE)
        filext = ('.' + inputString.split('.')[-1])
        newFileName = x.group(1)
        #Multiple film films indicate subtitles, create folder for these
        if any( x == filext for x in allowedSubtitleFileTypes ):
            newFilePath = os.path.join(newFilePath, x.group(1))
        isFilm = True
    except:
        isFilm = False
    

    #FOR SHOW
    if not isFilm:
        try:
            x = re.search(showRegex, inputString, re.IGNORECASE)
            showName = x.group(1)
            newFilePath = os.path.join( newFilePath , showName )
        except:
            print "No show name ( [show]name ) found"
            continue

        try: 
            x = re.search(fileNameRegex, inputString, re.IGNORECASE)
            fileName = x.group(1)
        except:
            print "No file found"
            continue

        fileName = re.sub(squareBracketsRegex, '', fileName) 
        fileName = fileName.replace('480', '')
        fileName = fileName.replace('720', '')
        fileName = fileName.replace('1080', '')
        fileName = fileName.replace('1280', '')
        fileName = fileName.replace('264', '')

        try:
            x = re.search(seasonRegex, inputString, re.IGNORECASE)
            season = x.group(1).zfill(2)
        except:
            x = re.search(sxxennRegex, fileName, re.IGNORECASE)
            try:
                season = x.group(1).zfill(2)
            except:
                x = re.search(xXnnRegex, fileName, re.IGNORECASE)
                try:
                    season = x.group(1).zfill(2)
                except:
                    x = re.search(xxnnRegex, fileName, re.IGNORECASE)
                    try:
                        season = x.group(1).zfill(2)
                    except:        
                        season = '01'

        newFilePath = os.path.join( newFilePath, ("Season " + season) )

        try:
            x = re.search(episodeRegex, inputString, re.IGNORECASE)
            newFilePath = os.path.join( newFilePath, x.group(1) )
        except:
            pass

        x = re.search(snnexxRegex, fileName, re.IGNORECASE)
        try:
            episode = x.group(1)
        except:
            x = re.search(exxRegex, fileName, re.IGNORECASE)
            try:
                episode = x.group(1)
            except:    
                x = re.search(nXxxRegex, fileName, re.IGNORECASE)
                try:
                    episode = x.group(1)
                except:
                    x = re.search(nnxxRegex, fileName, re.IGNORECASE)
                    try:
                        episode = x.group(1)
                    except:
                        x = re.search(nxxRegex, fileName, re.IGNORECASE)
                        try:
                            episode = x.group(1)
                        except:
                            x = re.search(xxRegex, fileName, re.IGNORECASE)
                            try:
                                episode = x.group(1)
                            except:
                                episode = index
                                print "Could not match filename to any episode regex"
                                print "User array index " + index

        newFileName = showName + " - S" + season + "E" + episode.zfill(2)

    newFileType = '.' + inputString.split('.')[-1]

    newFileNameAndPath = os.path.join( newFilePath, (newFileName + newFileType) )

    if os.path.isfile(newFileNameAndPath):
        print "File already exists. Creating copy"
        newFileNameAndPath = os.path.join( newFilePath ,(newFileName + " -copy[" + str(datetime.datetime.utcnow()) + "]" + newFileType) )

    if not os.path.exists(newFilePath):
        os.makedirs(newFilePath)

    try:
#       shutil.copy2(inputString, newFileNameAndPath)
        #shutil.move(inputString, newFileNameAndPath)
        print '*****'
        print "From: " + inputString
        print "Title: " + title
        #TODO windows security stuff    
        print "Created: " + newFileNameAndPath
    except:
        print( "<p>Error: %s</p>" % sys.exc_info()[0] )

print "Finished"