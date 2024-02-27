import http.client, json, time

LESSON_GROUP_ID = input("Geef die lesson-group id ahh broer: ")
COOKIE = input("Geef mij koekjes (ik heb honger): ")
LESSONS_SKIPPEN = int(input("Geef hoeveel lessons geskipt moeten worden: "))

conn = http.client.HTTPSConnection("metis.slimstampen.nl")
conn.request("GET", f"/ruggedlearning/api/lesson-group/{LESSON_GROUP_ID}", headers={"Cookie": COOKIE})
lijstje = [x["id"] for num, x in enumerate(json.loads(conn.getresponse().read())["lessonInfoList"]) if num >= LESSONS_SKIPPEN] #wth, we letten er niet op
print(lijstje)

for aantalGedaan, lessonId in enumerate(lijstje, 1):
    conn.request("GET", f"/ruggedlearning/api/response/getFirstCue/{lessonId}", headers={"Cookie": COOKIE})
    response = json.loads(conn.getresponse().read())
    sessionTime = 0

    SESSION_ID = response["sessionId"]
    a = 0
    while not response["sessionProgress"]["achievedCredit"]:
        currentFactId = response["cue"]["fact"]["id"]
        currentPrompt = response["cue"]["fact"]["cueTexts"][0]
        currentAnswer = response["cue"]["fact"]["answers"][0]
        
        currentBody = {
                "backspacedFirstLetter": False,
                "backspaceUsed": False,
                "alternatives": "[]",
                "answerMethod": "TEXT_INPUT",
                "numberOfChoices": 0,
                "presentedCueTextIndex": 0,
                "presentedImageIndex": 0,
                "mostDifficult": False,
                "correct": True,
                "keyStrokes": [],
                "reactionTime": 500,
                "presentationStartTime": int(time.time()*1000),
                "factId": currentFactId,
                "givenResponse": currentAnswer,
                "lessonId": lessonId,
                "sessionId": SESSION_ID
            }
        for index, char in enumerate(currentAnswer):
            currentBody["keyStrokes"].append({
                "character": char,
                "code": "Space" if char == " " else "Key" + char.upper(),
                "timeDown": currentBody["presentationStartTime"] + currentBody["reactionTime"] + 50 * index,
                "type":	"keydown"
            })

        currentBody["presentationDuration"] = 50 * len(currentAnswer) + currentBody["reactionTime"]
        currentBody["currentTime"] = currentBody["presentationStartTime"] + currentBody["presentationDuration"]
        sessionTime += currentBody["presentationDuration"]
        currentBody["sessionTime"] = sessionTime
        currentBody["data"] = json.dumps(currentBody) 

        time.sleep(currentBody["presentationDuration"] / 1000)

        conn.request("POST", "/ruggedlearning/api/response/save", body=json.dumps(currentBody), headers={"Content-Type": "application/json", "Cookie": COOKIE}) 

        response = json.loads(conn.getresponse().read())
        a += 1
        print(f"{currentPrompt} = {currentAnswer}, {a}")
    print(f"\n{aantalGedaan}/{len(lijstje)}")

conn.close()
print("\a")
time.sleep(0.5)