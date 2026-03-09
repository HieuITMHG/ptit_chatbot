start = 0
end = start + 500

chunks = []

while end < 1000:
    chunk = [i for i in range(start, end)]
    start = start + 500 - 50
    end = start + 500

    chunks.append(chunk)

for c in chunks:
    print(c)