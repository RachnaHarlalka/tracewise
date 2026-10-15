


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
