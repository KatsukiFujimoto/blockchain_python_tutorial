import base58
import codecs
import hashlib

from ecdsa import NIST256p
from ecdsa import SigningKey

import utils

class Wallet(object):
    def __init__(self):
        self._private_key = SigningKey.generate(curve=NIST256p)
        self._public_key = self._private_key.get_verifying_key()
        self._blockchain_address = self.generate_blockchain_address()

    @property
    def private_key(self):
        return self._private_key.to_string().hex()

    @property
    def public_key(self):
        return self._public_key.to_string().hex()

    @property
    def blockchain_address(self):
        return self._blockchain_address

    # How to create blockchain address
    # 1. Creating a public key with ECDSA（公開鍵の作成）
    # 2. SHA-256 for the public key（公開鍵をハッシュ化）どうして後で二回やるのにここでもやるのか
    # 3. Ripemd160 for the SHA-256（公開鍵のハッシュを短縮化）
    # 4. Add network byte（メインとテストのネットワークの判別用情報を付与）
    # 5. Double SHA-256（ネットワーク情報を2度ハッシュ化）どうして二回もやるのか
    # 6. Get checksum
    # 7. Concatenate public key and checksum（データ信頼性を確かめるためにデータを付与する）
    # 8. Encoding the key with Base58（送信するため、データをエンコードする）
    def generate_blockchain_address(self):
        # 2
        public_key_bytes = self._public_key.to_string()
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        # 3
        ripemd160_bpk = hashlib.new('ripemd160')
        ripemd160_bpk.update(sha256_bpk_digest)
        ripemd160_bpk_digest = ripemd160_bpk.digest()
        ripemd160_bpk_hex = codecs.encode(ripemd160_bpk_digest, 'hex')
        # 4
        network_byte = b'00'
        network_bitcoin_public_key = network_byte + ripemd160_bpk_hex
        network_bitcoin_public_key_bytes = codecs.decode(network_bitcoin_public_key, 'hex')
        # 5
        sha256_bpk = hashlib.sha256(network_bitcoin_public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        sha256_2_nbpk = hashlib.sha256(sha256_bpk_digest)
        sha256_2_nbpk_digest = sha256_2_nbpk.digest()
        sha256_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')
        # 6
        checksum = sha256_hex[:8]
        # 7
        address_hex = (network_bitcoin_public_key + checksum).decode('utf-8')
        # 8
        blockchain_address = base58.b58encode(address_hex).decode('utf-8')
        return blockchain_address

class Transaction(object):
    def __init__(self, sender_private_key, sender_public_key,
                sender_blockchain_address, recipient_blockchain_address, value):
        self.sender_private_key = sender_private_key
        self.sender_public_key = sender_public_key
        self.sender_blockchain_address = sender_blockchain_address
        self.recipient_blockchain_address = recipient_blockchain_address
        self.value = value

    def generate_signature(self):
        # sha256 = hashlib.sha256()
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': self.sender_blockchain_address,
            'recipient_blockchain_address': self.recipient_blockchain_address,
            'value': float(self.value)
        })
        # sha256.update(str(transaction).encode('utf-8'))
        # message = sha256.digest()
        message = hashlib.sha256(str(transaction).encode()).digest()
        private_key = SigningKey.from_string(bytes().fromhex(self.sender_private_key), curve=NIST256p)
        private_key_sign = private_key.sign(message)
        signature = private_key_sign.hex()
        return signature

if __name__ == '__main__':
    # wallet = Wallet()
    # print(wallet.private_key)
    # print(wallet.public_key)
    # print(wallet.blockchain_address)
    # t = Transaction(wallet.private_key, wallet.public_key, wallet.blockchain_address, 'B', 1.0)
    # print(t.generate_signature())

    wallet_M = Wallet()
    wallet_A = Wallet()
    wallet_B = Wallet()
    t = Transaction(
        wallet_A.private_key,
        wallet_A.public_key,
        wallet_A.blockchain_address,
        wallet_B.blockchain_address,
        1.0)

    ########### Blockchain Node
    import blockchain
    block_chain = blockchain.BlockChain(blockchain_address = wallet_M.blockchain_address)
    is_added = block_chain.add_transaction(
        wallet_A.blockchain_address,
        wallet_B.blockchain_address,
        1.0,
        wallet_A.public_key,
        t.generate_signature())
    print('Added?', is_added)
    block_chain.mining()
    utils.pprint(block_chain.chain)
    print('A', block_chain.calculate_total_amount(wallet_A.blockchain_address))
    print('B', block_chain.calculate_total_amount(wallet_B.blockchain_address))
    print('M', block_chain.calculate_total_amount(wallet_M.blockchain_address))
