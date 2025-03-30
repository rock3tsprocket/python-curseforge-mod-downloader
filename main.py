import httpx
import json

# search for mod itself

while True:

  searchTerm = input("Search term (Q to quit): ")

  if (searchTerm == "q") or (searchTerm == "Q"):
      exit("\n Exiting...")
      pass
  test = httpx.get('https://api.modrinth.com/v2/search?query='+searchTerm).json()["total_hits"]
  if test == 0:
    print('\n No results found!')
    print(" ")
  else:
    break
  pass


  
resp = httpx.get('https://api.modrinth.com/v2/search?query='+searchTerm).json()["hits"]

number = int(0)



while True:    
    
    if number == 10:
        print("\n Be more specific with your name.")
        
    
    first = resp[number]
    print(" ")
    print("Title:", first["title"])
    print("By:", first["author"])
    print("Desc:", first["description"])
    ID = first["project_id"]
        
    isThisIt = input("Is this it? (Y/N/Q/S): ")
    if (isThisIt == "Y") or (isThisIt == "y"):
        print(" ")
        break
    elif (isThisIt == "N") or (isThisIt == "n"):
        number = 1 + number
    elif (isThisIt == "S") or (isThisIt == "s"):
      while True:

        searchTerm = input("Search term (Q to quit): ")

        if (searchTerm == "q") or (searchTerm == "Q"):
            exit("\n Exiting...")
            pass
        test = httpx.get('https://api.modrinth.com/v2/search?query='+searchTerm).json()["total_hits"]
        if test == 0:
          print('\n No results found!')
          print(" ")
        else:
          break
        pass
      resp = httpx.get('https://api.modrinth.com/v2/search?query='+searchTerm).json()["hits"] 
        
    elif (isThisIt == "Q") or (isThisIt == "q"):
        exit("\n Exiting.")
    else:
        print("\n That's not an option.")

# ask the user for specific version

a = httpx.get('https://api.modrinth.com/v2/project/'+ID).json()['versions']

number = -1
while number != -11:
  def extract_id(idList):
    if idList:
      return idList[number]
    else:
      return None

  verid = extract_id(a)
  b = httpx.get('https://api.modrinth.com/v2/version/'+verid).json()['name'] + " " + str(httpx.get('https://api.modrinth.com/v2/version/'+verid).json()['game_versions'])
  print(str(number * -1)+".", b)
  number = number - 1
