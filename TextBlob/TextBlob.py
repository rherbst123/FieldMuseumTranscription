from textblob import TextBlob

with open("C:\\Users\\riley\\OneDrive\\Desktop\\CodeForMe\\python\\Input\\CommunityCitizenFreeResponses.txt", 'r', encoding="utf-8") as file:
    text = file.read()

lines = text.split('\n')
blobs = []
current_blob = ''
for line in lines:
    if line.startswith(' '):
        current_blob += line.strip() + ' '
    else:
        if current_blob:
            blobs.append(current_blob.strip())
        current_blob = line.strip()

if current_blob:
    blobs.append(current_blob.strip())

for i, blob in enumerate(blobs):
    print(f"Blob {i+1}: {blob} - Sentiment Polarity: {TextBlob(blob).sentiment.polarity}")
