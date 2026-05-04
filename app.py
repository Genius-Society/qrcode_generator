import os
import time
import shutil
import requests
import gradio as gr

EN_US = os.getenv("LANG") != "zh_CN.UTF-8"
API_QR = os.getenv("api_qr")
if not API_QR:
    raise EnvironmentError("请检查环境变量 api_qr")

TMP_DIR = os.path.join(os.path.dirname(__file__), "__pycache__")
ZH2EN = {
    "二维码输出尺寸": "Image size",
    "输入文本": "Input text",
    "输出二维码": "QR code",
    "输入文字在线生成二维码": "Enter text to generate a QR code.",
    "状态栏": "Status",
    "二维码生成器": "QR Code Generator",
}


def _L(zh_txt: str):
    return ZH2EN[zh_txt] if EN_US else zh_txt


def clean_dir(dir_path: str):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    os.makedirs(dir_path)


def download_file(url, local_filename):
    clean_dir(os.path.dirname(local_filename))
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(local_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return local_filename


def infer(img_size: int, input_txt: str):
    status = "Success"
    img = None
    try:
        if (not input_txt) or input_txt == "0":
            raise ValueError("Please input valid text!")

        img = download_file(
            (
                f"{API_QR}/?size={img_size}x{img_size}&data={input_txt}"
                if EN_US
                else f"{API_QR}/?text={input_txt}&size={img_size}"
            ),
            f"{TMP_DIR}/qrcode.jpg",
        )

        time.sleep(0.1)

    except Exception as e:
        status = f"{e}"

    return status, img


def main():
    return gr.Interface(
        fn=infer,
        inputs=[
            gr.Slider(35, 1000, 217, label=_L("二维码输出尺寸")),
            gr.Textbox(label=_L("输入文本"), placeholder=_L("输入文字在线生成二维码")),
        ],
        outputs=[
            gr.Textbox(label=_L("状态栏"), buttons=["copy"]),
            gr.Image(label=_L("输出二维码"), buttons=["download", "fullscreen"]),
        ],
        flagging_mode="never",
        title=_L("二维码生成器"),
    )


if __name__ == "__main__":
    main().launch(css="#gradio-share-link-button-0 { display: none; }", ssr_mode=False)
