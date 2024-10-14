from datetime import datetime
import json
import sys
import time
from urllib.parse import parse_qs, unquote

from fastmint import Fastmint


def load_query():
    try:
        with open('fastmint_query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File fastmint_query.txt not Found.")
        return [  ]
    except Exception as e:
        print("Terjadi kesalahan saat memuat token:", str(e))
        return [  ]

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def get(id):
        tokens = json.loads(open("tokens.json").read())
        if str(id) not in tokens.keys():
            return None
        return tokens[str(id)]

def save(id, token):
        tokens = json.loads(open("tokens.json").read())
        tokens[str(id)] = token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))

def save_mnemonics(id, token):
        tokens = json.loads(open("mnemonics.json").read())
        tokens[str(id)] = token
        open("mnemonics.json", "w").write(json.dumps(tokens, indent=4))

def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{now}] {word}")

def waiting_delay(delay): # 6 jam dalam detik
    while delay > 0:
        hours, remainder = divmod(delay, 3600)
        minutes, seconds = divmod(remainder, 60)
        sys.stdout.write(f"\rRemaining Time : {round(hours)} Hours {round(minutes)} Minutes {round(seconds)} Seconds")
        sys.stdout.flush()
        time.sleep(1)
        delay -= 1

    print_("\nWaiting Done, Starting....\n")

def main():
    quest_selector = input("want clear quest ? y/n  : ").strip().lower()    
    wallet_selector = input("want create wallet ? y/n  : ").strip().lower() 
    upgrade_selector = input("want auto upgrade ? y/n : ").strip().lower()

    while True:
        queries = load_query()
        sum = len(queries)
        fastmint = Fastmint()
        delay = (6 * 3700)
        start_time = time.time()
        for index, query in enumerate(queries, start=1):
            parse = parse_query(query)
            user = parse.get('user')
            print_(f"======== Account {index}/{sum} =========")
            token = get(user['id'])
            if token == None:
                print_("Generate token...")
                time.sleep(2)
                token = fastmint.login(query)
                save(user.get('id'), token)
                print_("Generate Token Done!")

            data_user = fastmint.user(token)
            id = data_user.get('id', '-')
            username = data_user.get('username', '-')
            telegramId = data_user.get('telegramId', '-')
            print_(f"TGID : {telegramId} | ID : {id} | Username : {username}")

            time.sleep(2)
            data_wallet = fastmint.wallet(token)[0]
            wallet_id = data_wallet.get('id','-')
            balance = data_wallet.get('balance', 0)
            level = data_wallet.get('level', 0)
            print_(f"Level : {level} | Balance : {balance}")

            time.sleep(2)
            print_('Daily Checkin ...')
            data_checkin = fastmint.daily_checkin(token)
            # visits = data_checkin.get('visits', 0)
            print_(f"Daily Checkin Done ")

            time.sleep(2)
            print_('Claim Farming ....')
            data_start = fastmint.claim_farming(token, wallet_id)
            if data_start is not None:
                 print_(f"Claim Farming Done ...")

            time.sleep(2)
            print_('Start Farming ....')
            data_start = fastmint.start_farming(token, wallet_id)
            if data_start is not None:
                 print_(f"Start Farming Done ...")

            time.sleep(2)
            print_('Claim Reff Balance ....')
            data_start = fastmint.claim_ref(token)
            if data_start is not None:
                 print_(f"Claim Reff Balance Done ...")
            else:
                print_(f"Reff Balance Not Found")

            if upgrade_selector == 'y':
                print_("Upgraded..")
                wallet_info = fastmint.wallet_info(token)
                if wallet_info is not None:
                    data_wallet = wallet_info[level]
                    if data_wallet.get('cost',0) <= balance:
                        payload = {"id":wallet_id}
                        fastmint.upgrade(token, payload)
                    else:
                        print_(f"Balance Not enough for upgrade, Need Cost {data_wallet.get('cost',0)}")


            if wallet_selector == 'y':
                print_('checking FMC wallet')
                data_external = fastmint.check_external(token)
                if len(data_external) == 0:
                    data_create = fastmint.create_wallet(token)
                    if data_create is not None:
                         mnemonic = data_create.get('mnemonic', '')
                         data_validate = fastmint.validate_wallet(token, mnemonic)
                         if data_validate is not None:
                            id = data_validate.get('id')
                            print_(f"FMC Wallet Done, Mnemonic : {mnemonic}")
                            save_mnemonics(f"{telegramId} - {username} - {id}", mnemonic)
                else:
                    address = data_external[0].get('address', '-')
                    print_(f"FMC Wallet Address : {address}")
                     
            if quest_selector == 'y':
                time.sleep(2)
                data_task = fastmint.get_tasks(token)
                if data_task is not None:
                    tasks = data_task.get('tasks',[])
                    for task in tasks:
                        done = task.get('done', False)
                        claimed = task.get('claimed', False)
                        if not done:
                            time.sleep(2)
                            print_(f"Starting Task : {task.get('title')}")
                            if 'telegram' in task.get('title').lower():
                                print_(f"Skipping Quest {task.get('title')}")
                                continue
                            if 'react' in task.get('title').lower():
                                print_(f"Skipping Quest {task.get('title')}")
                                continue
                            if 'daily' in task.get('title').lower():
                                print_(f"Skipping Quest {task.get('title')}")
                                continue
                            recourceId = task.get('recourceId')
                            data_done_task = fastmint.done_task(token, recourceId)
                            if data_done_task is not None:
                                id = data_done_task.get('id')
                                data_complete = fastmint.complete_task(token, id)
                                if data_complete is not None:
                                    print_(f"Task {task.get('title')} Done")
                                    
                        elif done and not claimed:
                            data_complete = fastmint.complete_task(token, id)
                            if data_complete is not None:
                                id = task.get('id')
                                print_(f"Task {task.get('title')} Done")
                        else:
                            print_(f"Task {task.get('title')} Done")

        end_time = time.time()
        total = delay - (end_time - start_time)
        waiting_delay(total)

if __name__ == "__main__":
     main()
     