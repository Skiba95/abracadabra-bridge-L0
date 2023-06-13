from web3 import Web3
from contract_abi import con_abi
import time
import random
from colorama import Fore, Style

time_from = 0
time_to = 30

private_keys = []
with open("private_keys.txt", "r") as file:
    private_keys = [line.strip() for line in file.readlines()]

web3 = Web3(Web3.HTTPProvider("https://fantom.publicnode.com"))

contract_address = "0xc5c01568a3b5d8c203964049615401aaf0783191"

start_time = time.time()

# Создаем список для хранения кошельков без успешных транзакций
wallets_without_success = []

for index, private_key in enumerate(private_keys):
    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(
        address=web3.to_checksum_address(contract_address),
        abi=con_abi
    )

    address_bytes = bytes.fromhex(account.address[2:])  # Пропустить префикс '0x'
    address_bytes_32 = bytes(12) + address_bytes  # Добавить 12 нулевых байтов (32 - 20)

    tx_data = (
        "0x000200000000000000000000000000000000000000000000000000000000000186a"
        "00000000000000000000000000000000000000000000000000000000000000000"
        f"{account.address[2:]}"
    )

    adapter_params_bytes = bytes.fromhex(tx_data[2:])  # Пропустить префикс '0x'
    
    # Генерируем случайное количество транзакций
    num_transactions = random.randint(1, 3)  # Измените диапазон на необходимый
    
    # Выводим информацию о кошельке
    print()
    print(f"{Fore.MAGENTA}------------------------------------------------------{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Кошелек #{index+1}:{Style.RESET_ALL} {account.address}")
    print(f"{Fore.MAGENTA}------------------------------------------------------{Style.RESET_ALL}")
    print()
    
    wallet_has_success = False
    
    for i in range(num_transactions):
        value = contract.functions.estimateSendFee(
            167,
            address_bytes_32,
            100000000000000,
            True,
            tx_data
        ).call()

        value = int(value[0])

        # Генерируем случайное значение для отправки токена
        token_amount = random.uniform(0.0001, 0.0034)  # Измените значения на необходимый диапазон

        # Преобразуйте значение токена в целое число с соответствующей единицей измерения
        token_amount_wei = int(token_amount * 1e18)  # Пример: преобразование в wei

        transaction = contract.functions.sendFrom(
            account.address,
            167,
            address_bytes_32,
            token_amount_wei,  # Передайте преобразованное значение токена
            (account.address, "0x0000000000000000000000000000000000000000", tx_data)
        ).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 500000,
            'gasPrice': web3.to_wei('110', 'gwei'),
            'chainId': 250,
            'value': value
        })

        signed_tx = web3.eth.account.sign_transaction(
            transaction, 
            private_key=private_key
        )
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Транзакция #{i+1} хеш: {tx_hash.hex()}")

        # Выводим отчет о выполненной транзакции
        if tx_receipt['status']:
            print(f"{Fore.GREEN}Транзакция успешно выполнена.{Style.RESET_ALL}")
            print()
            wallet_has_success = True
        else:
            print(f"{Fore.RED}Транзакция не выполнена.{Style.RESET_ALL}")
            print()

        # Генерируем случайную задержку перед следующей транзакцией
        delay = random.uniform(time_from, time_to)
        print(f"{Fore.BLUE}Ожидание перед следующей транзакцией: {delay} сек.{Style.RESET_ALL}")
        time.sleep(delay)
    
    if not wallet_has_success:
        wallets_without_success.append(account.address)

# Выводим отчет о кошельках без успешных транзакций
print()
print(f"{Fore.BLUE} ------------------------------------------------------{Style.RESET_ALL}")
print(f"{Fore.BLUE}|----- Отчет о кошельках без успешных транзакций ------|")
print(f"{Fore.BLUE} ------------------------------------------------------{Style.RESET_ALL}")
print()
for index, wallet in enumerate(wallets_without_success):
    print(f"{Fore.CYAN}Кошелек #{index+1}:{Style.RESET_ALL} {wallet}")
    print(f"{Fore.MAGENTA}------------------------------------------------------{Style.RESET_ALL}")
print(f"{Fore.BLUE}------------------------------------------------------------{Style.RESET_ALL}")

# Выводим общее время выполнения
total_time = time.time() - start_time
print(f"{Fore.CYAN}Общее время выполнения: {total_time} сек.{Style.RESET_ALL}")
