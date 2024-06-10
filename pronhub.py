import os
import shutil  
import requests
import json
import re  
import concurrent.futures  

# 设置代理，这里以 HTTP 代理为例  
proxies = {  
  "http": "http://your_proxy_ip:port",  
  "https": "https://your_proxy_ip:port",  
}  

class Pronhub():
    def __init__(self) -> None:
        self.username=''    
        self.password=''   
        self.cdn_url = '' 
        self.base_file_path = 'D:\\download' 
         
         


    # 获取·到下载列表
    def get_video_list(self,url):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'cookie': 'ua=e95fb8733ac3417b3aa284b34753f35d; platform=pc; bs=t7hzc8hfhrypgz3exwyiuq3mf0ucumpc; bsdd=t7hzc8hfhrypgz3exwyiuq3mf0ucumpc; ss=808305888140373452; fg_afaf12e314c5419a855ddc0bf120670f=24599.100000; fg_7d31324eedb583147b6dcbea0051c868=66008.100000; __s=6665BB8B-42FE722901BBD369A-2609EBEB; __l=6665BB8B-42FE722901BBD369A-2609EBEB; accessAgeDisclaimerPH=1; _gid=GA1.2.1765804021.1717943194; etavt={"66481743266e7":"1_24_2_NA|0"}; likedVideosTooltipHide=1; _ga_B39RFFWGYY=GS1.1.1717943197.1.1.1717943235.22.0.0; _ga=GA1.1.227821447.1717943194',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://cn.pornhub.com/?utm_source=pronhub.com&utm_medium=redirects&utm_campaign=tldredirects',
            'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-full-version': '"125.0.2535.67"',
            'sec-ch-ua-full-version-list': '"Microsoft Edge";v="125.0.2535.67", "Chromium";v="125.0.6422.112", "Not.A/Brand";v="24.0.0.0"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'
            }

        response = requests.request("GET", url, headers=headers, data={})
        
        html_text = response.text

        lines = html_text.split('\n')  # 按行分割文本  

        json_mediaDefinitions = None
        for i, line in enumerate(lines):  
            if '"isVR"' in line:  
                # 找到"isVR"，返回该行和它在文本中的索引（基于行）  
                index = line.find('"isVR"')  # 查找"isVR"的索引  
                line_text = line[index:]
                line_text = line_text.replace('};','}')
                line_text = line_text.replace('"isVR"','{"isVR"')
                json_data = json.loads(line_text)
                json_mediaDefinitions = json_data['mediaDefinitions']
                for item in json_mediaDefinitions:
                    # item['title'] = json_data['title']
                    item.setdefault('title', json_data['video_title'])  


        return json_mediaDefinitions 





    #单个视频下载 
    def down_sigle(self,file_path,url,video_id):
        print(f'm3u8_url=\n{url}')
        self.cdn_url = self.remove_last_slash_and_after(url)
        response = requests.request("GET", url, headers={}, data={}).text
        urls = self.read_m3u8(response)
        target_file_path = f"{self.base_file_path}/{video_id}/m3u8"
        if not os.path.exists(target_file_path):  
            os.makedirs(target_file_path)  
        for _url in  (urls):  
            print(file_path)
            m3u8_response = requests.request("GET",_url, headers={}, data={}).text
            ts_urls = self.read_m3u8(m3u8_response)
            
            self.download_files_multithreaded(ts_urls, target_file_path)

            self.merge_ts_files(target_file_path,f'{self.base_file_path}/{video_id}.ts')


    def sort_key(self,filename):  
        # 假设文件名形如 "file_001.ts", "file_002.ts" 等  
        match = re.search(r'(\d+)\.ts$', filename)  
        if match:  
            return int(match.group(1))  # 将文件名中的数字部分转换为整数用于排序  
        else:  
            return float('inf')  # 如果不是预期的格式，则放在排序的末尾  
    
    def merge_ts_files(self,input_dir, output_file):  
        # 确保输出文件不存在，如果存在则删除  
        if os.path.exists(output_file):  
            os.remove(output_file)  
    
        # 打开输出文件以追加模式（'ab'）写入  
        with open(output_file, 'ab') as outfile:  
            # 遍历输入目录中的所有文件，并对文件名进行排序  
            filenames = sorted(os.listdir(input_dir), key=self.sort_key)  
            for filename in filenames:  
                print(f'合并中----—{filename}')
                if filename.endswith('.ts'):  
                    # 构造文件的完整路径  
                    filepath = os.path.join(input_dir, filename)  
                    # 打开当前.ts文件并读取其内容  
                    with open(filepath, 'rb') as readfile:  
                        # 将内容写入输出文件  
                        shutil.copyfileobj(readfile, outfile) 

    def download_files_multithreaded(self,ts_urls, target_file_path):  
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:  # 限制最大工作线程数为5  
            futures = []  
            for index, ts_url in enumerate(ts_urls):  
                filename = f'{target_file_path}/{index}.ts'  
                future = executor.submit(self.download_file, ts_url, filename)  
                futures.append(future)  
    
            # 等待所有任务完成（可选）  
            for future in concurrent.futures.as_completed(futures):  
                try:  
                    # 获取任务的结果（如果有的话）  
                    result = future.result()  
                    # 注意：在这个例子中，download_file没有返回值，所以result是None  
                except Exception as exc:  
                    print(f"Generated an exception for {future.filename}: {exc}") 

    """  
    下载文件并保存到本地  
    """  
    def download_file(self,url, file_name):  
        print(f'下载ing {file_name}')
        response = requests.get(url, stream=True)  
        response.raise_for_status()  # 如果请求失败，则抛出HTTPError异常  
    
        with open(file_name, 'wb') as f:  
            for chunk in response.iter_content(chunk_size=8192):  
                f.write(chunk)  

    def remove_last_slash_and_after(self,url):  
        # 使用rsplit来从右边开始分割字符串，并只分割一次  
        # 这样我们可以得到最后一个'/'之前的部分  
        parts = url.rsplit('/', 1)  
        if len(parts) > 1:  
            # 如果存在'/'，则返回最后一个'/'之前的部分  
            return parts[0]  
        else:  
            # 如果不存在'/'，或者整个字符串就是'/'，则返回原始字符串  
            return url

    def read_m3u8(self,text):
        url_array = []
        text_lines = text.split('\n')  # 按行分割文本  
        for line in text_lines:  
            if not line.startswith('#') and len(line) > 0:  
                url_array.append(self.cdn_url + '/' +line)
        return url_array


    #多个视频下载 
    def main(self,url,path='.'):
        match = re.search(r'viewkey=(.+?)(&|$)', url)  
        video_id = match.group(1)
        array = self.get_video_list(url)
        for item in array:
            if not isinstance(item['quality'],list) and item['quality'] == '720':
             self.down_sigle(os.path.join(self.base_file_path,item['quality']+'.ts'),item['videoUrl'],video_id)
        pass

# 调用主程序
if __name__ == "__main__":  
    url = 'https://cn.pornhub.com/view_video.php?viewkey=66481743266e7'
    pronhub = Pronhub()   
    pronhub.main(url)
