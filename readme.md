# 爬虫

## 环境配置

我们推荐您使用 `python3.10`：

```shell
conda create -n crawler python=3.10
conda activate crawler
pip install -r requirements.txt
```

## 项目说明

### 清华云盘下载器

见 `TsinghuaCloudDownloader`

参数说明：
- -r: 可选项，表示递归下载文件夹下所有文件；
- -u <URL>: 必选项，填入清华云盘文件夹的共享链接；
- -s <SAVE_PATH>: 可选项，下载地址，默认为执行脚本时的目录地址；
- -t <TYPE>: 可选项，下载文件类型。为了增加灵活性，`TYPE` 应为合法的正则表达式。若您不熟悉正则表达式：
  - 可以使用 `ChatGPT` 等工具自动生成；
  - 简单的，若您希望下载所有 `.png` 类型的文件，可以使用 `-t \.\*\\\.png`，其中 `\` 为转义字符，其正则表达式的 `pattern` 实际是 `.*\.png`

您也可以使用 `python TsinghuaCloudDownloader/downloader.py -h` 来查看所有参数说明。

例如，您希望下载 `https://cloud.tsinghua.edu.cn/d/ba64d0debd0e4ad4bf92/` 文件下的所有 `.md` 文件，保存在 `./sql/` 目录下，可使用：

```shell
python TsinghuaCloudDownloader/downloader.py -r -u https://cloud.tsinghua.edu.cn/d/ba64d0debd0e4ad4bf92/ -s sql -t \.\*\\\.png
```

### Bilibili 下载器

见 `BiliiliDownloader`，本模块仅供暑培课程使用，请使用更成熟的开源项目。

#### 网页端 UP 主视频下载

参数说明：
- -a: avid;
- -b: bvid;
- --path <PATH>: 
- --qn <QN>;
- --fnval <FNVAL>;
- --fourk <FOURK>;
- --cookie <COOKIE>;
- --all: 可选项，下载当前视频的所有分 P。

具体参数含义说明请参考 [BAC Document](https://socialsisteryi.github.io/bilibili-API-collect/docs/video/videostream_url.html#视频流url)

使用前请在 `BilibiliDownloader/` 内新建 `config.json`，格式为：

```json
{
  "cookie": "xxxx"
}
```

### 知乎爬虫

见 `Zhihu`，相关内容可直接查看文件并自行根据需要修改代码。