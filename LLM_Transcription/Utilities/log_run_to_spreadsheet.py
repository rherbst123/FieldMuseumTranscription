import update_spreadsheet


def main(log_filepath, data):
    update_spreadsheet.append_to_csv(log_filepath, data)

if __name__ == "__main__":
    log_filepath = "DataAnalysis/runs_log.csv"
    data = [{
        "run_name": "gpt-4-2024-01-01-0100",
        "model": "gpt-4-vision-preview",
        "prompt": "Prompt 1.5.2",
        "dataset": "dataset1",
        "goal_of_run": "test script"
    }]
    main(log_filepath, data)