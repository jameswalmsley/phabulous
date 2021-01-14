import re
import os
from phabricator import Phabricator
from pprint import pprint

phab = Phabricator()

def __init__():
    phab.update_interfaces()

def phid_lookup(name):
    result = phab.phid.lookup(names=[name])
    if(result):
        return result[name]['phid']
    return None

def slug_lookup(slug):
    result = phab.project.search(constraints={'slugs':[slug]})
    pprint(result)

def get_phid_transactions(phid):
    result = phab.transaction.search(objectIdentifier=phid, constraints={})
    return result['data']

def get_tasks(phids):
    if phids and len(phids) > 0:
        result = phab.maniphest.search(constraints={'phids':phids}, attachments={'projects': True})
        return result['data']
    return []

def get_users(phids):
    result = phab.user.search(constraints={'phids':phids})
    return result['data']

def get_username(username):
    result = phab.user.search(constraints={'usernames':[username]})
    return result['data'][0]

def get_revision(phid):
    result = phab.differential.revision.search(constraints={'phids':[phid]})
    return result['data'][0]

def get_diff(phid):
    result = phab.differential.diff.search(constraints={'phids':[phid]})
    return result['data'][0]

def get_rawdiff(id):
    result = phab.differential.getrawdiff(diffID=str(id))
    return result[:]

def get_commitmessage(revision_id):
    result = phab.differential.getcommitmessage(revision_id=revision_id)
    return result[:]

def task_get_revision_phids(phid):
    phids = []
    result = phab.edge.search(sourcePHIDs=[phid], types=["task.revision"])
    for item in result.data:
        phids.append(item['destinationPHID'])

    return phids

def task_get_mentions(phid):
    phids = []
    result = phab.edge.search(sourcePHIDs=[phid], types=["mention"])
    for item in result.data:
        phids.append(item['destinationPHID'])
    return phids

def get_project(phid):
    result = phab.project.search(constraints={'phids': [phid]})
    return result['data'][0]

def transaction(type, value):
        return {'type': type, 'value': value}

def task_update(task, what):
    t = []
    if 'title' in what:
        t.append(transaction('title', task.title))
    if 'description' in what:
        t.append(transaction('description', task.description))
    if 'assigned' in what:
        t.append(transaction('owner', task.assigned.phid))
    if 'points' in what:
        t.append(transaction('points', task.points))

    if(len(t) > 0):
        phab.maniphest.edit(objectIdentifier=task.phid, transactions=t)

def domain():
    return phab.user.whoami()['primaryEmail'].split('@')[1]

status_symbols = {
    'accepted':'🟢',
    'needs-review': '🟠',
    'needs-revision': '🔨',
    'published': '🟣',
    'abandoned': '🛫',
    'draft': '🔵',
    'changes-planned': '🔴'
}

def get_status_symbol(status):
    if(status in status_symbols):
        return status_symbols[status]

    return " "

def strike(text):
    result = ''
    for c in text:
        result = result + c + '\u0336'
    return result

def vimwiki2phab(md):
    out = ""
    for line in md.splitlines():
        matches = re.findall('(\[\[T\d+\]\])', line)
        if matches:
            for t in matches:
                line = line.replace(t, t.replace('[','').replace(']', ''))
        out = out + line + os.linesep

    return out

def phab2vimwiki(input):
    md = ""
    for line in input.splitlines():
        matches = re.findall('(T\d+)', line)
        if len(matches) > 0:
            for t in matches:
                line = line.replace(t, '[[' + t + ']]')
        md = md + line + os.linesep

    return md