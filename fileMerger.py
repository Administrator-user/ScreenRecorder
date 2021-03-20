from moviepy.editor import *
import os

isMerging = False
def mergeFiles(output):
    isMerging = True
    try:
        #合并
        assert os.path.exists("./TempFiles/videoOutput.avi")
        assert os.path.exists("./TempFiles/soundOutput.avi")
        mergeVideo = VideoFileClip("TempFiles/videoOutput.avi")
        mergeAudio = AudioFileClip("TempFiles/soundOutput.wav")
        ratio = mergeAudio.duration/mergeVideo.duration
        mergeVideo = mergeVideo.fl_time(lambda t:t/ratio, apply_to=["mergeVideo"]).set_end(
            mergeAudio.duration)
        audioImplantedVideo = mergeVideo.set_audio(mergeAudio)
        resultVideo = CompositeVideoClip([audioImplantedVideo])
        resultVideo.write_videofile(output,codec="libx264")
        resultVideo.close()
        #删除缓存
        os.remove("TempFiles/soundOutput.wav")
        os.remove("TempFiles/videoOutput.avi")
    except Exception as exc:
        print(exc)
    isMerging = False
#加载合并
try:
    nameFile = open("TempFiles/videoNameTemp.tmp","r")
    nameFile.seek(0)
    videoName = nameFile.read()
except:
    videoName = "output.mp4"
mergeFiles(videoName)