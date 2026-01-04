import sys
import os
import asyncio
import uiautomation as auto
from .save import save_txt
import re
from difflib import SequenceMatcher
from .transformation import word_to_number

last_full_text = ""

saved_sentences = []

current_sentences = {}  # {sentence: stable_count}

def longest_common_prefix(a: str, b: str) -> int:
    i = 0
    max_len = min(len(a), len(b))
    while i < max_len and a[i] == b[i]:
        i += 1
    return i

def normalize_sentence(s: str) -> str:
    s = s.strip()
    # space
    s = re.sub(r'\s+', ' ', s)
    # lower letter
    s = s.lower()
    # "twenty twenty six" -> "2026"
    s = word_to_number(s)
    # symbol
    s = re.sub(r'\s+([.,!?])', r'\1', s)
    return s

def similarity_ratio(s1: str, s2: str) -> float:
    """calculate the similarity"""
    norm1 = normalize_sentence(s1)
    norm2 = normalize_sentence(s2)
    return SequenceMatcher(None, norm1, norm2).ratio()

def is_already_saved(sentence: str, threshold: float = 0.85) -> bool:
    """check similarity"""
    for saved in saved_sentences:
        if similarity_ratio(sentence, saved) >= threshold:
            return True
    return False

def is_substantial_sentence(s: str) -> bool:
    s = s.strip()
    if len(s) < 5:  
        return False
    if re.match(r'^[^a-zA-Z0-9\u4e00-\u9fff]*$', s):  #only symbol
        return False
    # filter
    words = s.lower().strip('.!?').split()
    if len(words) <= 2 and words[0] in ['but', 'and', 'so', 'or', 'basically']:
        return False
    return True

def split_into_sentences(text: str):
    
    parts = re.split(r'([.!?。!?]+)(?=\s+[A-Z]|\s*$)', text)
    
    sentences = []
    i = 0
    while i < len(parts):
        if i + 1 < len(parts) and re.match(r'^[.!?。!?]+$', parts[i + 1]):
            sentence = (parts[i] + parts[i + 1]).strip()
            i += 2
        else:
            sentence = parts[i].strip()
            i += 1
        
        if sentence and is_substantial_sentence(sentence):
            sentences.append(sentence)
    
    return sentences

def is_better_version(new_sentence: str, old_sentence: str) -> bool:
    # length
    if len(new_sentence) > len(old_sentence):
        return True
    
    # words
    new_words = len(re.findall(r'\b\w+\b', new_sentence))
    old_words = len(re.findall(r'\b\w+\b', old_sentence))
    if new_words > old_words:
        return True
    
    # nums
    if re.search(r'\d{4}', new_sentence) and not re.search(r'\d{4}', old_sentence):
        return True
    
    return False

def find_and_replace_similar(sentence: str, threshold: float = 0.85):
    
    for i, saved in enumerate(saved_sentences):
        if similarity_ratio(sentence, saved) >= threshold:
            should_replace = is_better_version(sentence, saved)
            return (i, should_replace)
    
    return (None, False)


def lc_detect():
    try:
        auto.SetGlobalSearchTimeout(0.5)
        
        desktop = auto.GetRootControl()
        captions_window = desktop.Control(
            searchDepth=1,
            ClassName="LiveCaptionsDesktopWindow",
            timeout = 0.2
        )


        if captions_window.Exists(0):
            print ("Live Captions Found")
            return True
        else:
            print(f"Live Captions Not Found")
            return False

    except Exception as e:
        print(f"Live Captions Not Found: {str(e)[:50]}...")
        return False

def cleanup_file(filename: str):
    try:
        if not os.path.exists(filename):
            return
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return
        
        cleaned_lines = []
        i = 0
        
        while i < len(lines):
            current_line = lines[i].strip()
            
            if '[UPDATED]' in current_line:
                updated_group = [current_line]
                j = i + 1
                
                while j < len(lines):
                    next_line = lines[j].strip()
                    if '[UPDATED]' in next_line:
                        prev_content = updated_group[-1].replace('[UPDATED]', '').strip()
                        next_content = next_line.replace('[UPDATED]', '').strip()
                        
                        if similarity_ratio(prev_content, next_content) >= 0.80:
                            updated_group.append(next_line)
                            j += 1
                        else:
                            break
                    else:
                        break
                
                if len(updated_group) >= 1:
                    if cleaned_lines:
                        last_saved = cleaned_lines[-1].strip()
                        first_updated = updated_group[0].replace('[UPDATED]', '').strip()
                        
                        if similarity_ratio(last_saved, first_updated) >= 0.80:
                            cleaned_lines.pop()
                    
                    final_sentence = updated_group[-1].replace('[UPDATED]', '').strip()
                    cleaned_lines.append(final_sentence + '\n')
                
                
                i = j
            else:
                cleaned_lines.append(lines[i])
                i += 1
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        
        print(f"\n[CLEANUP] File cleaned: {filename}")
        print(f"  Original lines: {len(lines)}")
        print(f"  Cleaned lines: {len(cleaned_lines)}")
        print(f"  Removed: {len(lines) - len(cleaned_lines)} duplicate lines")
        
    except Exception as e:
        print(f"[CLEANUP ERROR] {e}")


async def hook(filename, exit_event):
    global last_full_text, saved_sentences, current_sentences

    STABLE_THRESHOLD = 5  
    MAX_SAVED_SENTENCES = 100  

    try:
        if not lc_detect():
            return False

        desktop = auto.GetRootControl()
        captions_window = desktop.Control(
            searchDepth=1,
            ClassName="LiveCaptionsDesktopWindow"
        )
        captions_scrollviewer = captions_window.Control(
            searchDepth=5,
            AutomationId="CaptionsScrollViewer",
            ClassName="ScrollViewer"
        )

        print("Start capture...")
        print(f"Settings: STABLE_THRESHOLD={STABLE_THRESHOLD}, MIN_LENGTH=10, SIMILARITY=0.85")

        while not exit_event.is_set():
            current_text = captions_scrollviewer.Name.strip()

            if not current_text:
                await asyncio.sleep(0.2)
                continue

            sentences = split_into_sentences(current_text)

            current_frame_sentences = set(sentences)

            new_current_sentences = {}
            
            for sentence in current_frame_sentences:
                similar_index, should_replace = find_and_replace_similar(sentence)
                
                if similar_index is not None:
                    if should_replace:
                        old_sentence = saved_sentences[similar_index]
                        saved_sentences[similar_index] = sentence
                        print(f"[REPLACE]")
                        print(f"  OLD: {old_sentence}")
                        print(f"  NEW: {sentence}")
                        await save_txt(filename, f"[UPDATED] {sentence}")
                    continue
                
                if sentence in current_sentences:
                    new_current_sentences[sentence] = current_sentences[sentence] + 1
                else:
                    new_current_sentences[sentence] = 1
                
                if new_current_sentences[sentence] >= STABLE_THRESHOLD:
                    print(f"[SAVE] {sentence}")
                    await save_txt(filename, sentence)
                    
                    saved_sentences.append(sentence)
                    
                    if len(saved_sentences) > MAX_SAVED_SENTENCES:
                        saved_sentences.pop(0)  
            
            current_sentences = new_current_sentences
            
            last_full_text = current_text

            await asyncio.sleep(0.25)

        for sentence, count in current_sentences.items():
            similar_index, _ = find_and_replace_similar(sentence)
            if similar_index is None and count >= 2:
                print(f"[SAVE-EXIT] {sentence}")
                await save_txt(filename, sentence)
        
        cleanup_file(filename)
        
        print("[EXIT] Done!")

    except Exception as e:
        print(f"Exceptions Caught: {e}")
        return False