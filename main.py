import shlex


def _assert_num(cmd: list[str], num: int):
    """Function checks if the number of args is as expected"""
    assert len(cmd) == num


class TransactionStack:
    DEFAULT_VALUE = 'NULL'

    def __init__(self):
        self._memory = {}
        self._changes = []
        self._deletes = []

    def _no_transaction(self) -> bool:
        return not self._changes or not self._deletes

    def begin(self):
        self._changes.append({})
        self._deletes.append(set())

    def rollback(self) -> bool:
        if self._no_transaction():
            return False

        self._changes.pop()
        self._deletes.pop()

        return True

    def commit(self) -> bool:
        if self._no_transaction():
            return False

        while not self._no_transaction():
            changes = self._changes.pop()
            deletes = self._deletes.pop()

            for key, value in changes.items():
                self.set(key, value)

            for key in deletes:
                self.delete(key)

        return True

    def set(self, key: str, value: str) -> bool:
        if self._no_transaction():
            self._memory[key] = value
        else:
            if key in self._deletes[-1]:
                self._deletes[-1].remove(key)

            self._changes[-1][key] = value

        return True

    def delete(self, key: str) -> bool:
        if self._no_transaction():
            if key not in self._memory:
                return False

            del self._memory[key]
        else:
            if key in self._changes[-1]:
                del self._changes[-1][key]

            self._deletes[-1].add(key)

            return True

        return False

    def get(self, key: str) -> str:
        for ch, dl in list(zip(self._changes, self._deletes))[::-1]:
            if key in dl:
                return self.DEFAULT_VALUE

            if key in ch:
                return ch[key]

        return self._memory.get(key, self.DEFAULT_VALUE)

    @property
    def merged_memory(self):
        """Helper property for count function"""
        mem = self._memory.copy()

        for ch, dl in list(zip(self._changes, self._deletes)):
            for key, value in ch.items():
                mem[key] = value

            for key in dl:
                del mem[key]

        return mem

    def count(self, value: str) -> int:
        """This is very inefficient. I chose this implementation due to the
        fact that there were only a few minutes left. To be improved."""
        num = 0

        for key, value2 in self.merged_memory.items():
            if value == value2:
                num += 1

        return num


class Parser:
    def __init__(self):
        self._memory = TransactionStack()

    @staticmethod
    def log(arg):
        return print(arg)

    def parse_command(self, cmd):
        cmd = shlex.split(cmd)

        if not cmd:
            return

        try:
            if cmd[0] == 'GET':
                _assert_num(cmd, 2)
                self.cmd_get(cmd[1])
            elif cmd[0] == 'SET':
                _assert_num(cmd, 3)
                self.cmd_set(*cmd[1:])
            elif cmd[0] == 'DELETE':
                _assert_num(cmd, 2)
                self.cmd_delete(cmd[1])
            elif cmd[0] == 'BEGIN':
                _assert_num(cmd, 1)
                self.cmd_begin()
            elif cmd[0] == 'COMMIT':
                _assert_num(cmd, 1)
                self.cmd_commit()
            elif cmd[0] == 'ROLLBACK':
                _assert_num(cmd, 1)
                self.cmd_rollback()
            elif cmd[0] == 'COUNT':
                _assert_num(cmd, 2)
                self.cmd_count(cmd[1])
            else:
                self.log('WRONG COMMAND')
        except AssertionError:
            self.log('Wrong number of arguments.')

    def cmd_get(self, name: str):
        self.log(self._memory.get(name))

    def cmd_set(self, name: str, value: str):
        self._memory.set(name, value)

    def cmd_delete(self, name):
        self._memory.delete(name)

    def cmd_begin(self):
        self._memory.begin()

    def cmd_commit(self):
        if not self._memory.commit():
            self.log('NO TRANSACTION')

    def cmd_rollback(self):
        if not self._memory.rollback():
            self.log('NO TRANSACTION')

    def cmd_count(self, value: str):
        self.log(str(self._memory.count(value)))
