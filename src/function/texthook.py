import sys
import os
import asyncio
import uiautomation as auto
from .save import save_txt
import re

buffer = "none"  
processed_sentences = set()


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



async def hook(filename,exit_event):
    global exit_flag
    incomplete_sentence = ""
    try:
        lc_flag=lc_detect()
        if (lc_flag):
            desktop = auto.GetRootControl()
            captions_window = desktop.Control(searchDepth=1, ClassName="LiveCaptionsDesktopWindow")
            captions_scrollviewer = captions_window.Control(searchDepth=5, AutomationId="CaptionsScrollViewer", ClassName="ScrollViewer")
        else:
            return False
        
        print("Start capture...")
        
        while not exit_event.is_set():
            
            global buffer
            
            current_text = captions_scrollviewer.Name.strip()
            
            if current_text and current_text != buffer:
                buffer = current_text
                sentences = re.split(r'([。！？.!?])', buffer)
                complete_sentences = []

                for i in range(0, len(sentences) - 1, 2):
                    sentence = sentences[i] + sentences[i + 1]
                    sentence = sentence.strip()
                        
                    if sentence and sentence not in processed_sentences:
                        complete_sentences.append(sentence)
                        processed_sentences.add(sentence)
                        print(f"Saving sentence: {sentence}")  
                        await save_txt(filename, sentence)
                
                if len(sentences) % 2 == 1 and sentences[-1].strip():
                    incomplete_sentence = sentences[-1].strip() 
                    
            await asyncio.sleep(0.2)        
            
        if incomplete_sentence:
            print(f"Last incomplete sentence: {incomplete_sentence}") 
            await save_txt(filename,incomplete_sentence)
        
    except Exception as e:
        if incomplete_sentence:
            await save_txt(filename, incomplete_sentence)
            print(f"Saving incomplete sentence before exit: {incomplete_sentence}")
        print(f"Exceptions Caught: {e}")
        return False
        