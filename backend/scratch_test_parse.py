import sys
import json
from pathlib import Path
sys.path.append('c:/Hack/AutoTransAI/backend')

from app.services.video_translator.stt_parser import parse_gemini_stt_response

text = """{"language": "Chinese", "segments": [{"start_time": 0.0, "end_time": 4.19, "speaker_id": "Speaker 1", "text": "谁噗噗我家哥哥，我哥哥的手腕十个魔鬼抓住了，要我家哥哥遇害了，我捶要他出来"}, {"start_time": 4.19, "end_time": 7.99, "speaker_id": "Speaker 2", "text": "她都不管我家哥哥，有一句话叫做，你没有经历过别人的痛"}, {"start_time": 7.99, "end_time": 8.79, "speaker_id": "Speaker 3", "text": "好"}, {"start_time": 8.79, "end_time": 10.19, "speaker_id": "Speaker 3", "text": "我不敢"}, {"start_time": 11.97, "end_time": 15.07, "speaker_id": "Speaker 3", "text": "就因为你没有体会过，所以你可以站在一个旁观者的角度，然后就去批判他"}, {"start_time": 15.71, "end_time": 19.31, "speaker_id": "Speaker 2", "text": "因为他从来没有见过那种人间惨剧，所以他觉得，你可以站在一个旁观者的角度"}, {"start_time": 19.96, "end_time": 24.56, "speaker_id": "Speaker 3", "text": "小将去说教，如果你见过满目苍夷，你见过于飞的人，如果把你放在那个位置上，也许你还没有他做得好"}, {"start_time": 26.31, "end_time": 28.31, "speaker_id": "Speaker 2", "text": "我可以包容这世界所有的罪恶"}, {"start_time": 28.53, "end_time": 30.13, "speaker_id": "Speaker 3", "text": "这叫不叫慷他人之慨"}, {"start_time": 30.73, "end_time": 33.13, "speaker_id": "Speaker 2", "text": "你没有经历过别人经历过的事情，就不要去劝别人大度"}, {"start_time": 33.73, "end_time": 37.13, "speaker_id": "Speaker 2", "text": "你没有经历过别人的苦难，你就不要去当圣母，站在道德的制高点去批判别人"}, {"start_time": 38.33, "end_time": 39.73, "speaker_id": "Speaker 2", "text": "小三，看招"}, {"start_time": 41.59, "end_time": 44.89, "speaker_id": "Speaker 4", "text": "小三，老子拼了命也要跟你同归于尽"}, {"start_time": 45.36, "end_time": 47.16, "speaker_id": "Speaker 5", "text": "这是对他人苦难最大的亵渎"}, {"start_time": 47.16, "end_time": 50.46, "speaker_id": "Speaker 2", "text": "因为这个世界上，有太多事情是没办法感同身受的，只有针扎在自己身上，你才知道有多痛"}, {"start_time": 50.46, "end_time": 52.86, "speaker_id": "Speaker 5", "text": "小三，不要站在你的角度来批判我，你没有资格"}, {"start_time": 52.86, "end_time": 54.46, "speaker_id": "Speaker 2", "text": "因为你没有经历过，所以你不懂"}, {"start_time": 58.15, "end_time": 59.95, "speaker_id": "Speaker 4", "text": "停下，留下你们的手势。"}]}"""

try:
    res = parse_gemini_stt_response(text)
    print(f"SUCCESS: {len(res['segments'])} segments")
except Exception as e:
    print("FAILED")
    print(e)
