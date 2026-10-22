# STEP 3: chunking by hand
# - RAG = retrieve pieces -> add to prompt -> generate. Chunks make retrieval possible.
# - Small chunks: precise but cut ideas. Big chunks: whole ideas but noisy. Overlap fixes cuts.
# - File path is relative to where you RUN the script, not to this file.

def main():
  try:
    with open('../../../README.md','r') as f:
      file_content = f.read()

  except FileNotFoundError as e:
    print("error",e)
    return

  total_file_length = len(file_content)


  start = 0
  count = 0

  chunkSize = 1500

  while start < total_file_length :
    chunk = file_content[start: start+chunkSize]
    print(f"chunk {count}", chunk)
    print("---------------------***********************----------------------------")
    start += chunkSize
    count += 1




if __name__ == '__main__':
  main()
