import re, random, json, datetime

def confirmation(prompt='Are you sure? y/n\n'):
	while True:
		r = input(prompt)
		if r == 'y':
			return True
		elif r == 'n':
			return False
		else:
			print('Invalid input. Try again.')
			
def edit_entry(before, after):
	with open('formulaic_expressions.txt', 'r', encoding='utf-8') as f:
		lines = [l for l in f]
		for i, l in enumerate(lines):
			if l.strip() == before:
				lines[i] = after + "\n"
	with open('formulaic_expressions.txt', 'w', encoding='utf-8') as f:
		for l in lines:
			f.write(l)
	
def del_entry(zh):
	with open('formulaic_expressions.txt', 'r', encoding='utf-8') as f:
		new_lines = []
		for l in f:
			if not (pair_pattern.match(l) and pair_pattern.match(l)[1] == zh):
				new_lines.append(l)
	
	with open('formulaic_expressions.txt', 'w', encoding='utf-8') as f:
		for l in new_lines:
			f.write(l)
			
def is_dormant(zh, dic): # looks up a value zh in dictionary dic, returns whether it is dormant
	if zh not in dic:
		return True
	elif dic[zh][0] == "placeholder date":
		return True
		
	today_date = datetime.datetime.now().date()
	y, m, d = [int(x) for x in dic[zh][0].split('-')]
	last_date = datetime.datetime(y, m, d).date()
	
	consec_corrects = dic[zh][1]
	if consec_corrects >= 5:
		days_before_dormant = 14
	elif consec_corrects >= 3:
		days_before_dormant = 7
	else:
		days_before_dormant = 3
	if (today_date - last_date).days >= days_before_dormant:
		return True
	return False

def check_answer(guess, ans):
	def plural_diff(a, b):
		if len(b) > len(a):
			a, b = b, a
		if (a[-1] == "s" and a[:-1] == b) or (a[-2:] == "es" and a[:-2] == b) or (a[-3:] == "ies" and a[:-3] == b[:-1]):
			return True
		return False
	
	def break_hyphens(lst):
		temp = []
		for x in lst:
			if "-" in x:
				two = x.split("-")
				for word in two:
					temp.append(word)
			else:
				temp.append(x)
		return temp
	
	guess = guess.lower()
	ans = ans.lower()
	if guess == ans:
		return True
	temp1 = guess.split()
	temp2 = ans.split()
	
	temp1 = break_hyphens(temp1)
	temp2 = break_hyphens(temp2)
			
	temp1 = [x for x in temp1 if x not in ["the", "an", "a"]]
	temp2 = [x for x in temp2 if x not in ["the", "an", "a"]]
	
	if temp1 == temp2:
		return True
	elif len(temp1) == len(temp2):
		if all(plural_diff(temp1[i], temp2[i]) or temp1[i] == temp2[i] for i in range(len(temp1))):
			return True
	elif "".join(temp1) == "".join(temp2):
		return True
	return False

date_pattern = re.compile(r"\w{3,4} \d{1,2}")
pair_pattern = re.compile(r"(.+) - (.+)")
random_pattern = re.compile(r'random [1-9]{1}\d*')
random_dormant_pattern = re.compile(r'random dormant [1-9]{1}\d*')
 
try:
	with open('data_log.json', 'r', encoding='utf-8') as f:
		data = json.load(f)
except FileNotFoundError:
	with open('data_log.json', 'w', encoding='utf-8') as f:
		json.dump({}, f)
		
with open("formulaic_expressions.txt", "r", encoding="utf-8") as f:
	wordbank = {}
	lines = [l.strip() for l in f if l]
	for l in lines:
		if date_pattern.match(l):
			wordbank[l] = {}
			current_date = l
		elif pair_pattern.match(l):
			res = pair_pattern.match(l)
			zh = res[1]
			en = res[2]
			wordbank[current_date][zh] = en

def game():		
	wrongs = {}
	with open("data_log.json", 'r', encoding='utf-8') as f:
		data = json.load(f)
	
	all_words = {zh:en for k, v in wordbank.items() for zh, en in v.items()}
	
	for d in list(data):
		if d not in all_words:
			del data[d]
			print(f"Deleted {d} from logs.json.")
			
	with open("data_log.json", "w") as f:
		json.dump(data, f, indent=4)
			
	dormant_words = {zh:en for k, v in wordbank.items() for zh, en in v.items() if is_dormant(zh, data)}
	
	dates_string = "\n"	
	for d, ws in wordbank.items():
		dates_string += f"- {d} ({len(ws)} words)\n"
	print(f"Total words: {len(all_words)}")
	print(f'Dormant words: {len(dormant_words)}')

	print("\nSelect wordbank.\n- Enter a single date, or multiple dates separated by commas.\n- Type 'all' to select all.\n- Type 'all dormant' to pick all dormant words.\n- Type 'random n' to pick n random words.\n- Type 'random dormant n' to pick n random dormant words.\n- Type 'show dates' to show all dates. ")
	
	while True:
		user_input = input()
		if user_input == "all":
			bank = all_words
			
		elif user_input == "all dormant":
			bank = dormant_words
		
		elif "," in user_input:
			days = [x.strip() for x in user_input.split(",")]
			bank = {zh:en for d in days for zh, en in wordbank[d.capitalize()].items()}
		
		elif random_pattern.match(user_input):
			n = int(user_input.split()[1])
			if n > len(all_words):
				print('Number exceeds total words in wordbank.')
				continue
			picked = random.sample(list(all_words), n)
			bank = {zh:en for date, dic in wordbank.items() for zh, en in dic.items() if zh in picked}
			
		elif random_dormant_pattern.match(user_input):
			n = int(user_input.split()[2])
			if n > len(dormant_words):
				print('Number exceeds total words in dormant words.')
				continue
			picked = random.sample(list(dormant_words), n)
			bank = {zh:en for date, dic in wordbank.items() for zh, en in dic.items() if zh in picked}		
			
		elif date_pattern.match(user_input):
			bank = {zh:en for zh, en in wordbank[user_input.capitalize()].items()}
		
		elif user_input == "show dates":
			print(dates_string)
			continue
		else:
			print('Invalid input. Try again.')
			continue
		break
	
	keys = [k for k in bank]
	random.shuffle(keys)
	print(f"\n{len(bank)} words loaded.\n====================================\n")
	
	first = True
	reprompt = False
	while keys:
		if not reprompt:
			zh = keys.pop(0)
			en = bank[zh]
		ans = input(f"{zh} - ")
		
		try:
			data[zh]
		except KeyError:
			data[zh] = ["placeholder date", 0]
		
		if ans == "pass":
			print("Passed.")
			print(f"The answer was {en}.\n")
		elif ans == "delete previous":
			if first:
				print("No previous entry.\n")
			else:
				c = confirmation(f"Are you sure you want to delete {prev}? y/n\n")
				if c:	
					del_entry(prev)
					if prev in keys:
						keys.remove(prev)
					print(f"Deleted {prev}.\n")
				else:
					print("\n")
				reprompt = True
				continue
		elif ans == "edit previous":
			if first:
				print('No previous entry.\n')
			else:
				before = f"{prev} - {bank[prev]}"
				print(f'Editing: {before}')
				while True:
					after = input('Edit to: ')
					if pair_pattern.match(after):
						c = confirmation()
						if c:
							edit_entry(before, after)
							if prev in keys:
								keys.remove(prev)
							print("Edit successful.\n")
						else:
							print('\n')
						break
					else:
						print("Invalid input. Try again.")
				reprompt = True
				continue
				
		elif check_answer(ans, en):
			print(f"Correct! {len(keys)}/{len(bank)} left.\n")
			data[zh][0] = datetime.datetime.now().date().strftime('%Y-%m-%d')
			data[zh][1] += 1
			with open('data_log.json', 'w', encoding='utf-8') as f:
				json.dump(data, f, indent=4)
		else:
			keys.append(zh)
			print(f"Wrong. The answer was {en}. {len(keys)}/{len(bank)} left.\n")
			data[zh][1] = 0
			try:
				wrongs[f"{zh} - {en}"] += 1
			except KeyError:
				wrongs[f"{zh} - {en}"] = 1
				
		reprompt = False
		prev = zh
		if first:
			first = False
	
	if wrongs:
		print("Session ended. Stats:")
		sorted_keys = sorted(wrongs, key= lambda x:wrongs[x], reverse=True)
		for sk in sorted_keys:
			print(f"{sk}: wrong {wrongs[sk]} times.")
	else:
		print("Session ended. Congratulations for getting all correct!")
	print("====================================\n")

game()
while True:
	again = input("Go again? y/n ")
	if again == "y":
		print("====================================")
		game()
	elif again == "n":
		print("Program ended.")
		break
