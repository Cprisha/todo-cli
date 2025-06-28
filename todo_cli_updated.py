import pandas as pd
import os

def prioritytag(n):
    labels = {
        1: "Very High",
        2: "High",
        3: "Medium",
        4: "Low",
        5: "Very Low"
    }
    return labels.get(n, "Unknown")

def load(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if "Tags" not in df.columns:
            df["Tags"] = ""
        return df
    return pd.DataFrame(columns=["S.No.", "Todo", "Label", "Priority Number", "Tags"])

def get_valid_priority():
    while True:
        try:
            p = int(input("Enter priority (1–5): ").strip())
            if 1 <= p <= 5:
                return p
            print("Priority must be between 1 and 5.")
        except ValueError:
            print("Invalid input. Enter a number.")


def save(df, file_path):
    df.to_csv(file_path, index=False)

def backup(df):
    df.to_csv("undo_backup.csv", index=False)

def undoaction(file_path):
    backup_file = "undo_backup.csv"
    if os.path.exists(backup_file):
        backup_df = pd.read_csv(backup_file)
        save(backup_df, file_path)
        print("Undo successful. Last action reverted.")
    else:
        print("No backup available to undo.")

def next_serial(df):
    if df.empty:
        return 1
    return df["S.No."].max() + 1

completed_file = "completed_todos.csv"
if not os.path.exists(completed_file):
    pd.DataFrame(columns=["Todo", "List", "Label"]).to_csv(completed_file, index=False)

while True:
    list_name = input("Which list do you want to use? ").strip().lower()
    file_path = f"{list_name}.csv"
    while True:
        action = input("Type add, show, edit, complete, filter, view completed, undo or exit: ").strip().lower()
        if action == "add":
            df = load(file_path)
            todo = input("Enter a todo: ").strip()

            priority_num = get_valid_priority()
            priority_label = prioritytag(priority_num)

            tag = ""
            if input("Do you want to add a tag? (yes/no): ").strip().lower() == "yes":
                tag = input("Enter tag: ").strip()
            serial = next_serial(df)
            new_row = pd.DataFrame([[serial, todo, priority_label, priority_num, tag]],
                                   columns=["S.No.", "Todo", "Label", "Priority Number", "Tags"])
            df = pd.concat([df, new_row], ignore_index=True)
            save(df, file_path)
        elif action == "show":
            df = load(file_path)
            if df.empty:
                print("No todos yet.")
            else:
                display_df = df.sort_values(by="Priority Number")[["S.No.", "Todo", "Label", "Tags"]]
                print(display_df.to_string(index=False))
        elif action == "edit":
            df = load(file_path)
            if df.empty:
                print("No todos to edit.")
                continue
            print(df[["S.No.", "Todo", "Label", "Tags"]].to_string(index=False))
            try:
                target = int(input("Enter S.No. of the task to edit: "))
                if target not in df["S.No."].values:
                    print("Invalid S.No.")
                    continue
                backup(df)
                field = input("Edit name, priority, tag, or all?: ").strip().lower()
                if "name" in field or "all" in field:
                    new_name = input("Enter new todo name: ").strip()
                    df.loc[df["S.No."] == target, "Todo"] = new_name
                if "priority" in field or "all" in field:
                    new_priority = int(input("Enter new priority (1–5): "))
                    df.loc[df["S.No."] == target, "Priority Number"] = new_priority
                    df.loc[df["S.No."] == target, "Label"] = prioritytag(new_priority)
                if "tag" in field or "all" in field:
                    new_tag = input("Enter new tag: ").strip()
                    df.loc[df["S.No."] == target, "Tags"] = new_tag
                save(df, file_path)
                print("Task updated.")
                print("Task updated.")
            except ValueError:
                print("Invalid input.")
            except KeyError:
                print("Task not found.")

        elif action == "complete":
            df = load(file_path)
            if df.empty:
                print("No tasks to complete.")
                continue
                print(df[["S.No.", "Todo", "Label"]].to_string(index=False))
            try:
                complete_id = int(input("Enter S.No. of task to mark complete: "))
                row = df[df["S.No."] == complete_id]
                if row.empty:
                    print("Invalid S.No.")
                    continue
                backup(df)
                done_df = pd.read_csv(completed_file)
                completed_row = pd.DataFrame([[row["Todo"].values[0], list_name, row["Label"].values[0]]],
                                             columns=["Todo", "List", "Label"])
                done_df = pd.concat([done_df, completed_row], ignore_index=True)
                save(done_df, completed_file)
                df = df[df["S.No."] != complete_id]
                save(df, file_path)
                print("Task marked as complete.")
            except ValueError:
                print("Invalid S.No. or input.")
            except KeyError:
                print("Could not find the specified task.")

        elif action == "filter":
            df = load(file_path)
            if df.empty:
                print("No todos to filter.")
                continue
            print("Filter by: \n 1. Tag \n2. Priority")
            choice = input("Enter 1 or 2: ").strip()
            if choice == "1":
                tag_input = input("Enter tag to filter by: ").strip().lower()
                filtered = df[df["Tags"].fillna("").str.lower() == tag_input]
            elif choice == "2":
                try:
                    level = int(input("Enter priority number to filter by (1–5): "))
                    filtered = df[df["Priority Number"] == level]
                except ValueError:
                    print("Invalid priority number.")
                    continue
            else:
                print("Invalid filter choice.")
                continue
            if filtered.empty:
                print("No matching tasks found.")
            else:
                print(filtered[["S.No.", "Todo", "Label", "Tags"]].to_string(index=False))
        elif action == "view completed":
            done_df = pd.read_csv(completed_file)
            list_tasks = done_df[done_df["List"] == list_name]
            if list_tasks.empty:
                print(f"No completed tasks in {list_name}.")
            else:
                print("\nCompleted Tasks:\n")
                print(list_tasks[["Todo", "Label"]].to_string(index=False))
        elif action == "undo":
            undoaction(file_path)
        elif action == "exit":
            print(f"Exiting {list_name} list.")
            break
        else:
            print("Invalid command. Try again.")

    while True:
        print("\nYou've exited the list:", list_name)
        print("What would you like to do next?")
        print("1. View completed todos (all lists)")
        print("2. Switch to another list")
        print("3. Exit the app")
        post_choice = input("Enter choice (1/2/3): ").strip()

        if post_choice == "1":
            done_df = pd.read_csv(completed_file)
            if done_df.empty:
                print("No completed tasks yet.")
            else:
                print("\n Completed Todos Across All Lists:\n")
                print(done_df.to_string(index=False))
            input("Press Enter to return to main menu.")
            break
        elif post_choice == "2":
            break
        elif post_choice == "3":
            print("You are all done")
            exit()
        else:
            print("Invalid choice. Try 1, 2 or 3.")
