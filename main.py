import requests
import  json
import logging
import  csv
import pandas as pd


# Define Gobal Variables
database =''
token=''
values = {'database': database, 'token': token}

API_DOMAIN ="https://itm.arcc.albany.edu/WSG/"
APIs= dict(
    getAllUser=API_DOMAIN+"user/get/all",
    getAllProject=API_DOMAIN+"project/get/all",
    getAllThread=API_DOMAIN+"thread/get/all",
    getAllNote =API_DOMAIN+"note/get/all",
    getAllView=API_DOMAIN+"view/get/all",
    getNoteNoteByThreadID=API_DOMAIN+"thread/note/to_id",
    getProjectViewByPid=API_DOMAIN+"project/view/getbyId",
    getWonderingAreaByPid=API_DOMAIN+"wondering_area/get/byprojectid",
    getProjectThread=API_DOMAIN+"project/thread/get/all",
    getBuildOn=API_DOMAIN+"buildon/get",
    getNoteViewRecord=API_DOMAIN+"note_view_record/get/all",
    getNoteAuthor=API_DOMAIN+"note/author/get/all",
    getThreadNote=API_DOMAIN+"thread/note/get/all",
    getThreadWonderingArea=API_DOMAIN+"thread/wondering_area/get",
    getThreadView=API_DOMAIN+"thread/view/get",
    getViewNote=API_DOMAIN+"view/note/get/all"
)


#Interact with ITM API
def ITMAPI(url,data):
    result = requests.post(url, json=data)
    if result.status_code == 200 and result.json()['code']== 'success':
                return(json.loads(result.json()['obj']))
    else:
                print('GET {} failed with code: {}'.format(url, result.status_code))
                return -1

def getNoteViewDict():
    data = ITMAPI(APIs.get("getViewNote"), values)
    output = {}
    if data!=-1:
        for d in data:
            output[d["note_id"]] = d
    return output
def getAllNote():
    #{note)id,title,content,offset, create_time,}
    return ITMAPI(APIs.get("getAllNote"),values)

def getAllProject():
    return ITMAPI(APIs.get("getAllProject"), values)

def getAllThread():
    #{id, threadfocus, author_id, keywords,resources,status}
    return ITMAPI(APIs.get("getAllThread"), values)

def getAllUser():
    return ITMAPI(APIs.get("getAllUser"), values)

def getAllView():
    #{view_id,title,author_id,creat_time}
    return ITMAPI(APIs.get("getAllView"), values)

def get_note_author():
    #{node_id: {author_id: ***,first_name:***,last_name:***}
    return ITMAPI(APIs.get("getNoteAuthor"), values)

def get_note_thread_base():
    # {thread_id,node_id}
    return ITMAPI(APIs.get("getThreadNote"), values)

def get_note_thread(thread=[]):
    if len(thread)==0:
        thread = getAllThread();


def get_thread_note():
    return ITMAPI(APIs.get("getThreadNote"), values)

def get_build_on():
    return  ITMAPI(APIs.get("getBuildOn"), values)

def get_note_view_record():
    return ITMAPI(APIs.get("getNoteViewRecord"),values)

def get_wonder_area_based_on_thread_id(thread_id):
    if "threadid" not in values or values["threadid"]=="" or values["threadid"]!=thread_id:
        values["threadid"]=thread_id
    data = ITMAPI(APIs.get("getThreadWonderingArea"), values)
    return data if data !=-1 else []


def get_note_author_dict(notes_authors):
    #{note_id:[note_author_info]}
    output ={}
    for note_author in notes_authors:
        if note_author["note_id"] in output:
            output[note_author["note_id"]].append(note_author)
        else:
            output[note_author["note_id"]] =[note_author]
    return output

def get_thread_dict(threads,project_thread_dict,view_thread_dict):
    output ={}
    for thread in threads:
        output[thread["id"]]={ "id":thread["id"],"title":thread["threadfocus"],"keywords":thread["keywords"], "status":thread["status"],"wondering_area":get_wonder_area_based_on_thread_id(thread["id"]),"project":project_thread_dict[thread["id"]] if thread["id"] in project_thread_dict else [],"view": view_thread_dict[thread["id"]] if thread["id"] in view_thread_dict else [],}
    return output


def get_note_dict(notes):
    output = {}
    for d in notes:
        output[d["note_id"]] = d
    return output

def get_project_thread_dict(data):
    output={}
    if data != -1:
        for d in data:
            output[d["thread_id"]]=d
    return  output


def get_note_thread_dict(threads_note, threads_dict):
    output = {}
    for thread_note in threads_note:
        if thread_note["note_id"] in output:
            output[thread_note["note_id"]].append(
                threads_dict[thread_note["thread_id"]] if thread_note["thread_id"] in threads_dict else "")
        else:
            output[thread_note["note_id"]] = [
                threads_dict[thread_note["thread_id"]] if thread_note["thread_id"] in threads_dict else ""]
    return output

def get_project_thread():
    return ITMAPI(APIs.get("getProjectThread"),values)

def get_thread_view_dict():
    data = ITMAPI(APIs.get("getThreadView"),values)
    output={}
    if data != -1:
        for d in data:
            if d["thread_id"] not in output:
                output[d["thread_id"]] = [d]
            else:
                output[d["thread_id"]].append(d)
        return output
    else:
        return []
def getUserDict(users):
    output = {}
    for d in users:
        output[d["str_id"]] = d
    return output

def readConfigurationFile(file,sheet):
    #file format :  [{name: fileName, url: fileUrl, last:range}]
    excel_data_df=pd.read_excel(file,sheet, index_col=None, na_values=['NA'])
    return excel_data_df.to_dict(orient='record')

def workFlow(kf_file,sheet):

    notes=getAllNote()
    threads=getAllThread()
    views=getAllView()
    users=getAllUser()
    note_user=get_note_author()
    threads_note=get_thread_note()
    note_view_records=get_note_view_record()
    build_on = get_build_on()
    thread_project =get_project_thread()


    thread_project_dict = get_project_thread_dict(thread_project)
    thread_view_dict =get_thread_view_dict()
    #{thread_id:thread}
    thread_dict=get_thread_dict(threads,thread_project_dict,thread_view_dict)
    # {note_id:note}
    note_dict =get_note_dict(notes)
    # {note_id:thread}
    threads_note_dict=get_note_thread_dict(threads_note,thread_dict);

    user_dict = getUserDict(users)
    note_author_dict = get_note_author_dict(note_user)
    note_view_dict=getNoteViewDict()

    KF_data = readConfigurationFile(kf_file, sheet)
    output = []
    kf_unique=[]
    for kf_note in KF_data:
        note_id=kf_note["ID"]
        if note_id in note_dict:
            note = note_dict[note_id]
            # list of author
            authors =""
            author_ids=""
            #get note_author and its ids
            for author in note_author_dict[note_id] if note_id in note_author_dict else []:
                authors+=author['first_name']+"_"+author['last_name']+"@"
                author_ids=author['str_id']+"@"
            note["authors"] = authors
            note["author_ids"] = author_ids
            thread_note_review={}
            #note_view_records based on thread
            if note_id in threads_note_dict:
                for thread in threads_note_dict[note_id]:
                    thread_note_review[thread["id"]]=[]
                    for record in note_view_records:
                        if record["note_id"]== str(note["id"]) and record["thread_id"] == thread["id"]:
                           if record["author_id"]  in user_dict:
                                thread_note_review[thread["id"]].append(user_dict[record["author_id"]])
                           else:
                               print("User not is not found, but it in the note_view_records " +record["author_id"] )

            note["thread_note_view"] = thread_note_review

            note["threads"] = threads_note_dict[note_id] if note_id in threads_note_dict else []

            build_on_to=""
            build_by=""
            for build_on_note in build_on:
                if build_on_note["from_note_id"] == note_id:
                    build_on_to+="@"+build_on_note["to_note_id"]
                if build_on_note["to_note_id"] == note_id:
                    build_by += "@" + build_on_note["from_note_id"]
            note["buildOn"]=build_on_to
            note["buildBy"]=build_by
            note["view"]= note_view_dict[note_id] if note_id in note_view_dict else []
            note["Body with scaffold"]=kf_note["Body with scaffold"]
            note["Scaffold(s)"]=kf_note["Scaffold(s)"]
            note["Created"]=kf_note["Created"]
            output.append(note)
        else:
            note={}
            note["ID"] = kf_note["ID"]
            note["Title"] =kf_note["Title"]
            note["Author(s)"] =kf_note["Authors"]
            note["AuthorID(s)"] =kf_note["AuthorID(s)"]
            note["text Body without scaffolds"] = ""
            note["text Body with scaffolds"]=kf_note["Body with scaffold"]
            note["Scaffold(s)"] = kf_note["Scaffold(s)"]
            note["Created"] = kf_note["Created"]
            note["viewTitle(s)"]=kf_note["Views (title)"]
            note["ViewID(s)"]=kf_note["ViewID(s)"]
            note["kf_problem"]=""
            note["kf_keywords"] = ""
            note["builton-by-note ID(s)"]=""
            note["buildon-to-note ID(s)"] = ""
            note["ThreadID(s)"] = ""
            note["ThreadTitle(s)"] = ""
            note["read-times"] = ""
            note["read_by_uid"] = ""
            note["read_by_user_name"] = ""
            note["area_id"] = ""
            note["area_name"] = ""
            note["project_id"] = ""
            note["project_title"] = ""
            kf_unique.append(note)

    final_data = convertToPlain(output) + kf_unique

    meta_data=["ID","Title","Author(s)","AuthorID(s)","text Body without scaffolds","text Body with scaffolds","Scaffold(s)","Created","ViewID(s)","viewTitle(s)","kf_problem","kf_keywords","builton-by-note ID(s)","buildon-to-note ID(s)","ThreadID(s)","ThreadTitle(s)","read-times","read_by_uid","read_by_user_name","area_id","area_name","project_id","project_title"]
    location="/Users/jonkiky/Documents/"
    file_name="2019-2020.csv"
    saveTOCSV(meta_data,final_data,location,file_name)



def convertToPlain(data):

    # data sample
    # {'note_id': '5ba8f91f502a7223616c7549', 'title': 'Why is moss colors',
    #  'content': '\n\n\n\n\n<p><br>&nbsp;&nbsp;<span id="5ba8fb79502a7223616c761f" class="KFSupportStart mceNonEditable"></span> - why moss has different colors and what it means to have all these different colors&nbsp;- <span id="5ba8fb79502a7223616c761f" class="KFSupportEnd mceNonEditable"></span>&nbsp;&nbsp;<br><br>&nbsp;&nbsp;<span id="5ba8fb79502a7223616c7622" class="KFSupportStart mceNonEditable"></span> - is maybe it means it is poisonous&nbsp;or it means that its a different type of moss - <span id="5ba8fb79502a7223616c7622" class="KFSupportEnd mceNonEditable"></span>&nbsp;&nbsp;</p>\n\n',
    #  'offset': None, 'create_time': '2018-09-24T14:47:58.015Z', 'modify_time': '2018-09-24T14:58:01.822Z',
    #  'count': None, 'status': 'active', 'id': 83, 'doc_id': None, 'reason': None, 'authors': 'Serena_Thomas@',
    #  'author_ids': '5b942247502a7223616c130a@', 'thread_note_view': {35: []}, 'threads': [
    #     {'id': 35, 'title': 'Moss', 'keywords': '', 'status': 'Active', 'wondering_area': [
    #         {'thread_id': 6, 'wondering_area_id': 6, 'id': 6, 'name': 'Open area', 'logo': '', 'keywords': '',
    #          'overarching_questions': '', 'why_important': '', 'author_id': '5b875a3945b8a02554df7341',
    #          'create_time': '2018-08-30T02:47:36.997Z', 'modify_time': None, 'status': 'accepted',
    #          'message': '@message'}], 'project': {'project_id': 7, 'thread_id': 35, 'title': 'Ecosystem-5Kenyon',
    #                                               'goal': "Let's learn ecology together!", 'school_year_from': '2018/9',
    #                                               'school_year_to': '2018/1'},
    #      'view': {'id': 25, 'thread_id': 35, 'view_id': '5ba8f535502a7223616c728a',
    #               'title': 'Ecology-5 Kenyon-Plants in the GES courtyard-Moss', 'author_id': '5b8fedff45b8a02554df75a4',
    #               'create_time': '2018-09-24T14:31:17.053Z'}}], 'buildOn': '',
    #  'buildBy': '@5ba8fde8502a7223616c7760@5bcde595e196dc4872d2ce38'}


    notes = []
    for note in data:
        output={}
        for thread in note["threads"]:
            output["ID"] = note["note_id"]
            output["Title"]=note["title"]
            output["Author(s)"]=note["authors"]
            output["AuthorID(s)"] = note["author_ids"]
            output["text Body without scaffolds"]=""
            output["text Body with scaffolds"]=note["Body with scaffold"]
            output["Scaffold(s)"]=note["Scaffold(s)"]
            view_id=""
            view_title=""
            for view in thread["view"]:
                view_id= view["view_id"]+"@"
                view_title=view["title"]+"@"
            output["ViewID(s)"]=view_id
            output["viewTitle(s)"] = view_title
            output["kf_problem"]=""
            output["kf_keywords"]=""
            output["Created"]=note["Created"]
            output["builton-by-note ID(s)"]=note["buildBy"]
            output["buildon-to-note ID(s)"] = note["buildOn"]
            output["ThreadID(s)"]=thread["id"]
            output["ThreadTitle(s)"] = thread["title"]

            read_by_uid=""
            read_by_user_name=""
            read_times=0
            if thread["id"] in note["thread_note_view"]:
                record = note["thread_note_view"][thread["id"]]
                read_times=len(note["thread_note_view"][thread["id"]])
                for d in record:
                    read_by_uid=read_by_uid+str(d['str_id'])+"@"
                    read_by_user_name = read_by_user_name + d['first_name'] +" "+d['last_name'] + "@"
            output["read-times"] = read_times
            output["read_by_uid"] = read_by_uid
            output["read_by_user_name"] = read_by_user_name
            area_id = ""
            area_name= ""
            for area in thread["wondering_area"]:
                area_id =area_id+str(area["wondering_area_id"])+"@"
                area_name = area_name + area["name"]+"@"

            output["area_id"]=area_id
            output["area_name"]=area_name

            project_id =thread["project"]["project_id"] if "project_id" in thread["project"] else ""
            project_title=thread["project"]["title"] if "title" in thread["project"] else ""

            output["project_id"] = project_id
            output["project_title"] = project_title

        for view in note["view"]:
            if view["view_id"] not in output["ViewID(s)"]:
                output["ViewID(s)"]=output["ViewID(s)"]+view["view_id"]+"@"
                output["viewTitle(s)"] = output["viewTitle(s)"] + view["title"]+"@"
        notes.append(output)
    return notes

def saveTOCSV(meta_data,data,location,file_name):
    with open(location + file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=meta_data)
        writer.writeheader()
        for d in data:
            writer.writerow(d)


if __name__ == '__main__':

    # code need to be restrucuted. workFlow's logic is twisted
    workFlow("./itm.xlsx","2019-2020")

