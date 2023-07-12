import re
from typing import Tuple
import requests
import argparse
import os
from tqdm import tqdm


def argparser() -> argparse.Namespace:
    """
    Parse the arguments from command line
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--url", type=str, required=True, help="URL of tsinghua cloud"
    )
    parser.add_argument("-s", "--save", type=str, default=".", help="save path")
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        default=None,
        help="file type downloaded, in regex. e.g. if you want to install all the .png files, use -t \.\*\.png",
    )
    parser.add_argument("-r", action="store_true", help="whether recursive downloading")
    return parser.parse_args()


def get_uid(url: str) -> str:
    """
    Get the uid from the url
    """
    match = re.search(r"/([a-zA-Z0-9]+)\/?$", url)
    if match:
        return match.group(1)
    else:
        print("invalid URL")
        exit(0)


def get_file_folder_list(url: str, path: str) -> Tuple[list, list]:
    """
    Get the file list from the url/path
    Return the list of file and folder: [file_list, folder_list]
    """
    resp = requests.get(
        url=url,
        params={"thumbnail_size": 48, "path": path},
    ).json()
    file_list = []
    folder_list = []
    for item in resp["dirent_list"]:
        if item["is_dir"]:
            folder_list.append(item["folder_path"])
        else:
            file_list.append(item["file_path"])
    return file_list, folder_list


def make_dir(dir_path: str) -> None:
    """
    Make the directory recursively
    """
    dir_list = dir_path.split("/")
    if dir_list[0] == "":
        dir_list[0] = "/"
    for i in range(1, len(dir_list)):
        dir_list[i] = dir_list[i - 1] + "/" + dir_list[i]
    for dir in dir_list:
        if not os.path.exists(dir):
            print("mkdir: ", dir)
            os.makedirs(dir)


def download(url: str, file_list: list, dir_path: str, type: str) -> None:
    """
    Download the files
    """
    if dir_path[-1] == "/":
        dir_path = dir_path[:-1]

    if type is not None:
        print("download type: ", type)
        file_list = [file for file in file_list if re.search(type, file)]

    for file_path in file_list:
        resp = requests.get(url, params={"p": file_path, "dl": 1}, stream=True)
        download_path = dir_path + file_path
        if not os.path.exists(os.path.dirname(download_path)):
            make_dir(os.path.dirname(download_path))
        with open(download_path, "wb") as f, tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=int(resp.headers["Content-Length"]),
            desc=download_path,
        ) as pbar:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))


if __name__ == "__main__":
    args = argparser()

    uid = get_uid(args.url)

    # Get the file list
    file_list_url = (
        "https://cloud.tsinghua.edu.cn/api/v2.1/share-links/" + uid + "/dirents"
    )
    file_list, folder_list = get_file_folder_list(file_list_url, "/")
    if args.r:
        while len(folder_list) > 0:
            folder = folder_list.pop()
            new_file_list, new_folder_list = get_file_folder_list(file_list_url, folder)
            file_list.extend(new_file_list)
            folder_list.extend(new_folder_list)

    download_url = "https://cloud.tsinghua.edu.cn/d/" + uid + "/files"

    download(download_url, file_list, args.save, args.type)
