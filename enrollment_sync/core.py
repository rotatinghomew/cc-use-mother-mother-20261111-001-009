from __future__ import annotations
import hashlib,json,re
from collections import defaultdict,deque
from typing import Any,Mapping
def stable(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(v): return hashlib.sha256(stable(v).encode()).hexdigest()
class BusinessError(ValueError): pass

from enrollment_sync.cases.case_store import process_fixture
def run(raw,database):
 p=raw.get('payload',raw); today=int(p.get('today',0)); valid=[]; expired=[]; invalid=[]
 for doc in [dict(x) for x in p.get('documents',[])]:
  if not doc.get('document_id') or not doc.get('kind'): invalid.append(doc)
  elif int(doc.get('expires_day',10**9))<today: expired.append(doc)
  elif doc.get('checksum') and doc['checksum']!=digest(doc.get('content','')): invalid.append(doc)
  else: valid.append(doc)
 required=set(p.get('required_kinds',[])); missing=sorted(required-{x['kind'] for x in valid}); nodes=set(map(str,p.get('household_nodes',[]))); edges=[tuple(map(str,x)) for x in p.get('household_edges',[])]; outgoing=defaultdict(list); indegree={n:0 for n in nodes}
 for a,b in edges: outgoing[a].append(b); indegree.setdefault(a,0); indegree[b]=indegree.get(b,0)+1
 q=deque(sorted(n for n,d in indegree.items() if d==0)); order=[]
 while q:
  n=q.popleft(); order.append(n)
  for child in outgoing[n]: indegree[child]-=1; q.append(child) if indegree[child]==0 else None
 cycles=sorted(n for n,d in indegree.items() if d>0); local=set(map(str,p.get('local_roster',[]))); remote=set(map(str,p.get('remote_roster',[])))
 result={'valid_documents':valid,'expired':expired,'invalid':invalid,'missing':missing,'eligible':not expired and not invalid and not missing and not cycles,'household_order':order,'cycles':cycles,'portal_staged':not expired and not invalid and not missing,'roster_add':sorted(local-remote),'roster_remove':sorted(remote-local)}
 stored=process_fixture(database,{'subject_id':str(p.get('application_id','application-demo')),'request_key':digest(result),'payload':result})
 return {'enrollment':result,'stored':stored}
