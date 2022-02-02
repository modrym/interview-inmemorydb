from main import Parser

import pytest


@pytest.fixture
def output():
    return []


@pytest.fixture
def parser(monkeypatch, output):
    parser_ = Parser()
    parser_.returned = None

    def log(arg):
        output.append(arg)

    monkeypatch.setattr(parser_, 'log', log)

    return parser_


def test_script1(parser, output):
    parser.parse_command('SET a 10')
    parser.parse_command('GET a')
    assert output[-1] == '10'
    parser.parse_command('DELETE a')
    parser.parse_command('GET a')
    assert output[-1] == 'NULL'


def test_script2(parser, output):
    parser.parse_command('SET a 10')
    parser.parse_command('SET b 10')
    parser.parse_command('COUNT 10')
    assert output[-1] == '2'
    parser.parse_command('COUNT 20')
    assert output[-1] == '0'
    parser.parse_command('DELETE a')
    parser.parse_command('COUNT 10')
    assert output[-1] == '1'
    parser.parse_command('SET b 30')
    parser.parse_command('COUNT 10')
    assert output[-1] == '0'


def test_script3(parser, output):
    parser.parse_command('BEGIN')
    parser.parse_command('SET a 10')
    parser.parse_command('GET a')
    assert output[-1] == '10'
    parser.parse_command('BEGIN')
    parser.parse_command('SET a 20')
    parser.parse_command('GET a')
    assert output[-1] == '20'
    parser.parse_command('ROLLBACK')
    parser.parse_command('GET a')
    assert output[-1] == '10'
    parser.parse_command('ROLLBACK')
    parser.parse_command('GET a')
    assert output[-1] == 'NULL'


def test_script4(parser, output):
    parser.parse_command('BEGIN')
    parser.parse_command('SET a 30')
    parser.parse_command('BEGIN')
    parser.parse_command('SET a 40')
    parser.parse_command('COMMIT')
    parser.parse_command('GET a')
    assert output[-1] == '40'
    parser.parse_command('ROLLBACK')
    assert output[-1] == 'NO TRANSACTION'


# def test_script5(parser, output):
#     parser.parse_command('SET a 50')
#     parser.parse_command('BEGIN')
#     parser.parse_command('GET a')
#     assert output[-1] == '50'
#     parser.parse_command('SET a 60')
