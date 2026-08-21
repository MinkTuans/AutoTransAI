import pytest

def build_audio_timeline_filter(segments_data, total_video_duration):
    inputs = []
    filter_chain = []
    
    for idx, seg in enumerate(segments_data):
        inputs.extend(["-i", seg["path"]])
        delay_ms = max(0, round(seg["start_time"] * 1000))
        filter_chain.append(f"[{idx}:a]adelay=delays={delay_ms}:all=1[a{idx}]")

    num_segments = len(segments_data)
    if num_segments == 1:
        filter_graph = f"{filter_chain[0]};[a0]apad=whole_dur={total_video_duration:.2f}[outa]"
    else:
        mix_inputs = "".join(f"[a{i}]" for i in range(num_segments))
        filter_statements = ";".join(filter_chain)
        filter_graph = f"{filter_statements};{mix_inputs}amix=inputs={num_segments}:duration=longest:dropout_transition=0,apad=whole_dur={total_video_duration:.2f}[outa]"

    return inputs, filter_graph

def test_single_segment_filter():
    segs = [{"path": "seg1.wav", "start_time": 0.0}]
    inputs, fg = build_audio_timeline_filter(segs, 199.5)
    assert len(inputs) == 2
    assert "[0:a]adelay=delays=0:all=1[a0]" in fg
    assert "[0:a][1:a]adelay" not in fg
    assert "[a0]apad=whole_dur=199.50[outa]" in fg

def test_50_segments_filter():
    segs = [{"path": f"seg_{i}.wav", "start_time": i * 3.5} for i in range(50)]
    inputs, fg = build_audio_timeline_filter(segs, 199.5)
    assert len(inputs) == 100
    assert "[0:a]adelay=delays=0:all=1[a0]" in fg
    assert "[49:a]adelay=delays=171500:all=1[a49]" in fg
    assert "[0:a][1:a]adelay" not in fg
    assert "[a0][a1]" in fg
    assert "amix=inputs=50:duration=longest" in fg

def test_no_invalid_input_labels():
    segs = [{"path": f"seg_{i}.wav", "start_time": i * 2.0} for i in range(10)]
    _, fg = build_audio_timeline_filter(segs, 100.0)
    assert "[0:a][1:a]" not in fg
    assert "[1:a][2:a]" not in fg
