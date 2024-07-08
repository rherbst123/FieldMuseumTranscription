from textblob import TextBlob

with open("Name and diretory of input.txt", 'r', encoding="utf-8") as file:
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

with open("Name and Directory of Output.txt", 'w', encoding="utf-8") as file:
    for i, blob in enumerate(blobs):
        polarity = TextBlob(blob).sentiment.polarity
        file.write(f"Line {i+1}: Polarity: {polarity}\n")
