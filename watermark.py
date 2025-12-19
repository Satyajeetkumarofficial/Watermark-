import subprocess

def watermark_video(input_video, output_video, text, logo, scale, position):

    pos = {
        "bottom-center": "x=(w-text_w)/2:y=h-text_h-20",
        "bottom-left": "x=20:y=h-text_h-20",
        "bottom-right": "x=w-text_w-20:y=h-text_h-20",

        "top-left": "x=20:y=20",
        "top-center": "x=(w-text_w)/2:y=20",
        "top-right": "x=w-text_w-20:y=20",

        "middle-left": "x=20:y=(h-text_h)/2",
        "center": "x=(w-text_w)/2:y=(h-text_h)/2",
        "middle-right": "x=w-text_w-20:y=(h-text_h)/2"
    }

    draw_pos = pos.get(position, pos["bottom-center"])

    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-i", logo,
        "-filter_complex",
        f"[1:v]scale=iw*{scale}/100:-1[wm];"
        f"[0:v][wm]overlay=W-w-20:H-h-20,"
        f"drawtext=text='{text}':"
        f"fontcolor=white@0.85:"
        f"fontsize=24:"
        f"{draw_pos}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_video
    ]

    subprocess.run(cmd, check=True)
