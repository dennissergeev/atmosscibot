import sys
from twiply import init_api

api, _ = init_api()

n = int(sys.argv[1])
timeline = api.user_timeline(count=n)
for t in timeline:
    api.destroy_status(t.id)
print('{0} tweets removed.'.format(n))
