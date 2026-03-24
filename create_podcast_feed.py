from feedgen.feed import FeedGenerator
import json
from datetime import datetime, timezone
import os
import argparse
from urllib.parse import urlparse

def create_podcast_feed(talks_file: str, output_file: str, year: int):
    # Load the talks data
    with open(talks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create feed generator
    fg = FeedGenerator()
    fg.load_extension('podcast')

    # Set feed metadata
    fg.title(f'Migraine World Summit {year}')
    fg.description(f'Expert interviews and discussions from the Migraine World Summit {year}')
    fg.link(href=f'https://migraineworldsummit.com/summit/{year}-summit/')
    fg.language('en')
    fg.pubDate(datetime.now(timezone.utc))
    fg.image(data['logo_url'])
    
    # Add each talk as an episode
    for talk in data['talks']:
        fe = fg.add_entry()
        
        # Set episode title and description
        fe.title(talk['title'])
        description = f"Presenter: {talk['presenter_name']}\n"
        if talk['presenter_role']:
            description += f"Role: {talk['presenter_role']}\n"
        if talk['institution']:
            description += f"Institution: {talk['institution']}\n"
        if talk['key_questions']:
            description += "\nKey Questions:\n" + "\n".join(f"- {q}" for q in talk['key_questions'])

        # Add media file: prefer full audio, then 30-min audio, then full video
        media_url = (talk['media_links']['audio_full']
                     or talk['media_links']['audio_30min']
                     or talk['media_links']['video_full'])
        if media_url:
            mime_type = 'video/mp4' if media_url == talk['media_links']['video_full'] else 'audio/mpeg'
            fe.enclosure(media_url, 0, mime_type)
        elif talk.get('talk_url'):
            description += f"\n\n[Video only — watch on the website: {talk['talk_url']}]"

        fe.description(description)

        # Add presenter image
        if talk['presenter_image']:
            fe.podcast.itunes_image(talk['presenter_image'])

        # Add talk page link
        if talk.get('talk_url'):
            fe.link(href=talk['talk_url'])

        # Add publication date (use current date if not available)
        fe.pubDate(datetime.now(timezone.utc))

        # Add GUID (use media URL or talk URL or title)
        guid = media_url or talk.get('talk_url') or talk['title']
        fe.guid(guid)
        
        # Add duration if available (you might need to extract this from the audio file)
        # fe.podcast.itunes_duration('01:00:00')
    
    # Generate the feed
    fg.rss_file(output_file)
    print(f"Podcast feed generated: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate podcast feed from Migraine World Summit talks')
    parser.add_argument('--year', type=int, default=2026, help='Summit year (default: 2026)')
    args = parser.parse_args()

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define input and output paths
    talks_file = os.path.join(script_dir, 'talks.json')
    output_file = os.path.join(script_dir, f'mws{args.year}_podcast.xml')

    # Create the podcast feed
    create_podcast_feed(talks_file, output_file, args.year)

if __name__ == "__main__":
    main() 