import os
import sys
import xml.etree.ElementTree as XMLTree
import zipfile

print("JUNK IMAGE REMOVER v.2")
print("Helps you remove all unused image files from your H&M projects")
print("(c) 2016 Nikita Kovin")

project = ""
compressed = ""
topicsPath = ""
searchPaths = ""
method = 1
slash = ""
counter = 0
counterDeleted = 0
counterRemoved = 0
imageExtensions = [".png", ".jpg", ".jpeg", ".emf", ".gif", ".wmf", ".bmp"]
unusedPath = ""

while True:
    print("\nEnter a full path to the directory where your project is.")
    path = input("Bonk Enter, if it is in the same directory where the tool is:")
    if path and not os.path.isdir(path):
        print("\nThe directory does not exist.")
    else:
        if not path:
            path = os.path.dirname(os.path.abspath(__file__))
        if path[-1:] != "\\":
            slash = "\\"
        foundProject = False
        for file in os.listdir(path):
            if file.lower().endswith(".hmxz") or file.lower().endswith(".hmxp"):
                project = path + slash + file
                if file.lower().endswith(".hmxz"):
                    compressed = True
                else:
                    compressed = False
                    if os.path.isdir(path + "\Topics"):
                        topicsPath = path + "\Topics\\"
                foundProject = True
                break
        if not foundProject or not os.path.isfile(project):
            print("\nNo H&M project found in the directory. Please enter a valid path.")
        elif not compressed and not topicsPath:
            print("\nThe Topics directory is missing...")
        else:
            break

print("\nThe project file is located in:")

try:
    print(project)
except UnicodeEncodeError:
    print("<cannot read filename>")

while True:
    print("\nWhat shall we do with unused pictures?")
    print("   1: Prompt before deleting")
    print("   2: Delete without asking")
    print("   3: Move to a separate folder")
    print("   4: Do nothing, just present a list of unused images")
    try:
        method = int(input("Input a number of the desired option:"))
        if method in [1, 2, 3, 4]:
            break
        else:
            print("\nEnter 1,2,3 or 4.")
    except ValueError:
        print("\nYou must enter an integer value.")

print("\nThe selected method is", method, "\n")

if compressed:
    archive = zipfile.ZipFile(project, 'r')
    project = archive.read('project.hmxp')
    root = XMLTree.fromstring(project)
else:
    tree = XMLTree.parse(project)
    root = tree.getroot()

searchPathTag = root.find(".//*config-value[@name='searchpath']")
if searchPathTag is not None:
    for elem in searchPathTag.itertext():
        searchPaths = elem.split(";")
    if not searchPaths:
        input("FAILED: Cannot find project search paths. Press Enter to exit.")
        sys.exit()
else:
    input("FAILED: Project file is corrupted. Press Enter to exit.")
    sys.exit()

for SearchPath in searchPaths:
    if SearchPath[:1] == ".":
        # Search paths always end with \
        SearchPath = path + SearchPath[1:]
    if not os.path.isdir(SearchPath):
        print("WARNING: Search path ", end='')
        try:
            print(SearchPath, end='')
        except UnicodeEncodeError:
            print("<cannot read path>")
        print(" does not exist or is unreadable")
    else:
        images = [f for f in os.listdir(SearchPath) if os.path.isfile(os.path.join(SearchPath, f))]
        for image in images:
            if image.lower().endswith(".xml"):
                break
            imageFound = False
            if image.lower().endswith(tuple(imageExtensions)):
                if compressed:
                    topics = archive.namelist()
                else:
                    topics = [f for f in os.listdir(topicsPath) if os.path.isfile(os.path.join(topicsPath, f))]
                for topic in topics:
                    allowSearch = False
                    if compressed:
                        if topic.startswith('Topics') and topic.lower().endswith('.xml'):
                            topic = archive.read(topic).lower()
                            root = XMLTree.fromstring(topic)
                            allowSearch = True
                        else:
                            allowSearch = False
                    else:
                        topicPath = topicsPath + topic
                        tree = XMLTree.parse(topicPath)
                        root = tree.getroot()
                        allowSearch = True
                    if allowSearch:
                        if not compressed:
                            imageTag = root.find(".//*image[@src='" + image + "']")
                            if imageTag is None:
                                imageTag = root.find(".//*image[@src='" + image.lower() + "']")
                        else:
                            imageTag = root.find(".//*image[@src='" + image.lower() + "']")
                        if imageTag is not None:
                            imageFound = True
                            break
                if imageFound is False:
                    counter += 1
                    imagePath = SearchPath + image
                    if method == 1 or method == 2:
                        ack = "n"
                        if method == 1:
                            while True:
                                print("Delete file \"", end='')
                                try:
                                    ack = input(imagePath + "\"? Press [Y] or [N]:")
                                except UnicodeEncodeError:
                                    ack = input("<cannot read filename>\"? Press [Y] or [N]:")
                                ack = ack.lower()
                                if ack == "y" or ack == "n":
                                    break
                        else:
                            ack = "y"
                        if ack == "y":
                            try:
                                os.remove(imagePath)
                                counterDeleted += 1
                                print("Deleted image ", end="")
                                try:
                                    print(imagePath)
                                except UnicodeEncodeError:
                                    print("\"<cannot read filename>\"")
                            except OSError or PermissionError:
                                print("FAILED: Cannot delete image \"", end='')
                                try:
                                    print(imagePath, end='')
                                except UnicodeEncodeError:
                                    print("<cannot read filename>", end='')
                                print("\". Probably, it is in use or is already deleted.")
                    elif method == 3:
                        unusedPath = path + slash + "Trash\\"
                        if not os.path.exists(unusedPath):
                            os.makedirs(unusedPath)
                        try:
                            os.rename(imagePath, unusedPath + image)
                            counterRemoved += 1
                        except OSError or PermissionError:
                            print("FAILED: Cannot move image \"", end='')
                            try:
                                print(imagePath, end='')
                            except UnicodeEncodeError:
                                print("<cannot read filename>", end='')
                            print("\". Probably, it is in use, already deleted or moved to the destination directory.")
                    else:
                        try:
                            print(imagePath)
                        except UnicodeEncodeError:
                            print("<cannot read filename>")
                else:
                    if not image.lower().endswith(".png"):
                        print("WARNING: \"", end='')
                        try:
                            print(image, end='')
                        except UnicodeEncodeError:
                            print("<cannot read filename>", end='')
                        print("\" is not PNG. It is recommended to convert it.")

print("\nTotal number of unused images:", counter)
if method == 1 or method == 2:
    print("Total number of deleted images:", counterDeleted)
elif method == 3:
    print("Total number of removed images:", counterRemoved)
    if counterRemoved != 0:
        try:
            print("Unused images have been moved to " + unusedPath)
        except UnicodeEncodeError:
            pass
        
input("Press Enter to exit.")
sys.exit()
