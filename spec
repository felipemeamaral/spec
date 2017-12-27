#!/bin/sh
shopt -s nullglob # Sets nullglob
shopt -s nocaseglob # Sets nocaseglob
# ImgUR API Key
api_key=f6c67fcc0af0264
for f in *.flac *.mpeg *.wav *.aiff *.ogg *.m4a *.aac *.mp4 *.ape *.asf *.wma  ;do

  sox "$f" -n spectrogram -o "$f.png" -t "$f"
  optipng -quiet "$f.png"
  response=$(curl -H "Authorization: CLIENT-ID $api_key" -F "image=@$f.png" \
  https://api.imgur.com/3/image.xml 2>/dev/null | tail -n +2 | sed 's/http:/https:/g' )
  
  # Upload to imgur and replace http for https in the output
  response=$(curl -H "Authorization: CLIENT-ID $api_key" -F "image=@$f.png" \
    https://api.imgur.com/3/image.xml 2>/dev/null | tail -n +2 | sed 's/http:/https:/g' )
  sleep 3
  curl_attempt=2

  # Check for errors so we can retry
  while [[ "$curl_attempt" -le 3 && "$response" == *"error"* ]]; do
    if [[ "$quiet" != "1" ]]; then
      printf "\rSomething went wrong, trying again. Attempt $curl_attempt out of 3"
    fi
    ((curl_attempt++))
    sleep 2
    response=$(curl -H "Authorization: CLIENT-ID $api_key" -F "image=@$f.png" \
      https://api.imgur.com/3/image.xml 2>/dev/null | tail -n +2 | sed 's/http:/https:/g' )
  done

  if [[ "$response" == *"error"* ]]; then
    # Parse the actual error to display it
    curl_error=$(printf '%s\n' "$response" | sed -E 's/.*<error>(.*)<\/error>.*/\1/')
    printf "\rCouldn't upload this this image, reason: \"$curl_error\""
    rm "$f.png"
    return
  else

    # Get the text between <link> </link> in the xml output
    url=$(printf '%s\n' "$response" | sed -E 's/.*<link>(.*)<\/link>.*/\1/')
    # Print the image URL 
    printf '%s\n' "[img]$url[/img]"
    rm "$f.png"
  fi

done
