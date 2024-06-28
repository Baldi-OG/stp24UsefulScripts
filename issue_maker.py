import time
import pandas as pd
from pyautogui import hotkey, typewrite

df = pd.read_excel("stories.xlsx").iloc[42:]
for index, row in df.iterrows():
    title = row['Name'].replace('"', "'")
    c1 = row['Start'].replace('"', "'")
    c2 = row['Action'].replace('"', "'")
    c3 = row['Result'].replace('"', "'")
    body = ("<h2> Start </h2></br><i>" + c1 + "</i></br>" + "<h2> Action </h2></br><i>"
            + c2 + "</i></br>" + "<h2> Result </h2></br><i>" + c3 + "</i>")
    print(index, body)
    hotkey("ctrl", "shift", "t")
    typewrite("cd E:\\Uni\\Bachelor\\SoSe2024\\STP\\stp-24-team-s")
    hotkey("ENTER")
    typewrite(f'gh issue create --title "(Story) {title}" --body "{body}" -m "v2" --label "story"')
    hotkey("ENTER")
    time.sleep(5)
