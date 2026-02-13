import sys
import os
import shutil
import yt_dlp
from pydub import AudioSegment

def download_videos(singer_name, num_videos):
    """Downloads N videos from YouTube based on the singer's name."""
    temp_dir = "temp_mashup_downloads"
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Searching and downloading {num_videos} videos for '{singer_name}'...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True, 
        'extract_audio': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch{num_videos}:{singer_name}"])
        print("Download complete!")
        return temp_dir
    except Exception as e:
        print(f"An error occurred during downloading: {e}")
        sys.exit(1)

def process_and_merge_audio(temp_dir, duration, output_filename):
    """Removes the first Y seconds and keeps the rest of each file, then merges them."""
    print(f"Removing the first {duration} seconds and keeping the rest of each audio file...")
    merged_audio = AudioSegment.empty()
    
    try:
        for filename in os.listdir(temp_dir):
            if filename.endswith((".webm", ".m4a", ".mp3")):
                filepath = os.path.join(temp_dir, filename)
                
                # Load the audio file
                audio = AudioSegment.from_file(filepath)
                
                # THIS IS THE UPDATED CUTTING LINE:
                # audio[X:] means "Start at X milliseconds and keep everything until the end"
                cut_audio = audio[duration * 1000:]
                
                # Append to the final mashup
                merged_audio += cut_audio
                
        # Export the final file
        print("Merging all cut audios into a single output file...")
        merged_audio.export(output_filename, format="mp3")
        print(f"Success! Mashup saved to {output_filename}")
        
    except Exception as e:
        print(f"Error during audio processing: {e}. Make sure FFmpeg is installed and in your PATH.")
    finally:
        # Clean up the temporary folder
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("--- Mashup Program Started ---") 
    
    # Check for correct number of parameters
    if len(sys.argv) != 5:
        print("Error: Incorrect number of parameters.")
        print('Usage: python <Rollnumber>.py "<SingerName>" <NumberOfVideos> <AudioDuration> <OutputFileName>')
        sys.exit(1)

    singer_name = sys.argv[1]
    
    try:
        num_videos = int(sys.argv[2])
        audio_duration = int(sys.argv[3])
        output_filename = sys.argv[4]

        # Validate assignment constraints
        if num_videos <= 10:
            print("Error: The number of videos (N) must be greater than 10.")
            sys.exit(1)
            
        if audio_duration <= 20:
            print("Error: The audio duration (Y) must be greater than 20 seconds.")
            sys.exit(1)
            
        # Execute Steps
        temp_directory = download_videos(singer_name, num_videos)
        process_and_merge_audio(temp_directory, audio_duration, output_filename)

    except ValueError:
        print("Error: <NumberOfVideos> and <AudioDuration> must be valid integers.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(1)