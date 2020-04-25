import requests
import subprocess
import pandas as pd
import os
import threading

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}

# capture video,
# download video segments then save to a file.
def  captureVideo(url,last_index,output_location,out_file_nanme):
    #video segment name follows a name convention. ***1.ts/***2.ts
    for i in range(1,last_index+1):
        download_url = url+str(i)+".ts"
        result = requests.get(download_url, verify=False,stream=True,headers=HEADERS)
        print(result.status_code)
        if result.status_code == 200:
            saveToFile(result.content,output_location,out_file_nanme)
        else:
            print("erro: " + out_file_nanme)


def saveToFile(data,output_location,out_file_nanme):
    print("write to : "+out_file_nanme)
    with open(output_location + out_file_nanme, 'ab') as file:
        file.write(data)

# convert TS file to MP4
def convertTsToMP4(input,output):
    print("convert to : " + output)
    subprocess.run(['ffmpeg', '-i', input, output])



def readConfigurationFile(file):
    #file format :  [{name: fileName, url: fileUrl, last:range}]
    excel_data_df=pd.read_excel(file,'Sheet1', index_col=None, na_values=['NA'])
    return excel_data_df.to_dict(orient='record')


def workflow(download_location,output_location,configs):
    for config in configs:
        # Strean video split into segments.
        # download all segments , then merge into one ts file.

        # download link
        url = config['url']
        # number of video segment
        last_index = config['last']
        # merged file name
        file_name = config['name'].replace(" ", "_") + ".ts"
        # output file name
        output_file_name = config['name'].replace(" ", "_") + ".mp4"

        input = download_location + file_name
        output = output_location + output_file_name

        if not os.path.exists(output):
            captureVideo(url, last_index, download_location, file_name)
            convertTsToMP4(input, output)
        else:
            print("skip " + output_file_name)

def main():
    # captured video will save in here.
    download_location = "/Users/jonkiky/Documents/Pilates/save/"
    # Output location for transferred (MP4）video
    output_location= "/Users/jonkiky/Documents/Pilates/output/"
    #read configuration file
    # [{name: fileName, url: fileUrl, last:range}]
    configs = readConfigurationFile('./video.xlsx')
    print(len(configs))
    for index in range(1):

        start = int(index*len(configs)/1)
        end=int((index+1) * len(configs)/1)
        print("thread "+str(index))
        print(start)
        print(end)
        x = threading.Thread(target=workflow, args=(download_location,output_location,configs[start:end],))
        x.start()


if __name__ == '__main__':
    main()