from datetime import datetime

from ghapi.all import GhApi

if __name__ == '__main__':
    # GITHUB_TOKEN should be set, otherwise it would not work
    api = GhApi()

    owner = 'fipl-hse'
    repo = '2021-2-level-ctlr-admin'
    expiration_days = 3

    per_page = 100
    _ = api.actions.list_workflow_runs_for_repo(owner, repo, per_page=per_page)
    max_page_idx = api.last_page()
    print(f'Max page is {max_page_idx}')

    for page_idx in range(max_page_idx + 1):
        runs = api.actions.list_workflow_runs_for_repo(owner, repo, per_page=per_page, page=page_idx)
        for run in runs.workflow_runs:
            if run.event == 'push' and run.head_branch == 'main':
                print(f'Skipping #{run.id} as it was run for main branch')
                continue

            delta = datetime.utcnow() - datetime.strptime(run.updated_at, '%Y-%m-%dT%H:%M:%SZ')

            if delta.days > expiration_days:
                print(f'Removing workflow run #{run.id}. Author: {run.actor.login}')
                api.actions.delete_workflow_run(owner, repo, run.id)
            else:
                print(f'Skipping #{run.id} as it was run earlier than {delta.days} days ago')
