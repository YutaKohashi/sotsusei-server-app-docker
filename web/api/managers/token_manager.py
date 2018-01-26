from web.models import TokenTable
from web.models import StoreTable
from web.models import EmployeeTable
import uuid
import datetime
import secrets


class TokenManager:

    def create_token_sid(self, sid):
        token = str(self.__create_token())
        TokenTable(sid=StoreTable(sid=sid), token=token).save()
        return token

    def create_token_eid(self, eid):
        token = str(self.__create_token())
        TokenTable(eid=EmployeeTable(eid=eid), token=token).save()
        return token

    def revocation_token(self, token):
        try:
            row = TokenTable.objects.filter(token=token).first()
            row.enabled = False  # 失効
            row.save()
        except Exception as e:
            print(e.args)
        return True

    # def revocation_tokens(self, tokens):
    #     for token in tokens:
    #         self.revocation_token(token)
    #     return True

    def check_by_eid(self, eid, requestToken):
        try:
            rows = TokenTable.objects.filter(eid=EmployeeTable(eid=eid), enabled=True)

            for row in rows:
                token = row.token
                if self.__compare_token(requestToken,token):
                    return True
        except Exception as e:
            print(e.args)
        return False


    def check_by_sid(self, sid, requestToken):
        try:
            rows = TokenTable.objects.filter(sid=StoreTable(sid=sid), enabled=True)
            for row in rows:
                token = row.token
                if self.__compare_token(requestToken,token):
                    return True
                    # return False
        except Exception as e:
            print(e.args)

        return False

    # tokenを発行するメソッド
    def __create_token(self):
        token = secrets.token_hex()
        print('token発行  :  ' + str(token))
        return token

    # token1　と token2 を比較するメソッド
    def __compare_token(self, token1, token2):
        return secrets.compare_digest(token1, token2)