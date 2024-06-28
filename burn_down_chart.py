import pandas as pd
import time
import json
import win32clipboard
from pyautogui import hotkey, typewrite
from datetime import date, timedelta
import matplotlib.pyplot as plt


def compare_date(t1, t2):
    d1 = time.strptime(t1, "%Y-%m-%d")
    d2 = time.strptime(t2, "%Y-%m-%d")
    return d1 <= d2


def commands_in_shell(repo_path, author):
    hotkey("ctrl", "shift", "t")
    typewrite(f"cd {repo_path}")
    hotkey("ENTER")
    typewrite(
        f'$output=gh issue list -A "{author}" -s "all" --json title --json createdAt --json closedAt --json closed -L '
        f'100; Set-Clipboard -Value $output')
    hotkey("ENTER")


def json_into_df(_json_content, start_date_str, _to_filter, release=False):
    json_data = json.loads(_json_content)

    df_bc = pd.DataFrame(columns=["date", "planned", "actual"])

    created_issues = {}
    closed_issues = {}
    for row in json_data:
        task_title = row["title"]
        if task_title not in _to_filter:
            closed = row["closed"]
            create_date = row["createdAt"][:10]
            close_date = row["closedAt"]
            if closed:
                close_date = close_date[:10]
            if compare_date(start_date_str, create_date):
                if closed:
                    if close_date in closed_issues:
                        closed_issues[close_date] += 1
                    else:
                        closed_issues[close_date] = 1
                if create_date in created_issues:
                    created_issues[create_date] += 1
                else:
                    created_issues[create_date] = 1

    issue_count = sum([v for k, v in created_issues.items()])
    days = 26
    decay = int(issue_count / days) + 1
    start_date = date(int(start_date_str[:4]), int(start_date_str[5:7]), int(start_date_str[8:]))
    last_planned = 0
    last_actual = 0
    for single_date in [start_date + timedelta(n) for n in range(days + 2)]:
        d = str(single_date)
        newly_created = 0
        if d in created_issues:
            newly_created = created_issues[d]
            planned = newly_created + last_planned
        else:
            planned = last_planned
        if d in closed_issues:
            actual = last_actual - closed_issues[d] + newly_created
            last_actual = actual
        else:
            actual = last_actual + newly_created
            last_actual = actual

        if single_date != start_date:
            planned = planned - decay if planned - decay > 0 else 0
        last_planned = planned
        df_bc.loc[len(df_bc)] = [d[5:], planned, actual]

    if release:
        return df_bc
    else:
        return df_bc.iloc[14:]


def df_into_chart(df_bc, sprint, release=False):
    plt.plot(df_bc['date'], df_bc['planned'], marker='o', label='Planned')
    plt.plot(df_bc['date'], df_bc['actual'], marker='o', label='Actual')
    plt.xlabel('Date')
    plt.ylabel('Issue Count')
    if release:
        plt.title(f'Burndown Release 2')
    else:
        plt.title(f'Burndown Chart Sprint {sprint}')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    if release:
        plt.savefig(f'burndown_chart.png')
    else:
        plt.savefig(f'burndown_chart{sprint}.png')
    print("saved burndown chart")


if __name__ == "__main__":
    release_mode = True
    commands_in_shell("E:\\Uni\\Bachelor\\SoSe2024\\STP\\stp-24-team-s", "AshkanKiafard")
    time.sleep(2)
    win32clipboard.OpenClipboard()
    json_content = win32clipboard.GetClipboardData()
    to_filter = []
    df = json_into_df(json_content, "2024-05-27", to_filter, release_mode)
    df_into_chart(df, 4, release_mode)
