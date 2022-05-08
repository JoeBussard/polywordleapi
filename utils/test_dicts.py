import backend_setup

myCache, common_words, all_words = backend_setup.start_up_game_backend('a')

print("testing")
if "snaps" in list(common_words.values()):
  print("commn")

if "snaps" in all_words:
  print("all")
for x in list(common_words.values()):
  if x not in list(all_words.values()):
    print(x, "was in common words but not all_words")


