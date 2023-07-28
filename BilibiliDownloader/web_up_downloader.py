import requests
from typing import List, Tuple
from tqdm import tqdm
import os
import argparse
import json


def argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--avid", type=str, help="The video avid")
    parser.add_argument("-b", "--bvid", type=str, help="The video bvid")
    parser.add_argument(
        "--path", type=str, default=".", help="The path to save the video"
    )
    parser.add_argument("--qn", type=int, default=64, help="The quality of the video")
    parser.add_argument("--fnval", type=int, default=1, help="The fnval of the video")
    parser.add_argument("--fourk", type=int, default=0, help="Whether the video is 4k")
    parser.add_argument(
        "--cookie", type=str, default=None, help="The cookie of the user"
    )
    parser.add_argument(
        "--all", action="store_true", help="Whether to download all the videos"
    )
    return parser.parse_args()


def make_dir(dir_path: str) -> None:
    """
    Make the directory

    Args:
        dir_path: The path of the directory

    Returns:
        None
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


def get_video_ptitle_cid(vid: str, is_bvid: bool = True) -> Tuple[List[str], List[int]]:
    """
    Get the ptitle and cid of the video.

    Args:
        vid: The video id.
        is_bvid: Whether the vid is a bvid.

    Returns:
        The cid of the video.
    """
    if is_bvid:
        url = f"https://api.bilibili.com/x/player/pagelist?bvid={vid}"
    else:
        url = f"https://api.bilibili.com/x/player/pagelist?aid={vid}"
    response = requests.get(url)
    response.raise_for_status()
    title_list = [page["part"] for page in response.json()["data"]]
    cid_list = [page["cid"] for page in response.json()["data"]]
    return title_list, cid_list


def get_video(
    vid: str,
    cid: int,
    file_name: str,
    is_bvid: bool = True,
    qn: int = 16,
    fnval: int = 1,
    fourk: int = 0,
    cookie: str = None,
    path: str = ".",
) -> None:
    """
    Get the video.

    Args:
        vid: The video id.
        cid: The cid of the video.
        file_name: The file name of the video.
        is_bvid: Whether the vid is a bvid.
        qn: The quality of the video.
        fnval: The fnval of the video.
        fourk: Whether the video is 4k.
        cookie: The cookie of the user.
        path: The path to save the video.

    Returns:
        None.
    """
    if path[-1] == "/":
        path = path[:-1]
    if not os.path.exists(os.path.dirname(path)):
        make_dir(os.path.dirname(path))

    if is_bvid:
        url = f"https://api.bilibili.com/x/player/playurl?bvid={vid}&cid={cid}&qn={qn}&fnval={fnval}&fourk={fourk}"
    else:
        url = f"https://api.bilibili.com/x/player/playurl?avid={vid}&cid={cid}&qn={qn}&fnval={fnval}&fourk={fourk}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        "referer": "https://www.bilibili.com",
    }
    if cookie:
        headers["cookie"] = cookie
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(url)

    if fnval & 1:
        video_url = response.json()["data"]["durl"][0]["url"]
        response = requests.get(
            video_url, headers=headers, stream=True
        )
        path = path + f"/{file_name}.mp4"

        with open(path, "wb") as f, tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=int(response.headers["Content-Length"]),
            desc=path,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    if fnval & 16:
        audio_url = response.json()["data"]["dash"]["audio"][0]["baseUrl"]
        video_url = response.json()["data"]["dash"]["video"][0]["baseUrl"]

        response = requests.get(
            audio_url, headers=headers, stream=True
        )
        path_audio = path + "/audio.m4s"
        with open(path_audio, "wb") as f, tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=int(response.headers["Content-Length"]),
            desc=path_audio,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        response = requests.get(
            video_url, headers=headers, stream=True
        )
        path_video = path + "/video.m4s"
        with open(path_video, "wb") as f, tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=int(response.headers["Content-Length"]),
            desc=path_video,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        try:
            print(f"ffmpeg -i {path}/video.m4s -i {path}/audio.m4s -c:v copy -c:a copy -f mp4 {path}/{file_name}.mp4")
            os.system(
                f"ffmpeg -i {path}/video.m4s -i {path}/audio.m4s -c:v copy -c:a copy -f mp4 {path}/{file_name}.mp4"
            )
            os.system(f"rm -f {path}/video.m4s {path}/audio.m4s")
        except:
            print("ffmpeg error")


if __name__ == "__main__":
    args = argparser()
    if args.cookie is None:
        with open("BiLiBiLiDownloader/config.json", "r") as f:
            config = json.load(f)
        args.cookie = config["cookie"]

    if args.bvid:
        ptitle_list, cid_list = get_video_ptitle_cid(args.bvid)
        if not args.all:
            ptitle_list = ptitle_list[:1]
            cid_list = cid_list[:1]
        for idx, cid in enumerate(cid_list):
            get_video(
                args.bvid,
                cid,
                file_name=ptitle_list[idx],
                is_bvid=True,
                qn=args.qn,
                fnval=args.fnval,
                fourk=args.fourk,
                cookie=args.cookie,
                path=args.path,
            )
    elif args.avid:
        ptitle_list, cid_list = get_video_ptitle_cid(args.avid, is_bvid=False)
        if not args.all:
            ptitle_list = ptitle_list[:1]
            cid_list = cid_list[:1]
        for idx, cid in enumerate(cid_list):
            get_video(
                args.avid,
                cid,
                file_name=ptitle_list[idx],
                is_bvid=False,
                qn=args.qn,
                fnval=args.fnval,
                fourk=args.fourk,
                cookie=args.cookie,
                path=args.path,
            )
    else:
        print("Please input the avid or bvid")
