import re, glob, os, datetime, shutil, sys, platform
from os import walk

#rTorrent mode
try:
    title = str(sys.argv[1])
    location = str(sys.argv[2])
except:
    pass

#manual
try:
    #location = str(sys.argv[1])
    location = '/Users/rossphelan/Documents/test_folder'
except:
    print "arg LOCATION not found"
    sys.exit()

#Set destination dir
filmDstPath = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'converted')
showDstPath = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'converted')
srcPath = os.path.realpath( location )

#Regexes for folder and file detection
subfolderRegex = "\[subfolder\](.*?)\/"
showRegex = "\[show\](.*?)\/"
filmRegex = "\[film\](.*?)\/"
squareBracketsRegex = "(\[.*?\])"
fileNameRegex = "/([^/]*)\..*" 
fileTypeRegex = "\.([^/].*)"


#Regexes to detect different season filetypes. Order important
seasonRegexes = ["\[season\](\d*?)\/", "s(\d{1,2})e\d{1,2}", "(\d{1,2})x\d{2}", "[^(](\d{2})\d{2}"]
#seasonRegex = "\[season\](\d*?)\/"
#sxxennRegex = "s(\d{1,2})e\d{1,2}"
#xXnnRegex = "(\d{1,2})x\d{2}"
#xxnnRegex = "[^(](\d{2})\d{2}"

#Regexes to detect different episode filetypes. Order important
episodeRegexes = ["\[episode\](\d*?)\/", "s\d{1,2}e(\d{1,2})", "e(\d{2})", "\dx(\d{2})", "[^(]\d{2}(\d{2})", "\d(\d{2})", "(\d{2})"]
#episodeRegex = "\[episode\](\d*?)\/"
#snnexxRegex = "s\d{1,2}e(\d{1,2})"
#exxRegex = "e(\d{2})"
#nXxxRegex = "\dx(\d{2})"
#nnxxRegex = "[^(]\d{2}(\d{2})"
#nxxRegex = "\d(\d{2})"
#xxRegex = "(\d{2})"

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

print "Beginning"

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
    print "No files found"
    sys.exit()

#Generate new file name
for index, inputString in enumerate(inputStringArr): 
    print '*****'
    try:
           print "Title:    " + title
    except:
          pass
    print "From:     " + inputString

    try:
        x = re.search(subfolderRegex, inputString, re.IGNORECASE)
        newFilePath = os.path.join(newFilePath , x.group(1))
    except:
        pass

    #For Film
    try:
        newFilePath = filmDstPath
        x = re.search(filmRegex, inputString, re.IGNORECASE)
        filext = ('.' + inputString.split('.')[-1])
        newFileName = ''.join(c for c in x.group(1) if c in valid_chars).strip()
        #Multiple film films indicate subtitles, create folder for these
        if any( x == filext for x in allowedSubtitleFileTypes ):
            newFilePath = os.path.join(newFilePath, x.group(1))
        isFilm = True
    except:
        isFilm = False
    

    #For Show
    if not isFilm:
        newFilePath = showDstPath
        try:
            x = re.search(showRegex, inputString, re.IGNORECASE)
            showName = ''.join(c for c in x.group(1) if c in valid_chars).strip()
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
        for resultionType in resultionTypes:
            fileName = fileName.replace(resultionType, '')

        season = "01"
        for seasonRegex in seasonRegexes:
            try:
                x = re.search(seasonRegex, inputString, re.IGNORECASE)
                season = x.group(1).zfill(2)
                break
            except:
                pass

        newFilePath = os.path.join( newFilePath, ("Season " + season) )

        episode = index
        for episodeRegex in episodeRegexes:
            try:
                x = re.search(episodeRegex, inputString, re.IGNORECASE)
                episode = x.group(1).zfill(2)
                break
            except:
                pass

        newFileName = showName + " - S" + season + "E" + episode.zfill(2)

    newFileType = '.' + inputString.split('.')[-1]

    newFileNameAndPath = os.path.join( newFilePath, (newFileName + newFileType) )

    if os.path.isfile(newFileNameAndPath):
        print "File already exists. Creating copy"
        newFileNameAndPath = os.path.join( newFilePath ,(newFileName + " -copy(" + str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S-%f")
) + ")" + newFileType) )

    if not os.path.exists(newFilePath):
        os.makedirs(newFilePath)

    try:
#       shutil.copy2(inputString, newFileNameAndPath)
        #shutil.move(inputString, newFileNameAndPath)
        #TODO windows security stuff    
        print "Created:  " + newFileNameAndPath
    except:
        print( "<p>Error: %s</p>" % sys.exc_info()[0] )

print "Finished"