import requests
import webbrowser
import emoji

threshold = 10

def secondindex(stuff):
    count =0
    for i in range(len(stuff)):
        if count == 2:
            return i
        if stuff[i] == "\"":
            count+=1

def find(index,result):
    rt = []
    temp = result.split(index)
    for x in temp:
        count = 0
        num = secondindex(x)
        hold = x[0:num]
        if len(hold) == 14 and hold not in rt:
            rt.append(str(hold))
    return rt

def findAccounts(tag,training): ##finds accounts that post pictures with certain hashtags if it is for training
                                    ##it adds them to a training set and if it is for testing it adds it to a testing set
  url = "https://www.instagram.com/explore/tags/"+tag ##this line gets a number of photos that is given
  tagsearch = requests.request("GET", url).text
  photos  = find("code\":",tagsearch) ##photos assoicated with that hashtag
  for photo in photos:
    photo = photo.replace("\"","")
    photo = photo.replace(" ","") #small data cleaning
    photo = str(photo) #make the id number a string
    url = "https://www.instagram.com/p/"+photo #construct the url
    photosearch = requests.request("GET", url).text
    photosearch = photosearch.split("username\": \"") #finds the usernames
    commenters = []
    for x in photosearch[1:]: #skips the first index becuase it is the poster
        try:
            num = x.index("\"")
            commenter = str(x[0:num])
            commenters.append(commenter) #adds the commenters to the list of users
        except:
            pass
    temp = photosearch[-1]
    posternum = temp.index("\"")
    poster = temp[0:posternum] ##clean the information
    if training == "yes": # if we are training we don't add the commenters
        users = [str(poster)]
    else:
        users = [str(poster)]+commenters
    for user in users:
        if training == "yes": #if it is a trainging set we open the testset files
            testSet = open("testSet.csv","a")
            usedFile = "used2.csv"
            urlL = [line.replace("\n","") for line in open(usedFile,"r")]
        else: #otherwise we open the trainingSet
            testSet = open("trainingSet.csv","a")
            usedFile = "used.csv"
            urlL = [line.replace("\n","") for line in open(usedFile,"r")]
        url = "https://www.instagram.com/"+user
        if user not in urlL: #make sure that user was not already used and evaluated
            try:
                profilesearch = requests.request("GET", url).text
                num = profilesearch.index("biography")
                num2 = profilesearch.index("blocked_by_viewer")
                temp = profilesearch[num:num2]
                bio = temp[11:len(temp)-3] #pull out the user bio
                if training == "yes": # if it is training then we allow the user to answer
                    ans = input("illicit? ")
                else: # otherwise we leave it unknown
                    ans ="?"
                testSet.write(url+"\t"+ans+"\t"+bio+"\n")
                urlL2 = open(usedFile,"a")
                urlL2.write(user+"\n")
                urlL2.close()
            except:
                pass
        testSet.close()

def TrainerII(): ##uses the trainging set to find the ideal threshold
    global threshold
    trainingSet = [line.strip() for line in open("trainingSet.csv","r")] #opens the trainging set
    temp = [line.strip() for line in open("weights.csv")] #opens weights
    W={}
    for line in temp:
        line = line.split(",")
        W[line[0].replace("\"","")] = float(line[1]) # puts the weights in a dictionary
    alpha = .01
    flag = True
    count=0
    while(count<500): # while the perceptron has not made any changes
        count+=1
        print(str(count)+":"+str(threshold))
        flag = False
        for row in trainingSet:
            row = row.split("\t")
            bio = row[2]
            bio = bio.split(" ")
            weight = 0   # pull out all the user's info from the file and set the weight to 0
            for word in W:
                if word in bio:
                    weight+=(int(W[word])) # add up all the weights of the words
            if weight > threshold and row[1] == "n": # if the preceptron fired and it should not have
                for word in bio:
                    try:
                        W[word] = W[word]-alpha # decrease the value of each word
                    except:
                        W[word] = 0-alpha
                threshold = threshold + alpha # increase the value of the threshold
                flag = True # set flag to true to note that we made changes
            elif weight < threshold and row[1] == "y": #if the perceptron fired and it should not have
                for word in bio:
                    try:
                        W[word] = W[word]+alpha #increase the weight of each word
                    except:
                        W[word] = 0+alpha
                threshold = threshold - alpha # decrease the threashold
                flag = True #set the flag to true


    fl = open("weights.csv","r+")
    for word in W:
        fl.write(word+","+str(W[word])+"\n") # write all the weights to the weights file
    fl.close()

def reportII():
    trainingSet = [line.strip() for line in open("testSet.csv","r")]
    illicit = open("illicit.csv","a")
    global threshold
    temp = [line.strip() for line in open("weights.csv")]
    W={}
    for line in temp:
        line = line.split(",")
        W[line[0].replace("\"","")] = float(line[1])
    for row in trainingSet:
        row = row.split("\t")
        bio = row[2]
        bio = bio.split(" ")
        weight = 0
        for word in W:
            if word in bio:
                weight+=(int(W[word]))
        if weight > threshold:
            illicit.write(row[0]+",y\n")
        else:
            illicit.write(row[0]+",n\n")
    illicit.close()

def review():
    import webbrowser
    correct = 0
    wrong = 0
    reviewSet = [line.strip() for line in open("illicit.csv","r")]
    for line in reviewSet:
        line = line.split(",")
        webbrowser.open(line[0])
        ans = input("is illicit? ")
        if ans == line[1]:
            correct+=1
        else:
            wrong+=1
    print("wrong: "+str(wrong))
    print("correct: "+str(correct))
    print("percentage: "+str(correct/(wrong+correct)))



findAccounts("2a","yes")
