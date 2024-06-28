import re
import time
import json
import win32clipboard
from pyautogui import hotkey, typewrite
import datetime


def compare_date(t1, t2):
    d1 = time.strptime(t1, "%Y-%m-%d")
    d2 = time.strptime(t2, "%Y-%m-%d")
    return d1 <= d2


def find_closed_in_shell(repo_path):
    hotkey("ctrl", "shift", "t")
    typewrite(f"cd {repo_path}")
    hotkey("ENTER")
    typewrite(
        f'$output=gh issue list -s "all" --json number --json title --json state --json createdAt -L 1000; '
        f'Set-Clipboard -Value $output')
    hotkey("ENTER")


def list_issues_in_shell(_repo_path):
    hotkey("ctrl", "shift", "t")
    typewrite(f"cd {_repo_path}")
    hotkey("ENTER")
    typewrite(f'$output=gh project item-list 10 --owner "sekassel" --format json -L 1000; Set-Clipboard -Value $output')
    hotkey("ENTER")
    time.sleep(2)
    hotkey("ENTER")


def json_content_to_json_data(json_content):
    _json_data = json.loads(json_content)
    return _json_data


def sort_json_data(_json_data):
    filtered_data = [item for item in _json_data["items"] if "number" in item["content"]]
    sorted_data = sorted(filtered_data, key=lambda x: x["content"]["number"])
    _json_data["items"] = sorted_data
    return _json_data


def add_closed_and_sprint3_issues(_json_data):
    _closed_list = []
    to_filter = ["Save gangs for different user offline",
                 "save.json in gitignore",
                 "Avatar maker",
                 "Language",
                 "Filter out started games in browse games",
                 "Avatar editor in Edit Account Screen",
                 "Update user avatar in server"]
    sprint3_tasks = []
    sprint4_tasks = []
    for row in _json_data:
        closed = True if row["state"].lower() == "closed" else False
        number = int(row["number"])
        create_date = row["createdAt"][:10]
        task_title = row["title"]
        if closed:
            _closed_list.append(number)
        if task_title not in to_filter and compare_date("2024-05-27", create_date) and compare_date(create_date,
                                                                                                    "2024-06-7"):
            sprint3_tasks.append(number)
        if task_title in to_filter or compare_date("2024-06-7", create_date):
            sprint4_tasks.append(number)
    return _closed_list, sprint3_tasks, sprint4_tasks


def get_digits(text):
    return int(''.join(c for c in text if c.isdigit()))


def sort_and_str(l):
    l.sort()
    return [str(num) for num in l]


def find_sub_tasks_and_stories(task):
    subtasks = [get_digits(subtask) for subtask in re.findall("- \[.\] #[0-9]*", task)]
    subtasks = sort_and_str(subtasks)
    pattern = r'https://github\.com/sekassel/stp-24-team-s/issues/(\d+)'
    if "relevant stories" in task:
        stories = re.findall(pattern, task)
        stories = sort_and_str(stories)
    else:
        stories = []
    return subtasks, stories


def int_to_time(time_int):
    hours = time_int
    minutes = 60 * (hours % 1)

    return "%02d:%02d" % (hours, minutes) + "h"


def time_difference(time1, time2):
    dt1 = datetime.timedelta(hours=int(time1[:2]), minutes=int(time1[3:5]))
    dt2 = datetime.timedelta(hours=int(time2[:2]), minutes=int(time2[3:5]))
    time_diff = dt2 - dt1
    total_seconds = time_diff.total_seconds()
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if time_diff.total_seconds() < 0:
        sign = "-"
        time_diff = dt1 - dt2
        total_seconds = time_diff.total_seconds()
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
    else:
        sign = "+"
    result = f"{sign}{int(abs(hours))}:{int(abs(minutes)):02}"
    return result + "h"


def tasks_into_latex(json_data, closed_list, sprint3_list, sprint4_list):
    sprint3_tasks_latex = []
    sprint4_tasks_latex = []
    stories_latex = []

    stories_table = []
    tasks_table = []

    stories_table.append(r"""\setlength\LTleft{-1cm}
\begin{small}
    \sloppy
    \centering

    \begin{longtable}{| p{34pt} |  p{190pt} | p{52pt} | p{40pt} | p{34pt} |p{34pt} |}
    \caption{Übersichtstabelle aller Stories}\\ \hline
    
    \textbf{Ticket-Nr} & \centering\textbf{Name} & \textbf{Geschätzte Zeit} & \textbf{Aktuelle Zeit} & \textbf{Story Points} & \textbf{Status} \\ \hline 
    \endfirsthead

        \multicolumn{6}{c}
    {{ \tablename\ \thetable{} -- von letzter Seite fortgesetzt}} \\ \hline
    \textbf{Ticket-Nr} & \textbf{Name} & \textbf{Geschätzte Zeit} & \textbf{Aktuelle Zeit} & \textbf{Story Points} & \textbf{Status} \\ \hline 
    \endhead

    \multicolumn{6}{|c|}{Auf der folgenden Seite fortgesetzt} \\ \hline
    \endfoot


    \endlastfoot""")

    tasks_table.append(r"""\setlength\LTleft{-1cm}
\begin{small}
    \label{tab:tasks} 
    \sloppy
    \centering

    \begin{longtable}{| p{34pt} | p{34pt} | p{120pt} |p{52pt} |p{52pt} | p{34pt} |  p{48pt} |}
    \caption{Übersichtstabelle aller Tasks}\\ \hline
    
    \textbf{Ticket-Nr} & \textbf{Ticket-Type} & \centering\textbf{Name} & \textbf{Geschätzte Zeit} & \textbf{Echte Zeit} & \textbf{Sprint} & \textbf{Status} \\ \hline 
    \endfirsthead

        \multicolumn{7}{c}
    {{ \tablename\ \thetable{} -- von letzter Seite fortgesetzt}} \\ \hline
    \textbf{Ticket-Nr} & \textbf{Ticket-Type} & \centering\textbf{Name} & \textbf{Geschätzte Zeit} & \textbf{Echte Zeit} & \textbf{Sprint} & \textbf{Status} \\ \hline 
    \endhead

    \multicolumn{7}{|c|}{Auf der folgenden Seite fortgesetzt} \\ \hline
    \endfoot


    \endlastfoot""")

    tasks_count = 0
    stories_count = 0
    bugs_count = 0
    canceled_count = 0
    not_done_count = 0
    done_count = 0

    tasks_count_sprint3 = 0
    tasks_count_sprint4 = 0

    sprint3_total_real_time = 0
    sprint4_total_real_time = 0
    stories_total_real_time = 0

    sprint3_toal_estimated_time = 0
    sprint4_toal_estimated_time = 0
    stories_toal_estimated_time = 0

    no_estimated_time = []
    no_real_time = []

    for i, row in enumerate(json_data["items"]):
        task_title = row["title"]
        cancelled = "DEPRECATED" in task_title
        task_title = task_title.replace("(DEPRECATED)", "")
        ticket_number = row["content"]["number"]
        closed = True if ticket_number in closed_list else False

        if cancelled:
            task_status = "storniert"
        elif closed:
            task_status = "geschlossen"
        else:
            task_status = "unvollendet"

        try:
            task_type = row["issue Type"]
        except KeyError:
            # print(i, "No task type found: ", task_title)
            if not cancelled:
                continue
            else:
                print(task_title)

        try:
            labels = row["labels"]
            task_type = "Bug" if "bug" in labels else task_type
        except KeyError:
            pass

        try:
            sprint = row["sprint"]["title"]
        except KeyError:
            sprint = ""

        try:
            estimated_time = row["time Estimate (h)"]
        except KeyError:
            estimated_time = ""
            if task_type != "Story" and (sprint in ["Sprint 3",
                                                    "Sprint 4"] or ticket_number in sprint4_list or ticket_number in sprint3_list):
                no_estimated_time.append(f"{ticket_number} {task_type} {task_title}")

        try:
            real_time = row["time Total (h)"]
        except KeyError:
            real_time = ""
            if task_type != "Story" and (sprint in ["Sprint 3",
                                                    "Sprint 4"] or ticket_number in sprint4_list or ticket_number in sprint3_list):
                no_real_time.append(f"{ticket_number} {task_type} {task_title}")

        try:
            story_points = row["story Points"]
        except KeyError:
            story_points = ""

        if task_type != "Story":
            description = row["content"]["body"]

            patterns = [
                r'- \[(?:x| )\] #\d+',
                r'relevant stories:',
                r'- https://github\.com/sekassel/stp-24-team-s/issues/\d+(?:#issue-\S+)?',
                r'https://github\.com/sekassel/stp-24-team-s/issues/\d+(?:#issue-\S+)?',
                r'!\[.*?\]\(https://github\.com/sekassel/stp-24-team-s/assets/.*?\)',
                r'^\s*#.*\n?'
            ]
            combined_pattern = '|'.join(patterns)
            new_description = re.sub(combined_pattern, '', description)
            new_description = re.sub(r'\n\s*\n', '\n\n', new_description).strip()

            new_short_description = " ".join([word for i, word in enumerate(new_description.split(" ")) if i < 100])
            new_short_description = "\n".join(
                [line for i, line in enumerate(new_short_description.split("\n")) if i < 4])
            if len(new_short_description) < len(new_description):
                new_short_description += " ..."

            new_short_description = re.sub(r'(?<=- )\[\s*[x ]?\s*\]', '', new_short_description, flags=re.MULTILINE)

            subtasks, stories = find_sub_tasks_and_stories(description)
        else:
            new_short_description = ""
            subtasks, stories = [], []

        story_points_text = ""
        if story_points != "" and str(story_points) != "0":
            story_points_text = f"\nStory Points: & {story_points}\\\\"

        explaination = ""
        if task_type != "Story":
            if cancelled:
                explaination += "Diese Aufgabe ist storniert, da"
            elif not closed:
                explaination += ("Diese Aufgabe konnte während des zweiten Releases nicht vollständig abgeschlossen "
                                 "werden und wird in den nächsten Releases nachgeholt.\n")
            if estimated_time != "" and real_time != "":
                int_estimated_time = float(estimated_time)
                int_real_time = float(real_time)
                if int_estimated_time == int_real_time:
                    # explaination += "Hier stimmen die geschätzte Zeit und die Bearbeitungszeit komplett überein.
                    # Die Zeit war perfekt geschätzt.\n"
                    pass
                elif abs(int_estimated_time - int_real_time) <= float(int_estimated_time * 0.25):
                    explaination += ("Die geschätzte Zeit und die tatsächliche Bearbeitungszeit weichen ein bisschen "
                                     "voneinander ab. (Grund: ...)\n")
                elif abs(int_estimated_time - int_real_time) > float(int_estimated_time * 0.25):
                    explaination += "Geschätzte Zeit und Bearbeitungszeit weichen stark voneinander ab. (Grund: ...)\n"

        subtasks_text = ""
        if len(subtasks) > 0:
            subtasks_text = f"\nSubtasks: & {', '.join(subtasks)}\\\\"
            new_short_description = ("Alle Details finden sich in den Beschreibungen und Erklärungen der zugehörigen "
                                     "Subtasks.")
            explaination = ""
        else:
            new_short_description = ""

        stories_text = ""
        if len(stories) > 0:
            stories_text = f"\nRelevante Stories: & {', '.join(stories)}\\\\"

        explaination = explaination.strip()

        if task_type == "Story":
            task_title = task_title.replace("(Story)", "")

        actual_time_text = ""
        estimated_time_text = ""
        if estimated_time != "":
            estimated_time_text = int_to_time(estimated_time)
        if real_time != "":
            real_time_text = int_to_time(real_time)
            if estimated_time != "":
                diff_text = {}
                if estimated_time != real_time:
                    diff_text = f" ({time_difference(estimated_time_text, real_time_text)})"
                actual_time_text = f"\nEchte Zeit: & {real_time_text}{diff_text}\\\\"

        task = f"""
          \\textbf{{{task_type}: {task_title}}} (Ticket-Nr\\#{ticket_number})
          \\hrule \\vspace{{-15pt}}
          \\begin{{tabular}}{{r p{{0.75\\linewidth}}}}{story_points_text}
                  Beschreibung: & {new_short_description} \\vspace{{4pt}}\\\\ \\hdashline{subtasks_text}{stories_text}
                  Geschätzte Zeit: &  {estimated_time_text}\\\\{actual_time_text}
                  {'Erklärung: & ' if len(explaination) > 0 else ''}{explaination}
          \\end{{tabular}}
          \\hrule
          \\vspace{{15pt}}
          """

        if sprint in ["Sprint 3", "Sprint 4"] or ticket_number in sprint3_list + sprint4_list:
            if task_type == "Story":
                stories_count += 1
            elif task_type == "Bug":
                bugs_count += 1
            else:
                tasks_count += 1

        if task_type == "Story":
            if sprint in ["Sprint 3", "Sprint 4"] or cancelled:
                stories_latex.append(task)
                table_row = f"""{ticket_number} & {task_title} & {estimated_time_text} & {real_time_text} & {story_points} & {task_status} \\tabularnewline \hline"""
                stories_table.append(table_row)
                if estimated_time != "":
                    stories_toal_estimated_time += int(estimated_time)
                if real_time != "":
                    stories_total_real_time += int(real_time)
        else:
            if sprint == "Sprint 3" or ticket_number in sprint3_list:
                if ticket_number == 332:
                    print("332 found")
                if cancelled:
                    canceled_count += 1
                elif closed:
                    done_count += 1
                else:
                    not_done_count += 1

                tasks_count_sprint3 += 1
                sprint3_tasks_latex.append(task)
                table_row = f"""
                    {ticket_number} & 
                    {task_type} & 
                    {task_title} & 
                    {estimated_time_text} &
                    {real_time_text if real_time != "" else "-"} &
                     Sprint 3 &
                    {task_status} \\tabularnewline \hline"""

                tasks_table.append(table_row)
                if estimated_time != "":
                    sprint3_toal_estimated_time += int(estimated_time)
                if real_time != "":
                    sprint3_total_real_time += int(real_time)
            elif sprint == "Sprint 4" or ticket_number in sprint4_list:
                if cancelled:
                    canceled_count += 1
                elif closed:
                    done_count += 1
                else:
                    not_done_count += 1

                tasks_count_sprint4 += 1
                sprint4_tasks_latex.append(task)
                table_row = f"""{ticket_number} & {task_type} & {task_title} & {estimated_time_text} & {real_time_text if real_time != "" else "-"} & Sprint 4 & {task_status} \\tabularnewline \hline"""
                tasks_table.append(table_row)
                if estimated_time != "":
                    sprint4_toal_estimated_time += int(estimated_time)
                if real_time != "":
                    sprint4_total_real_time += int(real_time)

    print(f"tasks: {tasks_count}, bugs: {bugs_count}")
    print(f"sprint 3: {tasks_count_sprint3}, sprint 4: {tasks_count_sprint4}")
    print(f"done: {done_count}, not done: {not_done_count}, cancelled: {canceled_count}")

    # print("no real time: ")
    # for i, row in enumerate(no_real_time):
    #     print(i, row)

    stories_table.append(f"""
 \\multicolumn{{3}}{{c|}}{{}} & \\textbf{{$\\Sigma$: {stories_toal_estimated_time}:00h}} & \\textbf{{$\\Sigma$: {stories_total_real_time}:00h}} \\\\ \\cline{{4-5}}
        \\end{{longtable}}
    \\end{{small}}
""")

    tasks_table.append(f"""
    \\multicolumn{{3}}{{c|}}{{}} & \\textbf{{$\\Sigma$: {sprint4_toal_estimated_time + sprint3_toal_estimated_time}:00h}} & \\textbf{{$\\Sigma$: {sprint4_total_real_time + sprint3_total_real_time}:00h}} \\\\ \\cline{{4-5}}
        \\end{{longtable}}
    \\end{{small}}
    """)

    with open("sprint 3.txt", "w") as text_file:
        text_file.write("\n".join(sprint3_tasks_latex))

    print("saved sprint3_tasks_latex")

    with open("sprint 4.txt", "w") as text_file:
        text_file.write("\n".join(sprint4_tasks_latex))

    print("saved sprint4_tasks_latex")

    with open("stories.txt", "w") as text_file:
        text_file.write("\n".join(stories_latex))

    print("saved stories_latex")

    with open("stories_table.txt", "w") as text_file:
        text_file.write("\n".join(stories_table))

    print("saved stories_table")

    with open("tasks_table.txt", "w") as text_file:
        text_file.write("\n".join(tasks_table))

    print("saved tasks_table")


if __name__ == "__main__":
    repo_path = "E:\\Uni\\Bachelor\\SoSe2024\\STP\\stp-24-team-s"
    win32clipboard.OpenClipboard()

    # If you have already used step 1 before, copy the data from step 1 here, else you can delete these lines
    closed_list = [394, 379, 378, 376, 375, 374, 373, 372, 366, 365, 362, 357, 356, 355, 351, 349, 348, 346, 344, 343,
                   342, 341, 340, 339, 338, 336, 335, 334, 333, 332, 331, 330, 329, 328, 327, 326, 325, 324, 323, 322,
                   321, 320, 319, 318, 317, 316, 315, 314, 313, 312, 306, 305, 304, 303, 302, 301, 300, 299, 298, 297,
                   296, 295, 294, 293, 292, 291, 290, 289, 288, 286, 284, 283, 278, 277, 276, 275, 274, 273, 272, 271,
                   270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 258, 257, 256, 255, 254, 253, 252, 251, 250,
                   249, 248, 247, 246, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230,
                   229, 228, 227, 226, 225, 224, 223, 222, 221, 220, 219, 193, 176, 172, 160, 159, 156, 155, 154, 153,
                   147, 146, 145, 144, 143, 142, 133, 124, 123, 122, 121, 120, 119, 117, 116, 115, 114, 113, 112, 111,
                   110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89,
                   88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69,
                   68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44,
                   43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19,
                   18, 118, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    sprint3_list = [357, 356, 355, 351, 349, 348, 346, 344, 340, 339, 338, 336, 335, 334, 333, 332, 331, 330, 329, 328,
                    327, 326, 325, 324, 323, 322, 321, 320, 319, 318, 317, 316, 315, 314, 313, 306, 305, 304, 303, 302,
                    301, 300, 299, 298, 297, 296, 295, 294, 293, 292, 291, 290, 289, 288, 286, 284, 283, 282, 281, 280,
                    279, 278, 277, 276, 275, 274, 273, 272, 271, 270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260,
                    258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246, 245, 244, 243, 242, 241, 240, 239,
                    238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 227, 226, 225, 224, 223, 222, 221, 220, 219]
    sprint4_list = [445, 443, 442, 441, 440, 439, 438, 437, 436, 435, 434, 433, 432, 431, 430, 429, 428, 427, 426, 425,
                    424, 422, 421, 420, 419, 418, 417, 416, 415, 414, 413, 412, 411, 410, 409, 408, 407, 406, 405, 404,
                    403, 402, 401, 400, 399, 398, 397, 396, 395, 394, 380, 379, 378, 377, 376, 375, 374, 373, 372, 371,
                    368, 366, 365, 364, 362, 350, 343, 342, 341, 312]
    # Step 1
    # find_closed_in_shell(repo_path)
    # time.sleep(3)
    # json_content = win32clipboard.GetClipboardData()
    # json_data = json_content_to_json_data(json_content)
    # closed_list, sprint3_list, sprint4_list = add_closed_and_sprint3_issues(json_data)
    # print("closed_list = ", closed_list)
    # print("sprint3_list = ", sprint3_list)
    # print("sprint4_list = ", sprint4_list)

    # Step 2
    # Either use code to get data

    # list_issues_in_shell(repo_path)
    # time.sleep(5)
    # json_content = win32clipboard.GetClipboardData()
    # json_data = json_content_to_json_data(json_content)
    # json_data = sort_json_data(json_data)

    # or copy data in data.json yourself after excecuting the command in powershell (I prefer this way)
    with open("data.json", 'r') as file:
        json_data = json.load(file)
        json_data = sort_json_data(json_data)

    tasks_into_latex(json_data, closed_list, sprint3_list, sprint4_list)

    win32clipboard.CloseClipboard()
