import base64
import bcrypt
import psycopg
import enum
from datetime import datetime
from getpass import getpass

class UserType(enum.Enum):
    Admin = 0
    Trainer = 1
    Member = 2
    Unassigned = 3

currentUsername = "tempval" #unique identifier
currentUserType = UserType.Unassigned.value #permissions

dbname=input("Enter database name (default: projectdb): ")
user=input("Enter user (postgres): ")
password= getpass("Enter password: ")
inputstr = "dbname="+str(dbname)+" user="+str(user)+" password="+str(password)
db = psycopg.connect(inputstr)

#Checks if a password matches a hashed one
#takes a string and bytes respectively
def isPasswordValid(password, hashed_password):
    return bcrypt.checkpw(str.encode(password), hashed_password)

#Hashes a password with a RANDOM salt
#takes a string and returns bytes
def hashPassword(password):
    return bcrypt.hashpw(str.encode(password), bcrypt.gensalt())


def changePassword():
    cur = db.cursor()
    global currentUsername
    global currentUserType
    #get the corresponding hash for the stored password
    cur.execute("Select Password from Member where mUname = %s",([currentUsername]))
    rows = cur.fetchall()
    if(len(rows) == 0 or len(rows) > 1):
        print("Non-Unique Username! - Returning. (Impossible)\n")
        return
    currentPw = rows[0][0]
    #prompt user for password
    checkerPw = input("Enter current password: ")
    #call isPasswordValid to compare to stored password
    # if not same, go back, otherwise proceed
    if(isPasswordValid(checkerPw, currentPw) == False):
        print("Passwords don't match.\n")
        return
    #prompt user for new password (no password is and will go back)
    newPw = input("Enter new password: ")
    if(len(newPw) == 0):
        print("New password length 0, aborting.\n")
        return
    #hash the password
    newHashedPw = hashPassword(newPw)
    #create a request to replace the current user password+hash with the new one
    valid = True
    try:
        cur.execute("update Member set Password = %s where mUname = %s", (newHashedPw, currentUsername))
    except:
        valid = False
    if(valid == False):
        print("Update failed! - No idea why this happened.\n")
        db.rollback()
        return
    db.commit()
    #confirmation message
    print("Updated password successfully.\n")

def unauthorizedMainMenu():
    #interface for not logged in users
    #Member Login
    #Trainer Login
    #Admin Login
    #Register
    #Quit
    while(1):
        print("Welcome to the Health and Fitness Club.\n1. Member Login\n2. Trainer Login\n3. Admin Login\n4. Register\n5. Quit\n")
        selection = input("Enter selection: ")
        selection=int(selection)
        match selection:
            case 1:
                login(UserType.Member.value)
            case 2:
                login(UserType.Trainer.value)
            case 3:
                login(UserType.Admin.value)
            case 4:
                register()
            case _:
                print("Quitting...\n")
                exit()
    exit()

def register():
    cur = db.cursor()
    
    #ask for username
    # if it already exists, ask again.
    while(1):
        newUname = input("Enter your username (permanent): ")
        cur.execute("Select mUname from Member where mUname =%s", ([newUname]))
        if(len(cur.fetchall()) > 0):
            print("This username already exists.")
        else:
            break
    #ask for name
    newName = input("Enter your name: ")
    #ask for password
    # if pw 0 length, ask again.
    while(1):
        newPassword = input("Enter your password: ")
        if(len(newPassword) == 0):
            print("Password must be longer than 0 characters!")
        else:
            break
    newPassword = hashPassword(newPassword)
    #ask for height
    tempHeight = input("Enter your height: ")
    newHeight = 0
    if(len(tempHeight) > 0):
        if(tempHeight.isdigit() == False):
                print("Not valid digit, defaulting to 0")
        else:
            newHeight = int(tempHeight)
    #ask for weight
    tempWeight = input("Enter your weight: ")
    newWeight = 0
    if(len(tempWeight) > 0):
        if(tempWeight.isdigit() == False):
                print("Not valid digit, defaulting to 0")
        else:
            newWeight = int(tempWeight)
    #try to add
    valid = True
    try:
        cur.execute("insert into Member (Name, mUname, Password, Height, Weight) values(%s,%s,%s,%s,%s)", (newName, newUname, newPassword, newHeight, newWeight))
    except:
        valid = False
    if(valid == False):
        print("Add failed! Contact an administrator.")
        db.rollback()
    else:
        db.commit()
        print("Account successfully created")
        #create a bill for this account
        cur.execute("insert into Bill (Amount, mUname) values(%s, %s)", (100, newUname))
        db.commit()



    
    return

def memberMainMenu():
    #interface for the member main menu
    #Display Profile
    #Edit Profile
    #View Dashboard
    #View Schedule
    #Create a Personal Session
    #Edit a Personal Session
    #Group Class Menu
    #View bills
    #Log out
    while(1):
        print("\nWelcome member "+currentUsername+".\n")
        print("1. Display Profile\n2. Edit Profile\n3. View Dashboard\n4. View Schedule\n5. Create Personal Session\n6. Edit Personal Session\n7. Delete Personal Session\n8. Group Class Menu\n9. Bill Menu\n10. Log Out\n")
        selection = input("Enter selection: ")
        selection=int(selection)
        match selection:
            case 1:
                displayProfile(currentUsername, currentUserType)
            case 2:
                profileEditMenu()
            case 3:
                displayDashboard()
            case 4:
                viewSchedule(currentUsername, currentUserType)
            case 5:
                createPersonalSession()
            case 6:
                editPersonalSession()
            case 7:
                deletePersonalSession()
            case 8:    
                groupClassMenu()
            case 9:
                memberBillMenu()
            case _:
                logout()
                return
    return

def trainerMainMenu():
    #interface for trainers
    #Display Profile
    #Edit Profile
    #Print available days
    #Show Schedule
    #Add available day
    #Remove available day
    #Search for member
    #Log out
    while(1):
        print("\nWelcome trainer "+currentUsername+".\n")
        print("1. Display Profile\n2. Edit Profile\n3. View Available Days\n4. View Schedule\n5. Search for Member\n6. Log out\n")
        selection = input("Enter selection: ")
        selection=int(selection)
        match selection:
            case 1:
                displayProfile(currentUsername, currentUserType)
            case 2:
                profileEditMenu()
            case 3:
                printTrainerAvailableDays(currentUsername)
            case 4:
                viewSchedule(currentUsername, currentUserType)
            case 5:
                memberSearch()
            case _:
                logout()
                return
    return

def adminMainMenu():
    #interface for admins
    #Display Profile
    #Edit Profile
    #Display Users
    #Display Trainers
    #Room Manager
    #Group Class Menu
    #Payment Manager
    #Log out
    while(1):
        print("\nWelcome admin "+currentUsername+".\n")
        print("1. Display Profile\n2. Display Members\n3. Display Trainers\n4. Room Manager\n5. Group Class Menu\n6. Payment Manager\n7. Log out")
        selection = input("Enter selection: ")
        selection=int(selection)
        match selection:
            case 1:
                displayProfile(currentUsername, currentUserType)
            case 2:
                printMembers()
            case 3:
                printTrainers()
            case 4:
                roomManager()
            case 5:
                groupClassManager()
            case 6:
                paymentManagerMenu()
            case _:
                logout()
                return
    return




def login(logintype):
    cur = db.cursor()
    global currentUsername
    global currentUserType
    #have user enter a username and password
    username = input("Enter username: ")
    password = input("Enter password: ") #getpass("Enter password: ")
    #query corresponding relation with username
    #super vulnerable to sql injection attack. Too bad!
    # there are ways to mitigate the risk but that's way out of scope for this project
    match logintype:
        case UserType.Admin.value:
            cur.execute("Select Password from Administrator where aUname =%s",([username]))
        case UserType.Trainer.value:
            cur.execute("Select Password from Trainer where tUname =%s",([username]))
        case _:
            cur.execute("Select Password from Member where mUname =%s",([username]))
    rows = cur.fetchall()
    if(len(rows) == 0 or len(rows) > 1): #if there isn't a matching username or somehow more than 1
        print("Invalid username/password\n")
        return
    hashed_password = rows[0][0]
    #get the password and then run the checker
    isValid = isPasswordValid(password, hashed_password)
    #if anything goes wrong just say invalid username/password combination
    if(isValid == False):
        print("Invalid username or password\n")
        return
    #if success we log in and go to the corresponding menu
    currentUsername = username
    currentUserType = logintype
    match logintype:
        case UserType.Admin.value:
            adminMainMenu()
        case UserType.Trainer.value:
            trainerMainMenu()
        case _:
            memberMainMenu()
    return

def logout():
    global currentUsername
    global currentUserType
    #set Permission back to defaults
    CurrentUserType = UserType.Unassigned.value
    #We don't need to change the username since its never used when logged out
    #run unauthorizedmainmenu
    unauthorizedMainMenu() #builds up on stack. Too bad!
    return

def profileEditMenu():
    cur = db.cursor()
    global currentUsername
    global currentUserType
    #all users may edit name and password.
    #members may also add/edit/remove goal, add achievement, and edit helth metrics
    #trainers may edit the days they are available.
    displayString = "Options:\n"
    match currentUserType:
        case UserType.Member.value:
            displayString = displayString + "1. Edit Name\n2. Edit Password\n3. Goal Menu\n4. Add Achievement\n5. Edit Weight\n6. Edit Height"
        case UserType.Trainer.value:
            displayString = displayString + "1. Add Available Day\n2. Remove Available Day"
    print(displayString)
    selection = input("Enter selection: ")
    if(selection.isdigit() == False):
        print("You didn't enter a valid selection.")
        return
    selection = int(selection)
    match currentUserType:
        case UserType.Member.value:
            match selection:
                case 1:
                    changeName()
                case 2:
                    changePassword()
                case 3:
                    goalMenu()
                case 4:
                    addAchievement()
                case 5:
                    changeWeight()
                case 6:
                    changeHeight()
        case UserType.Trainer.value:
            match selection:
                case 1:
                    addAvailableDay()
                case 2:
                    removeAvailableDay()
            
    
    return

def changeName():
    cur = db.cursor()
    global currentUsername
    global currentUserType
    #get the current name
    cur.execute("Select Name from Member where mUname = %s",([currentUsername]))
    rows = cur.fetchall()
    currentName = rows[0][0]
    
    newName = input("Enter new name: ")
    if(len(newName) == 0):
        print("New name length 0, aborting.\n")
        return
    if(newName == currentName):
        print("Same name, no modifications performed")
        return

    valid = True
    try:
        cur.execute("update Member set Name = %s where mUname = %s", (newName, currentUsername))
    except:
        valid = False
    if(valid == False):
        print("Update failed! - No idea why this happened.\n")
        db.rollback()
        return
    db.commit()
    #confirmation message
    print("Updated Name successfully.\n")

def goalMenu():
    cur = db.cursor()
    global currentUsername
    global currentUserType
    #get the current goal
    cur.execute("Select * from Goal where mUname = %s",([currentUsername]))
    rows = cur.fetchall()
    if(len(rows) == 0):
        print("No goals.")
        selection = input("Would you like to create a goal? (Y/N): ")
        if(selection == "Y"):
            addGoal()
        else:
            return

    #if no goal, theres add goal button
    #   just two prompts to ask about weight and time goals
    #if there is a goal
    #1. Set weight goal
    #2. Set time goal
    #3. Delete goals
    print("Goal Menu\n1. Set Weight Goal\n2. Set Time Goal\n3. Delete Goals")
    selection = input("Selection: ")
    if(selection.isdigit() == False):
        print("You didn't enter a valid selection.")
        return
    selection = int(selection)
    match(selection):
        case 1:
            setWeightGoal()
        case 2:
            setTimeGoal()
        case 3:
            deleteGoals()
    return

def addGoal():
    cur = db.cursor()
    global currentUsername
    global currentUserType
    #get the current goal
    cur.execute("Select * from Goal where mUname = %s",([currentUsername]))
    rows = cur.fetchall()
    if(len(rows) > 0):
        print("There is already goal object.")
        return
    
    weightGoal = input("Enter weight goal: ")
    if(weightGoal.isdigit() == False):
        print("You didn't enter a number.")
        return
    weightGoal = int(weightGoal)
    timeGoal = input("Enter time goal: ")
    if(timeGoal.isdigit() == False):
        print("You didn't enter a number.")
        return
    timeGoal = int(timeGoal)
    cur.execute("insert into Goal (mUname, WeightGoal, TimeGoal) values(%s,%s,%s)",(currentUsername, weightGoal, timeGoal))
    db.commit()
    print("Added successfully")
    return

def setWeightGoal():
    cur = db.cursor()
    global currentUsername
    global currentUserType
    #get the current goal
    cur.execute("Select * from Goal where mUname = %s",([currentUsername]))
    rows = cur.fetchall()
    if(len(rows) == 0):
        print("No goals.")
        return
    
    weightGoal = input("Enter weight goal: ")
    if(weightGoal.isdigit() == False):
        print("You didn't enter a number.")
        return
    weightGoal = int(weightGoal)
    cur.execute("update Goal set WeightGoal=%s where mUname=%s", (weightGoal, currentUsername))
    db.commit()
    return

def setTimeGoal():
    cur = db.cursor()
    global currentUsername
    global currentUserType
    #get the current goal
    cur.execute("Select * from Goal where mUname = %s",([currentUsername]))
    rows = cur.fetchall()
    if(len(rows) == 0):
        print("No goals.")
        return

    timeGoal = input("Enter time goal: ")
    if(timeGoal.isdigit() == False):
        print("You didn't enter a number.")
        return
    timeGoal = int(timeGoal)
    cur.execute("update Goal set TimeGoal=%s where mUname=%s", (timeGoal, currentUsername))
    db.commit()
    
    return

def deleteGoals():
    cur = db.cursor()
    global currentUsername
    global currentUserType
    #get the current goal
    cur.execute("Select * from Goal where mUname = %s",([currentUsername]))
    rows = cur.fetchall()
    if(len(rows) == 0):
        print("No goals to delete!")
        return

    cur.execute("Delete from Goal where mUname = %s",([currentUsername]))
    db.commit()
    print("Removed goals successfully")
    
    return

def addAchievement():
    global currentUsername
    global currentUserType
    #a prompt for description
    desc = input("Enter what you did:\n")
    if(len(desc) == 0):
        print("You didn't enter anything")
        return
    cur = db.cursor()
    try:
        cur.execute("insert into Achievement (mUname, Description) values(%s,%s)", (currentUsername, desc))
    except:
        print("Add failed!")
        db.rollback()
        return
    db.commit()
    print("Added successfully")
    return

def changeWeight():
    global currentUsername
    global currentUserType
    #a prompt for weight
    weight = input("Enter what you weigh:\n")
    if(len(weight) == 0):
        print("You didn't enter anything")
        return
    if(weight.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    weight = int(weight)
    cur = db.cursor()
    try:
        cur.execute("update Member set Weight=%s where mUname=%s", (weight, currentUsername))
    except:
        print("update failed!")
        db.rollback()
        return
    db.commit()
    print("updated weight successfully")
    return

def changeHeight():
    global currentUsername
    global currentUserType
    #a prompt for height
    height = input("Enter your height:\n")
    if(len(height) == 0):
        print("You didn't enter anything")
        return
    if(height.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    height = int(height)
    cur = db.cursor()
    try:
        cur.execute("update Member set Height=%s where mUname=%s", (height, currentUsername))
    except:
        print("update failed!")
        db.rollback()
        return
    db.commit()
    print("updated height successfully")
    return

def displayProfile(username, usertype):
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #get the details of a given user.
    #in general, print out Name, username
    #for specific member, print goals and weight+height
    #do nothing special for trainers or admin.
    match usertype:
        case UserType.Admin.value:
            cur.execute("Select * from Administrator where aUname =%s",([username]))
        case UserType.Trainer.value:
            cur.execute("Select * from Trainer where tUname =%s",([username]))
        case _:
            cur.execute("Select * from Member where mUname =%s",([username]))
    rows = cur.fetchall()
    if(len(rows) == 0 or len(rows) > 1): #if there isn't a matching username or somehow more than 1
        print("Invalid username\n") #this probably won't happen!
        return
    profile = rows[0]
    match usertype:
        case UserType.Admin.value:
            print("Administrator\nName: "+profile[0]+"\nUsername: "+profile[1])
        case UserType.Trainer.value:
            print("Trainer\nName: "+profile[0]+"\nUsername: "+profile[1])
        case _:
            print("Member\nName: "+profile[0]+"\nUsername: "+profile[1]+"\nHeight: "+str(profile[3])+"\nWeight: "+str(profile[4]))
            #try to get goals
            cur.execute("Select * from Goal where mUname =%s",([username]))
            rows = cur.fetchall()
            if(len(rows) == 1):
                goals = rows[0]
                print("Weight Goal: "+str(goals[1])+" Time Goal: "+str(goals[2]))
            else:
                print("No Goals Set.\n")
    
    return

def displayDashboard():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #print every single attended session/class, achievements, and weight + height (why is this different from profile? are health statistics and metrics different?)
    if(currentUserType != UserType.Member.value):
        print("Not a member!\n")
        return
    cur.execute("Select * from Member where mUname =%s",([currentUsername]))
    rows = cur.fetchall()
    profile = rows[0]
    if(len(rows) == 0 or len(rows) > 1): #if there isn't a matching username or somehow more than 1
        print("Invalid username\n") #this probably won't happen!
        return
    print("\nHello "+profile[0]+". Here is your dashboard.\n""\nHeight: "+str(profile[3])+"\nWeight: "+str(profile[4]))
    cur.execute("Select * from Achievement where mUname=%s",([currentUsername]))
    rows = cur.fetchall()
    if(len(rows) > 0):
        print("Achievements:")
        for entry in rows:
            print(str(entry[2])+": "+entry[1])
    viewSchedule(currentUsername, currentUserType)
    return

def viewSchedule(username, usertype):
    global currentUsername
    global currentUserType
    #if its admin, return
    #otherwise, print personal then group classes
    #this applies for both trainer and member
    if(usertype == UserType.Admin.value):
        return
    printPersonalSessions(username, usertype)
    printGroupClasses(username, usertype)
    return

#displays all personal classes which have been registered for by the user
def printPersonalSessions(username, usertype):
    global currentUsername
    global currentUserType
    cur = db.cursor()
    if(usertype == UserType.Admin.value):
        return
    #if its admin, return
    #otherwise, print personal
    match usertype:
        case UserType.Trainer.value:
            cur.execute("Select * from PersonalSession where tUname =%s",([username]))
        case _:
            cur.execute("Select * from PersonalSession where mUname =%s",([username]))
    rows = cur.fetchall()
    if(len(rows) > 0):
        print("Personal Sessions:")
        for entry in rows:
            print("ID:"+str(entry[0])+" Date:"+str(entry[1])+" Member:"+entry[2]+" Trainer:"+entry[3]+" Room:"+str(entry[4]))
    return

#displays all group classes which have been registered for by the user
def printGroupClasses(username, usertype):
    global currentUsername
    global currentUserType
    cur = db.cursor()
    if(usertype == UserType.Admin.value):
        return
    #if its admin, return
    #otherwise, print group
    match usertype:
        case UserType.Trainer.value:
            cur.execute("Select * from GroupSession where tUname =%s",([username]))
            rows = cur.fetchall()
            if(len(rows) > 0):
                print("Group Sessions:")
                for entry in rows:
                    print("ID:"+str(entry[0])+" Date:"+str(entry[1])+" Trainer:"+entry[3]+" Room:"+str(entry[4])+" Description:"+entry[2])
        case _:
            cur.execute("Select gSID from Group_Participant where mUname =%s",([username]))
            matchinggSID = cur.fetchall()
            if(len(matchinggSID)==0):
                return
            print("\nGroup Sessions:")
            for gSID in matchinggSID:
                cur.execute("Select * from GroupSession where gSID =%s",([gSID[0]]))
                rows = cur.fetchall()
                if(len(rows) > 0):
                    for entry in rows:
                        print("ID:"+str(entry[0])+" Date:"+str(entry[1])+" Trainer:"+entry[3]+" Room:"+str(entry[4])+" Description:"+entry[2])  
    return


def createPersonalSession():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #query user for a list of invalid dates
    #ask user for a date
    #if invalid, go back
    #query trainers for the entered date that aren't hosting something on that date
    #if no trainers show up, call this function again
    #otherwise, put tUname into array and get user to select one
    #if invalid, then we go back to menu
    #the database will try to find the first available room.
    # if no room, then go back to menu
    #create a new personal session for that date with that instructor.
    date = input("Enter a date to set the class to (YYYY-MM-DD): ")
    dateformat = "%Y-%m-%d"
    valid = True
    #ensuring the date is in the correct format
    try:
        result = bool(datetime.strptime(date, dateformat))
    except:
        valid = False
    if(valid == False):
        print("invalid date format")
        return

    trainerArray = []
    cur.execute("select * from Availability where Availability.aDate =%s and aDate > CURRENT_DATE", ([date]))
    trainers = cur.fetchall()
    if(len(trainers) == 0):
        print("no trainers available on this date")
        return
    print("Available Trainers:")
    for trainer in trainers:
        print("Username: "+trainer[0])
        trainerArray.append(trainer[0])

    trainerUsername = input("Enter a trainer username: ")
    if (trainerUsername not in trainerArray):
        print("That's not a valid trainer")
        return

    cur.execute("select rID from Room")
    displayrooms = cur.fetchall()
    print("Available rooms:")
    for room in displayrooms:
        print("Room #: "+str(room[0]))

    roomID = input("Enter a room ID: ")
    if(roomID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    roomID = int(roomID)
    cur.execute("select * from Room where Room.rID =%s", ([roomID]))
    rooms = cur.fetchall()
    if(len(rooms) == 0):
        print("no rooms available on this date")
        return
    
    try:
        cur.execute("insert into PersonalSession (SessionDate,mUname,tUname,rID) values(%s,%s,%s,%s)",(date, currentUsername,trainerUsername,roomID))
    except:
        print("insert failed")
        db.rollback()
        return
    db.commit()
    print("Class created!")
    return

def editPersonalSession():
    global currentUsername
    global currentUserType
    #display session IDs and details and ask user which to edit
    # if invalid, return to menu
    #if valid, give 2 options: delete or edit date
    #edit date prints available dates for the trainer. if not entered valid, leave
    #delete just deletes the session
    cur = db.cursor()
    classID = input("Enter a personal class ID to edit: ")
    if(classID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    classID = int(classID)

    cur.execute("select * from PersonalSession where pSID =%s and SessionDate > CURRENT_DATE and mUname =%s", (classID,currentUsername)) #cant edit classes on day of or before, thats not cool
    classes = cur.fetchall()
    if(len(classes) == 0):
        print("no classes match")
        return
    

    date = input("Enter a date to set the class to (YYYY-MM-DD): ")
    dateformat = "%Y-%m-%d"
    valid = True
    #ensuring the date is in the correct format
    try:
        result = bool(datetime.strptime(date, dateformat))
    except:
        valid = False
    if(valid == False):
        print("invalid date format")
        return

    trainerArray = []
    cur.execute("select * from Availability where Availability.aDate =%s", ([date]))
    trainers = cur.fetchall()
    if(len(trainers) == 0):
        print("no trainers available on this date")
        return
    print("Available Trainers:")
    for trainer in trainers:
        print("Username: "+trainer[0])
        trainerArray.append(trainer[0])

    trainerUsername = input("Enter a trainer username: ")
    if (trainerUsername not in trainerArray):
        print("That's not a valid trainer")
        return
    try:
        cur.execute("Update PersonalSession set tUname =%s, SessionDate =%s where pSID =%s",(trainerUsername,date, classID))
        #cur.execute("Update PersonalSession set SessionDate =%s where pSID =%s",(date,classID))
    except:
        print("Update failed")
        db.rollback()
        return
    db.commit()
    return

def deletePersonalSession():
    global currentUsername
    global currentUserType
    classID = input("Enter a personal class ID to delete: ")
    if(classID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    classID = int(classID)
    cur = db.cursor()
    cur.execute("select * from PersonalSession where pSID =%s and SessionDate > CURRENT_DATE and mUname =%s", (classID,currentUsername)) #cant delete classes on day of or before, thats not cool. also can't delete sessions belonging to other users
    classes = cur.fetchall()
    if(len(classes) == 0):
        print("no classes match")
        return
    #delete a specific session
    cur.execute("delete from PersonalSession where pSID=%s", ([classID]))
    db.commit()
    return

#member specific - displays group classes you can actually register for
def printAllGroupClasses():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    cur.execute("select * from GroupSession where SessionDate > CURRENT_DATE")
    rows = cur.fetchall()
    if(len(rows) == 0):
        print("There are no group sessions available for registration.")
        return
    for entry in rows:
        print("ID:"+str(entry[0])+" Date:"+str(entry[1])+" Trainer:"+entry[3]+" Room:"+str(entry[4])+" Description:"+entry[2])
    return

def joinGroupClass():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    classID = input("Enter class id to join: ")
    if(classID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    classID = int(classID)
    cur.execute("select * from GroupSession where SessionDate > CURRENT_DATE and gSID = %s", ([classID]))
    rows =cur.fetchall()
    if(len(rows) == 0):
        print("There are no matching group sessions available for registration.")
        return
    rows = cur.execute("select * from Group_Participant where mUname = %s and gSID = %s", (currentUsername,classID)).fetchall()
    if(len(rows) != 0):
        print("The selected session has already been registered for.")
        return
    cur.execute("insert into Group_Participant (gSID, mUname) values(%s,%s)",(classID, currentUsername))
    db.commit()
    print("Class joined!")
    return

def leaveGroupClass():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    classID = input("Enter class id to leave: ")
    if(classID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    classID = int(classID)

    rows = cur.execute("select * from GroupSession where SessionDate > CURRENT_DATE and gSID = %s", ([classID])).fetchall()
    if(len(rows) == 0):
        print("There are no matching group sessions available to leave from.")
        return
    rows = cur.execute("select * from Group_Participant where mUname = %s and gSID = %s", (currentUsername,classID)).fetchall()
    if(len(rows) == 0):
        print("You aren't registered for this session.")
        return
    cur.execute("delete from Group_Participant where gSID=%s and mUname=%s",(classID, currentUsername))
    db.commit()
    print("Class left successfully!")
    return

def groupClassMenu():
    global currentUsername
    global currentUserType
    #member specific group class menu
    #option which lists all group classes and their ids
    #option which lists joined group classes
    #option which lets member join a class.
    # must have a non-conflicting date.
    #option which lets member leave a class.
    print("Group Class Menu\n1. Display all joinable group classes\n2. Display all joined group classes\n3. Join a Class\n4. Leave a Class")
    selection = input("Enter selection: ")
    if(selection.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    selection = int(selection)
    match selection:
        case 1:
            printAllGroupClasses()
        case 2:
            printGroupClasses(currentUsername, currentUserType)
        case 3:
            joinGroupClass()
        case 4:
            leaveGroupClass()
    return


def getTrainerAvailableDays(username):
    global currentUsername
    global currentUserType
    cur = db.cursor()
    cur.execute("Select aDate from Availability where tUname =%s",([username]))
    rows = cur.fetchall()
    if(len(rows) == 0):
        return []
    returned = []
    for availability in rows:
        returned.append(availability[0])
    return returned

def printTrainerAvailableDays(username):
    global currentUsername
    global currentUserType
    #print all of them
    rows = getTrainerAvailableDays(username)
    if(rows == 0):
        print("This trainer has no days set as available.")
        return
    for date in rows:
        print(date)
    return

def printTrainerNonConflictingDays(username):
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #query for the dates which trainer is both available and doesnt have session, and is ahead of current date.
    cur.execute("Select aDate from Availability where tUname =%s and aDate > CURRENT_DATE",([username]))
    rows = cur.fetchall()
    if(len(rows) == 0):
        print("This trainer has no days set as available.")
        return
    validDates = []
    for row in rows:
        validDates.append(row[0])
    #get every date where the trainer is busy
    #dates in personalsession
    cur.execute("Select SessionDate from PersonalSession where tUname =%s and SessionDate > CURRENT_DATE",([username]))
    rows = cur.fetchall()
    if(len(rows) > 0):
        datesToRemove = []
        for row in rows:
            datesToRemove.append(row[0])
        validDates = list(filter(lambda i: i not in datesToRemove, validDates))
    #dates in groupsession
    cur.execute("Select SessionDate from GroupSession where tUname =%s and SessionDate > CURRENT_DATE",([username]))
    rows = cur.fetchall()
    if(len(rows) > 0):
        datesToRemove = []
        for row in rows:
            datesToRemove.append(row[0])
        validDates = list(filter(lambda i: i not in datesToRemove, validDates))
    if(len(rows) == 0):
        print("This trainer has no days available for registration.")
        return
    for date in validDates:
        print(date)
        
    return

def memberBillMenu():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #print all the bills
    print("Here are your bills:")
    cur.execute("Select * from Bill where mUname =%s",([currentUsername]))
    bills = cur.fetchall()
    billDict = {}
    for bill in bills:
        print("ID:"+str(bill[0])+" Amount:"+str(bill[1])+" Paid?:"+str(bill[2])+" Verified?:"+str(bill[3]))
        billDict[bill[0]] = bill[2]
    
    #enter bill id to pay the bill
    billID = input("Enter bill ID to pay (Enter nothing to go back.): ")
    if(len(billID) == 0):
        return
    #any invalid bill will return to previous menu
    billID=int(billID)
    if(billID not in billDict.keys()):
        print("Invalid bill ID")
        return
    if(billDict[billID] == True):
        print("Bill already paid!")
        return
    cur.execute("update Bill set IS_PAID = %s where bID=%s", (True, billID))
    db.commit()
    return

def addAvailableDay():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #for the logged in trainer, ask for a day to make available.
    #if its a valid date, add it.
    #otherwise, return to menu
    date = input("Enter a date to make available (YYYY-MM-DD): ")
    dateformat = "%Y-%m-%d"
    valid = True
    #ensuring the date is in the correct format
    try:
        result = bool(datetime.strptime(date, dateformat))
    except:
        valid = False
    if(valid == True):
        """#we probably dont even need this since the db takes case of the conflicts and just spits out errors if we try
        alreadyAvail = getTrainerAvailableDays(currentUsername)
        if(date in alreadyAvail):
            print("Date already available.")
        else:
        """
        try:
            cur.execute("insert into Availability (tUname, aDate) values (%s,%s)", (currentUsername, date))
        except:
            print("Add failed! A trainer cannot have 2 identical dates!")
            valid = False
        if(valid):
            db.commit()
        else:
            db.rollback()
        return;
    else:
        print("invalid date format.")
        return
    return

def removeAvailableDay():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #same as above but for remove.
    #enter any date after current date and it will become unavailable.
    #any trainer events that day will be cancelled -> delete them too.
    date = input("Enter a date to remove (YYYY-MM-DD): ")
    dateformat = "%Y-%m-%d"
    valid = True
    #ensuring the date is in the correct format
    try:
        result = bool(datetime.strptime(date, dateformat))
    except:
        valid = False
    if(valid == False):
        print("invalid date format.")
        return

    cur.execute("delete from Availability where tUname=%s and aDate=%s", (currentUsername, date))
    db.commit()
    cur.execute("delete from GroupSession where tUname=%s and SessionDate=%s", (currentUsername, date))
    db.commit()
    cur.execute("delete from PersonalSession where tUname=%s and SessionDate=%s", (currentUsername, date))
    db.commit()
    
    return

def memberSearch():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #enter a username and will query for a member.
    #will return right after
    queryName = input("Enter name to search: ")
    cur.execute("Select * from Member where Name like %(namequery)s", ({ 'namequery': '%{}%'.format(queryName)}))
    rows = cur.fetchall()
    i = 1
    if(len(rows) > 0):
        print("Matching Members for "+queryName+": ")
        for entry in rows:
            print("User "+str(i)+":")
            displayProfile(entry[1],UserType.Member.value)
            print("\n")
            i += 1
    else:
        print("No matching members.")
    return

def printMembers():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #query for set of all members. ADMIN ONLY
    if(currentUserType != UserType.Admin.value):
        return
    cur.execute("Select * from Member")
    rows = cur.fetchall()
    if(len(rows) > 0):
        print("Members:")
        for entry in rows:
            print("Name: "+entry[0]+"\nUsername: "+entry[1]+"\nPassword: "+str(entry[2]))
    else:
        print("No members.")
    return

def printTrainers():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #query for set of all trainers. ADMIN ONLY
    if(currentUserType != UserType.Admin.value):
        return
    cur.execute("Select * from Trainer")
    rows = cur.fetchall()
    if(len(rows) > 0):
        print("Trainers:")
        for entry in rows:
            print("Name: "+entry[0]+"\nUsername: "+entry[1]+"\nPassword: "+str(entry[2]))
    else:
        print("No trainers.")
    return

def roomManager():
    global currentUsername
    global currentUserType
    #interface
    #print all rooms + equipment status
    #maintain equipment (really simple, just prompt for a room# to repair)
    #clear room for a day (basically cancel classes for a room for a day)
    print("Room Manager\n1. Display Rooms\n2. Equipment Maintainer\n3. Clear a Room for a day")
    
    selection = input("Enter your choice:\n")
    if(selection.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    selection = int(selection)
    match selection:
        case 1:
            displayRooms()
        case 2:
            fixEquipment()
        case 3:
            clearRoom()
    return

def displayRooms():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #query for set of all rooms.
    cur.execute("Select * from Room")
    rows = cur.fetchall()
    if(len(rows) > 0):
        print("Rooms:")
        for entry in rows:
            print("Room #: "+str(entry[0])+"\nEquipment Condition: "+str(entry[1])+"%")
    else:
        print("No Rooms.")
    return

def fixEquipment():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    roomID = input("Enter room id to fix: ")
    if(roomID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    roomID = int(roomID)
    #find the room if it exists, and then set its equipment to 100
    cur.execute("Select * from Room where rID=%s",([roomID]))
    rooms = cur.fetchall()
    if(len(rooms) == 0):
        print("No room found.")
        return

    cur.execute("update Room set EquipCond = %s where rID=%s", (100, roomID))
    db.commit()
    print("room equipment fixed!")
    
    
    return

def clearRoom():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    roomID = input("Enter room to clear for a day: ")
    if(roomID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    roomID = int(roomID)
    
    date = input("Enter date (YYYY-MM-DD): ")
    dateformat = "%Y-%m-%d"
    valid = True
    #ensuring the date is in the correct format
    try:
        result = bool(datetime.strptime(date, dateformat))
    except:
        valid = False
        print("Invalid date.")
        return

    #find the personal and/or group session which matches the room id and takes place at the date and delete them
    cur.execute("delete from GroupSession where SessionDate=%s and rID=%s", (date, roomID))
    db.commit()
    cur.execute("delete from PersonalSession where SessionDate=%s and rID=%s", (date, roomID))
    db.commit()

    print("Cleared Day.")
    
    return

def groupClassManager():
    global currentUsername
    global currentUserType
    #interface
    #1. Create group class
    #2. Edit group class
    #3. Cancel Group class
    print("Group Class Manager\n1. Create Group Class\n2. Edit Group Class\n3. Cancel Group Class")
    selection = input("Selection: ")
    if(selection.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    selection = int(selection)
    match selection:
        case 1:
            createGroupClass()
        case 2:
            editGroupClass()
        case 3:
            deleteGroupClass()
    
    return

def createGroupClass():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #query user for a list of invalid dates
    #ask user for a date
    #if invalid, go back
    #query trainers for the entered date that aren't hosting something on that date
    #if no trainers show up, call this function again
    #otherwise, put tUname into array and get user to select one
    #if invalid, then we go back to menu
    #the database will try to find the first available room.
    # if no room, then go back to menu
    #create a new group class for that date with that instructor.
    date = input("Enter a date to set the class to (YYYY-MM-DD): ")
    dateformat = "%Y-%m-%d"
    valid = True
    #ensuring the date is in the correct format
    try:
        result = bool(datetime.strptime(date, dateformat))
    except:
        valid = False
    if(valid == False):
        print("invalid date format")
        return

    trainerArray = []
    cur.execute("select * from Availability where Availability.aDate =%s", ([date]))
    trainers = cur.fetchall()
    if(len(trainers) == 0):
        print("no trainers available on this date")
        return
    print("Available Trainers:")
    for trainer in trainers:
        print("Username: "+trainer[0])
        trainerArray.append(trainer[0])

    trainerUsername = input("Enter a trainer username: ")
    if (trainerUsername not in trainerArray):
        print("That's not a valid trainer")
        return

    roomID = input("Enter a room ID: ")
    if(roomID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    roomID = int(roomID)
    cur.execute("select * from Room where Room.rID =%s", ([roomID]))
    rooms = cur.fetchall()
    if(len(rooms) == 0):
        print("no rooms available on this date")
        return

    description = input("Enter a description: ")
    
    try:
        cur.execute("insert into GroupSession (SessionDate,Description,tUname,rID) values(%s,%s,%s,%s)",(date, description,trainerUsername,roomID))
    except:
        print("insert failed")
        db.rollback()
        return
    db.commit()
    print("Class created!")
    return

def editGroupClass():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    #You can change the date.
    #gives a list of valid rooms and trainers for a specific date.
    #type room number.
    #if invalid, do nothing
    #otherwise set group class to a new room.

    classID = input("Enter a group class ID to edit: ")
    if(classID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    classID = int(classID)

    cur.execute("select * from GroupSession where gSID =%s and SessionDate > CURRENT_DATE", ([classID])) #cant edit classes on day of or before, thats not cool
    classes = cur.fetchall()
    if(len(classes) == 0):
        print("no classes match")
        return
    

    date = input("Enter a date to set the class to (YYYY-MM-DD): ")
    dateformat = "%Y-%m-%d"
    valid = True
    #ensuring the date is in the correct format
    try:
        result = bool(datetime.strptime(date, dateformat))
    except:
        valid = False
    if(valid == False):
        print("invalid date format")
        return

    trainerArray = []
    cur.execute("select * from Availability where Availability.aDate =%s", ([date]))
    trainers = cur.fetchall()
    if(len(trainers) == 0):
        print("no trainers available on this date")
        return
    print("Available Trainers:")
    for trainer in trainers:
        print("Username: "+trainer[0])
        trainerArray.append(trainer[0])

    trainerUsername = input("Enter a trainer username: ")
    if (trainerUsername not in trainerArray):
        print("That's not a valid trainer")
        return
    try:
        cur.execute("update GroupSession set SessionDate = %s, tUname = %s where gSID = %s",(date,trainerUsername,classID))
    except:
        print("Update failed")
        db.rollback()
        return
    db.commit()
    return

def deleteGroupClass():
    global currentUsername
    global currentUserType
    selection = input("Enter a group class ID to delete: ")
    if(selection.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    selection = int(selection)
    cur = db.cursor()
    #delete a specific group class
    cur.execute("delete from GroupSession where gSID=%s", ([classID])) #cascade so group participant will also be deleted.
    db.commit()
    return

def paymentManagerMenu():
    global currentUsername
    global currentUserType
    #interface
    #1. list all bills
    #2. List unpaid bills
    #3. List paid but unverified bills
    #4. Verify a bill
    # this just involves entering a number
    # if verified/unpaid/invalid do nothing
    # otherwise verify it.
    print("Payment Manager\n1. List all bills\n2. List unpaid bills\n3. List paid & unverified bills\n4. Verify a bill")
    selection = input("Enter selection: ")
    if(selection.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    selection = int(selection)
    match selection:
        case 1:
            displayAllBills()
        case 2:
            displayUnpaidBills()
        case 3:
            displayPaidUnverifiedBills()
        case 4:
            billVerifier()
        case _:
            return
    return

def displayAllBills():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    cur.execute("Select * from Bill")
    bills = cur.fetchall()
    for bill in bills:
        print("ID:"+str(bill[0])+" Username:"+bill[4]+" Amount:"+str(bill[1])+" Paid?:"+str(bill[2])+" Verified?:"+str(bill[3]))
    return

def displayUnpaidBills():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    cur.execute("Select * from Bill where IS_PAID=FALSE")
    bills = cur.fetchall()
    for bill in bills:
        print("ID:"+str(bill[0])+" Username:"+bill[4]+" Amount:"+str(bill[1])+" Paid?:"+str(bill[2])+" Verified?:"+str(bill[3]))
    return

def displayPaidUnverifiedBills():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    cur.execute("Select * from Bill where IS_PAID=TRUE and IS_VERIFIED=FALSE")
    bills = cur.fetchall()
    for bill in bills:
        print("ID:"+str(bill[0])+" Username:"+bill[4]+" Amount:"+str(bill[1])+" Paid?:"+str(bill[2])+" Verified?:"+str(bill[3]))
    return

def billVerifier():
    global currentUsername
    global currentUserType
    cur = db.cursor()
    billID = input("Enter Bill ID: ")
    if(billID.isdigit() == False):
        print("You didn't enter a valid number.")
        return
    billID = int(billID)

    cur.execute("Select * from Bill where IS_PAID=TRUE and IS_VERIFIED=FALSE and bID=%s",([billID]))
    bills = cur.fetchall()
    if(len(bills) == 0):
        print("No bill with matching ID and is paid but unverified found.")
        return

    cur.execute("update Bill set IS_VERIFIED = %s where bID=%s", (True, billID))
    db.commit()
    print("Bill verified!")
    
    return

"""
def isTrainerAvailable(date, tUname):
    cur = db.cursor()
    trainerArray = []
    cur.execute("select * from Availability where aDate =%s and tUname=%s", (date, tUname))
    result = cur.fetchall()
    if(len(result) == 0):
        return False

    
    
    return
"""
unauthorizedMainMenu()
