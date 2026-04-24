import os, subprocess, re
from vars import CREDIT
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message

#======================================================================
def get_youtube_video_id(url):
    patterns = [
        r'(?:[?&]v=|v%3D)([A-Za-z0-9_-]{11})',
        r'youtu\.be\/([A-Za-z0-9_-]{11})',
        r'youtube(?:-nocookie)?\.com\/embed\/([A-Za-z0-9_-]{11})',
        r'youtube(?:-nocookie)?\.com\/shorts\/([A-Za-z0-9_-]{11})',
        r'youtube(?:-nocookie)?\.com\/live\/([A-Za-z0-9_-]{11})',
        r'youtube\.com\/watch\?.*?v=([A-Za-z0-9_-]{11})',
        r'([A-Za-z0-9_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None
#===========================================================================================================================
def extract_names_and_urls(file_content):
    lines = file_content.strip().split("\n")
    data = []
    for line in lines:
        if ":" in line:
            name, url = line.split(":", 1)
            data.append((name.strip(), url.strip()))
    return data

#===========================================================================================================================
def extract_title(text):
    text = text.strip()
    if not text.startswith(("(", "[")):
        return "Untitled", text or "Untitled"
    pair = {"(": ")", "[": "]"}
    open_b = text[0]
    close_b = pair[open_b]
    stack = []
    for idx, char in enumerate(text):
        if char == open_b:
            stack.append(char)
        elif char == close_b:
            stack.pop()
        if not stack:
            topic = text[1:idx].strip()
            title = text[idx+1:].strip()
            return topic or "Untitled", title or "Untitled"
    return "Untitled", text or "Untitled"

#===========================================================================================================================
def organize_by_subject(urls):
    subjects = {}
    for name, url in urls:
        topic, title = extract_title(name)
        if topic not in subjects:
            subjects[topic] = []
        subjects[topic].append((title, url))
    return subjects

#===========================================================================================================================
def categorize_urls(urls):
    videos = []
    pdfs = []
    others = []
    for name, url in urls:
        if ("akamaized.net/" in url or "1942403233.rsc.cdn77.org/" in url) and ".pdf" not in url:
            new_url = f"https://www.khanglobalstudies.com/player?src={url}"
            videos.append((name, new_url))
        elif "youtu" in url:
            video_id = get_youtube_video_id(url)
            new_url = f"https://yewtu.be/embed/{video_id}"
            url = f"{new_url}"
            videos.append((name, url))
        elif ".m3u8" in url or ".mp4" in url or ".mpd" in url:
            videos.append((name, url))
        elif ".pdf" in url and "utkarshapp" not in url and "cwmediabkt99" not in url and "crwilladmin" not in url:
            new_url = f"https://docs.google.com/viewer?url={url}&embedded=true"
            url = f"{new_url}"
            pdfs.append((name, url))
        elif ".pdf" in url and ("utkarshapp" in url or "cwmediabkt99" in url or "crwilladmin" in url):
            pdfs.append((name, url))
        else:
            others.append((name, url))
    return videos, pdfs, others

#===========================================================================================================================

def generate_subject_html(file_name, subjects):
    name = os.path.splitext(file_name)[0]
    
    # First, categorize each subject's items
    categorized_subjects = {}
    for subject, items in subjects.items():
        videos = []
        pdfs = []
        others = []
        for title, url in items:
            if ("akamaized.net/" in url or "1942403233.rsc.cdn77.org/" in url) and ".pdf" not in url:
                new_url = f"https://www.khanglobalstudies.com/player?src={url}"
                videos.append((title, new_url))
            elif "youtu" in url:
                video_id = get_youtube_video_id(url)
                new_url = f"https://yewtu.be/embed/{video_id}"
                url = f"{new_url}"
                videos.append((title, url))
            elif ".m3u8" in url or ".mp4" in url or ".mpd" in url:
                videos.append((title, url))
            elif ".pdf" in url and "utkarshapp" not in url and "cwmediabkt99" not in url and "crwilladmin" not in url:
                new_url = f"https://docs.google.com/viewer?url={url}&embedded=true"
                url = f"{new_url}"
                pdfs.append((title, url))
            elif ".pdf" in url and ("utkarshapp" in url or "cwmediabkt99" in url or "crwilladmin" in url):
                pdfs.append((title, url))
            else:
                others.append((title, url))
        categorized_subjects[subject] = {
            'videos': videos,
            'pdfs': pdfs,
            'others': others
        }
    
    # Generate folder structure HTML
    subjects_menu = ""
    folders_content = ""
    
    for i, (subject, categories) in enumerate(categorized_subjects.items()):
        # Subject folder button
        subjects_menu += f'<div class="subject-folder" data-subject="{subject.lower()}" onclick="openFolder({i})">📁 {subject}</div>'
        
        # Generate category tabs for this subject
        vids_items = []
        for title, url in categories['videos']:
            ext = url.split('.')[-1].split('?')[0] if '.' in url else 'mp4'
            vids_items.append(f'<a href="#" onclick="playVideo(\'{url}\', \'{ext}\')" class="video-item">{title}</a>')
        vids = "".join(vids_items)
        
        pdf = "".join(f'<a href="{url}" target="_blank" class="pdf-item">{title}</a>' for title, url in categories['pdfs'])
        oth = "".join(f'<a href="{url}" target="_blank" class="other-item">{title}</a>' for title, url in categories['others'])
        
        folders_content += f'''
        <div id="folder-{i}" class="folder-content" data-subject-index="{i}">
            <div class="folder-header">
                <button class="back-btn" onclick="closeFolder()">🔙 Back</button>
                <h2>{subject}</h2>
            </div>
            
            <!-- Folder Search Bar -->
            <div class="folder-search">
                <input type="text" id="folder-search-{i}" class="folder-search-input" placeholder="🔍 Search in this subject..." onkeyup="searchInFolder({i})">
            </div>
            
            <div class="tab-container">
                <div class="tab" onclick="showCategory('videos-{i}')">📹 Videos ({len(categories['videos'])})</div>
                <div class="tab" onclick="showCategory('pdfs-{i}')">📄 PDFs ({len(categories['pdfs'])})</div>
                <div class="tab" onclick="showCategory('others-{i}')">📁 Others ({len(categories['others'])})</div>
            </div>
            
            <div id="videos-{i}" class="category-content">
                <h3>📹 Videos</h3>
                <div class="links-list" id="videos-list-{i}">{vids if vids else "<p class='empty-message'>No videos available</p>"}</div>
                <div id="videos-empty-{i}" class="category-empty-message" style="display:none;">❌ No matching videos found</div>
            </div>
            
            <div id="pdfs-{i}" class="category-content" style="display:none;">
                <h3>📄 PDFs</h3>
                <div class="links-list" id="pdfs-list-{i}">{pdf if pdf else "<p class='empty-message'>No PDFs available</p>"}</div>
                <div id="pdfs-empty-{i}" class="category-empty-message" style="display:none;">❌ No matching PDFs found</div>
            </div>
            
            <div id="others-{i}" class="category-content" style="display:none;">
                <h3>📁 Other Files</h3>
                <div class="links-list" id="others-list-{i}">{oth if oth else "<p class='empty-message'>No other files available</p>"}</div>
                <div id="others-empty-{i}" class="category-empty-message" style="display:none;">❌ No matching files found</div>
            </div>
        </div>
        '''
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{name}</title>
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet"/>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', 'Noto Sans', 'System UI', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', Arial, sans-serif;
        }}
        
        body {{
            background: #f5f7fa;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .header {{
            width: 100%;
            max-width: 800px;
            margin: 20px auto 0;
            background: #1c1c1c;
            color: white;
            padding: 15px 20px;
            text-align: center;
            font-size: 16px;
            font-weight: 500;
            border-radius: 10px 10px 0 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .header small {{
            display: block;
            font-size: 13px;
            color: #ccc;
            margin-top: 5px;
        }}
        
        #video-player {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            background: #1c1c1c;
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            position: relative;  /* for absolute positioning of the button */
        }}
        
        .video-js {{
            width: 100% !important;
            height: auto !important;
            aspect-ratio: 16/9;
        }}
        
        /* Button to open video in new tab */
        .open-tab-button {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 10;
            background: rgba(0,0,0,0.6);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        .open-tab-button:hover {{
            background: rgba(0,0,0,0.8);
        }}
        
        /* Playback speed button customization */
        .vjs-playback-rate .vjs-menu {{
            width: 80px;
        }}
        
        .vjs-playback-rate .vjs-menu-item {{
            font-size: 14px;
            text-align: center;
        }}
        
        /* Main subjects menu */
        #main-view {{
            width: 100%;
            max-width: 800px;
            margin: 20px auto;
        }}
        
        .main-search {{
            width: 100%;
            margin-bottom: 20px;
            padding: 0 10px;
        }}
        
        .main-search input {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            transition: all 0.3s ease;
            outline: none;
        }}
        
        .main-search input:focus {{
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }}
        
        .subjects-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            padding: 0 10px;
        }}
        
        .subject-folder {{
            display: inline-block;
            padding: 12px 20px;
            background: white;
            border-radius: 25px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            font-size: 14px;
            transition: all 0.3s ease;
        }}
        
        .subject-folder:hover {{
            background: #007bff;
            color: white;
            transform: translateY(-2px);
        }}
        
        .subject-folder.hidden {{
            display: none;
        }}
        
        #noSubjects {{
            width: 100%;
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 14px;
            display: none;
        }}
        
        /* Folder content */
        .folder-content {{
            display: none;
            width: 100%;
            max-width: 800px;
            margin: 20px auto;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .folder-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .folder-header h2 {{
            margin: 0;
            color: #333;
            font-size: 18px;
            font-weight: 600;
        }}
        
        .back-btn {{
            padding: 8px 20px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            margin-right: 15px;
            font-size: 13px;
            transition: background 0.3s ease;
        }}
        
        .back-btn:hover {{
            background: #5a6268;
        }}
        
        /* Folder search bar */
        .folder-search {{
            width: 100%;
            margin: 15px 0;
        }}
        
        .folder-search input {{
            width: 100%;
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: all 0.3s ease;
        }}
        
        .folder-search input:focus {{
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }}
        
        /* Category tabs */
        .tab-container {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
        }}
        
        .tab {{
            flex: 1;
            padding: 12px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 25px;
            cursor: pointer;
            text-align: center;
            font-size: 14px;
            font-weight: 500;
            color: #666;
            transition: all 0.3s ease;
        }}
        
        .tab:hover {{
            background: #007bff;
            color: white;
            border-color: #007bff;
        }}
        
        /* Category content */
        .category-content {{
            margin-top: 20px;
        }}
        
        .category-content h3 {{
            font-size: 16px;
            margin-bottom: 15px;
            color: #333;
            padding-bottom: 8px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .links-list {{
            margin-top: 10px;
        }}
        
        .links-list a {{
            display: block;
            padding: 12px 15px;
            background: #f8f9fa;
            margin: 8px 0;
            border-radius: 8px;
            text-decoration: none;
            color: #007bff;
            font-size: 14px;
            transition: all 0.3s ease;
            word-break: break-word;
        }}
        
        .links-list a:hover {{
            background: #007bff;
            color: white;
            transform: translateX(5px);
        }}
        
        .empty-message {{
            color: #666;
            text-align: center;
            padding: 20px;
            font-size: 14px;
        }}
        
        .category-empty-message {{
            color: #dc3545;
            text-align: center;
            padding: 20px;
            font-size: 14px;
            background: #fff;
            border-radius: 8px;
            margin-top: 10px;
        }}
        
        .footer {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto 20px;
            padding: 15px;
            background: #1c1c1c;
            color: white;
            text-align: center;
            font-size: 13px;
            border-radius: 0 0 10px 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        {name}<br>
        <small>Subject Wise | {CREDIT}</small>
    </div>
    
    <div id="video-player">
        <video id="player" class="video-js vjs-default-skin" controls preload="auto" width="640" height="360"></video>
        <button class="open-tab-button" onclick="openInNewTab()" title="Open video in new tab">↗</button>
    </div>
    
    <!-- Main subjects view -->
    <div id="main-view">
        <!-- Main Search Bar for Subjects -->
        <div class="main-search">
            <input type="text" id="subjectSearch" placeholder="🔍 Search subjects..." onkeyup="searchSubjects()">
        </div>
        
        <div class="subjects-container" id="subjectsContainer">
            {subjects_menu}
        </div>
        <div id="noSubjects">❌ No matching subjects found</div>
    </div>
    
    <!-- Folder contents -->
    {folders_content}
    
    <div class="footer">Extracted By : {CREDIT}</div>
    
    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script>
        const player = videojs('player', {{
            controls: true,
            autoplay: false,
            preload: 'auto',
            fluid: true,
            aspectRatio: '16:9',
            playbackRates: [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3],
            html5: {{
                hls: {{
                    enableLowInitialPlaylist: true,
                    smoothQualityChange: true,
                    overrideNative: true
                }},
                nativeAudioTracks: false,
                nativeVideoTracks: false
            }}
        }});
        
        let currentVideoUrl = '';   // <-- new global variable to store the last played URL
        
        function openInNewTab() {{
            if (currentVideoUrl) {{
                window.open(currentVideoUrl, '_blank');
            }} else {{
                alert('No video loaded');
            }}
        }}
        
        function getVideoType(url) {{
            if (url.includes('.m3u8')) {{
                return 'application/x-mpegURL';
            }} else if (url.includes('.mp4')) {{
                return 'video/mp4';
            }} else if (url.includes('.webm')) {{
                return 'video/webm';
            }} else if (url.includes('.ogg')) {{
                return 'video/ogg';
            }} else {{
                return 'video/mp4'; // default
            }}
        }}
        
        function playVideo(url, ext) {{
            currentVideoUrl = url;   // <-- store the URL
            
            // For YouTube links
            if (url.includes('youtu')) {{
                window.open(url, '_blank');
                return;
            }}
            
            // For other video links
            const videoType = getVideoType(url);
            
            // Special handling for different video types
            if (url.includes('.m3u8')) {{
                player.src({{
                    src: url,
                    type: 'application/x-mpegURL'
                }});
            }} else {{
                // For MP4 and other direct video files
                player.src({{
                    src: url,
                    type: videoType
                }});
            }}
            
            // Add error handling
            player.ready(function() {{
                player.play().catch(function(error) {{
                    console.log('Playback failed: ' + error);
                    // Fallback - open in new tab if playback fails
                    if (confirm('Video playback failed. Open in new tab?')) {{
                        window.open(url, '_blank');
                    }}
                }});
            }});
        }}
        
        // Search Subjects function
        function searchSubjects() {{
            const searchTerm = document.getElementById('subjectSearch').value.toLowerCase();
            const subjects = document.querySelectorAll('.subject-folder');
            let visibleCount = 0;
            
            subjects.forEach(subject => {{
                const subjectName = subject.textContent.toLowerCase();
                if(subjectName.includes(searchTerm)) {{
                    subject.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    subject.classList.add('hidden');
                }}
            }});
            
            const noSubjectsMsg = document.getElementById('noSubjects');
            if(visibleCount === 0) {{
                noSubjectsMsg.style.display = 'block';
            }} else {{
                noSubjectsMsg.style.display = 'none';
            }}
        }}
        
        // Search within folder function
        function searchInFolder(folderIndex) {{
            const searchTerm = document.getElementById(`folder-search-${{folderIndex}}`).value.toLowerCase();
            
            // Get current visible category
            const folder = document.getElementById(`folder-${{folderIndex}}`);
            const visibleCategory = Array.from(folder.querySelectorAll('.category-content')).find(c => c.style.display !== 'none');
            
            if(!visibleCategory) return;
            
            const categoryId = visibleCategory.id;
            const categoryType = categoryId.split('-')[0]; // videos, pdfs, or others
            
            // Get all items in this category
            const items = visibleCategory.querySelectorAll('.links-list a');
            const emptyMessage = document.getElementById(`${{categoryType}}-empty-${{folderIndex}}`);
            const listContainer = document.getElementById(`${{categoryType}}-list-${{folderIndex}}`);
            
            let visibleCount = 0;
            
            items.forEach(item => {{
                const itemText = item.textContent.toLowerCase();
                if(itemText.includes(searchTerm)) {{
                    item.style.display = 'block';
                    visibleCount++;
                }} else {{
                    item.style.display = 'none';
                }}
            }});
            
            // Show/hide empty message
            if(visibleCount === 0) {{
                emptyMessage.style.display = 'block';
                listContainer.style.display = 'none';
            }} else {{
                emptyMessage.style.display = 'none';
                listContainer.style.display = 'block';
            }}
        }}
        
        function openFolder(index) {{
            document.getElementById('main-view').style.display = 'none';
            document.querySelectorAll('.folder-content').forEach(f => f.style.display = 'none');
            const folder = document.getElementById(`folder-${{index}}`);
            folder.style.display = 'block';
            
            // Show videos category by default
            showCategory(`videos-${{index}}`);
            
            // Clear folder search
            document.getElementById(`folder-search-${{index}}`).value = '';
        }}
        
        function closeFolder() {{
            document.getElementById('main-view').style.display = 'block';
            document.querySelectorAll('.folder-content').forEach(f => f.style.display = 'none');
            
            // Refresh subject search when coming back
            searchSubjects();
        }}
        
        function showCategory(categoryId) {{
            // Hide all category contents in the current folder
            const folder = document.getElementById(categoryId).closest('.folder-content');
            folder.querySelectorAll('.category-content').forEach(c => c.style.display = 'none');
            
            // Show selected category
            document.getElementById(categoryId).style.display = 'block';
            
            // Get folder index from categoryId
            const folderIndex = categoryId.split('-')[1];
            
            // Trigger search in this category to update visibility
            searchInFolder(parseInt(folderIndex));
        }}
        
        // Add global error handler for video player
        player.on('error', function() {{
            console.log('Video error:', player.error());
        }});
    </script>
</body>
</html>
"""

#=====================================================================================================
# Function to generate normal HTML (existing style)
def generate_normal_html(file_name, videos, pdfs, others):
    file_name_without_extension = os.path.splitext(file_name)[0]

    video_items = []
    for name, url in videos:
        ext = url.split('.')[-1].split('?')[0] if '.' in url else 'mp4'
        video_items.append(f'<a href="#" onclick="playVideo(\'{url}\', \'{ext}\')">{name}</a>')
    video_links = "".join(video_items)
    
    pdf_links = "".join(f'<a href="{url}" target="_blank">{name}</a>' for name, url in pdfs)
    other_links = "".join(f'<a href="{url}" target="_blank">{name}</a>' for name, url in others)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_name_without_extension}</title>
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet"/>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', 'Noto Sans', 'System UI', sans-serif;
        }}

        body {{
            background: #f5f7fa;
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .header {{
            width: 100%;
            max-width: 800px;
            margin: 20px auto 0;
            background: #1c1c1c;
            color: white;
            padding: 15px 20px;
            text-align: center;
            font-size: 16px;
            font-weight: 500;
            border-radius: 10px 10px 0 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        .header small {{
            display: block;
            font-size: 13px;
            color: #ccc;
            margin-top: 5px;
        }}

        #video-player {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            background: #1c1c1c;
            padding: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
        }}

        .video-js {{
            width: 100% !important;
            height: auto !important;
            aspect-ratio: 16/9;
        }}

        /* Button to open video in new tab */
        .open-tab-button {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 10;
            background: rgba(0,0,0,0.6);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        .open-tab-button:hover {{
            background: rgba(0,0,0,0.8);
        }}

        /* Playback speed button customization */
        .vjs-playback-rate .vjs-menu {{
            width: 80px;
        }}
        
        .vjs-playback-rate .vjs-menu-item {{
            font-size: 14px;
            text-align: center;
        }}

        .search-bar {{
            width: 100%;
            max-width: 800px;
            margin: 20px auto;
            padding: 0 10px;
        }}

        .search-bar input {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            transition: all 0.3s ease;
            outline: none;
        }}

        .search-bar input:focus {{
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }}

        .no-results {{
            width: 100%;
            max-width: 800px;
            margin: 20px auto;
            padding: 0 10px;
            color: #dc3545;
            font-weight: 500;
            text-align: center;
            display: none;
        }}

        .container {{
            display: flex;
            justify-content: center;
            gap: 10px;
            width: 100%;
            max-width: 800px;
            margin: 20px auto;
            padding: 0 10px;
        }}

        .tab {{
            flex: 1;
            padding: 12px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            font-weight: 500;
            text-align: center;
            color: #666;
        }}

        .tab:hover {{
            background: #007bff;
            color: white;
            border-color: #007bff;
        }}

        .content {{
            display: none;
            width: 100%;
            max-width: 800px;
            margin: 20px auto;
            padding: 25px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        .content h2 {{
            font-size: 18px;
            margin-bottom: 15px;
            color: #333;
            font-weight: 600;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}

        .links-list {{
            margin-top: 15px;
        }}

        .links-list a {{
            display: block;
            padding: 12px 15px;
            background: #f8f9fa;
            margin: 8px 0;
            border-radius: 8px;
            text-decoration: none;
            color: #007bff;
            font-size: 14px;
            transition: all 0.3s ease;
            word-break: break-word;
        }}

        .links-list a:hover {{
            background: #007bff;
            color: white;
            transform: translateX(5px);
        }}

        .footer {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto 20px;
            padding: 15px;
            background: #1c1c1c;
            color: white;
            text-align: center;
            font-size: 13px;
            border-radius: 0 0 10px 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        {file_name_without_extension}
        <small>Extracted By : {CREDIT}</small>
    </div>

    <div id="video-player">
        <video id="player" class="video-js vjs-default-skin" controls preload="auto" width="640" height="360"></video>
        <button class="open-tab-button" onclick="openInNewTab()" title="Open video in new tab">↗</button>
    </div>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="🔍 Search videos, PDFs, or other files..." onkeyup="filterContent()">
    </div>

    <div id="noResults" class="no-results">❌ No results found</div>

    <div class="container">
        <div class="tab" onclick="showContent('videos')">📹 Videos ({len(videos)})</div>
        <div class="tab" onclick="showContent('pdfs')">📄 PDFs ({len(pdfs)})</div>
        <div class="tab" onclick="showContent('others')">📁 Others ({len(others)})</div>
    </div>

    <div id="videos" class="content">
        <h2>📹 Video Lectures</h2>
        <div class="links-list">{video_links if video_links else "<p style='color:#666; text-align:center; padding:20px;'>No videos available</p>"}</div>
    </div>

    <div id="pdfs" class="content">
        <h2>📄 PDF Documents</h2>
        <div class="links-list">{pdf_links if pdf_links else "<p style='color:#666; text-align:center; padding:20px;'>No PDFs available</p>"}</div>
    </div>

    <div id="others" class="content">
        <h2>📁 Other Files</h2>
        <div class="links-list">{other_links if other_links else "<p style='color:#666; text-align:center; padding:20px;'>No other files available</p>"}</div>
    </div>

    <div class="footer">Extracted By : {CREDIT}</div>

    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script>
        const player = videojs('player', {{
            controls: true,
            autoplay: false,
            preload: 'auto',
            fluid: true,
            aspectRatio: '16:9',
            playbackRates: [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3],
            html5: {{
                hls: {{
                    enableLowInitialPlaylist: true,
                    smoothQualityChange: true,
                    overrideNative: true
                }},
                nativeAudioTracks: false,
                nativeVideoTracks: false
            }}
        }});
        
        let currentVideoUrl = '';   // <-- new global variable
        
        function openInNewTab() {{
            if (currentVideoUrl) {{
                window.open(currentVideoUrl, '_blank');
            }} else {{
                alert('No video loaded');
            }}
        }}
        
        function getVideoType(url) {{
            if (url.includes('.m3u8')) {{
                return 'application/x-mpegURL';
            }} else if (url.includes('.mp4')) {{
                return 'video/mp4';
            }} else if (url.includes('.webm')) {{
                return 'video/webm';
            }} else if (url.includes('.ogg')) {{
                return 'video/ogg';
            }} else {{
                return 'video/mp4'; // default
            }}
        }}
        
        function playVideo(url, ext) {{
            currentVideoUrl = url;   // <-- store the URL
            
            // For YouTube links
            if (url.includes('youtu')) {{
                window.open(url, '_blank');
                return;
            }}
            
            // For other video links
            const videoType = getVideoType(url);
            
            // Special handling for different video types
            if (url.includes('.m3u8')) {{
                player.src({{
                    src: url,
                    type: 'application/x-mpegURL'
                }});
            }} else {{
                // For MP4 and other direct video files
                player.src({{
                    src: url,
                    type: videoType
                }});
            }}
            
            // Add error handling
            player.ready(function() {{
                player.play().catch(function(error) {{
                    console.log('Playback failed: ' + error);
                    // Fallback - open in new tab if playback fails
                    if (confirm('Video playback failed. Open in new tab?')) {{
                        window.open(url, '_blank');
                    }}
                }});
            }});
        }}
        
        function showContent(tabName) {{
            document.querySelectorAll('.content').forEach(c => c.style.display = 'none');
            document.getElementById(tabName).style.display = 'block';
            filterContent();
        }}
        
        function filterContent() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            let hasResults = false;
            
            document.querySelectorAll('.content').forEach(content => {{
                const links = content.querySelectorAll('.links-list a');
                let categoryHasResults = false;
                
                links.forEach(link => {{
                    if(link.textContent.toLowerCase().includes(searchTerm)) {{
                        link.style.display = 'block';
                        categoryHasResults = true;
                        hasResults = true;
                    }} else {{
                        link.style.display = 'none';
                    }}
                }});
                
                // Hide category heading if no results
                const heading = content.querySelector('h2');
                if(heading) {{
                    heading.style.display = categoryHasResults ? 'block' : 'none';
                }}
                
                // Hide empty message if there are results
                const emptyMsg = content.querySelector('p');
                if(emptyMsg && emptyMsg.style.color === '#666') {{
                    emptyMsg.style.display = categoryHasResults ? 'none' : 'block';
                }}
            }});
            
            document.getElementById('noResults').style.display = hasResults ? 'none' : 'block';
        }}
        
        // Show videos tab by default
        document.addEventListener('DOMContentLoaded', () => {{
            showContent('videos');
        }});
        
        // Add global error handler for video player
        player.on('error', function() {{
            console.log('Video error:', player.error());
        }});
    </script>
</body>
</html>
    """
    return html_template

#=================================================================================================================================

async def html_handler(bot: Client, message: Message):
    editable = await message.reply_text("𝐖𝐞𝐥𝐜𝐨𝐦𝐞! 𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐩𝐥𝐨𝐚𝐝 𝐚 .𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐜𝐨𝐧𝐭𝐚𝐢𝐧𝐢𝐧𝐠 𝐔𝐑𝐋𝐬.✓")
    input_file = await bot.listen(editable.chat.id)
    if not (input_file.document and input_file.document.file_name.endswith('.txt')):
        return await message.reply_text("**❌ Invalid file!**")
    await editable.delete()
    file_path = await input_file.download()
    file_name = os.path.basename(file_path).replace(".txt", "").replace("_", " ")
    
    with open(file_path, "r") as f:
        content = f.read()
    
    urls = extract_names_and_urls(content)
    videos, pdfs, others = categorize_urls(urls)
    subjects = organize_by_subject(urls)
    
    subject_html = generate_subject_html(file_name, subjects)
    subject_html_path = f"{file_name}_subject.html"
    with open(subject_html_path, "w", encoding="utf-8") as f:
        f.write(subject_html)

    normal_html = generate_normal_html(file_name, videos, pdfs, others)
    normal_html_path = f"{file_name}_normal.html"
    with open(normal_html_path, "w", encoding="utf-8") as f:
        f.write(normal_html)

    try:
        await message.reply_document(
            subject_html_path,
            caption=f"📚 **Subject Wise HTML Generated!**\n"
                   f"<blockquote><b>🌐 `{file_name}`</b></blockquote>\n"
                   f"🌟 **Extracted By : {CREDIT}**"
        )
    
        await message.reply_document(
            normal_html_path,
            caption=f"📄 **Normal HTML Generated!**\n"
                   f"<blockquote><b>🌐 `{file_name}`</b></blockquote>\n"
                   f"🌟 **Extracted By : {CREDIT}**"
        )
        
    except Exception as e:
        await message.reply_text(f"**Fail Reason »**\n<blockquote><i>{str(e)}</i></blockquote>")
    finally:
        for path in [file_path, subject_html_path, normal_html_path]:
            if os.path.exists(path):
                os.remove(path)

#===========================================================================================================================
        
def register_html_handlers(bot):
    @bot.on_message(filters.command("t2h"))
    async def call(bot: Client, message: Message):
        await html_handler(bot, message)
