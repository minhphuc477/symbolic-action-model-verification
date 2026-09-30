import os
import subprocess

env = os.environ.copy()
env['FILTER_BRANCH_SQUELCH_WARNING'] = '1'

env_script = '''
export GIT_AUTHOR_NAME="Le Tran Minh Phuc"
export GIT_AUTHOR_EMAIL="mphuc666@gmail.com"
export GIT_COMMITTER_NAME="Le Tran Minh Phuc"
export GIT_COMMITTER_EMAIL="mphuc666@gmail.com"
'''

cmd = ['git', 'filter-branch', '-f', '--env-filter', env_script, 'HEAD']

result = subprocess.run(cmd, env=env, capture_output=True, text=True)
print("Return code:", result.returncode)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
